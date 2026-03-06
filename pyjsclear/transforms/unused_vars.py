"""Remove unreferenced variables."""

from .base import Transform
from ..traverser import traverse, REMOVE
from ..scope import build_scope_tree


class UnusedVariableRemover(Transform):
    """Remove variables with 0 references after other transforms."""

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        self._remove_unused(scope_tree)
        return self.has_changed()

    def _remove_unused(self, scope):
        # For global scope, only remove known-internal names (decoder artifacts)
        # that are clearly not exports (e.g. _0x prefixed obfuscator names).
        skip_global = scope.parent is None

        for name, binding in list(scope.bindings.items()):
            if not binding.references and binding.kind != 'param':
                # In global scope, only remove obfuscator-internal names (_0x...)
                if skip_global and not name.startswith('_0x'):
                    continue
                # No references - remove the declaration
                node = binding.node
                if isinstance(node, dict) and node.get('type') == 'VariableDeclarator':
                    self._remove_declarator(node)
                elif isinstance(node, dict) and node.get('type') == 'FunctionDeclaration':
                    self._remove_function_decl(node)

        for child in scope.children:
            self._remove_unused(child)

    def _remove_declarator(self, declarator):
        """Remove a VariableDeclarator from its parent."""
        def enter(node, parent, key, index):
            if node.get('type') == 'VariableDeclaration':
                decls = node.get('declarations', [])
                for i, d in enumerate(decls):
                    if d is declarator:
                        # Check if init has side effects
                        init = d.get('init')
                        if init and self._has_side_effects(init):
                            return  # Keep it
                        decls.pop(i)
                        self.set_changed()
                        if not decls:
                            return REMOVE
                        return
        traverse(self.ast, {'enter': enter})

    def _remove_function_decl(self, func_node):
        """Remove a FunctionDeclaration."""
        def enter(node, parent, key, index):
            if node is func_node:
                self.set_changed()
                return REMOVE
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
        if ntype in ('ArrayExpression', 'ObjectExpression', 'FunctionExpression',
                      'ArrowFunctionExpression'):
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
