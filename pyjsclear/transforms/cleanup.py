"""Miscellaneous cleanup transforms.

- Empty if removal: ``if (expr) {}`` removed when expr is side-effect-free
- Optional catch binding: ``catch (e) {}`` to ``catch {}`` when e is unused
- Return undefined: ``return undefined;`` to ``return;``
- Var/let to const when binding is never reassigned
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_side_effect_free
from .base import Transform


if TYPE_CHECKING:
    from ..scope import Scope


class FunctionNodeType(StrEnum):
    """ESTree function node types."""

    DECLARATION = 'FunctionDeclaration'
    EXPRESSION = 'FunctionExpression'
    ARROW = 'ArrowFunctionExpression'


_FUNCTION_NODE_TYPES = frozenset(FunctionNodeType)


class EmptyIfRemover(Transform):
    """Remove empty if statements.

    - ``if (expr) {}`` with no else: removed (when expr is side-effect-free)
    - ``if (expr) {} else { body }``: rewritten to ``if (!expr) { body }``
    """

    def execute(self) -> bool:
        """Remove empty if-blocks, optionally flipping to the else branch."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> object | None:
            if node.get('type') != 'IfStatement':
                return None
            consequent = node.get('consequent')
            if not self._is_empty_block(consequent):
                return None
            alternate = node.get('alternate')
            if not alternate:
                if is_side_effect_free(node.get('test')):
                    self.set_changed()
                    return REMOVE
                return None
            # if (expr) {} else { body } -> if (!expr) { body }
            node['test'] = {
                'type': 'UnaryExpression',
                'operator': '!',
                'prefix': True,
                'argument': node['test'],
            }
            node['consequent'] = alternate
            node['alternate'] = None
            self.set_changed()
            return None

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    @staticmethod
    def _is_empty_block(node: dict | None) -> bool:
        """Return True if ``node`` is an empty BlockStatement."""
        if not isinstance(node, dict):
            return False
        if node.get('type') != 'BlockStatement':
            return False
        return not node.get('body')


