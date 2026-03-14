"""Normalize hex numeric literals (0x0f -> 15) by clearing their raw field."""

from ..traverser import traverse
from .base import Transform


class HexNumerics(Transform):
    """Convert hex numeric literals to decimal representation."""

    def execute(self) -> bool:
        """Replace hex raw literals with their decimal string equivalents."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            """Convert a single hex numeric literal node to decimal."""
            if node.get('type') != 'Literal':
                return
            value = node.get('value')
            if not isinstance(value, (int, float)):
                return
            raw_literal = node.get('raw')
            if not isinstance(raw_literal, str):
                return
            if not raw_literal.startswith(('0x', '0X')):
                return
            match value:
                case float() if value == int(value) and value >= 0:
                    node['raw'] = str(int(value))
                case _:
                    node['raw'] = str(value)
            self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
