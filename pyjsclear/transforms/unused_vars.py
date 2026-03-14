"""Remove unreferenced variables."""

from __future__ import annotations

from ..scope import BindingKind
from ..scope import Scope
from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import traverse
from ..utils.ast_helpers import get_child_keys
from .base import Transform


_SIDE_EFFECT_TYPES = frozenset(
    {
        'CallExpression',
        'NewExpression',
        'AssignmentExpression',
        'UpdateExpression',
    }
)
_PURE_TYPES = frozenset(
    {
        'Literal',
        'Identifier',
        'ThisExpression',
        'ArrayExpression',
        'ObjectExpression',
        'FunctionExpression',
        'ArrowFunctionExpression',
    }
)


class UnusedVariableRemover(Transform):
    """Remove variables with zero references after other transforms."""

    rebuild_scope = True

    def execute(self) -> bool:
        """Run the unused-variable removal pass and return whether anything changed."""
        if self.scope_tree is not None:
            scope_tree = self.scope_tree
        else:
            scope_tree, _ = build_scope_tree(self.ast)

        declarators_to_remove: set[int] = set()
        functions_to_remove: set[int] = set()
        self._collect_unused(scope_tree, declarators_to_remove, functions_to_remove)

        if not declarators_to_remove and not functions_to_remove:
            return False

        self._batch_remove(declarators_to_remove, functions_to_remove)
        return self.has_changed()

    def _collect_unused(
        self,
        scope: Scope,
        declarator_ids: set[int],
        function_ids: set[int],
    ) -> None:
        """Walk the scope tree and record ids of unused declarators and functions."""
        is_global = scope.parent is None

        for name, binding in scope.bindings.items():
            if binding.references or binding.kind == BindingKind.PARAM:
                continue
            if is_global and not name.startswith('_0x'):
                continue

            node = binding.node
            if not isinstance(node, dict):
                continue

            node_type = node.get('type')
            match node_type:
                case 'VariableDeclarator':
                    initializer = node.get('init')
                    if not initializer or not self._has_side_effects(initializer):
                        declarator_ids.add(id(node))
                case 'FunctionDeclaration':
                    function_ids.add(id(node))

        for child_scope in scope.children:
            self._collect_unused(child_scope, declarator_ids, function_ids)

    def _batch_remove(
        self,
        declarators_to_remove: set[int],
        functions_to_remove: set[int],
    ) -> None:
        """Remove all collected unused declarations in a single traversal."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> object:
            """Visitor callback that removes unused variable and function declarations."""
            node_type = node.get('type')

            if node_type == 'FunctionDeclaration' and id(node) in functions_to_remove:
                self.set_changed()
                return REMOVE

            if node_type != 'VariableDeclaration':
                return None

            declarations = node.get('declarations')
            if not declarations:
                return None

            filtered_declarations = [
                declarator for declarator in declarations if id(declarator) not in declarators_to_remove
            ]
            if len(filtered_declarations) == len(declarations):
                return None

            self.set_changed()
            if not filtered_declarations:
                return REMOVE

            node['declarations'] = filtered_declarations
            return None

        traverse(self.ast, {'enter': enter})

    def _has_side_effects(self, node: dict) -> bool:
        """Conservative check -- returns True if the expression may have side effects."""
        if not isinstance(node, dict):
            return False

        node_type = node.get('type', '')
        if node_type in _SIDE_EFFECT_TYPES:
            return True
        if node_type in _PURE_TYPES:
            return False

        # Recurse into children (ArrayExpression, ObjectExpression, BinaryExpression, etc.)
        for child_key in get_child_keys(node):
            child = node.get(child_key)
            if child is None:
                continue
            if isinstance(child, list):
                if any(isinstance(item, dict) and self._has_side_effects(item) for item in child):
                    return True
            elif isinstance(child, dict) and self._has_side_effects(child):
                return True

        return False
