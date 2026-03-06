"""Remove redundant variable reassignments.

Detects: var x = y; (where y is also a variable)
And replaces all references to x with y, then removes x.
"""

from ..scope import build_scope_tree
from ..utils.ast_helpers import is_identifier
from .base import Transform


class ReassignmentRemover(Transform):
    """Remove redundant reassignments like x = y where y is used identically."""

    # Well-known globals that are safe to inline as reassignment targets
    _WELL_KNOWN_GLOBALS = frozenset(
        {
            'JSON',
            'Object',
            'Array',
            'String',
            'Number',
            'Boolean',
            'Math',
            'Date',
            'RegExp',
            'Error',
            'Map',
            'Set',
            'WeakMap',
            'WeakSet',
            'Promise',
            'Symbol',
            'Proxy',
            'Reflect',
            'console',
            'parseInt',
            'parseFloat',
            'isNaN',
            'isFinite',
            'Buffer',
            'process',
            'require',
            'undefined',
            'NaN',
            'Infinity',
        }
    )

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        self._process_scope(scope_tree)
        self._inline_assignment_aliases(scope_tree)
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
            if target_name == name:
                continue
            target_binding = scope.get_binding(target_name)
            # Allow inlining if target is a well-known global or a constant binding
            if target_binding:
                if not target_binding.is_constant:
                    continue
            elif target_name not in self._WELL_KNOWN_GLOBALS:
                continue

            # Replace all references to `name` with `target_name`
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if (
                    ref_parent
                    and ref_parent.get('type') == 'AssignmentExpression'
                    and ref_key == 'left'
                ):
                    continue
                if (
                    ref_parent
                    and ref_parent.get('type') == 'VariableDeclarator'
                    and ref_key == 'id'
                ):
                    continue
                new_id = {'type': 'Identifier', 'name': target_name}
                if ref_index is not None:
                    ref_parent[ref_key][ref_index] = new_id
                else:
                    ref_parent[ref_key] = new_id
                self.set_changed()

        for child in scope.children:
            self._process_scope(child)

    def _inline_assignment_aliases(self, scope_tree):
        """Inline aliases created by `var x; ... x = y;` patterns.

        Handles the obfuscator pattern where a variable is declared without
        init, then assigned once to another identifier, and only read after that.
        """
        self._process_assignment_aliases(scope_tree)

    def _remove_assignment_statement(self, assignment_node):
        """Remove the ExpressionStatement containing the given assignment expression."""
        from ..traverser import REMOVE, traverse

        def enter(node, parent, key, index):
            if (
                node.get('type') == 'ExpressionStatement'
                and node.get('expression') is assignment_node
            ):
                self.set_changed()
                return REMOVE

        traverse(self.ast, {'enter': enter})

    def _process_assignment_aliases(self, scope):
        for name, binding in list(scope.bindings.items()):
            if binding.is_constant or binding.kind == 'param':
                continue

            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue

            # Must be declared without init: `var x;`
            if node.get('init') is not None:
                continue

            # Look for exactly one write (assignment) in references
            writes = []
            reads = []
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if (
                    ref_parent
                    and ref_parent.get('type') == 'AssignmentExpression'
                    and ref_key == 'left'
                ):
                    writes.append((ref_node, ref_parent, ref_key, ref_index))
                else:
                    reads.append((ref_node, ref_parent, ref_key, ref_index))

            if len(writes) != 1:
                continue

            # The single write must be: x = <identifier>
            _, write_parent, _, _ = writes[0]
            rhs = write_parent.get('right')
            if not rhs or not is_identifier(rhs):
                continue

            target_name = rhs['name']
            if target_name == name:
                continue

            # The target must be constant or a well-known global
            target_binding = scope.get_binding(target_name)
            if target_binding:
                if not target_binding.is_constant:
                    continue
            elif target_name not in self._WELL_KNOWN_GLOBALS:
                continue

            # Replace all reads of `name` with `target_name`
            for ref_node, ref_parent, ref_key, ref_index in reads:
                new_id = {'type': 'Identifier', 'name': target_name}
                if ref_index is not None:
                    ref_parent[ref_key][ref_index] = new_id
                else:
                    ref_parent[ref_key] = new_id
                self.set_changed()

            self._remove_assignment_statement(write_parent)

        for child in scope.children:
            self._process_assignment_aliases(child)
