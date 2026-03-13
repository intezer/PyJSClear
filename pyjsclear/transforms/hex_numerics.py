"""Normalize hex numeric literals (0x0f → 15) by clearing their raw field."""

from ..traverser import traverse
from .base import Transform


class HexNumerics(Transform):
    """Convert hex numeric literals to decimal representation."""

    def execute(self) -> bool:

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            if node.get('type') != 'Literal':
                return
            value = node.get('value')
            if not isinstance(value, (int, float)):
                return
            raw = node.get('raw')
            if not isinstance(raw, str):
                return
            if not raw.startswith(('0x', '0X')):
                return
            if isinstance(value, float) and value == int(value) and value >= 0:
                node['raw'] = str(int(value))
            else:
                node['raw'] = str(value)
            self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
