"""Miscellaneous cleanup transforms.

- Optional catch binding: `catch (e) {}` → `catch {}` when e is unused
- Return undefined: `return undefined;` → `return;`
- Var to const: `var x = ...` → `const x = ...` when x is never reassigned
"""

from ..scope import build_scope_tree
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


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
