"""Flatten else { if(...) {} } to else if(...) {}."""

from ..traverser import traverse
from .base import Transform


class ElseIfFlattener(Transform):
    """Convert `else { if (...) { } }` to `else if (...) { }`.

    Targets deeply nested if-else chains produced by control flow deobfuscation
    where each else block wraps a single if statement.
    """

    def execute(self):
        def enter(node, parent, key, index):
            if node.get('type') != 'IfStatement':
                return
            alt = node.get('alternate')
            if not alt or alt.get('type') != 'BlockStatement':
                return
            body = alt.get('body', [])
            if len(body) != 1:
                return
            inner = body[0]
            if inner.get('type') != 'IfStatement':
                return
            # Flatten: replace the block with the inner if
            node['alternate'] = inner
            self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
