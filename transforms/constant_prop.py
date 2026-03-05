"""Constant propagation — replace references to constant variables with their literal values."""

import copy
from .base import Transform
from ..traverser import traverse, SKIP
from ..scope import build_scope_tree
from ..utils.ast_helpers import is_literal, is_identifier, deep_copy


class ConstantProp(Transform):
    """Find `const x = <literal>` and replace all references with the literal."""

    rebuild_scope = True

    def execute(self):
        scope_tree, node_scope = build_scope_tree(self.ast)

        # Find constant bindings with literal values
        replacements = {}  # name -> literal_node
        to_remove = []  # (parent_body_list, index) of declarations to remove

        def _find_constants(scope):
            for name, binding in scope.bindings.items():
                if not binding.is_constant:
                    continue
                # Check if it has a literal init value
                node = binding.node
                init_val = None
                if isinstance(node, dict) and node.get('type') == 'VariableDeclarator':
                    init_val = node.get('init')
                if init_val and is_literal(init_val):
                    # Don't propagate if name shadows a global or has too many refs
                    replacements[id(binding)] = (binding, init_val)

            for child in scope.children:
                _find_constants(child)

        _find_constants(scope_tree)

        if not replacements:
            return False

        # Replace references
        bindings_replaced = set()
        for bind_id, (binding, literal) in replacements.items():
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if ref_parent and ref_parent.get('type') == 'AssignmentExpression' and ref_key == 'left':
                    continue  # Don't replace assignment targets
                if ref_parent and ref_parent.get('type') == 'UpdateExpression':
                    continue
                if ref_parent and ref_parent.get('type') == 'VariableDeclarator' and ref_key == 'id':
                    continue
                # Replace
                new_node = deep_copy(literal)
                if ref_index is not None:
                    ref_parent[ref_key][ref_index] = new_node
                else:
                    ref_parent[ref_key] = new_node
                self.set_changed()
                bindings_replaced.add(bind_id)

        # Remove declarations that were fully propagated
        for bind_id in bindings_replaced:
            binding = replacements[bind_id][0]
            if binding.assignments:
                continue  # has reassignments, don't remove
            # Remove the declaration
            decl_node = binding.node
            if isinstance(decl_node, dict) and decl_node.get('type') == 'VariableDeclarator':
                # Find the VariableDeclaration parent and remove this declarator
                self._remove_declarator(decl_node)

        return self.has_changed()

    def _remove_declarator(self, declarator_node):
        """Remove a VariableDeclarator from its parent VariableDeclaration."""
        def enter(node, parent, key, index):
            if node.get('type') == 'VariableDeclaration':
                decls = node.get('declarations', [])
                for i, d in enumerate(decls):
                    if d is declarator_node:
                        decls.pop(i)
                        self.set_changed()
                        # If no more declarators, mark for removal
                        if not decls:
                            from ..traverser import REMOVE
                            return REMOVE
                        return SKIP
        traverse(self.ast, {'enter': enter})
