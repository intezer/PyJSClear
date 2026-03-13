"""Base transform class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..traverser import build_parent_map

if TYPE_CHECKING:
    from ..scope import Scope


class Transform:
    """Base class for all AST transforms."""

    # Subclasses can set this to True to trigger scope rebuild after execution
    rebuild_scope = False

    def __init__(
        self,
        ast: dict,
        scope_tree: Scope | None = None,
        node_scope: dict[int, Scope] | None = None,
    ) -> None:
        self.ast = ast
        self.scope_tree = scope_tree
        self.node_scope = node_scope
        self._changed = False
        self._parent_map = None

    def execute(self) -> bool:
        """Execute the transform. Returns True if the AST was modified."""
        raise NotImplementedError

    def set_changed(self) -> None:
        self._changed = True

    def has_changed(self) -> bool:
        return self._changed

    def get_parent_map(self):
        """Lazily build and return a parent map for the AST.

        Returns dict mapping id(node) -> (parent, key, index).
        Call invalidate_parent_map() after AST modifications.
        """
        if self._parent_map is None:
            self._parent_map = build_parent_map(self.ast)
        return self._parent_map

    def invalidate_parent_map(self):
        """Invalidate the cached parent map after AST modifications."""
        self._parent_map = None

    def find_parent(self, target_node):
        """Find the parent of a node using the parent map. Returns (parent, key, index) or None."""
        pm = self.get_parent_map()
        return pm.get(id(target_node))
