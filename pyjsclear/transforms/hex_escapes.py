"""Decode \\xHH hex escape sequences in string literals."""

import re

from ..traverser import traverse
from .base import Transform


# Hex escapes that are safe to decode: printable ASCII (0x20-0x7e)
# excluding backslash (0x5c) and quote characters (0x22, 0x27).
_EXCLUDED_CHAR_CODES: set[int] = {0x22, 0x27, 0x5C}

_HEX_ESCAPE_PATTERN: re.Pattern[str] = re.compile(r'\\x([0-9a-fA-F]{2})')
_STRING_LITERAL_PATTERN: re.Pattern[str] = re.compile(r"""(['"])((?:(?!\1|\\).|\\.)*?)\1""")


def _replace_single_hex_escape(hex_match: re.Match[str]) -> str:
    """Replace a single hex escape with its decoded character if printable."""
    char_value = int(hex_match.group(1), 16)
    if 0x20 <= char_value <= 0x7E and char_value not in _EXCLUDED_CHAR_CODES:
        return chr(char_value)
    return hex_match.group(0)


def _replace_hex_in_string_literal(match_result: re.Match[str]) -> str:
    """Decode hex escapes within a matched string literal."""
    quote = match_result.group(1)
    content = match_result.group(2)
    decoded = _HEX_ESCAPE_PATTERN.sub(_replace_single_hex_escape, content)
    return quote + decoded + quote


class HexEscapes(Transform):
    """Pre-AST regex pass to decode hex escape sequences."""

    def execute(self) -> bool:
        """Decode hex/unicode escapes in string literal raw values."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            """Rebuild raw string for literals containing hex or unicode escapes."""
            if node.get('type') != 'Literal' or not isinstance(node.get('value'), str):
                return
            raw_string = node.get('raw', '')
            if '\\x' not in raw_string and '\\u' not in raw_string:
                return

            value = node['value']
            new_raw_string = (
                '"'
                + value.replace('\\', '\\\\')
                .replace('"', '\\"')
                .replace('\n', '\\n')
                .replace('\r', '\\r')
                .replace('\t', '\\t')
                + '"'
            )
            if new_raw_string != raw_string:
                node['raw'] = new_raw_string
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
    return _STRING_LITERAL_PATTERN.sub(_replace_hex_in_string_literal, code)
