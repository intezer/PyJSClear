"""Remove unreferenced variables."""

from ..scope import build_scope_tree
from ..traverser import REMOVE, traverse
from .base import Transform


class UnusedVariableRemover(Transform):
    """Remove variables with 0 references after other transforms."""

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        declarators_to_remove = set()
        functions_to_remove = set()
        self._collect_unused(scope_tree, declarators_to_remove, functions_to_remove)
        if not declarators_to_remove and not functions_to_remove:
            return False
        self._batch_remove(declarators_to_remove, functions_to_remove)
        return self.has_changed()

    def _collect_unused(self, scope, declarators, functions):
        skip_global = scope.parent is None

        for name, binding in scope.bindings.items():
            if not binding.references and binding.kind != 'param':
                if skip_global and not name.startswith('_0x'):
                    continue
                node = binding.node
                if isinstance(node, dict):
                    ntype = node.get('type')
                    if ntype == 'VariableDeclarator':
                        init = node.get('init')
                        if not init or not self._has_side_effects(init):
                            declarators.add(id(node))
                    elif ntype == 'FunctionDeclaration':
                        functions.add(id(node))

        for child in scope.children:
            self._collect_unused(child, declarators, functions)

    def _batch_remove(self, declarators_to_remove, functions_to_remove):
        """Remove all collected unused declarations in a single traversal."""

        def enter(node, parent, key, index):
            ntype = node.get('type')
            if ntype == 'FunctionDeclaration' and id(node) in functions_to_remove:
                self.set_changed()
                return REMOVE
            if ntype == 'VariableDeclaration':
                decls = node.get('declarations')
                if decls:
                    new_decls = [d for d in decls if id(d) not in declarators_to_remove]
                    if len(new_decls) < len(decls):
                        self.set_changed()
                        if not new_decls:
                            return REMOVE
                        node['declarations'] = new_decls

        traverse(self.ast, {'enter': enter})

    def _has_side_effects(self, node):
        """Conservative check for side effects in an expression."""
        if not isinstance(node, dict):
            return False
        ntype = node.get('type', '')
        if ntype == 'CallExpression':
            return True
        if ntype == 'NewExpression':
            return True
        if ntype == 'AssignmentExpression':
            return True
        if ntype == 'UpdateExpression':
            return True
        if ntype in ('Literal', 'Identifier', 'ThisExpression'):
            return False
        if ntype in (
            'ArrayExpression',
            'ObjectExpression',
            'FunctionExpression',
            'ArrowFunctionExpression',
        ):
            return False
        # For binary/unary, check children
        from ..utils.ast_helpers import get_child_keys

        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, dict) and self._has_side_effects(item):
                        return True
            elif isinstance(child, dict) and self._has_side_effects(child):
                return True
        return False
