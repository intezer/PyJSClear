"""Decode \\xHH hex escape sequences in string literals."""

import re
from .base import Transform


class HexEscapes(Transform):
    """Pre-AST regex pass to decode hex escape sequences."""

    def execute(self):
        # This works on the raw source before/after AST
        # But since we operate on AST, we decode hex in string literal raw values
        from ..traverser import traverse

        def enter(node, parent, key, index):
            if node.get('type') == 'Literal' and isinstance(node.get('value'), str):
                raw = node.get('raw', '')
                if '\\x' in raw or '\\u' in raw:
                    # The value is already decoded by parser, just fix raw
                    val = node['value']
                    new_raw = '"' + val.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t') + '"'
                    if new_raw != raw:
                        node['raw'] = new_raw
                        self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


def decode_hex_escapes_source(code):
    """Decode hex escapes in source code string (pre-parse pass)."""
    def replace_hex(m):
        return chr(int(m.group(1), 16))

    def replace_in_string(m):
        quote = m.group(1)
        content = m.group(2)
        decoded = re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, content)
        return quote + decoded + quote

    # Match string literals and decode hex escapes within them
    result = re.sub(r"""(['"])((?:(?!\1|\\).|\\.)*?)\1""", replace_in_string, code)
    return result
