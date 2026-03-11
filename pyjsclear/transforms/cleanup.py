"""Miscellaneous cleanup transforms.

- Empty if removal: `if (expr) {}` → removed when expr is side-effect-free
- Optional catch binding: `catch (e) {}` → `catch {}` when e is unused
- Return undefined: `return undefined;` → `return;`
- Var to const: `var x = ...` → `const x = ...` when x is never reassigned
"""

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


def _is_side_effect_free(node):
    """Check if an expression node is side-effect-free (safe to discard)."""
    if not isinstance(node, dict):
        return False
    t = node.get('type')
    if t == 'Literal':
        return True
    if t == 'Identifier':
        return True
    if t == 'MemberExpression':
        return _is_side_effect_free(node.get('object')) and (
            not node.get('computed') or _is_side_effect_free(node.get('property'))
        )
    if t == 'UnaryExpression':
        if node.get('operator') in ('-', '+', '!', '~', 'typeof', 'void'):
            return _is_side_effect_free(node.get('argument'))
    if t == 'BinaryExpression' or t == 'LogicalExpression':
        return _is_side_effect_free(node.get('left')) and _is_side_effect_free(node.get('right'))
    if t == 'ConditionalExpression':
        return (
            _is_side_effect_free(node.get('test'))
            and _is_side_effect_free(node.get('consequent'))
            and _is_side_effect_free(node.get('alternate'))
        )
    return False


class EmptyIfRemover(Transform):
    """Remove empty if statements.

    - ``if (expr) {}`` with no else → removed (when expr is side-effect-free)
    - ``if (expr) {} else { body }`` → ``if (!expr) { body }``
    """

    def execute(self):

        def enter(node, parent, key, index):
            if node.get('type') != 'IfStatement':
                return
            consequent = node.get('consequent')
            if not self._is_empty_block(consequent):
                return
            alternate = node.get('alternate')
            if not alternate:
                # if (expr) {} — remove entirely if test is pure
                if _is_side_effect_free(node.get('test')):
                    self.set_changed()
                    return REMOVE
            else:
                # if (expr) {} else { body } → if (!expr) { body }
                node['test'] = {
                    'type': 'UnaryExpression',
                    'operator': '!',
                    'prefix': True,
                    'argument': node['test'],
                }
                node['consequent'] = alternate
                node['alternate'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    @staticmethod
    def _is_empty_block(node):
        """Check if a node is an empty block statement ``{}``."""
        if not isinstance(node, dict):
            return False
        if node.get('type') != 'BlockStatement':
            return False
        body = node.get('body')
        return not body or len(body) == 0


class TrailingReturnRemover(Transform):
    """Remove trailing ``return;`` at the end of function bodies.

    A bare ``return;`` as the last statement of a function or method body
    has no effect and can be removed for cleaner output.
    """

    _FUNC_TYPES = frozenset({'FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'})

    def execute(self):

        def enter(node, parent, key, index):
            if node.get('type') not in self._FUNC_TYPES:
                return
            body = node.get('body')
            if not isinstance(body, dict) or body.get('type') != 'BlockStatement':
                return
            stmts = body.get('body')
            if not stmts or not isinstance(stmts, list):
                return
            last = stmts[-1]
            if isinstance(last, dict) and last.get('type') == 'ReturnStatement' and last.get('argument') is None:
                stmts.pop()
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


class OptionalCatchBinding(Transform):
    """Remove unused catch clause parameters (ES2019 optional catch binding)."""

    def execute(self):

        def enter(node, parent, key, index):
            if node.get('type') != 'CatchClause':
                return
            param = node.get('param')
            if not param or not is_identifier(param):
                return
            param_name = param['name']
            body = node.get('body')
            if not body:
                return
            # Check if param_name is referenced anywhere in the catch body
            if not self._is_name_used(body, param_name):
                node['param'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _is_name_used(self, body, name):
        """Check if an identifier name is used anywhere in the subtree."""
        found = [False]

        def cb(node, parent):
            if found[0]:
                return
            if is_identifier(node) and node.get('name') == name:
                found[0] = True

        simple_traverse(body, cb)
        return found[0]


class ReturnUndefinedCleanup(Transform):
    """Simplify `return undefined;` to `return;`."""

    def execute(self):

        def enter(node, parent, key, index):
            if node.get('type') != 'ReturnStatement':
                return
            arg = node.get('argument')
            if not arg:
                return
            if is_identifier(arg) and arg.get('name') == 'undefined':
                node['argument'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


class LetToConst(Transform):
    """Convert ``let`` declarations to ``const`` when the binding is never reassigned.

    Unlike ``var`` → ``const``, both ``let`` and ``const`` are block-scoped,
    so no additional block-position checks are needed.  Only converts when:
    - The declaration has exactly one declarator with an initializer
    - The binding has no assignments after declaration
    """

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        safe_declarators = set()
        self._collect_let_const_candidates(scope_tree, safe_declarators)

        if not safe_declarators:
            return False

        def enter(node, parent, key, index):
            if node.get('type') != 'VariableDeclaration':
                return
            if node.get('kind') != 'let':
                return
            decls = node.get('declarations', [])
            if len(decls) == 1 and id(decls[0]) in safe_declarators:
                node['kind'] = 'const'
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _collect_let_const_candidates(self, scope, safe_declarators):
        """Find let bindings that are never reassigned and have initializers."""
        for name, binding in scope.bindings.items():
            if binding.kind != 'let':
                continue
            if binding.assignments:
                continue
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            if not node.get('init'):
                continue
            safe_declarators.add(id(node))

        for child in scope.children:
            self._collect_let_const_candidates(child, safe_declarators)


class VarToConst(Transform):
    """Convert `var` declarations to `const` when the binding is never reassigned.

    Only converts `var` to `const` when:
    - The declaration has exactly one declarator with an initializer
    - The binding has no assignments after declaration
    - The declaration is a direct child of a function body (not inside a
      nested block like if/for/try/switch), since var is function-scoped
      but const is block-scoped
    """

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        safe_declarators = set()
        self._collect_const_candidates(scope_tree, safe_declarators)

        if not safe_declarators:
            return False

        # Track which BlockStatements are direct function bodies
        func_body_ids = set()
        self._collect_func_bodies(self.ast, func_body_ids)

        def enter(node, parent, key, index):
            if node.get('type') != 'VariableDeclaration':
                return
            if node.get('kind') != 'var':
                return
            # Only convert if parent is a function body or Program
            if not parent:
                return
            parent_type = parent.get('type')
            if parent_type == 'BlockStatement':
                if id(parent) not in func_body_ids:
                    return  # Inside a nested block — unsafe
            else:
                return
            decls = node.get('declarations', [])
            if len(decls) == 1 and id(decls[0]) in safe_declarators:
                node['kind'] = 'const'
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _collect_func_bodies(self, ast, func_body_ids):
        """Collect ids of BlockStatements that are direct function bodies."""

        def cb(node, parent):
            if node.get('type') in ('FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'):
                body = node.get('body')
                if body and body.get('type') == 'BlockStatement':
                    func_body_ids.add(id(body))

        simple_traverse(ast, cb)

    def _collect_const_candidates(self, scope, safe_declarators, in_function=False):
        """Find var bindings that are never reassigned and have initializers."""
        if in_function:
            for name, binding in scope.bindings.items():
                if binding.kind != 'var':
                    continue
                if binding.assignments:
                    continue
                node = binding.node
                if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                    continue
                if not node.get('init'):
                    continue
                safe_declarators.add(id(node))

        for child in scope.children:
            self._collect_const_candidates(child, safe_declarators, in_function or child.is_function)
