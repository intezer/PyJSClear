"""Decode \\xHH hex escape sequences in string literals."""

import re

from ..traverser import traverse
from .base import Transform


class HexEscapes(Transform):
    """Pre-AST regex pass to decode hex escape sequences."""

    def execute(self) -> bool:
        # Decode hex/unicode escapes in string literal raw values (value already decoded by parser)

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            if node.get('type') != 'Literal' or not isinstance(node.get('value'), str):
                return
            raw_string = node.get('raw', '')
            if '\\x' not in raw_string and '\\u' not in raw_string:
                return
            value = node['value']
            new_raw = (
                '"'
                + value.replace('\\', '\\\\')
                .replace('"', '\\"')
                .replace('\n', '\\n')
                .replace('\r', '\\r')
                .replace('\t', '\\t')
                + '"'
            )
            if new_raw != raw_string:
                node['raw'] = new_raw
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()


def decode_hex_escapes_source(code: str) -> str:
    """Decode hex escapes in source code string (pre-parse pass).

    Only decodes hex escapes that produce printable characters (0x20-0x7e),
    excluding the backslash (0x5c) and quote characters which would break
    string literal syntax. Control characters (newlines, tabs, nulls etc.)
    are left as \\xHH to avoid breaking the parser.
    """

    def replace_in_string(match_result: re.Match) -> str:
        quote = match_result.group(1)
        content = match_result.group(2)

        # Decode hex escapes, but skip backslash, both quote chars,
        # and control chars. Quote chars are left for AST-level handling
        # which normalizes to double quotes like Babel.
        def replace_hex_in_context(hex_match: re.Match) -> str:
            char_value = int(hex_match.group(1), 16)
            if 0x20 <= char_value <= 0x7E and char_value not in (0x22, 0x27, 0x5C):
                return chr(char_value)
            return hex_match.group(0)

        decoded = re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex_in_context, content)
        return quote + decoded + quote

    # Match string literals and decode hex escapes within them
    return re.sub(r"""(['"])((?:(?!\1|\\).|\\.)*?)\1""", replace_in_string, code)
