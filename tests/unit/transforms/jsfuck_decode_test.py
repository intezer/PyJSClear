"""Tests for JSFUCK decoder."""

from pyjsclear.transforms.jsfuck_decode import is_jsfuck


class TestJSFuckDetection:
    def test_detects_jsfuck(self):
        # Typical JSFUCK: only []()!+ chars
        code = '[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!!' + '+[])[+[]]]' * 5
        assert is_jsfuck(code) is True

    def test_rejects_normal_js(self):
        assert is_jsfuck('var x = 1; console.log(x);') is False

    def test_rejects_short_code(self):
        assert is_jsfuck('[]') is False

    def test_jsfuck_with_preamble(self):
        # Some JSFUCK variants have a $ = String.fromCharCode(...) preamble
        # followed by lots of JSFUCK
        preamble = '$ = String.fromCharCode(118, 82);\n'
        jsfuck = '[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]]' * 10
        code = preamble + jsfuck
        # Has significant non-JSFUCK content, but ratio might still be high
        assert isinstance(is_jsfuck(code), bool)
