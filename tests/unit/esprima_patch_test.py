"""Unit tests for pyjsclear.esprima_patch (linear string/template scanning)."""

import time

import esprima
import pytest

import pyjsclear.esprima_patch as esprima_patch


def _literal_value(code):
    return esprima.parseScript(code).body[0].declarations[0].init.value


def _template_cooked(code):
    quasi = esprima.parseScript(code).body[0].declarations[0].init.quasis[0]
    return quasi.value.cooked


class TestPatchApplied:
    def test_patch_targets_supported_version(self):
        assert esprima.__version__ in esprima_patch._SUPPORTED_ESPRIMA_VERSIONS

    def test_scanner_methods_are_replaced(self):
        assert getattr(esprima.scanner.Scanner.scanStringLiteral, '_linearized', False)
        assert getattr(esprima.scanner.Scanner.scanTemplate, '_linearized', False)


class TestStringLiteralEquivalence:
    @pytest.mark.parametrize(
        'code, expected',
        [
            (r"var a='';", ''),
            (r"var a='plain';", 'plain'),
            (r'var a="double";', 'double'),
            (r"var a='tab\ttab\nnl';", 'tab\ttab\nnl'),
            (r"var a='\r\b\f\v';", '\r\b\f\x0b'),
            (r"var a='\x41\x42';", 'AB'),
            (r"var a='\u{1F600}';", '\U0001f600'),
            (r"var a='\101\102';", 'AB'),  # octal
            (r"var a='\0';", '\0'),
            (r"var a='\z\q';", 'zq'),  # unknown escape -> literal char
            (r"var a='\\';", '\\'),
            (r"var a='quote\'in';", "quote'in"),
            (r"var a='émoji😀';", 'émoji😀'),
            ("var a='line\\\ncont';", 'linecont'),  # line continuation
            ("var a='line\\\r\ncont';", 'linecont'),  # CRLF continuation
        ],
    )
    def test_value(self, code, expected):
        assert _literal_value(code) == expected


class TestTemplateEquivalence:
    @pytest.mark.parametrize(
        'code, expected',
        [
            ('var a=`plain`;', 'plain'),
            (r'var a=`tab\tnl\n`;', 'tab\tnl\n'),
            (r'var a=`\x41B`;', 'AB'),
            ('var a=`raw\nline`;', 'raw\nline'),
        ],
    )
    def test_cooked(self, code, expected):
        assert _template_cooked(code) == expected


class TestInvalidLiteralsStillRaise:
    @pytest.mark.parametrize(
        'code',
        [
            r"var a='unterminated;",
            "var a='raw\nnl';",
            r"var a='\x4';",
            r"var a='\8';",
        ],
    )
    def test_raises(self, code):
        with pytest.raises(esprima.Error):
            esprima.parseScript(code)


class TestLinearScaling:
    def test_large_single_string_literal_parses_in_linear_time(self):
        # Unpatched this is O(n^2): ~7s+ at 1MB. Patched it is well under a second.
        body = ('ABCDefgh0123+/' * (1024 * 1024 // 14 + 1))[: 1024 * 1024]
        code = "var s='" + body + "';"

        start = time.perf_counter()
        value = _literal_value(code)
        elapsed = time.perf_counter() - start

        assert value == body
        assert elapsed < 3.0, f'parse took {elapsed:.2f}s; quadratic scan likely regressed'
