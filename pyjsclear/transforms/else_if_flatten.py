"""Flatten else { if(...) {} } to else if(...) {}."""

from __future__ import annotations

from ..traverser import traverse
from .base import Transform


class ElseIfFlattener(Transform):
    """Convert `else { if (...) { } }` to `else if (...) { }`.

    Targets deeply nested if-else chains produced by control flow deobfuscation
    where each else block wraps a single if statement.
    """

    def _enter_node(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Flatten a single else-block containing only an if-statement."""
        if node.get('type') != 'IfStatement':
            return

        alternate_node = node.get('alternate')
        if not alternate_node or alternate_node.get('type') != 'BlockStatement':
            return

        block_body: list[dict] = alternate_node.get('body', [])
        if len(block_body) != 1:
            return

        inner_if_statement: dict = block_body[0]
        if inner_if_statement.get('type') != 'IfStatement':
            return

        node['alternate'] = inner_if_statement
        self.set_changed()

    def execute(self) -> bool:
        """Run the flattening pass over the entire AST."""
        traverse(self.ast, {'enter': self._enter_node})
        return self.has_changed()
