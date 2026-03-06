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
                    new_raw = (
                        '"'
                        + val.replace('\\', '\\\\')
                        .replace('"', '\\"')
                        .replace('\n', '\\n')
                        .replace('\r', '\\r')
                        .replace('\t', '\\t')
                        + '"'
                    )
                    if new_raw != raw:
                        node['raw'] = new_raw
                        self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


def decode_hex_escapes_source(code):
    """Decode hex escapes in source code string (pre-parse pass).

    Only decodes hex escapes that produce printable characters (0x20-0x7e),
    excluding the backslash (0x5c) and quote characters which would break
    string literal syntax. Control characters (newlines, tabs, nulls etc.)
    are left as \\xHH to avoid breaking the parser.
    """

    def replace_hex(m):
        val = int(m.group(1), 16)
        # Only decode printable ASCII (space through tilde), excluding
        # backslash and the quote character that delimits this string
        # (quote char is handled at the string level below).
        if 0x20 <= val <= 0x7E and val != 0x5C:  # exclude backslash
            return chr(val)
        return m.group(0)  # keep original \xHH

    def replace_in_string(m):
        quote = m.group(1)
        content = m.group(2)

        # Decode hex escapes, but skip backslash, both quote chars,
        # and control chars. Quote chars are left for AST-level handling
        # which normalizes to double quotes like Babel.
        def replace_hex_in_context(hm):
            val = int(hm.group(1), 16)
            if 0x20 <= val <= 0x7E and val not in (0x22, 0x27, 0x5C):
                return chr(val)
            return hm.group(0)

        decoded = re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex_in_context, content)
        return quote + decoded + quote

    # Match string literals and decode hex escapes within them
    result = re.sub(r"""(['"])((?:(?!\1|\\).|\\.)*?)\1""", replace_in_string, code)
    return result