class TrailingReturnRemover(Transform):
    """Remove trailing bare ``return;`` at the end of function bodies."""

    def execute(self) -> bool:
        """Strip redundant trailing return statements from function bodies."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            if node.get('type') not in _FUNCTION_NODE_TYPES:
                return
            body = node.get('body')
            if not isinstance(body, dict) or body.get('type') != 'BlockStatement':
                return
            statements = body.get('body')
            if not statements or not isinstance(statements, list):
                return
            last_statement = statements[-1]
            if (
                isinstance(last_statement, dict)
                and last_statement.get('type') == 'ReturnStatement'
                and last_statement.get('argument') is None
            ):
                statements.pop()
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


class OptionalCatchBinding(Transform):
    """Remove unused catch clause parameters (ES2019 optional catch binding)."""

    def execute(self) -> bool:
        """Nullify catch parameters that are never referenced in the body."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            if node.get('type') != 'CatchClause':
                return
            parameter = node.get('param')
            if not parameter or not is_identifier(parameter):
                return
            parameter_name = parameter['name']
            body = node.get('body')
            if not body:
                return
            if not self._is_name_used(body, parameter_name):
                node['param'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _is_name_used(self, subtree: dict, identifier_name: str) -> bool:
        """Return True if ``identifier_name`` appears anywhere in ``subtree``."""
        found = False

        def callback(node: dict, parent: dict | None) -> None:
            nonlocal found
            if found:
                return
            if is_identifier(node) and node.get('name') == identifier_name:
                found = True

        simple_traverse(subtree, callback)
        return found


class ReturnUndefinedCleanup(Transform):
    """Simplify ``return undefined;`` to ``return;``."""

    def execute(self) -> bool:
        """Replace explicit ``return undefined`` with bare ``return``."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            if node.get('type') != 'ReturnStatement':
                return
            argument = node.get('argument')
            if not argument:
                return
            if is_identifier(argument) and argument.get('name') == 'undefined':
                node['argument'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


class LetToConst(Transform):
    """Convert ``let`` declarations to ``const`` when the binding is never reassigned.

    Unlike ``var`` to ``const``, both ``let`` and ``const`` are block-scoped,
    so no additional block-position checks are needed.  Only converts when:
    - The declaration has exactly one declarator with an initializer
    - The binding has no assignments after declaration
    """

    def execute(self) -> bool:
        """Promote single-declarator ``let`` bindings to ``const`` when safe."""
        scope_tree = self.scope_tree if self.scope_tree is not None else build_scope_tree(self.ast)[0]
        safe_declarator_ids: set[int] = set()
        self._collect_let_const_candidates(scope_tree, safe_declarator_ids)

        if not safe_declarator_ids:
            return False

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            if node.get('type') != 'VariableDeclaration':
                return
            if node.get('kind') != 'let':
                return
            declarations = node.get('declarations', [])
            if len(declarations) == 1 and id(declarations[0]) in safe_declarator_ids:
                node['kind'] = 'const'
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _collect_let_const_candidates(
        self,
        scope: Scope,
        safe_declarator_ids: set[int],
    ) -> None:
        """Find ``let`` bindings that are never reassigned and have initializers."""
        for binding_name, binding in scope.bindings.items():
            if binding.kind != 'let':
                continue
            if binding.assignments:
                continue
            declaration_node = binding.node
            if not isinstance(declaration_node, dict):
                continue
            if declaration_node.get('type') != 'VariableDeclarator':
                continue
            if not declaration_node.get('init'):
                continue
            safe_declarator_ids.add(id(declaration_node))

        for child_scope in scope.children:
            self._collect_let_const_candidates(child_scope, safe_declarator_ids)


class VarToConst(Transform):
    """Convert ``var`` declarations to ``const`` when the binding is never reassigned.

    Only converts ``var`` to ``const`` when:
    - The declaration has exactly one declarator with an initializer
    - The binding has no assignments after declaration
    - The declaration is a direct child of a function body (not inside a
      nested block like if/for/try/switch), since ``var`` is function-scoped
      but ``const`` is block-scoped
    """

    def execute(self) -> bool:
        """Promote single-declarator ``var`` bindings to ``const`` when safe."""
        scope_tree = self.scope_tree if self.scope_tree is not None else build_scope_tree(self.ast)[0]
        safe_declarator_ids: set[int] = set()
        self._collect_const_candidates(scope_tree, safe_declarator_ids, in_function=True)

        if not safe_declarator_ids:
            return False

        function_body_ids: set[int] = set()
        self._collect_function_bodies(self.ast, function_body_ids)

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            if node.get('type') != 'VariableDeclaration':
                return
            if node.get('kind') != 'var':
                return
            if not parent:
                return
            if not self._is_safe_parent_for_var(parent, function_body_ids):
                return
            declarations = node.get('declarations', [])
            if len(declarations) == 1 and id(declarations[0]) in safe_declarator_ids:
                node['kind'] = 'const'
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    @staticmethod
    def _is_safe_parent_for_var(parent: dict, function_body_ids: set[int]) -> bool:
        """Return True if ``parent`` is a safe location to convert var to const."""
        match parent.get('type'):
            case 'Program':
                return True
            case 'BlockStatement':
                return id(parent) in function_body_ids
            case _:
                return False

    def _collect_function_bodies(self, ast: dict, function_body_ids: set[int]) -> None:
        """Collect ids of BlockStatements that are direct function bodies."""

        def callback(node: dict, parent: dict | None) -> None:
            if node.get('type') not in _FUNCTION_NODE_TYPES:
                return
            body = node.get('body')
            if body and body.get('type') == 'BlockStatement':
                function_body_ids.add(id(body))

        simple_traverse(ast, callback)

    def _collect_const_candidates(
        self,
        scope: Scope,
        safe_declarator_ids: set[int],
        in_function: bool = False,
    ) -> None:
        """Find ``var`` bindings that are never reassigned and have initializers."""
        if in_function:
            for binding_name, binding in scope.bindings.items():
                if binding.kind != 'var':
                    continue
                if binding.assignments:
                    continue
                declaration_node = binding.node
                if not isinstance(declaration_node, dict):
                    continue
                if declaration_node.get('type') != 'VariableDeclarator':
                    continue
                if not declaration_node.get('init'):
                    continue
                safe_declarator_ids.add(id(declaration_node))

        for child_scope in scope.children:
            self._collect_const_candidates(child_scope, safe_declarator_ids, in_function or child_scope.is_function)
