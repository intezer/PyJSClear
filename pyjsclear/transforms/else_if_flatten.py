"""Flatten else { if(...) {} } to else if(...) {}."""

from ..traverser import traverse
from .base import Transform


class ElseIfFlattener(Transform):
    """Convert `else { if (...) { } }` to `else if (...) { }`.

    Targets deeply nested if-else chains produced by control flow deobfuscation
    where each else block wraps a single if statement.
    """

    def _enter_node(self, node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
        if node.get('type') != 'IfStatement':
            return
        alternate_node = node.get('alternate')
        if not alternate_node or alternate_node.get('type') != 'BlockStatement':
            return
        body = alternate_node.get('body', [])
        if len(body) != 1:
            return
        inner_if = body[0]
        if inner_if.get('type') != 'IfStatement':
            return
        # Flatten: replace the block with the inner if
        node['alternate'] = inner_if
        self.set_changed()

    def execute(self) -> bool:
        traverse(self.ast, {'enter': self._enter_node})
        return self.has_changed()
