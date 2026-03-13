"""Base transform class."""

from __future__ import annotations

from typing import TYPE_CHECKING

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

    def execute(self) -> bool:
        """Execute the transform. Returns True if the AST was modified."""
        raise NotImplementedError

    def set_changed(self) -> None:
        self._changed = True

    def has_changed(self) -> bool:
        return self._changed
