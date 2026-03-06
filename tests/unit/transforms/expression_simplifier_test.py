"""Unit tests for ExpressionSimplifier transform."""

import pytest

from pyjsclear.transforms.expression_simplifier import ExpressionSimplifier
from tests.unit.conftest import normalize, roundtrip


def rt(js_code):
    """Shorthand roundtrip for ExpressionSimplifier."""
    code, changed = roundtrip(js_code, ExpressionSimplifier)
    return normalize(code), changed


class TestUnaryExpressions:
    def test_not_true(self):
        code, changed = rt("!true;")
        assert changed is True
        assert code == "false;"

    def test_not_false(self):
        code, changed = rt("!false;")
        assert changed is True
        assert code == "true;"

    def test_not_zero(self):
        code, changed = rt("!0;")
        assert changed is True
        assert code == "true;"

    def test_not_one(self):
        code, changed = rt("!1;")
        assert changed is True
        assert code == "false;"

    def test_typeof_null(self):
        code, changed = rt("typeof null;")
        assert changed is True
        assert code == normalize('"object";')

    def test_typeof_undefined(self):
        code, changed = rt("typeof undefined;")
        assert changed is True
        assert code == normalize('"undefined";')

    def test_void_zero(self):
        code, changed = rt("void 0;")
        assert changed is True
        assert code == "undefined;"

    def test_bitwise_not_zero(self):
        code, changed = rt("~0;")
        assert changed is True
        assert code == "-1;"

    def test_bitwise_not_nan_via_undefined(self):
        code, changed = rt("~undefined;")
        assert changed is True
        assert code == "-1;"

    def test_negative_literal_no_change(self):
        """Negative numeric literals are already in normal form."""
        code, changed = rt("-5;")
        assert changed is False
        assert code == "-5;"


class TestBinaryArithmetic:
    def test_addition(self):
        code, changed = rt("1 + 2;")
        assert changed is True
        assert code == "3;"

    def test_subtraction(self):
        code, changed = rt("10 - 3;")
        assert changed is True
        assert code == "7;"

    def test_multiplication(self):
        code, changed = rt("2 * 3;")
        assert changed is True
        assert code == "6;"

    def test_division(self):
        code, changed = rt("10 / 2;")
        assert changed is True
        assert code == "5;"

    def test_modulo(self):
        code, changed = rt("10 % 3;")
        assert changed is True
        assert code == "1;"


class TestStringConcat:
    def test_string_concat(self):
        code, changed = rt('"a" + "b";')
        assert changed is True
        assert code == normalize('"ab";')

    def test_string_number_coercion(self):
        code, changed = rt('"x" + 1;')
        assert changed is True
        assert code == normalize('"x1";')


class TestComparison:
    def test_strict_equal_true(self):
        code, changed = rt("1 === 1;")
        assert changed is True
        assert code == "true;"

    def test_strict_not_equal_true(self):
        code, changed = rt("1 !== 2;")
        assert changed is True
        assert code == "true;"

    def test_null_loose_equals_undefined(self):
        code, changed = rt("null == undefined;")
        assert changed is True
        assert code == "true;"

    def test_null_strict_not_equals_undefined(self):
        code, changed = rt("null === undefined;")
        assert changed is True
        assert code == "false;"


class TestBitwise:
    def test_bitwise_or(self):
        code, changed = rt("5 | 3;")
        assert changed is True
        assert code == "7;"

    def test_bitwise_and(self):
        code, changed = rt("5 & 3;")
        assert changed is True
        assert code == "1;"

    def test_bitwise_xor(self):
        code, changed = rt("5 ^ 3;")
        assert changed is True
        assert code == "6;"

    def test_left_shift(self):
        code, changed = rt("1 << 2;")
        assert changed is True
        assert code == "4;"


class TestConditionalSimplification:
    def test_ternary_false_true_becomes_not(self):
        code, changed = rt("x ? false : true;")
        assert changed is True
        assert code == "!x;"

    def test_ternary_true_false_no_change(self):
        """x ? true : false should not be simplified by this rule."""
        code, changed = rt("x ? true : false;")
        assert changed is False
        assert code == "x ? true : false;"


class TestSubtractNegative:
    def test_x_minus_neg_y_becomes_x_plus_y(self):
        code, changed = rt("x - (-3);")
        assert changed is True
        assert code == "x + 3;"


class TestNoChangeForNonConstant:
    def test_variable_addition(self):
        code, changed = rt("a + b;")
        assert changed is False
        assert code == "a + b;"

    def test_variable_unary(self):
        code, changed = rt("!x;")
        assert changed is False
        assert code == "!x;"


class TestDivisionByZero:
    def test_no_fold_division_by_zero(self):
        code, changed = rt("10 / 0;")
        assert changed is False
        assert code == "10 / 0;"

    def test_no_fold_modulo_by_zero(self):
        code, changed = rt("10 % 0;")
        assert changed is False
        assert code == "10 % 0;"
