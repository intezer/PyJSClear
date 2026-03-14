"""Unit tests for ExpressionSimplifier transform."""

import math

import pytest

from pyjsclear.transforms.expression_simplifier import _JS_NULL
from pyjsclear.transforms.expression_simplifier import ExpressionSimplifier
from tests.unit.conftest import normalize
from tests.unit.conftest import roundtrip


def rt(js_code: str) -> tuple:
    """Shorthand roundtrip for ExpressionSimplifier."""
    code, changed = roundtrip(js_code, ExpressionSimplifier)
    return normalize(code), changed


class TestUnaryExpressions:
    def test_not_true(self):
        code, changed = rt('!true;')
        assert changed is True
        assert code == 'false;'

    def test_not_false(self):
        code, changed = rt('!false;')
        assert changed is True
        assert code == 'true;'

    def test_not_zero(self):
        code, changed = rt('!0;')
        assert changed is True
        assert code == 'true;'

    def test_not_one(self):
        code, changed = rt('!1;')
        assert changed is True
        assert code == 'false;'

    def test_typeof_null(self):
        code, changed = rt('typeof null;')
        assert changed is True
        assert code == normalize('"object";')

    def test_typeof_undefined(self):
        code, changed = rt('typeof undefined;')
        assert changed is True
        assert code == normalize('"undefined";')

    def test_void_zero(self):
        code, changed = rt('void 0;')
        assert changed is True
        assert code == 'undefined;'

    def test_bitwise_not_zero(self):
        code, changed = rt('~0;')
        assert changed is True
        assert code == '-1;'

    def test_bitwise_not_nan_via_undefined(self):
        code, changed = rt('~undefined;')
        assert changed is True
        assert code == '-1;'

    def test_negative_literal_no_change(self):
        """Negative numeric literals are already in normal form."""
        code, changed = rt('-5;')
        assert changed is False
        assert code == '-5;'


class TestBinaryArithmetic:
    def test_addition(self):
        code, changed = rt('1 + 2;')
        assert changed is True
        assert code == '3;'

    def test_subtraction(self):
        code, changed = rt('10 - 3;')
        assert changed is True
        assert code == '7;'

    def test_multiplication(self):
        code, changed = rt('2 * 3;')
        assert changed is True
        assert code == '6;'

    def test_division(self):
        code, changed = rt('10 / 2;')
        assert changed is True
        assert code == '5;'

    def test_modulo(self):
        code, changed = rt('10 % 3;')
        assert changed is True
        assert code == '1;'


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
        code, changed = rt('1 === 1;')
        assert changed is True
        assert code == 'true;'

    def test_strict_not_equal_true(self):
        code, changed = rt('1 !== 2;')
        assert changed is True
        assert code == 'true;'

    def test_null_loose_equals_undefined(self):
        code, changed = rt('null == undefined;')
        assert changed is True
        assert code == 'true;'

    def test_null_strict_not_equals_undefined(self):
        code, changed = rt('null === undefined;')
        assert changed is True
        assert code == 'false;'


class TestBitwise:
    def test_bitwise_or(self):
        code, changed = rt('5 | 3;')
        assert changed is True
        assert code == '7;'

    def test_bitwise_and(self):
        code, changed = rt('5 & 3;')
        assert changed is True
        assert code == '1;'

    def test_bitwise_xor(self):
        code, changed = rt('5 ^ 3;')
        assert changed is True
        assert code == '6;'

    def test_left_shift(self):
        code, changed = rt('1 << 2;')
        assert changed is True
        assert code == '4;'


class TestConditionalSimplification:
    def test_ternary_false_true_becomes_not(self):
        code, changed = rt('x ? false : true;')
        assert changed is True
        assert code == '!x;'

    def test_ternary_true_false_no_change(self):
        """x ? true : false should not be simplified by this rule."""
        code, changed = rt('x ? true : false;')
        assert changed is False
        assert code == 'x ? true : false;'


class TestSubtractNegative:
    def test_x_minus_neg_y_becomes_x_plus_y(self):
        code, changed = rt('x - (-3);')
        assert changed is True
        assert code == 'x + 3;'


