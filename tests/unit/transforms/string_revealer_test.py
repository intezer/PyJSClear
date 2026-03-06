import math

import pytest

from pyjsclear.transforms.string_revealer import (
    StringRevealer,
    WrapperInfo,
    _eval_numeric,
    _js_parse_int,
)
from tests.unit.conftest import normalize, parse_expr, roundtrip


# ================================================================
# _eval_numeric
# ================================================================


class TestEvalNumeric:
    """Tests for the _eval_numeric helper."""

    def test_integer_literal(self):
        node = parse_expr("42")
        assert _eval_numeric(node) == 42

    def test_float_literal(self):
        node = parse_expr("3.14")
        assert _eval_numeric(node) == pytest.approx(3.14)

    def test_unary_negative(self):
        node = parse_expr("-7")
        assert _eval_numeric(node) == -7

    def test_unary_positive(self):
        node = parse_expr("+5")
        assert _eval_numeric(node) == 5

    def test_binary_addition(self):
        node = parse_expr("3 + 4")
        assert _eval_numeric(node) == 7

    def test_binary_subtraction(self):
        node = parse_expr("10 - 3")
        assert _eval_numeric(node) == 7

    def test_binary_multiplication(self):
        node = parse_expr("6 * 7")
        assert _eval_numeric(node) == 42

    def test_binary_division(self):
        node = parse_expr("20 / 4")
        assert _eval_numeric(node) == 5.0

    def test_division_by_zero_returns_none(self):
        node = parse_expr("1 / 0")
        assert _eval_numeric(node) is None

    def test_nested_expression(self):
        node = parse_expr("(2 + 3) * 4")
        assert _eval_numeric(node) == 20

    def test_string_literal_returns_none(self):
        node = parse_expr('"hello"')
        assert _eval_numeric(node) is None

    def test_identifier_returns_none(self):
        node = parse_expr("x")
        assert _eval_numeric(node) is None

    def test_non_dict_returns_none(self):
        assert _eval_numeric(None) is None
        assert _eval_numeric(42) is None

    def test_unsupported_operator_returns_none(self):
        node = parse_expr("2 << 3")
        assert _eval_numeric(node) is None


# ================================================================
# _js_parse_int
# ================================================================


class TestJsParseInt:
    """Tests for the _js_parse_int helper."""

    def test_pure_integer(self):
        assert _js_parse_int("123") == 123

    def test_leading_digits_with_trailing_chars(self):
        assert _js_parse_int("12abc") == 12

    def test_no_leading_digits_returns_nan(self):
        result = _js_parse_int("abc")
        assert math.isnan(result)

    def test_negative_number(self):
        assert _js_parse_int("-42") == -42

    def test_positive_sign(self):
        assert _js_parse_int("+99") == 99

    def test_whitespace_stripped(self):
        assert _js_parse_int("  56  ") == 56

    def test_empty_string_returns_nan(self):
        result = _js_parse_int("")
        assert math.isnan(result)

    def test_non_string_returns_nan(self):
        result = _js_parse_int(42)
        assert math.isnan(result)

    def test_none_returns_nan(self):
        result = _js_parse_int(None)
        assert math.isnan(result)


# ================================================================
# WrapperInfo
# ================================================================


class TestWrapperInfo:
    """Tests for WrapperInfo.get_effective_index."""

    def test_basic_offset(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=10, func_node={})
        assert info.get_effective_index([5]) == 15

    def test_negative_offset(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=-3, func_node={})
        assert info.get_effective_index([10]) == 7

    def test_zero_offset(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=0, func_node={})
        assert info.get_effective_index([7]) == 7

    def test_param_index_selects_correct_arg(self):
        info = WrapperInfo("w", param_index=1, wrapper_offset=100, func_node={})
        assert info.get_effective_index(["ignored", 5]) == 105

    def test_param_index_out_of_bounds_returns_none(self):
        info = WrapperInfo("w", param_index=2, wrapper_offset=0, func_node={})
        assert info.get_effective_index([1]) is None

    def test_non_numeric_arg_returns_none(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=0, func_node={})
        assert info.get_effective_index(["not_a_number"]) is None

    def test_get_key_with_key_param(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=0, func_node={}, key_param_index=1)
        assert info.get_key([10, "secret"]) == "secret"

    def test_get_key_without_key_param(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=0, func_node={})
        assert info.get_key([10]) is None

    def test_get_key_index_out_of_bounds(self):
        info = WrapperInfo("w", param_index=0, wrapper_offset=0, func_node={}, key_param_index=5)
        assert info.get_key([10]) is None


# ================================================================
# Strategy 1: Direct string arrays
# ================================================================


class TestDirectArrays:
    """Tests for direct array declaration and replacement."""

    def test_basic_direct_array(self):
        js = 'var arr = ["hello", "world"]; x(arr[0]); y(arr[1]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert 'x("hello")' in code
        assert 'y("world")' in code

    def test_direct_array_multiple_accesses(self):
        js = 'var arr = ["a", "b", "c"]; f(arr[0]); g(arr[1]); h(arr[2]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"a"' in code
        assert '"b"' in code
        assert '"c"' in code

    def test_direct_array_out_of_bounds_no_replacement(self):
        js = 'var arr = ["hello"]; x(arr[5]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert "arr[5]" in code

    def test_direct_array_non_numeric_index_no_replacement(self):
        js = 'var arr = ["hello", "world"]; x(arr[y]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert "arr[y]" in code

    def test_direct_array_single_element(self):
        js = 'var arr = ["only"]; x(arr[0]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"only"' in code

    def test_direct_array_preserves_non_array_vars(self):
        js = 'var x = 42; console.log(x);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_mixed_element_array_not_replaced(self):
        js = 'var arr = ["hello", 42]; x(arr[0]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert "arr[0]" in code


# ================================================================
# No string arrays => returns False
# ================================================================


class TestNoStringArrays:
    """Tests for code with no string array patterns."""

    def test_plain_code_returns_false(self):
        js = "var x = 1; console.log(x);"
        _, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_empty_program_returns_false(self):
        js = ""
        _, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_non_string_array_returns_false(self):
        js = "var arr = [1, 2, 3]; x(arr[0]);"
        _, changed = roundtrip(js, StringRevealer)
        assert changed is False


# ================================================================
# Obfuscator.io pattern: short arrays (< 5 strings) don't trigger
# ================================================================


class TestObfuscatorIoShortArray:
    """Short string arrays (< 5 elements) should not trigger obfuscator.io strategy."""

    def test_short_array_function_not_detected(self):
        # This mimics an obfuscator.io function pattern but with < 5 strings.
        # The array function detection requires >= 5 strings.
        js = """
        function _0xArr() {
            var a = ["s1", "s2", "s3"];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # Should NOT have decoded since array has < 5 elements
        assert "_0xDec" in code or changed is False
