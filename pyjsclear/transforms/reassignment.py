"""Remove redundant variable reassignments.

Detects: var x = y; (where y is also a variable)
And replaces all references to x with y, then removes x.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


if TYPE_CHECKING:
    from ..scope import Binding
    from ..scope import Scope


class _NodeType(StrEnum):
    """ESTree AST node types used by this module."""

    ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
    EXPRESSION_STATEMENT = 'ExpressionStatement'
    IDENTIFIER = 'Identifier'
    VARIABLE_DECLARATOR = 'VariableDeclarator'


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

    def execute(self) -> bool:
        """Run reassignment removal and alias inlining. Return True if AST was modified."""
        if self.scope_tree is not None:
            scope_tree = self.scope_tree
        else:
            scope_tree, _ = build_scope_tree(self.ast)
        self._process_scope(scope_tree)
        self._inline_assignment_aliases(scope_tree)
        return self.has_changed()

    def _is_valid_inline_target(self, scope: Scope, target_name: str) -> bool:
        """Check whether target_name is safe to inline (constant binding or well-known global)."""
        target_binding = scope.get_binding(target_name)
        if target_binding and not target_binding.is_constant:
            return False
        if not target_binding and target_name not in self._WELL_KNOWN_GLOBALS:
            return False
        return True

    def _replace_references(
        self,
        references: list[tuple[dict, dict | None, str | None, int | None]],
        target_name: str,
        *,
        skip_writes: bool = False,
    ) -> None:
        """Replace identifier references with a new identifier pointing to target_name."""
        for reference_node, reference_parent, reference_key, reference_index in references:
            if skip_writes and reference_parent:
                parent_type = reference_parent.get('type')
                if parent_type == _NodeType.ASSIGNMENT_EXPRESSION and reference_key == 'left':
                    continue
                if parent_type == _NodeType.VARIABLE_DECLARATOR and reference_key == 'id':
                    continue

            new_identifier = {'type': _NodeType.IDENTIFIER, 'name': target_name}
            if reference_index is not None:
                reference_parent[reference_key][reference_index] = new_identifier
            else:
                reference_parent[reference_key] = new_identifier
            self.set_changed()

    def _process_scope(self, scope: Scope) -> None:
        """Inline constant `var x = y` declarations, replacing all reads of x with y."""
        for name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue
            if binding.kind == 'param':
                continue

            target_name = self._get_simple_init_target(binding)
            if target_name is None or target_name == name:
                continue
            if not self._is_valid_inline_target(scope, target_name):
                continue

            self._replace_references(binding.references, target_name, skip_writes=True)

        for child in scope.children:
            self._process_scope(child)

    def _get_simple_init_target(self, binding: Binding) -> str | None:
        """Return the identifier name from a simple `var x = y` init, or None."""
        node = binding.node
        if not isinstance(node, dict) or node.get('type') != _NodeType.VARIABLE_DECLARATOR:
            return None

        declaration_id = node.get('id')
        if not declaration_id or declaration_id.get('type') != _NodeType.IDENTIFIER:
            return None

        initializer = node.get('init')
        if not initializer or not is_identifier(initializer):
            return None

        return initializer.get('name', '')

    def _inline_assignment_aliases(self, scope_tree: Scope) -> None:
        """Inline aliases created by `var x; ... x = y;` patterns.

        Handles the obfuscator pattern where a variable is declared without
        init, then assigned once to another identifier, and only read after that.
        """
        self._process_assignment_aliases(scope_tree)

    def _remove_assignment_statement(self, assignment_node: dict) -> None:
        """Remove the ExpressionStatement containing the given assignment expression."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> object | None:
            if node.get('type') == _NodeType.EXPRESSION_STATEMENT and node.get('expression') is assignment_node:
                self.set_changed()
                return REMOVE
            return None

        traverse(self.ast, {'enter': enter})

    def _process_assignment_aliases(self, scope: Scope) -> None:
        """Inline `var x; x = y;` patterns by replacing reads of x with y."""
        for name, binding in list(scope.bindings.items()):
            if binding.is_constant or binding.kind == 'param':
                continue

            node = binding.node
            if not isinstance(node, dict) or node.get('type') != _NodeType.VARIABLE_DECLARATOR:
                continue

            # Must be declared without init: `var x;`
            if node.get('init') is not None:
                continue

            writes, reads = self._partition_references(binding)
            if len(writes) != 1:
                continue

            # The single write must be: x = <identifier>
            _, write_parent, _, _ = writes[0]
            right_hand_side = write_parent.get('right')
            if not right_hand_side or not is_identifier(right_hand_side):
                continue

            target_name = right_hand_side['name']
            if target_name == name:
                continue
            if not self._is_valid_inline_target(scope, target_name):
                continue

            self._replace_references(reads, target_name)
            self._remove_assignment_statement(write_parent)

        for child in scope.children:
            self._process_assignment_aliases(child)

    @staticmethod
    def _partition_references(
        binding: Binding,
    ) -> tuple[
        list[tuple[dict, dict | None, str | None, int | None]],
        list[tuple[dict, dict | None, str | None, int | None]],
    ]:
        """Split binding references into writes (left-hand assignments) and reads."""
        writes: list[tuple[dict, dict | None, str | None, int | None]] = []
        reads: list[tuple[dict, dict | None, str | None, int | None]] = []
        for reference in binding.references:
            reference_node, reference_parent, reference_key, reference_index = reference
            if (
                reference_parent
                and reference_parent.get('type') == _NodeType.ASSIGNMENT_EXPRESSION
                and reference_key == 'left'
            ):
                writes.append(reference)
            else:
                reads.append(reference)
        return writes, reads