class TestNoChangeForNonConstant:
    def test_variable_addition(self):
        code, changed = rt('a + b;')
        assert changed is False
        assert code == 'a + b;'

    def test_variable_unary(self):
        code, changed = rt('!x;')
        assert changed is False
        assert code == '!x;'


class TestDivisionByZero:
    def test_no_fold_division_by_zero(self):
        code, changed = rt('10 / 0;')
        assert changed is False
        assert code == '10 / 0;'

    def test_no_fold_modulo_by_zero(self):
        code, changed = rt('10 % 0;')
        assert changed is False
        assert code == '10 % 0;'


# ---------------------------------------------------------------------------
# Coverage gap tests
# ---------------------------------------------------------------------------


class TestAwaitSimplification:
    """Lines 91-98: await (0, expr) simplification."""

    def test_await_sequence_simplified(self):
        code, changed = rt('async function f() { await (0, fetch()); }')
        assert changed is True
        assert 'await fetch()' in code

    def test_await_non_sequence_unchanged(self):
        code, changed = rt('async function f() { await fetch(); }')
        assert changed is False


class TestUnsupportedUnaryOperator:
    """Line 105: unsupported unary operator returns None."""

    def test_delete_operator_not_folded(self):
        code, changed = rt('delete x.y;')
        assert changed is False


class TestUnsupportedBinaryOperator:
    """Line 129: unsupported binary operator."""

    def test_in_operator_not_folded(self):
        code, changed = rt('"x" in obj;')
        assert changed is False

    def test_instanceof_not_folded(self):
        code, changed = rt('x instanceof Array;')
        assert changed is False


