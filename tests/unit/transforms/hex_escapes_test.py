"""Tests for pyjsclear.transforms.hex_escapes."""

import pytest

from pyjsclear.transforms.hex_escapes import HexEscapes, decode_hex_escapes_source
from tests.unit.conftest import roundtrip


# ---------------------------------------------------------------------------
# HexEscapes transform (AST-level)
# ---------------------------------------------------------------------------

class TestHexEscapesTransform:
    def test_hex_escape_string_decoded(self):
        """String with \\xHH escapes should have its raw updated."""
        js = r'''var a = "\x48\x65\x6c\x6c\x6f";'''
        result, changed = roundtrip(js, HexEscapes)
        assert changed is True
        # The generated code should contain the readable string
        assert "Hello" in result

    def test_value_preserved_after_decode(self):
        """The runtime value of the string must remain the same."""
        js = r'''var a = "\x48\x65\x6c\x6c\x6f";'''
        result, changed = roundtrip(js, HexEscapes)
        assert changed is True
        assert '"Hello"' in result

    def test_no_hex_escapes_no_change(self):
        """Strings without hex or unicode escapes should not be modified."""
        js = 'var a = "Hello";'
        result, changed = roundtrip(js, HexEscapes)
        assert changed is False
        assert '"Hello"' in result

    def test_unicode_escapes_trigger(self):
        """Unicode \\uHHHH escapes should also trigger raw rebuild."""
        js = r'''var a = "\u0048\u0065\u006c\u006c\u006f";'''
        result, changed = roundtrip(js, HexEscapes)
        assert changed is True
        assert "Hello" in result

    def test_numeric_literal_not_affected(self):
        """Numeric literals should not be touched."""
        js = "var a = 42;"
        result, changed = roundtrip(js, HexEscapes)
        assert changed is False

    def test_mixed_hex_and_plain(self):
        """Strings mixing hex escapes and plain text should be decoded."""
        js = r'''var a = "\x48i";'''
        result, changed = roundtrip(js, HexEscapes)
        assert changed is True
        assert "Hi" in result

    def test_special_chars_escaped_in_raw(self):
        """Characters like newline in the value should be escaped in raw."""
        js = r'''var a = "\x48\x0a";'''
        result, changed = roundtrip(js, HexEscapes)
        assert changed is True
        # The newline (0x0a) should appear as \\n in the generated raw
        assert "\\n" in result


# ---------------------------------------------------------------------------
# decode_hex_escapes_source (regex source-level)
# ---------------------------------------------------------------------------

class TestDecodeHexEscapesSource:
    def test_basic_hex_decode(self):
        """Printable hex escapes inside a string literal are decoded."""
        code = r"""var a = '\x48\x65\x6c\x6c\x6f';"""
        result = decode_hex_escapes_source(code)
        assert "'Hello'" in result

    def test_double_quoted_string(self):
        """Works inside double-quoted strings as well."""
        code = r'''var a = "\x48\x65\x6c\x6c\x6f";'''
        result = decode_hex_escapes_source(code)
        assert '"Hello"' in result

    def test_control_chars_preserved(self):
        """Control characters (e.g. \\x0a) should NOT be decoded."""
        code = r"""var a = '\x0a';"""
        result = decode_hex_escapes_source(code)
        assert r"\x0a" in result

    def test_null_char_preserved(self):
        """Null byte \\x00 is a control char and should stay encoded."""
        code = r"""var a = '\x00';"""
        result = decode_hex_escapes_source(code)
        assert r"\x00" in result

    def test_double_quote_preserved(self):
        """0x22 (double quote) should be kept as \\x22."""
        code = r"""var a = '\x22';"""
        result = decode_hex_escapes_source(code)
        assert r"\x22" in result

    def test_single_quote_preserved(self):
        """0x27 (single quote) should be kept as \\x27."""
        code = r"""var a = "\x27";"""
        result = decode_hex_escapes_source(code)
        assert r"\x27" in result

    def test_backslash_preserved(self):
        """0x5c (backslash) should be kept as \\x5c."""
        code = r"""var a = '\x5c';"""
        result = decode_hex_escapes_source(code)
        assert r"\x5c" in result

    def test_non_string_hex_not_decoded(self):
        """Hex sequences outside of string literals should not be touched."""
        code = r"""// comment \x48\x65\x6c\x6c\x6f"""
        result = decode_hex_escapes_source(code)
        # Outside quotes, should remain unchanged
        assert result == code

    def test_mixed_printable_and_control(self):
        """Mix of printable and control chars: only printable ones decoded."""
        code = r"""var a = '\x48\x0a\x65';"""
        result = decode_hex_escapes_source(code)
        assert "H" in result
        assert "e" in result
        assert r"\x0a" in result

    def test_uppercase_hex_digits(self):
        """Uppercase hex digits should also be decoded."""
        code = r"""var a = '\x48\x45\x4C';"""
        result = decode_hex_escapes_source(code)
        assert "HEL" in result

    def test_empty_string_unchanged(self):
        """An empty string literal should pass through unchanged."""
        code = "var a = '';"
        result = decode_hex_escapes_source(code)
        assert result == code

    def test_no_strings_unchanged(self):
        """Code with no string literals should pass through unchanged."""
        code = "var a = 42;"
        result = decode_hex_escapes_source(code)
        assert result == code

    def test_space_boundary_decoded(self):
        """0x20 (space) is the lower printable boundary and should be decoded."""
        code = r"""var a = '\x20';"""
        result = decode_hex_escapes_source(code)
        assert "' '" in result

    def test_tilde_boundary_decoded(self):
        """0x7e (tilde) is the upper printable boundary and should be decoded."""
        code = r"""var a = '\x7e';"""
        result = decode_hex_escapes_source(code)
        assert "'~'" in result

    def test_del_char_preserved(self):
        """0x7f (DEL) is above 0x7e and should NOT be decoded."""
        code = r"""var a = '\x7f';"""
        result = decode_hex_escapes_source(code)
        assert r"\x7f" in result
