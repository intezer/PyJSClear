"""Constant propagation — replace references to constant variables with their literal values."""

from __future__ import annotations

from collections.abc import Iterator

from ..scope import Binding
from ..scope import Scope
from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import SKIP
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_literal
from .base import Transform


def _should_skip_reference(reference_parent: dict | None, reference_key: str | None) -> bool:
    """Return True if this reference should not be replaced with its literal value."""
    if not reference_parent:
        return True
    match reference_parent.get('type'):
        case 'AssignmentExpression' if reference_key == 'left':
            return True
        case 'UpdateExpression':
            return True
        case 'VariableDeclarator' if reference_key == 'id':
            return True
    return False


def _batch_remove_declarators(
    ast: dict,
    declarator_nodes: set[int],
    set_changed: callable,
) -> None:
    """Remove multiple VariableDeclarators in a single AST traversal.

    *declarator_nodes* is a set of id() values for the declarator dicts to remove.
    """
    if not declarator_nodes:
        return

    def enter(
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> str | None:
        if node.get('type') != 'VariableDeclaration':
            return None
        declarations = node.get('declarations', [])
        original_len = len(declarations)
        # Filter in-place, keeping only non-target declarators
        kept = [d for d in declarations if id(d) not in declarator_nodes]
        if len(kept) == original_len:
            return None
        set_changed()
        if not kept:
            return REMOVE
        declarations[:] = kept
        return SKIP

    traverse(ast, {'enter': enter})


class ConstantProp(Transform):
    """Find `const x = <literal>` and replace all references with the literal."""

    rebuild_scope = True

    def execute(self) -> bool:
        """Run constant propagation over the AST. Return True if any change was made."""
        scope_tree = self.scope_tree if self.scope_tree is not None else build_scope_tree(self.ast)[0]

        replacements = dict(self._iter_constant_bindings(scope_tree))
        if not replacements:
            return False

        bindings_replaced = self._replace_references(replacements)
        self._remove_fully_propagated(replacements, bindings_replaced)
        return self.has_changed()

    def _iter_constant_bindings(self, scope: Scope) -> Iterator[tuple[int, tuple[Binding, dict]]]:
        """Yield (binding_id, (binding, literal)) for constant bindings with literal init values."""
        for _name, binding in scope.bindings.items():
            if not binding.is_constant:
                continue
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            initial_value = node.get('init')
            if not initial_value or not is_literal(initial_value):
                continue
            yield id(binding), (binding, initial_value)

        for child in scope.children:
            yield from self._iter_constant_bindings(child)

    def _replace_references(self, replacements: dict[int, tuple[Binding, dict]]) -> set[int]:
        """Replace all qualifying references with their literal values."""
        bindings_replaced: set[int] = set()
        for binding_id, (binding, literal) in replacements.items():
            for reference_node, reference_parent, reference_key, reference_index in binding.references:
                if _should_skip_reference(reference_parent, reference_key):
                    continue
                new_node = deep_copy(literal)
                if reference_index is not None:
                    reference_parent[reference_key][reference_index] = new_node
                else:
                    reference_parent[reference_key] = new_node
                self.set_changed()
                bindings_replaced.add(binding_id)
        return bindings_replaced

    def _remove_fully_propagated(
        self,
        replacements: dict[int, tuple[Binding, dict]],
        bindings_replaced: set[int],
    ) -> None:
        """Remove declarations whose bindings were fully propagated."""
        to_remove: set[int] = set()
        for binding_id in bindings_replaced:
            binding = replacements[binding_id][0]
            if binding.assignments:
                continue
            declarator_node = binding.node
            if not isinstance(declarator_node, dict):
                continue
            if declarator_node.get('type') != 'VariableDeclarator':
                continue
            to_remove.add(id(declarator_node))
        _batch_remove_declarators(self.ast, to_remove, self.set_changed)