class TestSimplifyExprNonDict:
    """Line 153: _simplify_expr with non-dict node."""

    def test_non_dict_passthrough(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._simplify_expr(None)
        assert result is None

        result = es._simplify_expr(42)
        assert result == 42


class TestNestedBinaryInBinary:
    """Lines 159-160: _simplify_expr for BinaryExpression (nested)."""

    def test_nested_binary_folded(self):
        code, changed = rt('(1 + 2) + 3;')
        assert changed is True
        assert code == '6;'

    def test_nested_binary_mixed(self):
        code, changed = rt('(2 * 3) + (4 - 1);')
        assert changed is True
        assert code == '9;'


class TestGetResolvableValueNonDict:
    """Line 174: _get_resolvable_value with non-dict."""

    def test_non_dict_returns_false(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        val, ok = es._get_resolvable_value(None)
        assert ok is False

        val, ok = es._get_resolvable_value('string')
        assert ok is False


class TestRegexLiteral:
    """Line 178: regex literal returns not resolvable."""

    def test_regex_not_resolvable(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        node = {'type': 'Literal', 'value': {}, 'regex': {'pattern': 'abc', 'flags': 'g'}}
        val, ok = es._get_resolvable_value(node)
        assert ok is False


class TestEmptyArrayObjectResolvable:
    """Lines 189, 191: empty array/object as resolvable values."""

    def test_unary_plus_empty_array(self):
        """+ [] → 0"""
        code, changed = rt('+[];')
        assert changed is True
        assert code == '0;'

    def test_empty_object_string_concat(self):
        """'' + {} → '[object Object]'"""
        code, changed = rt('"" + {};')
        assert changed is True
        assert '[object Object]' in code


class TestMoreUnaryOperators:
    """Lines 197, 199: various unary operators."""

    def test_plus_null(self):
        """+null → 0"""
        code, changed = rt('+null;')
        assert changed is True
        assert code == '0;'

    def test_typeof_true(self):
        code, changed = rt('typeof true;')
        assert changed is True
        assert '"boolean"' in code

    def test_typeof_string(self):
        code, changed = rt('typeof "hello";')
        assert changed is True
        assert '"string"' in code

    def test_typeof_array(self):
        code, changed = rt('typeof [];')
        assert changed is True
        assert '"object"' in code


class TestExponentiation:
    """Line 233: ** operator."""

    def test_power(self):
        code, changed = rt('2 ** 3;')
        assert changed is True
        assert code == '8;'


class TestUnsignedRightShift:
    """Lines 243-247: >>> operator."""

    def test_unsigned_right_shift(self):
        code, changed = rt('5 >>> 1;')
        assert changed is True
        assert code == '2;'


class TestComparisonOperators:
    """Lines 254-261: comparison operators."""

    def test_less_than(self):
        code, changed = rt('3 < 5;')
        assert changed is True
        assert code == 'true;'

    def test_less_than_or_equal(self):
        code, changed = rt('5 <= 5;')
        assert changed is True
        assert code == 'true;'

    def test_greater_than(self):
        code, changed = rt('5 > 3;')
        assert changed is True
        assert code == 'true;'

    def test_greater_than_or_equal(self):
        code, changed = rt('5 >= 5;')
        assert changed is True
        assert code == 'true;'

    def test_less_than_false(self):
        code, changed = rt('5 < 3;')
        assert changed is True
        assert code == 'false;'


class TestAbstractEquality:
    """Lines 269-271: abstract equality edge cases."""

    def test_null_eq_zero(self):
        code, changed = rt('null == 0;')
        assert changed is True
        assert code == 'false;'

    def test_null_neq_zero(self):
        code, changed = rt('null != 0;')
        assert changed is True
        assert code == 'true;'


class TestStrictEqualityNull:
    """Line 278: strict equality with null."""

    def test_null_strict_eq_zero(self):
        code, changed = rt('null === 0;')
        assert changed is True
        assert code == 'false;'

    def test_null_strict_eq_null(self):
        code, changed = rt('null === null;')
        assert changed is True
        assert code == 'true;'


class TestJsTruthyEdgeCases:
    """Lines 283-294: _js_truthy edge cases."""

    def test_truthy_nan(self):
        """NaN is falsy."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_truthy(float('nan')) is False

    def test_truthy_empty_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_truthy('') is False

    def test_truthy_nonempty_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_truthy('hello') is True

    def test_truthy_empty_array(self):
        """In JS, [] is truthy."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_truthy([]) is True

    def test_truthy_empty_dict(self):
        """In JS, {} is truthy."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_truthy({}) is True


class TestJsTypeof:
    """Lines 301-311: _js_typeof for various types."""

    def test_typeof_boolean(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_typeof(True) == 'boolean'

    def test_typeof_number(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_typeof(42) == 'number'

    def test_typeof_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_typeof('hello') == 'string'

    def test_typeof_list(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_typeof([]) == 'object'

    def test_typeof_dict(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_typeof({}) == 'object'


class TestJsToNumber:
    """Lines 319-339: _js_to_number for various types."""

    def test_bool_true(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number(True) == 1

    def test_bool_false(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number(False) == 0

    def test_string_numeric(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number('5') == 5

    def test_null_to_zero(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number(_JS_NULL) == 0

    def test_undefined_to_nan(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._js_to_number(None)
        assert math.isnan(result)

    def test_list_to_zero(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number([]) == 0


class TestJsToString:
    """Lines 343-358: _js_to_string for various types."""

    def test_null_to_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_string(_JS_NULL) == 'null'

    def test_undefined_to_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_string(None) == 'undefined'

    def test_bool_to_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_string(True) == 'true'
        assert es._js_to_string(False) == 'false'

    def test_list_to_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_string([]) == ''

    def test_dict_to_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_string({}) == '[object Object]'


class TestJsCompare:
    """Lines 362-380: _js_compare for string comparison and NaN."""

    def test_string_comparison(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_compare('b', 'a') > 0
        assert es._js_compare('a', 'b') < 0
        assert es._js_compare('a', 'a') == 0

    def test_nan_comparison(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._js_compare(float('nan'), 1)
        assert math.isnan(result)

        result = es._js_compare(1, float('nan'))
        assert math.isnan(result)


class TestValueToNode:
    """Lines 384-403: _value_to_node for various types."""

    def test_null_value(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._value_to_node(_JS_NULL)
        assert result['type'] == 'Literal'
        assert result['value'] is None

    def test_negative_number(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._value_to_node(-5)
        assert result['type'] == 'UnaryExpression'
        assert result['operator'] == '-'
        assert result['argument']['value'] == 5

    def test_nan_returns_none(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._value_to_node(float('nan'))
        assert result is None

    def test_infinity_returns_none(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._value_to_node(float('inf'))
        assert result is None

    def test_string_value(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._value_to_node('hello')
        assert result['type'] == 'Literal'
        assert result['value'] == 'hello'

    def test_undefined_value(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        result = es._value_to_node(None)
        assert result['type'] == 'Identifier'
        assert result['name'] == 'undefined'


class TestAwaitSingleExpressionUnchanged:
    """Line 96: await with SequenceExpression of length <= 1 is unchanged."""

    def test_await_sequence_single_expression(self):
        """SequenceExpression with only 1 expression should not be simplified."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        # Manually construct the AST for await (expr) with a single-element sequence
        ast = {
            'type': 'Program',
            'body': [
                {
                    'type': 'ExpressionStatement',
                    'expression': {
                        'type': 'AwaitExpression',
                        'argument': {
                            'type': 'SequenceExpression',
                            'expressions': [{'type': 'Identifier', 'name': 'fetch'}],
                        },
                    },
                }
            ],
        }
        es2 = ExpressionSimplifier(ast)
        es2._simplify_awaits()
        # Should not change because len(exprs) <= 1
        assert ast['body'][0]['expression']['argument']['type'] == 'SequenceExpression'

    def test_await_empty_sequence(self):
        ast = {
            'type': 'Program',
            'body': [
                {
                    'type': 'ExpressionStatement',
                    'expression': {
                        'type': 'AwaitExpression',
                        'argument': {
                            'type': 'SequenceExpression',
                            'expressions': [],
                        },
                    },
                }
            ],
        }
        es = ExpressionSimplifier(ast)
        es._simplify_awaits()
        assert ast['body'][0]['expression']['argument']['type'] == 'SequenceExpression'


class TestUnaryExceptionHandling:
    """Lines 122-123: Exception during unary evaluation."""

    def test_unary_minus_undefined_returns_nan_no_node(self):
        """-undefined → NaN, which _value_to_node returns None for."""
        code, changed = rt('-undefined;')
        # -undefined produces NaN, which can't be represented as a literal
        assert changed is False


class TestUnsignedRightShiftMore:
    """Line 243: >>> unsigned right shift."""

    def test_unsigned_right_shift_large(self):
        code, changed = rt('-1 >>> 0;')
        assert changed is True
        # -1 >>> 0 in JS is 4294967295
        assert '4294967295' in code


class TestGeComparison:
    """Lines 262-263: >= comparison operator."""

    def test_ge_equal(self):
        code, changed = rt('3 >= 3;')
        assert changed is True
        assert code == 'true;'

    def test_ge_false(self):
        code, changed = rt('2 >= 3;')
        assert changed is True
        assert code == 'false;'


class TestNullEqZero:
    """Line 271: null == 0 → false (null only equals undefined)."""

    def test_undefined_loose_eq_zero_false(self):
        """undefined == 0 → false."""
        code, changed = rt('undefined == 0;')
        assert changed is True
        assert code == 'false;'


class TestJsTruthyNaN:
    """Lines 283, 293-294: NaN is falsy, unknown type uses bool()."""

    def test_truthy_fallback_default(self):
        """Lines 293-294: _js_truthy with unknown type uses bool(value)."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        # A custom object that is truthy
        assert es._js_truthy(object()) is True


class TestJsTypeofDefault:
    """Lines 310-311: _js_typeof for unknown types returns 'undefined'."""

    def test_typeof_unknown_type(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_typeof(object()) == 'undefined'


class TestJsToNumberEdgeCases:
    """Lines 334-335, 338-339: _js_to_number for list and unknown types."""

    def test_list_to_number(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number([1, 2, 3]) == 0

    def test_unknown_type_to_number(self):
        """Line 338-339: default case returns 0."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number(object()) == 0

    def test_string_non_numeric_to_number(self):
        """Lines 334-335: non-numeric string returns 0."""
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number('abc') == 0

    def test_string_negative_to_number(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._js_to_number('-5') == -5


class TestJsToStringUnknown:
    """Lines 357-358: _js_to_string for unknown type."""

    def test_unknown_type_to_string(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        obj = object()
        result = es._js_to_string(obj)
        assert result == str(obj)


class TestValueToNodeUnknown:
    """Line 403: _value_to_node for unknown type returns None."""

    def test_list_returns_none(self):
        es = ExpressionSimplifier({'type': 'Program', 'body': []})
        assert es._value_to_node([1, 2]) is None
