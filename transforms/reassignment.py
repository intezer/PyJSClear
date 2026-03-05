"""Remove redundant variable reassignments.

Detects: var x = y; (where y is also a variable)
And replaces all references to x with y, then removes x.
"""

from .base import Transform
from ..scope import build_scope_tree
from ..utils.ast_helpers import is_identifier, deep_copy


class ReassignmentRemover(Transform):
    """Remove redundant reassignments like x = y where y is used identically."""

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        self._process_scope(scope_tree)
        return self.has_changed()

    def _process_scope(self, scope):
        for name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue
            if binding.kind == 'param':
                continue

            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue

            init = node.get('init')
            if not init or not is_identifier(init):
                continue

            target_name = init.get('name', '')
            target_binding = scope.get_binding(target_name)
            if not target_binding:
                continue
            if not target_binding.is_constant:
                continue

            # Replace all references to `name` with `target_name`
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if ref_parent and ref_parent.get('type') == 'AssignmentExpression' and ref_key == 'left':
                    continue
                if ref_parent and ref_parent.get('type') == 'VariableDeclarator' and ref_key == 'id':
                    continue
                new_id = {'type': 'Identifier', 'name': target_name}
                if ref_index is not None:
                    ref_parent[ref_key][ref_index] = new_id
                else:
                    ref_parent[ref_key] = new_id
                self.set_changed()

        for child in scope.children:
            self._process_scope(child)
