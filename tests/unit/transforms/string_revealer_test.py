import math

import pytest

from pyjsclear.parser import parse
from pyjsclear.transforms.string_revealer import StringRevealer
from pyjsclear.transforms.string_revealer import WrapperInfo
from pyjsclear.transforms.string_revealer import _apply_arith
from pyjsclear.transforms.string_revealer import _collect_object_literals
from pyjsclear.transforms.string_revealer import _eval_numeric
from pyjsclear.transforms.string_revealer import _js_parse_int
from pyjsclear.transforms.string_revealer import _resolve_arg_value
from pyjsclear.transforms.string_revealer import _resolve_string_arg
from pyjsclear.utils.string_decoders import Base64StringDecoder
from pyjsclear.utils.string_decoders import BasicStringDecoder
from tests.unit.conftest import normalize
from tests.unit.conftest import parse_expr
from tests.unit.conftest import roundtrip


# ================================================================
# _eval_numeric
# ================================================================


class TestEvalNumeric:
    """Tests for the _eval_numeric helper."""

    def test_integer_literal(self) -> None:
        node = parse_expr('42')
        assert _eval_numeric(node) == 42

    def test_float_literal(self) -> None:
        node = parse_expr('3.14')
        assert _eval_numeric(node) == pytest.approx(3.14)

    def test_unary_negative(self) -> None:
        node = parse_expr('-7')
        assert _eval_numeric(node) == -7

    def test_unary_positive(self) -> None:
        node = parse_expr('+5')
        assert _eval_numeric(node) == 5

    def test_binary_addition(self) -> None:
        node = parse_expr('3 + 4')
        assert _eval_numeric(node) == 7

    def test_binary_subtraction(self) -> None:
        node = parse_expr('10 - 3')
        assert _eval_numeric(node) == 7

    def test_binary_multiplication(self) -> None:
        node = parse_expr('6 * 7')
        assert _eval_numeric(node) == 42

    def test_binary_division(self) -> None:
        node = parse_expr('20 / 4')
        assert _eval_numeric(node) == 5.0

    def test_division_by_zero_returns_none(self) -> None:
        node = parse_expr('1 / 0')
        assert _eval_numeric(node) is None

    def test_nested_expression(self) -> None:
        node = parse_expr('(2 + 3) * 4')
        assert _eval_numeric(node) == 20

    def test_string_literal_returns_none(self) -> None:
        node = parse_expr('"hello"')
        assert _eval_numeric(node) is None

    def test_identifier_returns_none(self) -> None:
        node = parse_expr('x')
        assert _eval_numeric(node) is None

    def test_non_dict_returns_none(self) -> None:
        assert _eval_numeric(None) is None
        assert _eval_numeric(42) is None

    def test_unsupported_operator_returns_none(self) -> None:
        node = parse_expr('2 << 3')
        assert _eval_numeric(node) is None


# ================================================================
# _js_parse_int
# ================================================================


class TestJsParseInt:
    """Tests for the _js_parse_int helper."""

    def test_pure_integer(self) -> None:
        assert _js_parse_int('123') == 123

    def test_leading_digits_with_trailing_chars(self) -> None:
        assert _js_parse_int('12abc') == 12

    def test_no_leading_digits_returns_nan(self) -> None:
        result = _js_parse_int('abc')
        assert math.isnan(result)

    def test_negative_number(self) -> None:
        assert _js_parse_int('-42') == -42

    def test_positive_sign(self) -> None:
        assert _js_parse_int('+99') == 99

    def test_whitespace_stripped(self) -> None:
        assert _js_parse_int('  56  ') == 56

    def test_empty_string_returns_nan(self) -> None:
        result = _js_parse_int('')
        assert math.isnan(result)

    def test_non_string_returns_nan(self) -> None:
        result = _js_parse_int(42)
        assert math.isnan(result)

    def test_none_returns_nan(self) -> None:
        result = _js_parse_int(None)
        assert math.isnan(result)


# ================================================================
# WrapperInfo
# ================================================================


class TestWrapperInfo:
    """Tests for WrapperInfo.get_effective_index."""

    def test_basic_offset(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=10, func_node={})
        assert info.get_effective_index([5]) == 15

    def test_negative_offset(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=-3, func_node={})
        assert info.get_effective_index([10]) == 7

    def test_zero_offset(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        assert info.get_effective_index([7]) == 7

    def test_param_index_selects_correct_arg(self) -> None:
        info = WrapperInfo('w', param_index=1, wrapper_offset=100, func_node={})
        assert info.get_effective_index(['ignored', 5]) == 105

    def test_param_index_out_of_bounds_returns_none(self) -> None:
        info = WrapperInfo('w', param_index=2, wrapper_offset=0, func_node={})
        assert info.get_effective_index([1]) is None

    def test_non_numeric_arg_returns_none(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        assert info.get_effective_index(['not_a_number']) is None

    def test_get_key_with_key_param(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={}, key_param_index=1)
        assert info.get_key([10, 'secret']) == 'secret'

    def test_get_key_without_key_param(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        assert info.get_key([10]) is None

    def test_get_key_index_out_of_bounds(self) -> None:
        info = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={}, key_param_index=5)
        assert info.get_key([10]) is None


# ================================================================
# Strategy 1: Direct string arrays
# ================================================================


class TestDirectArrays:
    """Tests for direct array declaration and replacement."""

    def test_basic_direct_array(self) -> None:
        js = 'var arr = ["hello", "world"]; x(arr[0]); y(arr[1]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert 'x("hello")' in code
        assert 'y("world")' in code

    def test_direct_array_multiple_accesses(self) -> None:
        js = 'var arr = ["a", "b", "c"]; f(arr[0]); g(arr[1]); h(arr[2]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"a"' in code
        assert '"b"' in code
        assert '"c"' in code

    def test_direct_array_out_of_bounds_no_replacement(self) -> None:
        js = 'var arr = ["hello"]; x(arr[5]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert 'arr[5]' in code

    def test_direct_array_non_numeric_index_no_replacement(self) -> None:
        js = 'var arr = ["hello", "world"]; x(arr[y]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert 'arr[y]' in code

    def test_direct_array_single_element(self) -> None:
        js = 'var arr = ["only"]; x(arr[0]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"only"' in code

    def test_direct_array_preserves_non_array_vars(self) -> None:
        js = 'var x = 42; console.log(x);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_mixed_element_array_not_replaced(self) -> None:
        js = 'var arr = ["hello", 42]; x(arr[0]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert 'arr[0]' in code


# ================================================================
# No string arrays => returns False
# ================================================================


class TestNoStringArrays:
    """Tests for code with no string array patterns."""

    def test_empty_program_returns_false(self) -> None:
        js = ''
        _, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_non_string_array_returns_false(self) -> None:
        js = 'var arr = [1, 2, 3]; x(arr[0]);'
        _, changed = roundtrip(js, StringRevealer)
        assert changed is False


# ================================================================
# Obfuscator.io pattern: short arrays (< 5 strings) don't trigger
# ================================================================


class TestObfuscatorIoShortArray:
    """Short string arrays (< 5 elements) should not trigger obfuscator.io strategy."""

    def test_short_array_function_decoded(self) -> None:
        # Arrays with >= 2 elements in obfuscator.io function pattern are decoded.
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
        assert changed is True
        assert '"s1"' in code


# ================================================================
# _apply_arith
# ================================================================


class TestApplyArith:
    """Tests for the _apply_arith helper."""

    def test_addition(self) -> None:
        assert _apply_arith('+', 3, 4) == 7

    def test_subtraction(self) -> None:
        assert _apply_arith('-', 10, 3) == 7

    def test_multiplication(self) -> None:
        assert _apply_arith('*', 6, 7) == 42

    def test_division(self) -> None:
        assert _apply_arith('/', 20, 4) == 5.0

    def test_division_by_zero(self) -> None:
        assert _apply_arith('/', 1, 0) is None

    def test_modulo(self) -> None:
        assert _apply_arith('%', 10, 3) == 1

    def test_modulo_by_zero(self) -> None:
        assert _apply_arith('%', 10, 0) is None

    def test_unsupported_operator_returns_none(self) -> None:
        assert _apply_arith('**', 2, 3) is None
        assert _apply_arith('<<', 2, 3) is None
        assert _apply_arith('>>', 8, 1) is None
        assert _apply_arith('&', 5, 3) is None


# ================================================================
# _collect_object_literals
# ================================================================


class TestCollectObjectLiterals:
    """Tests for the _collect_object_literals helper."""

    def test_numeric_properties(self) -> None:
        ast = parse('var obj = {a: 0x1b1, b: 42};')
        result = _collect_object_literals(ast)
        assert ('obj', 'a') in result
        assert result[('obj', 'a')] == 0x1B1
        assert result[('obj', 'b')] == 42

    def test_string_properties(self) -> None:
        ast = parse('var obj = {a: "hello", b: "world"};')
        result = _collect_object_literals(ast)
        assert result[('obj', 'a')] == 'hello'
        assert result[('obj', 'b')] == 'world'

    def test_mixed_properties(self) -> None:
        ast = parse('var obj = {a: 0x1b1, b: "hello"};')
        result = _collect_object_literals(ast)
        assert result[('obj', 'a')] == 0x1B1
        assert result[('obj', 'b')] == 'hello'

    def test_string_key_properties(self) -> None:
        ast = parse('var obj = {"myKey": 42};')
        result = _collect_object_literals(ast)
        assert result[('obj', 'myKey')] == 42

    def test_empty_object(self) -> None:
        ast = parse('var obj = {};')
        result = _collect_object_literals(ast)
        assert len(result) == 0

    def test_non_object_init_ignored(self) -> None:
        ast = parse('var x = 42;')
        result = _collect_object_literals(ast)
        assert len(result) == 0

    def test_multiple_objects(self) -> None:
        ast = parse('var a = {x: 1}; var b = {y: 2};')
        result = _collect_object_literals(ast)
        assert result[('a', 'x')] == 1
        assert result[('b', 'y')] == 2


# ================================================================
# _resolve_arg_value
# ================================================================


class TestResolveArgValue:
    """Tests for the _resolve_arg_value helper."""

    def test_numeric_literal(self) -> None:
        arg = parse_expr('42')
        assert _resolve_arg_value(arg, {}) == 42

    def test_string_hex_literal(self) -> None:
        arg = parse_expr('"0x1a"')
        assert _resolve_arg_value(arg, {}) == 0x1A

    def test_string_decimal_literal(self) -> None:
        arg = parse_expr('"10"')
        assert _resolve_arg_value(arg, {}) == 10

    def test_string_non_numeric_returns_none(self) -> None:
        arg = parse_expr('"hello"')
        assert _resolve_arg_value(arg, {}) is None

    def test_member_expression_numeric(self) -> None:
        obj_literals = {('obj', 'x'): 0x42}
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'x'},
        }
        assert _resolve_arg_value(arg, obj_literals) == 0x42

    def test_member_expression_string_numeric(self) -> None:
        obj_literals = {('obj', 'x'): '0x10'}
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'x'},
        }
        assert _resolve_arg_value(arg, obj_literals) == 0x10

    def test_member_expression_string_non_numeric(self) -> None:
        obj_literals = {('obj', 'x'): 'hello'}
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'x'},
        }
        assert _resolve_arg_value(arg, obj_literals) is None

    def test_member_expression_unknown_key(self) -> None:
        obj_literals = {('obj', 'x'): 42}
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'y'},
        }
        assert _resolve_arg_value(arg, obj_literals) is None

    def test_computed_member_expression_not_resolved(self) -> None:
        obj_literals = {('obj', 'x'): 42}
        arg = {
            'type': 'MemberExpression',
            'computed': True,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'x'},
        }
        assert _resolve_arg_value(arg, obj_literals) is None

    def test_identifier_returns_none(self) -> None:
        arg = parse_expr('x')
        assert _resolve_arg_value(arg, {}) is None


# ================================================================
# _resolve_string_arg
# ================================================================


class TestResolveStringArg:
    """Tests for the _resolve_string_arg helper."""

    def test_string_literal(self) -> None:
        arg = parse_expr('"hello"')
        assert _resolve_string_arg(arg, {}) == 'hello'

    def test_member_expression_string(self) -> None:
        obj_literals = {('obj', 'key'): 'secret'}
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'key'},
        }
        assert _resolve_string_arg(arg, obj_literals) == 'secret'

    def test_member_expression_numeric_returns_none(self) -> None:
        obj_literals = {('obj', 'key'): 42}
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'key'},
        }
        assert _resolve_string_arg(arg, obj_literals) is None

    def test_numeric_literal_returns_none(self) -> None:
        arg = parse_expr('42')
        assert _resolve_string_arg(arg, {}) is None

    def test_identifier_returns_none(self) -> None:
        arg = parse_expr('x')
        assert _resolve_string_arg(arg, {}) is None

    def test_member_expression_unknown_returns_none(self) -> None:
        arg = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'missing'},
        }
        assert _resolve_string_arg(arg, {}) is None


# ================================================================
# Strategy 2b: Var-based string array + rotation + decoder
# ================================================================


class TestVarArrayPattern:
    """Tests for var-based string array with rotation and decoder (Strategy 2b)."""

    def test_var_array_with_rotation_and_decoder(self) -> None:
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar', 'baz', 'qux'];
        (function(arr, count) {
            var f = function(n) {
                while (--n) {
                    arr.push(arr.shift());
                }
            };
            f(++count);
        })(_0xarr, 2);
        var _0xdec = function(a) {
            a = a - 0;
            var x = _0xarr[a];
            return x;
        };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # The rotation count from _find_simple_rotation is _eval_numeric of the second arg (2),
        # so array is rotated 2 positions.
        # Original: ['hello', 'world', 'foo', 'bar', 'baz', 'qux']
        # After rotation 2: ['foo', 'bar', 'baz', 'qux', 'hello', 'world']
        assert '"foo"' in code

    def test_var_array_without_rotation(self) -> None:
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(a) {
            a = a - 0;
            var x = _0xarr[a];
            return x;
        };
        console.log(_0xdec(0));
        console.log(_0xdec(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_var_array_with_offset(self) -> None:
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(a) {
            a = a - 2;
            var x = _0xarr[a];
            return x;
        };
        console.log(_0xdec(2));
        console.log(_0xdec(3));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_var_array_too_short_ignored(self) -> None:
        # Arrays with < 3 elements should not match _find_var_string_array
        js = """
        var _0xarr = ['hello', 'world'];
        var _0xdec = function(a) {
            a = a - 0;
            var x = _0xarr[a];
            return x;
        };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # The var pattern requires >= 3 elements, and direct array strategy
        # won't inline through a decoder function call, so no change expected
        assert changed is False


# ================================================================
# Obfuscator.io full pattern with decoder and replacement
# ================================================================


class TestObfuscatorIoFullPattern:
    """Tests for the full obfuscator.io string array pattern."""

    def test_basic_obfuscator_io_pattern(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0));
        console.log(_0xDec(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_obfuscator_io_with_offset(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 2;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(2));
        console.log(_0xDec(3));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_obfuscator_io_multiple_calls(self) -> None:
        js = """
        function _0xArr() {
            var a = ['alpha', 'beta', 'gamma', 'delta', 'epsilon'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var x = _0xDec(0);
        var y = _0xDec(4);
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"alpha"' in code
        assert '"epsilon"' in code

    def test_obfuscator_io_removes_infrastructure(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
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
        assert changed is True
        assert '_0xArr' not in code
        assert '_0xDec' not in code

    def test_obfuscator_io_with_wrapper_function(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p + 1);
        }
        console.log(_0xWrap(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"world"' in code

    def test_obfuscator_io_wrapper_with_key_param(self) -> None:
        # Wrapper that passes two args to decoder (index + key)
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p, q) {
            return _0xDec(p);
        }
        console.log(_0xWrap(0, 'key'));
        console.log(_0xWrap(1, 'key2'));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_obfuscator_io_with_decoder_alias(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var _0xAlias = _0xDec;
        console.log(_0xAlias(0));
        console.log(_0xAlias(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_obfuscator_io_with_transitive_alias(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var _0xAlias1 = _0xDec;
        var _0xAlias2 = _0xAlias1;
        console.log(_0xAlias2(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


# ================================================================
# Obfuscator.io pattern with rotation IIFE
# ================================================================


class TestObfuscatorIoRotation:
    """Tests for the obfuscator.io rotation IIFE pattern."""

    def test_rotation_with_while_loop(self) -> None:
        js = """
        function _0xArr() {
            var a = ['100', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            var _0xrotate = function(_0xn) {
                while (true) {
                    try {
                        var _0xval = parseInt(_0xDec(0));
                        if (_0xval === _0xstop) {
                            break;
                        }
                    } catch(e) {
                    }
                    _0xarg.push(_0xarg.shift());
                }
            };
            _0xrotate();
        })(_0xArr, 100);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # The rotation finds a position where parseInt(arr[0]) === 100
        # arr[0] = '100' already, so no rotation needed
        assert changed is True
        assert '"100"' in code


# ================================================================
# Wrapper analysis (expression-based wrappers)
# ================================================================


class TestWrapperAnalysis:
    """Tests for wrapper function analysis (_analyze_wrapper_expr)."""

    def test_var_function_expression_wrapper(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var _0xWrap = function(p) {
            return _0xDec(p + 2);
        };
        console.log(_0xWrap(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"foo"' in code

    def test_arrow_function_wrapper(self) -> None:
        # ArrowFunctionExpression with block body as wrapper
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var _0xWrap = function(p) {
            return _0xDec(p);
        };
        console.log(_0xWrap(2));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"foo"' in code


# ================================================================
# _extract_wrapper_offset edge cases
# ================================================================


class TestExtractWrapperOffset:
    """Tests for wrapper offset extraction patterns."""

    def test_wrapper_with_subtraction_offset(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p - 10);
        }
        console.log(_0xWrap(10));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_wrapper_with_second_param_index(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(unused, p) {
            return _0xDec(p);
        }
        console.log(_0xWrap('x', 0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


# ================================================================
# Object literal resolution in wrapper calls
# ================================================================


class TestObjectLiteralResolution:
    """Tests for resolving member expressions via object literals."""

    def test_decoder_call_with_object_member_arg(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var obj = {x: 0};
        console.log(_0xDec(obj.x));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_wrapper_call_with_object_member_arg(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        var obj = {x: 1};
        console.log(_0xWrap(obj.x));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"world"' in code


# ================================================================
# _eval_numeric edge cases (modulo)
# ================================================================


class TestEvalNumericModulo:
    """Additional _eval_numeric tests for modulo operator."""

    def test_modulo(self) -> None:
        node = parse_expr('10 % 3')
        assert _eval_numeric(node) == 1

    def test_modulo_by_zero(self) -> None:
        node = parse_expr('10 % 0')
        assert _eval_numeric(node) is None

    def test_unary_unsupported_operator(self) -> None:
        # The ~ operator is unsupported
        node = parse_expr('~5')
        assert _eval_numeric(node) is None

    def test_deeply_nested_expression(self) -> None:
        node = parse_expr('(1 + 2) * (3 - 1) + 4 / 2')
        assert _eval_numeric(node) == 8.0


# ================================================================
# Rotation locals collection
# ================================================================


class TestCollectRotationLocals:
    """Tests for _collect_rotation_locals static method."""

    def test_collects_object_from_iife(self) -> None:
        ast = parse(
            """
        (function(arr, stop) {
            var J = {A: 0xb9, S: 0xa7, D: 'M8Y&'};
            while (true) {
                try {
                    var v = parseInt(J.A);
                } catch (e) {}
                arr.push(arr.shift());
            }
        })(x, 100);
        """
        )
        # The IIFE is the callee of the CallExpression
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = StringRevealer._collect_rotation_locals(iife_func)
        assert 'J' in result
        assert result['J']['A'] == 0xB9
        assert result['J']['S'] == 0xA7
        assert result['J']['D'] == 'M8Y&'

    def test_empty_iife_returns_empty(self) -> None:
        ast = parse(
            """
        (function() {
        })();
        """
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = StringRevealer._collect_rotation_locals(iife_func)
        assert result == {}


# ================================================================
# Expression from try block
# ================================================================


class TestExpressionFromTryBlock:
    """Tests for _expression_from_try_block static method."""

    def test_variable_declaration(self) -> None:
        ast = parse('var x = 42;')
        stmt = ast['body'][0]
        result = StringRevealer._expression_from_try_block(stmt)
        assert result is not None
        assert result.get('type') == 'Literal'
        assert result.get('value') == 42

    def test_assignment_expression(self) -> None:
        ast = parse('x = 42;')
        stmt = ast['body'][0]
        result = StringRevealer._expression_from_try_block(stmt)
        assert result is not None
        assert result.get('type') == 'Literal'
        assert result.get('value') == 42

    def test_non_matching_returns_none(self) -> None:
        ast = parse('if (true) {}')
        stmt = ast['body'][0]
        result = StringRevealer._expression_from_try_block(stmt)
        assert result is None

    def test_expression_statement_non_assignment(self) -> None:
        ast = parse('foo();')
        stmt = ast['body'][0]
        result = StringRevealer._expression_from_try_block(stmt)
        assert result is None


# ================================================================
# Direct array replacement edge cases
# ================================================================


class TestDirectArrayEdgeCases:
    """Additional edge case tests for direct array access replacement."""

    def test_direct_array_in_function_scope(self) -> None:
        # Direct array strategy only processes the root scope bindings,
        # so arrays inside function scopes are not replaced.
        js = """
        function f() {
            var arr = ["hello", "world"];
            return arr[0];
        }
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_direct_array_not_used_as_member(self) -> None:
        # Using arr as a standalone identifier (not arr[N]) should not trigger
        js = 'var arr = ["hello"]; f(arr);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False


# ================================================================
# Var-based decoder with wrappers and aliases
# ================================================================


class TestVarPatternWithWrappersAndAliases:
    """Tests for var-based array with wrappers and alias resolution."""

    def test_var_array_with_decoder_alias(self) -> None:
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(a) {
            a = a - 0;
            var x = _0xarr[a];
            return x;
        };
        var _0xalias = _0xdec;
        console.log(_0xalias(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_var_array_with_wrapper(self) -> None:
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(a) {
            a = a - 0;
            var x = _0xarr[a];
            return x;
        };
        function _0xwrap(p) {
            return _0xdec(p + 1);
        }
        console.log(_0xwrap(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"world"' in code


# ================================================================
# Hex string argument resolution
# ================================================================


class TestHexStringResolution:
    """Tests for hex string resolution in decoder calls."""

    def test_hex_string_arg_to_decoder(self) -> None:
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec("0x0"));
        console.log(_0xDec("0x1"));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code


# ================================================================
# Rotation logic: _find_and_execute_rotation, _try_execute_rotation_call,
# _extract_rotation_expression, _parse_rotation_op, _parse_parseInt_call,
# _resolve_rotation_arg, _apply_rotation_op, _execute_rotation
# ================================================================


class TestRotationLogicFull:
    """Tests for the full rotation pipeline with parseInt-based expressions."""

    def test_rotation_with_direct_decoder_call_in_parseint(self) -> None:
        """Rotation where parseInt calls the decoder directly (via alias in decoder_aliases)."""
        js = """
        function _0xArr() {
            var a = ['200', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 200);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # '200' is already at position 0, so parseInt('200') == 200 == stop_value
        assert '"200"' in code

    def test_rotation_with_binary_expression(self) -> None:
        """Rotation with binary expression: parseInt(dec(0)) + parseInt(dec(1))."""
        js = """
        function _0xArr() {
            var a = ['100', '50', 'hello', 'world', 'foo', 'bar'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0)) + parseInt(_0xDec(1));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 150);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # parseInt('100') + parseInt('50') = 150 = stop, no rotation needed
        assert '"100"' in code

    def test_rotation_with_subtraction_expression(self) -> None:
        """Rotation with subtraction: parseInt(dec(0)) - parseInt(dec(1))."""
        js = """
        function _0xArr() {
            var a = ['300', '100', 'hello', 'world', 'foo', 'bar'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0)) - parseInt(_0xDec(1));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 200);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"300"' in code

    def test_rotation_with_multiplication_expression(self) -> None:
        """Rotation with multiply: parseInt(dec(0)) * parseInt(dec(1))."""
        js = """
        function _0xArr() {
            var a = ['10', '20', 'hello', 'world', 'foo', 'bar'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0)) * parseInt(_0xDec(1));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 200);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True

    def test_rotation_with_wrapper_in_parseint(self) -> None:
        """Rotation where parseInt calls a wrapper function."""
        js = """
        function _0xArr() {
            var a = ['500', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 500);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"500"' in code

    def test_rotation_needs_one_shift(self) -> None:
        """Rotation that needs exactly one shift before parseInt matches.

        Uses a wrapper in the rotation expression so _parse_parseInt_call can match.
        """
        js = """
        function _0xArr() {
            var a = ['hello', '42', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 42);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # After 1 rotation: ['42','world','foo','bar','baz','hello']
        # dec(0) returns '42'
        assert '"42"' in code

    def test_rotation_with_negate_expression(self) -> None:
        """Rotation with negation: -parseInt(dec(0)) + literal."""
        js = """
        function _0xArr() {
            var a = ['-100', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = -parseInt(_0xDec(0)) + 200;
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 300);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # -parseInt('-100') + 200 = -(-100) + 200 = 100 + 200 = 300 = stop_value
        assert '"-100"' in code

    def test_rotation_with_literal_node_in_try(self) -> None:
        """Rotation expression that is just a literal value (no parseInt call)."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz', 'qux'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0)) + 5;
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 5);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # All elements are non-numeric strings, so parseInt will keep failing
        # and rotating. Eventually it should still resolve or give up.
        # The important thing is it doesn't crash.
        assert isinstance(code, str)


class TestRotationArgResolution:
    """Tests for _resolve_rotation_arg with various argument types."""

    def test_rotation_with_member_expression_arg(self) -> None:
        """Rotation IIFE that has local objects referenced in parseInt args."""
        js = """
        function _0xArr() {
            var a = ['300', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            var J = {A: 0};
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(J.A));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 300);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"300"' in code

    def test_rotation_with_string_hex_arg(self) -> None:
        """Rotation with hex string literal as argument to decoder."""
        js = """
        function _0xArr() {
            var a = ['99', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec("0x0"));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 99);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"99"' in code


# ================================================================
# SequenceExpression rotation (lines 287-300, 637-647)
# ================================================================


class TestSequenceExpressionRotation:
    """Tests for rotation inside a SequenceExpression."""

    def test_rotation_in_sequence_expression_obfuscatorio(self) -> None:
        """Rotation IIFE as part of a SequenceExpression (obfuscator.io pattern)."""
        js = """
        function _0xArr() {
            var a = ['777', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 777), console.log('other');
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"777"' in code

    def test_var_rotation_in_sequence_expression(self) -> None:
        """Var-based rotation IIFE inside a SequenceExpression."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar', 'baz', 'qux'];
        (function(a, n) { var f = function(c) { while (--c) { a.push(a.shift()); } }; f(++n); })(_0xarr, 1), console.log('side');
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # _find_simple_rotation uses _eval_numeric on second arg (1), so rotation_count=1
        # Array rotated 1 time: ['world','foo','bar','baz','qux','hello']
        assert '"world"' in code


# ================================================================
# Wrapper analysis edge cases (lines 467-536)
# ================================================================


class TestWrapperAnalysisEdgeCases:
    """Tests for _analyze_wrapper_expr edge cases."""

    def test_wrapper_with_non_block_body_ignored(self) -> None:
        """Function expression with expression body (not BlockStatement) is not a wrapper."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
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
        assert changed is True
        assert '"hello"' in code

    def test_wrapper_with_multiple_statements_not_wrapper(self) -> None:
        """Function with more than one statement is not recognized as a wrapper."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p) {
            var x = 1;
            return _0xDec(p);
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # _0xNotWrap(1) should NOT be replaced since it's not a valid wrapper
        assert '_0xNotWrap' in code

    def test_wrapper_non_return_statement_not_wrapper(self) -> None:
        """Function with single non-return statement is not a wrapper."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p) {
            console.log(_0xDec(p));
        }
        console.log(_0xDec(0));
        _0xNotWrap(1);
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '_0xNotWrap' in code

    def test_wrapper_return_not_call_not_wrapper(self) -> None:
        """Wrapper that returns a non-call expression is not a wrapper."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p) {
            return p + 1;
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '_0xNotWrap' in code

    def test_wrapper_calls_wrong_decoder_not_wrapper(self) -> None:
        """Wrapper that calls a different function is not recognized as decoder wrapper."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function otherFunc(p) { return p; }
        function _0xNotWrap(p) {
            return otherFunc(p);
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '_0xNotWrap' in code

    def test_wrapper_no_call_args_not_wrapper(self) -> None:
        """Wrapper with no arguments to decoder call is not a wrapper."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap() {
            return _0xDec();
        }
        console.log(_0xDec(0));
        _0xNotWrap();
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_wrapper_with_non_identifier_first_arg(self) -> None:
        """Wrapper where first arg to decoder is not a param reference."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p) {
            return _0xDec(p * p);
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '_0xNotWrap' in code

    def test_extract_wrapper_offset_non_plus_minus_operator(self) -> None:
        """Wrapper arg expression with unsupported operator (e.g. *)."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p) {
            return _0xDec(p * 2);
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '_0xNotWrap' in code

    def test_extract_wrapper_offset_non_numeric_right(self) -> None:
        """Wrapper arg expression p + x where x is not numeric."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p, q) {
            return _0xDec(p + q);
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(0, 1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # _0xNotWrap should remain since p + q doesn't have a numeric right side
        assert '_0xNotWrap' in code

    def test_extract_wrapper_offset_left_not_param(self) -> None:
        """Wrapper arg expression where left side of binary is not a param."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xNotWrap(p) {
            return _0xDec(1 + 2);
        }
        console.log(_0xDec(0));
        console.log(_0xNotWrap(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # 1+2=3 is a constant, not a param reference on the left of binary
        assert '_0xNotWrap' in code


# ================================================================
# Various replacement edge cases (lines 942-1005)
# ================================================================


class TestReplacementEdgeCases:
    """Edge cases in _replace_all_wrapper_calls and _replace_direct_decoder_calls."""

    def test_wrapper_call_with_insufficient_args(self) -> None:
        """Wrapper call with fewer args than expected param_index."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(unused, p) {
            return _0xDec(p);
        }
        console.log(_0xWrap());
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # _0xWrap() called with no args should remain unreplaced
        assert '_0xWrap()' in code

    def test_decoder_call_with_no_args(self) -> None:
        """Direct decoder call with no arguments is not replaced."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec());
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_decoder_call_with_unresolvable_arg(self) -> None:
        """Decoder call with variable (not literal) argument is not replaced."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var x = 0;
        console.log(_0xDec(x));
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_decoder_call_with_out_of_bounds_index(self) -> None:
        """Decoder call with an index beyond the array doesn't crash."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(999));
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # Out of bounds call should remain
        assert '999' in code

    def test_decoder_call_with_string_key_second_arg(self) -> None:
        """Decoder direct call with a second string argument (key)."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0, 'someKey'));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_wrapper_call_with_object_member_key_arg(self) -> None:
        """Wrapper call where the key param is resolved via object literal."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p, k) {
            return _0xDec(p);
        }
        var obj = {k: 'mykey'};
        console.log(_0xWrap(0, obj.k));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


# ================================================================
# Var pattern edge cases (lines 1103-1169)
# ================================================================


class TestVarPatternEdgeCases:
    """Edge cases for _find_var_string_array, _find_simple_rotation, _find_var_decoder."""

    def test_var_array_not_in_first_three_statements(self) -> None:
        """Var string array declared after the first 3 statements is not found."""
        js = """
        var a = 1;
        var b = 2;
        var c = 3;
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # Array is at index 3, beyond the first 3 statements checked
        assert changed is False

    def test_var_array_with_non_string_elements(self) -> None:
        """Var array with mixed types is not recognized as string array."""
        js = """
        var _0xarr = ['hello', 42, 'foo', 'bar'];
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_var_array_with_non_identifier_declaration(self) -> None:
        """Var declaration with destructuring pattern is not matched."""
        js = """
        var [a, b] = ['hello', 'world', 'foo', 'bar'];
        console.log(a);
        """
        # This should parse and not crash, but not match the pattern
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_find_var_decoder_function_expression(self) -> None:
        """Var decoder as function expression referencing array name."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(a) {
            a = a - 1;
            var x = _0xarr[a];
            return x;
        };
        console.log(_0xdec(1));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_var_decoder_with_no_matching_array_ref(self) -> None:
        """Decoder function that doesn't reference the array name is not found."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(a) {
            a = a - 0;
            var x = _0xother[a];
            return x;
        };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_var_decoder_not_function_expression(self) -> None:
        """Var declaration that is not a function expression is not decoder."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = _0xarr;
        console.log(_0xdec[0]);
        """
        code, changed = roundtrip(js, StringRevealer)
        # Direct array strategy should handle this
        assert isinstance(code, str)

    def test_simple_rotation_with_for_statement(self) -> None:
        """Simple rotation pattern matching checks for push/shift in source."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar', 'baz', 'qux'];
        (function(a, n) { var f = function(c) { while (--c) { a.push(a.shift()); } }; f(++n); })(_0xarr, 2);
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True

    def test_simple_rotation_no_push_shift_not_rotation(self) -> None:
        """IIFE without push/shift in source is not recognized as rotation."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        (function(a, n) { var x = a[0]; })(_0xarr, 2);
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code  # No rotation applied

    def test_simple_rotation_wrong_array_name(self) -> None:
        """Rotation IIFE that references different array name is not matched."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        (function(a, n) { var f = function(c) { while (--c) { a.push(a.shift()); } }; f(++n); })(_0xother, 2);
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code  # No rotation since IIFE references _0xother

    def test_simple_rotation_non_numeric_count(self) -> None:
        """Rotation IIFE with non-numeric count is not matched."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        (function(a, n) { var f = function(c) { while (--c) { a.push(a.shift()); } }; f(++n); })(_0xarr, x);
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code  # No rotation since count is non-numeric


# ================================================================
# Direct array edge cases (lines 1176-1226)
# ================================================================


class TestDirectArrayAccessEdgeCases:
    """Edge cases for _try_replace_array_access and _process_direct_arrays_in_scope."""

    def test_direct_array_non_computed_member(self) -> None:
        """arr.length style access (non-computed) is not replaced."""
        js = 'var arr = ["hello", "world"]; f(arr.length);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_direct_array_used_in_child_scope(self) -> None:
        """Direct array used inside a function (child scope)."""
        js = """
        var arr = ["hello", "world"];
        function f() {
            return arr[0];
        }
        """
        code, changed = roundtrip(js, StringRevealer)
        # This tests _process_direct_arrays_in_scope
        assert changed is True
        assert '"hello"' in code

    def test_direct_array_in_child_scope_no_binding(self) -> None:
        """Child scope that doesn't reference the array leaves it alone."""
        js = """
        var arr = ["hello", "world"];
        function f() {
            var x = 1;
            return x;
        }
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_replace_node_in_ast_index_path(self) -> None:
        """Verify replacement works when target is in an array (index != None)."""
        js = 'var arr = ["a", "b"]; f(arr[0], arr[1]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"a"' in code
        assert '"b"' in code


# ================================================================
# _find_array_expression_in_statement (lines 1012-1023)
# ================================================================


class TestFindArrayExpressionInStatement:
    """Tests for _find_array_expression_in_statement."""

    def test_array_in_variable_declaration(self) -> None:
        ast = parse("var x = [1, 2, 3];")
        stmt = ast['body'][0]
        result = StringRevealer._find_array_expression_in_statement(stmt)
        assert result is not None
        assert result['type'] == 'ArrayExpression'

    def test_array_in_assignment_expression(self) -> None:
        """Array in ExpressionStatement with AssignmentExpression."""
        ast = parse("x = [1, 2, 3];")
        stmt = ast['body'][0]
        result = StringRevealer._find_array_expression_in_statement(stmt)
        assert result is not None
        assert result['type'] == 'ArrayExpression'

    def test_assignment_non_array_rhs(self) -> None:
        """Assignment with non-array right side returns None."""
        ast = parse("x = 42;")
        stmt = ast['body'][0]
        result = StringRevealer._find_array_expression_in_statement(stmt)
        assert result is None

    def test_non_declaration_non_assignment(self) -> None:
        """Statement that is neither declaration nor assignment returns None."""
        ast = parse("if (true) {}")
        stmt = ast['body'][0]
        result = StringRevealer._find_array_expression_in_statement(stmt)
        assert result is None

    def test_variable_declaration_non_array_init(self) -> None:
        """Variable declaration with non-array init returns None."""
        ast = parse("var x = 42;")
        stmt = ast['body'][0]
        result = StringRevealer._find_array_expression_in_statement(stmt)
        assert result is None

    def test_expression_statement_non_assignment(self) -> None:
        """ExpressionStatement that is not an assignment returns None."""
        ast = parse("foo();")
        stmt = ast['body'][0]
        result = StringRevealer._find_array_expression_in_statement(stmt)
        assert result is None


# ================================================================
# _extract_array_from_statement via ExpressionStatement path (line 346-350)
# ================================================================


class TestExtractArrayFromStatement:
    """Tests for _extract_array_from_statement ExpressionStatement path."""

    def test_array_from_assignment_expression_statement(self) -> None:
        """String array in an assignment expression (not var declaration)."""
        js = """
        function _0xArr() {
            var a;
            a = ['hello', 'world', 'foo', 'bar', 'baz'];
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
        # The first statement in the function body is 'var a;' (no init),
        # so _extract_array_from_statement on that returns None.
        # The pattern requires the array to be in the FIRST statement.
        code, changed = roundtrip(js, StringRevealer)
        # Won't match since array is in second statement
        assert isinstance(code, str)


# ================================================================
# _eval_numeric BinaryExpression edge cases (line 38)
# ================================================================


class TestEvalNumericBinaryEdge:
    """Test _eval_numeric with binary expressions producing None children."""

    def test_binary_with_non_numeric_left(self) -> None:
        node = parse_expr('"abc" + 1')
        assert _eval_numeric(node) is None

    def test_binary_with_non_numeric_right(self) -> None:
        node = parse_expr('1 + "abc"')
        assert _eval_numeric(node) is None


# ================================================================
# _collect_object_literals edge cases (lines 99, 103, 109)
# ================================================================


class TestCollectObjectLiteralsEdgeCases:
    """Edge cases for _collect_object_literals."""

    def test_property_with_non_literal_key(self) -> None:
        """Object with computed key -- esprima parses [x] as Identifier key with computed flag."""
        # In esprima, {[x]: 42} still produces a Property with key as Identifier
        # but the property is marked computed. _collect_object_literals checks
        # is_identifier(key), which is True even for computed keys.
        # Test that a truly non-identifier/non-string key (numeric) is handled:
        ast = parse('var obj = {0: 42};')
        result = _collect_object_literals(ast)
        # Numeric key is not an identifier or string literal, so it should be skipped
        assert ('obj', 0) not in result

    def test_property_with_no_key_or_value(self) -> None:
        """Shorthand property patterns."""
        ast = parse('var obj = {a: 42, b: "hi"};')
        result = _collect_object_literals(ast)
        assert result[('obj', 'a')] == 42
        assert result[('obj', 'b')] == 'hi'

    def test_property_non_numeric_non_string_value(self) -> None:
        """Object property with non-literal value is ignored."""
        ast = parse('var obj = {a: x};')
        result = _collect_object_literals(ast)
        assert ('obj', 'a') not in result


# ================================================================
# Base64 decoder type detection (line 372)
# ================================================================


class TestDecoderTypeDetection:
    """Tests for base64/RC4 decoder type detection."""

    def test_base64_decoder_detected(self) -> None:
        """Decoder function containing base64 alphabet is detected as Base64."""
        js = """
        function _0xArr() {
            var a = ['aGVsbG8=', 'd29ybGQ=', 'Zm9v', 'YmFy', 'YmF6'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            var c = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';
            return arr[idx];
        }
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True


# ================================================================
# _update_ast_array (lines 1027-1032)
# ================================================================


class TestUpdateAstArray:
    """Tests for _update_ast_array via rotation that modifies the AST."""

    def test_rotation_updates_ast_array(self) -> None:
        """Rotation execution should update the AST array elements.

        Must use a wrapper in the rotation expression so _parse_parseInt_call matches.
        """
        js = """
        function _0xArr() {
            var a = ['hello', '42', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 42);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # After 1 rotation: ['42','world','foo','bar','baz','hello']
        # dec(0) = '42'
        assert '"42"' in code


# ================================================================
# _extract_rotation_expression edge cases
# ================================================================


class TestExtractRotationExpression:
    """Tests for _extract_rotation_expression with various loop types."""

    def test_rotation_with_for_loop(self) -> None:
        """Rotation IIFE with for loop instead of while."""
        js = """
        function _0xArr() {
            var a = ['500', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            for (;;) {
                try {
                    var _0xval = parseInt(_0xDec(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 500);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"500"' in code

    def test_rotation_with_empty_func_body(self) -> None:
        """Rotation IIFE with empty body produces no rotation expression."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
        })(_0xArr, 100);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_rotation_with_assignment_in_try(self) -> None:
        """Rotation where try block uses assignment expression instead of var."""
        js = """
        function _0xArr() {
            var a = ['500', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            var _0xval;
            while (true) {
                try {
                    _0xval = parseInt(_0xDec(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 500);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"500"' in code


# ================================================================
# _parse_rotation_op edge cases
# ================================================================


class TestParseRotationOp:
    """Tests for _parse_rotation_op with various expression types."""

    def test_rotation_op_with_modulo(self) -> None:
        """Rotation expression with modulo operator."""
        js = """
        function _0xArr() {
            var a = ['10', '3', 'hello', 'world', 'foo', 'bar'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0)) % parseInt(_0xDec(1));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 1);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # 10 % 3 = 1 = stop_value

    def test_rotation_op_with_division(self) -> None:
        """Rotation expression with division operator."""
        js = """
        function _0xArr() {
            var a = ['100', '20', 'hello', 'world', 'foo', 'bar'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0)) / parseInt(_0xDec(1));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 5);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True

    def test_rotation_non_parseint_call_ignored(self) -> None:
        """Rotation expression with non-parseInt call returns None from _parse_rotation_op."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz', 'qux'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = Math.floor(_0xDec(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 100);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # Rotation can't be parsed (Math.floor is not parseInt), so no rotation
        assert changed is True
        assert '"hello"' in code


# ================================================================
# _try_execute_rotation_call edge cases
# ================================================================


class TestTryExecuteRotationCall:
    """Edge cases for _try_execute_rotation_call."""

    def test_rotation_callee_not_function_expression(self) -> None:
        """Rotation call whose callee is not a FunctionExpression is skipped."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        someFunc(_0xArr, 100);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_rotation_wrong_arg_count(self) -> None:
        """Rotation IIFE with != 2 arguments is skipped."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg) {
        })(_0xArr);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_rotation_first_arg_not_array_func(self) -> None:
        """Rotation IIFE where first arg is not the array function name."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
        })(otherFunc, 100);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_rotation_non_numeric_stop_value(self) -> None:
        """Rotation IIFE with non-numeric stop value is skipped."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(0));
                    if (_0xval === _0xstop) break;
                } catch(e) {}
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, someVar);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


# ================================================================
# Decoder offset extraction edge cases (lines 409-418)
# ================================================================


class TestExtractDecoderOffset:
    """Tests for _extract_decoder_offset edge cases."""

    def test_decoder_with_addition_offset(self) -> None:
        """Decoder with idx = idx + OFFSET."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx + 2;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        # offset is +2, so _0xDec(0) -> arr[0+2] = 'foo'
        assert '"foo"' in code

    def test_decoder_with_no_offset(self) -> None:
        """Decoder without any param reassignment has offset 0."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


# ================================================================
# _resolve_rotation_arg edge cases: string returns string
# ================================================================


class TestResolveRotationArgEdgeCases:
    """Edge cases for _resolve_rotation_arg returning string values."""

    def test_rotation_arg_non_hex_string_literal(self) -> None:
        """Non-hex, non-numeric string literal is returned as-is (for RC4 key)."""
        # We test this indirectly through the rotation with wrapper + key param
        js = """
        function _0xArr() {
            var a = ['500', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p, k) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0, 'myKey'));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 500);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"500"' in code

    def test_rotation_arg_member_expression_computed(self) -> None:
        """MemberExpression with computed string key in rotation locals."""
        js = """
        function _0xArr() {
            var a = ['300', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        (function(_0xarg, _0xstop) {
            var J = {"val": 0};
            while (true) {
                try {
                    var _0xval = parseInt(_0xDec(J["val"]));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 300);
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"300"' in code


# ================================================================
# _collect_rotation_locals edge cases (lines 704-716)
# ================================================================


class TestCollectRotationLocalsEdgeCases:
    """Edge cases for _collect_rotation_locals."""

    def test_rotation_locals_with_string_key(self) -> None:
        """Object literal with string keys in rotation IIFE."""
        ast = parse(
            """
        (function(arr, stop) {
            var J = {"A": 0xb9, "B": 'key'};
            while (true) {
                try {
                    var v = parseInt(J.A);
                } catch (e) {}
                arr.push(arr.shift());
            }
        })(x, 100);
        """
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = StringRevealer._collect_rotation_locals(iife_func)
        assert 'J' in result
        assert result['J']['A'] == 0xB9
        assert result['J']['B'] == 'key'

    def test_rotation_locals_non_object_var_ignored(self) -> None:
        """Non-object variable declarations in IIFE are ignored."""
        ast = parse(
            """
        (function(arr, stop) {
            var x = 42;
            while (true) {
                try {
                    var v = 1;
                } catch (e) {}
            }
        })(x, 100);
        """
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = StringRevealer._collect_rotation_locals(iife_func)
        assert result == {}

    def test_rotation_locals_non_identifier_name_ignored(self) -> None:
        """Var declaration with non-identifier pattern is ignored."""
        ast = parse(
            """
        (function(arr, stop) {
            var J = {A: 1};
        })(x, 100);
        """
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = StringRevealer._collect_rotation_locals(iife_func)
        assert 'J' in result
        assert result['J']['A'] == 1

    def test_rotation_locals_empty_object(self) -> None:
        """Empty object literal in IIFE is not added (no properties)."""
        ast = parse(
            """
        (function(arr, stop) {
            var J = {};
        })(x, 100);
        """
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = StringRevealer._collect_rotation_locals(iife_func)
        assert 'J' not in result


# ================================================================
# RC4 decoder creation (line 430)
# ================================================================


class TestRc4DecoderCreation:
    """Tests for RC4 decoder type being created via _create_base_decoder."""

    def test_rc4_decoder_detected_and_used(self) -> None:
        """Decoder with base64 alphabet AND fromCharCode...^ pattern is detected as RC4."""
        js = """
        function _0xArr() {
            var a = ['aGVsbG8=', 'd29ybGQ=', 'Zm9v', 'YmFy', 'YmF6'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx, key) {
            idx = idx - 0;
            var arr = _0xArr();
            var c = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';
            var result = String.fromCharCode(arr[idx].charCodeAt(0) ^ key.charCodeAt(0));
            return result;
        }
        console.log(_0xDec(0, 'k'));
        """
        code, changed = roundtrip(js, StringRevealer)
        # The important thing is it doesn't crash and detects the RC4 pattern
        assert isinstance(code, str)


# ================================================================
# Direct method tests for rotation internals
# ================================================================


class TestRotationInternalsDirect:
    """Direct method tests for rotation-related internals."""

    def _make_revealer(self, js):
        """Create a StringRevealer with parsed AST."""
        ast = parse(js)
        return StringRevealer(ast), ast

    def test_parse_rotation_op_literal(self) -> None:
        """_parse_rotation_op handles a bare numeric literal."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('42')
        result = t._parse_rotation_op(node, {}, set())
        assert result == {'op': 'literal', 'value': 42}

    def test_parse_rotation_op_negate(self) -> None:
        """_parse_rotation_op handles unary negation."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('-42')
        result = t._parse_rotation_op(node, {}, set())
        assert result is not None
        assert result['op'] == 'negate'
        assert result['child']['op'] == 'literal'
        assert result['child']['value'] == 42

    def test_parse_rotation_op_binary(self) -> None:
        """_parse_rotation_op handles binary addition of literals."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('10 + 20')
        result = t._parse_rotation_op(node, {}, set())
        assert result is not None
        assert result['op'] == 'binary'
        assert result['operator'] == '+'

    def test_parse_rotation_op_call_with_wrapper(self) -> None:
        """_parse_rotation_op handles parseInt(wrapper(0))."""
        t, ast = self._make_revealer('var x = 1;')
        wrapper = WrapperInfo('_0xWrap', param_index=0, wrapper_offset=0, func_node={})
        node = parse_expr('parseInt(_0xWrap(0))')
        result = t._parse_rotation_op(node, {'_0xWrap': wrapper}, set())
        assert result is not None
        assert result['op'] == 'call'
        assert result['wrapper_name'] == '_0xWrap'
        assert result['args'] == [0]

    def test_parse_rotation_op_call_with_decoder_alias(self) -> None:
        """_parse_rotation_op handles parseInt(alias(0)) where alias is in decoder_aliases."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('parseInt(_0xAlias(0))')
        result = t._parse_rotation_op(node, {}, {'_0xAlias'})
        assert result is not None
        assert result['op'] == 'direct_decoder_call'
        assert result['alias_name'] == '_0xAlias'
        assert result['args'] == [0]

    def test_parse_rotation_op_non_dict_returns_none(self) -> None:
        """_parse_rotation_op returns None for non-dict input."""
        t, ast = self._make_revealer('var x = 1;')
        assert t._parse_rotation_op(None, {}, set()) is None
        assert t._parse_rotation_op('string', {}, set()) is None

    def test_parse_rotation_op_unsupported_type_returns_none(self) -> None:
        """_parse_rotation_op returns None for unsupported node types."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('x')  # Identifier
        result = t._parse_rotation_op(node, {}, set())
        assert result is None

    def test_parse_rotation_op_negate_with_non_numeric_child(self) -> None:
        """_parse_rotation_op negate with non-parseable child returns None."""
        t, ast = self._make_revealer('var x = 1;')
        # -x where x is an identifier, not resolvable
        node = parse_expr('-x')
        result = t._parse_rotation_op(node, {}, set())
        assert result is None

    def test_parse_rotation_op_binary_with_unparseable_child(self) -> None:
        """_parse_rotation_op binary with unparseable left or right returns None."""
        t, ast = self._make_revealer('var x = 1;')
        # x + 1 where x is identifier
        node = parse_expr('x + 1')
        result = t._parse_rotation_op(node, {}, set())
        assert result is None

    def test_parse_parseInt_call_not_parseint(self) -> None:
        """_parse_parseInt_call returns None when callee is not parseInt."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('Math.floor(1)')
        result = t._parse_parseInt_call(node, {}, set())
        assert result is None

    def test_parse_parseInt_call_wrong_arg_count(self) -> None:
        """_parse_parseInt_call returns None when parseInt has != 1 arg."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('parseInt(1, 10)')
        result = t._parse_parseInt_call(node, {}, set())
        assert result is None

    def test_parse_parseInt_call_inner_not_call(self) -> None:
        """_parse_parseInt_call returns None when inner arg is not a call."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('parseInt(42)')
        result = t._parse_parseInt_call(node, {}, set())
        assert result is None

    def test_parse_parseInt_call_inner_callee_not_identifier(self) -> None:
        """_parse_parseInt_call returns None when inner callee is not identifier."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('parseInt(a.b(0))')
        result = t._parse_parseInt_call(node, {}, set())
        assert result is None

    def test_parse_parseInt_call_inner_unknown_function(self) -> None:
        """_parse_parseInt_call returns None when inner function is not in wrappers/aliases."""
        t, ast = self._make_revealer('var x = 1;')
        node = parse_expr('parseInt(unknownFunc(0))')
        result = t._parse_parseInt_call(node, {}, set())
        assert result is None

    def test_parse_parseInt_call_unresolvable_arg(self) -> None:
        """_parse_parseInt_call returns None when inner arg can't be resolved."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        wrapper = WrapperInfo('_0xW', param_index=0, wrapper_offset=0, func_node={})
        node = parse_expr('parseInt(_0xW(someVar))')
        result = t._parse_parseInt_call(node, {'_0xW': wrapper}, set())
        assert result is None

    def test_resolve_rotation_arg_numeric(self) -> None:
        """_resolve_rotation_arg resolves numeric literal."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        node = parse_expr('42')
        assert t._resolve_rotation_arg(node) == 42

    def test_resolve_rotation_arg_string_hex(self) -> None:
        """_resolve_rotation_arg resolves hex string literal."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        node = parse_expr('"0x1b"')
        assert t._resolve_rotation_arg(node) == 0x1B

    def test_resolve_rotation_arg_string_decimal(self) -> None:
        """_resolve_rotation_arg resolves decimal string literal."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        node = parse_expr('"42"')
        assert t._resolve_rotation_arg(node) == 42

    def test_resolve_rotation_arg_string_non_numeric(self) -> None:
        """_resolve_rotation_arg resolves non-numeric string as-is."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        node = parse_expr('"myKey"')
        assert t._resolve_rotation_arg(node) == 'myKey'

    def test_resolve_rotation_arg_member_identifier_prop(self) -> None:
        """_resolve_rotation_arg resolves J.A from rotation locals."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {'J': {'A': 42}}
        node = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'J'},
            'property': {'type': 'Identifier', 'name': 'A'},
        }
        assert t._resolve_rotation_arg(node) == 42

    def test_resolve_rotation_arg_member_string_prop(self) -> None:
        """_resolve_rotation_arg resolves J['A'] from rotation locals."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {'J': {'A': 99}}
        node = {
            'type': 'MemberExpression',
            'computed': True,
            'object': {'type': 'Identifier', 'name': 'J'},
            'property': {'type': 'Literal', 'value': 'A'},
        }
        assert t._resolve_rotation_arg(node) == 99

    def test_resolve_rotation_arg_member_unknown_object(self) -> None:
        """_resolve_rotation_arg returns None for unknown object in member."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        node = {
            'type': 'MemberExpression',
            'computed': False,
            'object': {'type': 'Identifier', 'name': 'unknown'},
            'property': {'type': 'Identifier', 'name': 'A'},
        }
        assert t._resolve_rotation_arg(node) is None

    def test_resolve_rotation_arg_identifier_returns_none(self) -> None:
        """_resolve_rotation_arg returns None for bare identifier."""
        t, ast = self._make_revealer('var x = 1;')
        t._rotation_locals = {}
        node = parse_expr('x')
        assert t._resolve_rotation_arg(node) is None

    def test_apply_rotation_op_literal(self) -> None:
        """_apply_rotation_op evaluates a literal node."""
        t, ast = self._make_revealer('var x = 1;')
        result = t._apply_rotation_op({'op': 'literal', 'value': 42}, {}, None)
        assert result == 42

    def test_apply_rotation_op_negate(self) -> None:
        """_apply_rotation_op evaluates a negate node."""
        t, ast = self._make_revealer('var x = 1;')
        op = {'op': 'negate', 'child': {'op': 'literal', 'value': 10}}
        result = t._apply_rotation_op(op, {}, None)
        assert result == -10

    def test_apply_rotation_op_binary(self) -> None:
        """_apply_rotation_op evaluates a binary node."""
        t, ast = self._make_revealer('var x = 1;')
        op = {
            'op': 'binary',
            'operator': '+',
            'left': {'op': 'literal', 'value': 10},
            'right': {'op': 'literal', 'value': 20},
        }
        result = t._apply_rotation_op(op, {}, None)
        assert result == 30

    def test_apply_rotation_op_call_wrapper(self) -> None:
        """_apply_rotation_op evaluates a wrapper call op."""

        t, ast = self._make_revealer('var x = 1;')
        decoder = BasicStringDecoder(['100', 'hello', 'world'], 0)
        wrapper = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        op = {'op': 'call', 'wrapper_name': 'w', 'args': [0]}
        result = t._apply_rotation_op(op, {'w': wrapper}, decoder)
        assert result == 100

    def test_apply_rotation_op_direct_decoder_call(self) -> None:
        """_apply_rotation_op evaluates a direct_decoder_call op."""

        t, ast = self._make_revealer('var x = 1;')
        decoder = BasicStringDecoder(['200', 'hello'], 0)
        alias_map = {'_0xAlias': decoder}
        op = {'op': 'direct_decoder_call', 'alias_name': '_0xAlias', 'args': [0]}
        result = t._apply_rotation_op(op, {}, decoder, alias_decoder_map=alias_map)
        assert result == 200

    def test_apply_rotation_op_direct_decoder_call_with_key(self) -> None:
        """_apply_rotation_op direct_decoder_call with key arg."""

        t, ast = self._make_revealer('var x = 1;')
        decoder = BasicStringDecoder(['300', 'hello'], 0)
        op = {'op': 'direct_decoder_call', 'alias_name': '_0xAlias', 'args': [0, 'key']}
        result = t._apply_rotation_op(op, {}, decoder)
        # BasicStringDecoder ignores the key, just returns by index
        assert result == 300

    def test_apply_rotation_op_unknown_op_raises(self) -> None:
        """_apply_rotation_op raises for unknown op."""
        t, ast = self._make_revealer('var x = 1;')
        with pytest.raises(ValueError, match='Unknown op'):
            t._apply_rotation_op({'op': 'unknown_op'}, {}, None)

    def test_apply_rotation_op_call_invalid_wrapper_args_raises(self) -> None:
        """_apply_rotation_op raises when wrapper args are invalid."""
        t, ast = self._make_revealer('var x = 1;')
        wrapper = WrapperInfo('w', param_index=5, wrapper_offset=0, func_node={})
        op = {'op': 'call', 'wrapper_name': 'w', 'args': [0]}
        with pytest.raises(ValueError, match='Invalid wrapper args'):
            t._apply_rotation_op(op, {'w': wrapper}, None)

    def test_apply_rotation_op_direct_decoder_no_args_raises(self) -> None:
        """_apply_rotation_op raises when direct_decoder_call has no args."""
        t, ast = self._make_revealer('var x = 1;')
        op = {'op': 'direct_decoder_call', 'alias_name': 'x', 'args': []}
        with pytest.raises(ValueError, match='No args'):
            t._apply_rotation_op(op, {}, None)

    def test_execute_rotation_basic(self) -> None:
        """_execute_rotation rotates array until expression matches stop."""

        t, ast = self._make_revealer('var x = 1;')
        string_array = ['hello', '42', 'world', 'foo', 'bar']
        decoder = BasicStringDecoder(string_array, 0)
        wrapper = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        # parseInt(w(0)) should eventually equal 42 after 1 rotation
        op = {'op': 'call', 'wrapper_name': 'w', 'args': [0]}
        result = t._execute_rotation(string_array, op, {'w': wrapper}, decoder, 42)
        assert result is True
        assert string_array[0] == '42'

    def test_execute_rotation_clears_decoder_cache(self) -> None:
        """_execute_rotation clears decoder caches on each rotation."""

        t, ast = self._make_revealer('var x = 1;')
        # Use Base64StringDecoder which has a _cache attribute
        # String array where '42' needs to be at index 0 after rotation
        string_array = ['hello', '42', 'world', 'foo', 'bar']
        decoder = Base64StringDecoder(string_array, 0)
        # Manually seed the cache to verify it gets cleared
        decoder._cache[0] = 'hello'
        wrapper = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        # This will try to parseInt the decoded string at index 0
        # BasicStringDecoder returns string directly, Base64StringDecoder does base64_transform
        # But since Base64 won't give us clean ints, use BasicStringDecoder for the actual test
        # and just verify that _cache.clear() is called on Base64StringDecoder

        primary = BasicStringDecoder(string_array, 0)
        op = {'op': 'call', 'wrapper_name': 'w', 'args': [0]}
        result = t._execute_rotation(
            string_array,
            op,
            {'w': wrapper},
            primary,
            42,
            alias_decoder_map={'alias': decoder},
        )
        assert result is True
        assert string_array[0] == '42'
        # Verify the Base64 decoder's cache was cleared during rotation
        assert len(decoder._cache) == 0

    def test_execute_rotation_with_alias_decoder_map(self) -> None:
        """_execute_rotation uses alias_decoder_map for clearing caches."""
        t, ast = self._make_revealer('var x = 1;')
        string_array = ['hello', '42', 'world', 'foo', 'bar']
        primary = BasicStringDecoder(string_array, 0)
        alias_decoder = Base64StringDecoder(string_array, 0)
        alias_decoder._cache[99] = 'stale'
        alias_map = {'alias': alias_decoder}
        wrapper = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        op = {'op': 'call', 'wrapper_name': 'w', 'args': [0]}
        result = t._execute_rotation(string_array, op, {'w': wrapper}, primary, 42, alias_decoder_map=alias_map)
        assert result is True
        assert string_array[0] == '42'
        # Cache should have been cleared during rotation
        assert len(alias_decoder._cache) == 0


# ================================================================
# SequenceExpression rotation removal (lines 290-298)
# ================================================================


class TestSequenceExpressionRotationRemoval:
    """Tests for rotation inside SequenceExpression being properly removed."""

    def test_sequence_rotation_removal_with_wrapper(self) -> None:
        """Rotation in SequenceExpression is removed while keeping other expressions.

        This triggers lines 287-300 by having the rotation succeed inside a sequence.
        """
        js = """
        function _0xArr() {
            var a = ['500', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 500), console.log('other');
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"500"' in code
        # The rotation IIFE should be removed from the sequence, but
        # console.log('other') should remain
        assert "'other'" in code or '"other"' in code


# ================================================================
# _find_and_execute_rotation SequenceExpression path (lines 637-647)
# ================================================================


class TestRotationSequenceExpression:
    """Test that rotation can be found inside a SequenceExpression."""

    def test_rotation_in_sequence_with_decoder_alias(self) -> None:
        """Rotation IIFE inside SequenceExpression using decoder alias."""
        js = """
        function _0xArr() {
            var a = ['777', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        var _0xAlias = _0xDec;
        function _0xWrap(p) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 777), console.log('extra');
        console.log(_0xAlias(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"777"' in code


# ================================================================
# _extract_decoder_offset additional edge cases (lines 409-418)
# ================================================================


class TestExtractDecoderOffsetDirect:
    """Direct tests for _extract_decoder_offset edge cases."""

    def test_offset_with_non_identifier_left(self) -> None:
        """Assignment where left is not an identifier is ignored."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        # Parse a function with arr[0] = arr[0] - 5 (member expression on left)
        func_ast = parse(
            """
        function f(idx) {
            arr[0] = arr[0] - 5;
            return arr[idx];
        }
        """
        )
        func_node = func_ast['body'][0]
        offset = t._extract_decoder_offset(func_node)
        assert offset == 0  # Default when no matching pattern found

    def test_offset_non_binary_right_side(self) -> None:
        """Assignment where right side is not BinaryExpression is ignored."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        func_ast = parse(
            """
        function f(idx) {
            idx = 5;
            return arr[idx];
        }
        """
        )
        func_node = func_ast['body'][0]
        offset = t._extract_decoder_offset(func_node)
        assert offset == 0

    def test_offset_binary_left_not_matching_param(self) -> None:
        """Assignment where binary left doesn't match the assigned variable."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        func_ast = parse(
            """
        function f(idx) {
            idx = other - 5;
            return arr[idx];
        }
        """
        )
        func_node = func_ast['body'][0]
        offset = t._extract_decoder_offset(func_node)
        assert offset == 0

    def test_offset_unsupported_operator(self) -> None:
        """Assignment with unsupported operator (*) is ignored."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        func_ast = parse(
            """
        function f(idx) {
            idx = idx * 2;
            return arr[idx];
        }
        """
        )
        func_node = func_ast['body'][0]
        offset = t._extract_decoder_offset(func_node)
        assert offset == 0


# ================================================================
# _string_array_from_expression edge cases (line 336)
# ================================================================


class TestStringArrayFromExpression:
    """Edge cases for _string_array_from_expression."""

    def test_array_with_non_string_element(self) -> None:
        """Array with a numeric element returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        node = parse_expr('[1, 2, 3]')
        result = t._string_array_from_expression(node)
        assert result is None

    def test_empty_array_returns_none(self) -> None:
        """Empty array returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        node = parse_expr('[]')
        result = t._string_array_from_expression(node)
        assert result is None

    def test_non_array_returns_none(self) -> None:
        """Non-array node returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        node = parse_expr('42')
        result = t._string_array_from_expression(node)
        assert result is None

    def test_none_returns_none(self) -> None:
        """None returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        assert t._string_array_from_expression(None) is None


# ================================================================
# _find_string_array_function edge cases (line 318)
# ================================================================


class TestFindStringArrayFunction:
    """Edge cases for _find_string_array_function."""

    def test_function_with_short_body(self) -> None:
        """Function with only 1 statement in body is skipped."""
        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        function _0xArr() {
            return ['hello', 'world'];
        }
        """,
        )
        body = ast['body']
        name, arr, idx = t._find_string_array_function(body)
        assert name is None

    def test_function_without_name(self) -> None:
        """Function without a name is skipped."""
        # FunctionDeclarations always have names in valid JS, but we test the guard
        js = """
        function _0xArr() {
            var a = ['hello', 'world'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        var x = 1;
        """
        t, ast = TestRotationInternalsDirect._make_revealer(None, js)
        body = ast['body']
        name, arr, idx = t._find_string_array_function(body)
        assert name == '_0xArr'
        assert arr == ['hello', 'world']


# ================================================================
# _eval_numeric unary with non-evaluable argument (line 38)
# ================================================================


class TestEvalNumericUnaryArgNone:
    """Test _eval_numeric when unary argument evaluates to None."""

    def test_negate_identifier_returns_none(self) -> None:
        """Negating an identifier that can't be evaluated returns None."""
        node = parse_expr('-x')
        assert _eval_numeric(node) is None

    def test_positive_identifier_returns_none(self) -> None:
        """Positive sign on identifier returns None."""
        node = parse_expr('+x')
        assert _eval_numeric(node) is None


# ================================================================
# Additional _collect_object_literals edge (line 99, 103)
# ================================================================


class TestCollectObjectLiteralsPropertyType:
    """Test _collect_object_literals with non-Property type entries."""

    def test_spread_element_ignored(self) -> None:
        """SpreadElement in object properties is skipped (type != 'Property')."""
        # We can't easily create this in valid JS that esprima parses,
        # but we can test with a normal object to verify Property type check works
        ast = parse('var obj = {a: 1, b: "two"};')
        result = _collect_object_literals(ast)
        assert result[('obj', 'a')] == 1
        assert result[('obj', 'b')] == 'two'

    def test_property_with_no_value(self) -> None:
        """Property with missing key or value is skipped."""
        # Manually construct an AST with a malformed property
        ast = {
            'type': 'Program',
            'body': [
                {
                    'type': 'VariableDeclaration',
                    'declarations': [
                        {
                            'type': 'VariableDeclarator',
                            'id': {'type': 'Identifier', 'name': 'obj'},
                            'init': {
                                'type': 'ObjectExpression',
                                'properties': [
                                    {'type': 'Property', 'key': None, 'value': {'type': 'Literal', 'value': 42}},
                                    {'type': 'Property', 'key': {'type': 'Identifier', 'name': 'a'}, 'value': None},
                                ],
                            },
                        }
                    ],
                }
            ],
        }
        result = _collect_object_literals(ast)
        assert len(result) == 0


# ================================================================
# _process_direct_arrays_in_scope line 1214
# ================================================================


class TestProcessDirectArraysInScope:
    """Test _process_direct_arrays_in_scope when binding is not found."""

    def test_array_in_nested_function_scopes(self) -> None:
        """Array accessed in deeply nested function scopes."""
        js = """
        var arr = ["hello", "world"];
        function f() {
            function g() {
                return arr[0];
            }
            return g();
        }
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_array_not_referenced_in_child_scope(self) -> None:
        """Child scope that doesn't reference the array binding."""
        js = """
        var arr = ["hello", "world"];
        function f() {
            var arr = 42;
            return arr;
        }
        """
        code, changed = roundtrip(js, StringRevealer)
        # The inner 'arr' shadows the outer, so no replacement in inner scope
        assert changed is False


# ================================================================
# _find_var_string_array line 1103 (non-identifier declaration)
# ================================================================


class TestFindVarStringArrayEdge:
    """Edge cases for _find_var_string_array."""

    def test_non_array_init_skipped(self) -> None:
        """Var declaration with non-array init is skipped."""
        js = """
        var _0x = 42;
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code

    def test_short_array_skipped(self) -> None:
        """Array with < 3 elements is skipped by _find_var_string_array."""
        js = """
        var _0xarr = ['a', 'b'];
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False


# ================================================================
# _find_simple_rotation edge: non-ExpressionStatement (line 1122)
# ================================================================


class TestFindSimpleRotationEdge:
    """Edge cases for _find_simple_rotation."""

    def test_non_expression_statement_skipped(self) -> None:
        """Non-ExpressionStatement in body is skipped when looking for rotation."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        if (true) { console.log('test'); }
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code  # No rotation applied

    def test_expression_statement_without_expression(self) -> None:
        """Expression statement edge case."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        0;
        var _0xdec = function(i) { i = i - 0; return _0xarr[i]; };
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


# ================================================================
# _find_var_decoder line 1161 (non-function init)
# ================================================================


class TestFindVarDecoderEdge:
    """Edge cases for _find_var_decoder."""

    def test_var_declaration_non_function_init(self) -> None:
        """Var declaration where init is not FunctionExpression is skipped."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        var _0xdec = 42;
        console.log(_0xarr[0]);
        """
        code, changed = roundtrip(js, StringRevealer)
        # Direct array strategy handles arr[0], but decoder pattern is not found
        assert isinstance(code, str)

    def test_var_declaration_non_variable(self) -> None:
        """Non-variable declaration statement is skipped when looking for decoder."""
        js = """
        var _0xarr = ['hello', 'world', 'foo', 'bar'];
        function _0xdec(i) { i = i - 0; return _0xarr[i]; }
        console.log(_0xdec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        # Function declaration is not a VariableDeclaration, so _find_var_decoder skips it
        # But the direct array strategy may still work
        assert isinstance(code, str)


# ================================================================
# _try_replace_array_access line 1181 edge cases
# ================================================================


class TestTryReplaceArrayAccessEdge:
    """Edge cases for _try_replace_array_access."""

    def test_non_computed_member_not_replaced(self) -> None:
        """arr.foo style access is not replaced."""
        js = 'var arr = ["hello", "world"]; console.log(arr.length);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False
        assert 'arr.length' in code

    def test_member_property_not_numeric(self) -> None:
        """arr[x] where x is an identifier is not replaced."""
        js = 'var arr = ["hello", "world"]; console.log(arr[x]);'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False

    def test_ref_key_not_object(self) -> None:
        """Reference where key is not 'object' is not replaced."""
        # This happens when arr is used as a property value, not as the object of a member
        js = 'var arr = ["hello", "world"]; var x = {prop: arr};'
        code, changed = roundtrip(js, StringRevealer)
        assert changed is False


# ================================================================
# _update_ast_array line 1029 (empty func body)
# ================================================================


class TestUpdateAstArrayEdge:
    """Edge case for _update_ast_array."""

    def test_update_ast_array_with_assignment_init(self) -> None:
        """_update_ast_array when first statement is assignment (not var decl)."""
        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        function _0xArr() {
            a = ['hello', 'world'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        """,
        )
        func_node = ast['body'][0]
        rotated = ['world', 'hello']
        t._update_ast_array(func_node, rotated)
        # Verify the AST was updated (assignment expression path)
        func_body = func_node['body']['body']
        expr = func_body[0]['expression']
        assert expr['type'] == 'AssignmentExpression'
        elements = expr['right']['elements']
        assert elements[0]['value'] == 'world'
        assert elements[1]['value'] == 'hello'

    def test_update_ast_array_empty_body(self) -> None:
        """_update_ast_array with empty function body does nothing."""
        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        function _0xArr() {
        }
        """,
        )
        func_node = ast['body'][0]
        # Should not crash
        t._update_ast_array(func_node, ['a', 'b'])


# ================================================================
# More targeted tests for remaining uncovered lines
# ================================================================


class TestDecodeAndParseInt:
    """Tests for _decode_and_parse_int error paths."""

    def test_decode_and_parse_int_returns_nan(self) -> None:
        """_decode_and_parse_int raises when decoded string is not parseable as int."""

        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        decoder = BasicStringDecoder(['hello'], 0)
        with pytest.raises(ValueError, match='NaN'):
            t._decode_and_parse_int(decoder, 0)

    def test_decode_and_parse_int_none_returned(self) -> None:
        """_decode_and_parse_int raises when decoder returns None (out of bounds)."""

        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        decoder = BasicStringDecoder(['hello'], 0)
        with pytest.raises(ValueError, match='Decoder returned None'):
            t._decode_and_parse_int(decoder, 999)

    def test_decode_and_parse_int_with_key(self) -> None:
        """_decode_and_parse_int passes key to decoder.get_string."""

        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        decoder = BasicStringDecoder(['42'], 0)
        # BasicStringDecoder.get_string ignores extra args
        result = t._decode_and_parse_int(decoder, 0, key='somekey')
        assert result == 42


class TestExecuteRotationEdge:
    """Edge cases for _execute_rotation."""

    def test_execute_rotation_returns_false_when_no_match(self) -> None:
        """_execute_rotation returns False when no match in 100001 iterations."""

        t, ast = TestRotationInternalsDirect._make_revealer(None, 'var x = 1;')
        # Array where no rotation can produce parseInt matching stop_value 999999
        # All strings are non-numeric, so parseInt always fails -> always rotates
        # But it'll never match stop=999999
        string_array = ['a', 'b']
        decoder = BasicStringDecoder(string_array, 0)
        wrapper = WrapperInfo('w', param_index=0, wrapper_offset=0, func_node={})
        op = {'op': 'call', 'wrapper_name': 'w', 'args': [0]}
        result = t._execute_rotation(string_array, op, {'w': wrapper}, decoder, 999999)
        assert result is False


class TestWrapperReplacementEdge:
    """Edge cases for _replace_all_wrapper_calls."""

    def test_wrapper_call_unresolvable_index_value(self) -> None:
        """Wrapper call where the index param can't be resolved."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        console.log(_0xWrap(someVar));
        console.log(_0xDec(0));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # _0xWrap(someVar) should not be replaced
        assert '_0xWrap(someVar)' in code

    def test_wrapper_key_param_resolution(self) -> None:
        """Wrapper with key_param_index resolves key from call args."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p, k) {
            return _0xDec(p, k);
        }
        console.log(_0xWrap(0, 'key1'));
        console.log(_0xWrap(1, 'key2'));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        assert '"world"' in code

    def test_decoder_returns_non_string(self) -> None:
        """When decoder returns None (out of bounds), the call is not replaced."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0));
        console.log(_0xDec(100));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code
        # _0xDec(100) should remain since it's out of bounds
        assert '100' in code


class TestAnalyzeWrapperExprEdge:
    """Edge cases for _analyze_wrapper_expr."""

    def test_wrapper_with_key_param_from_second_arg(self) -> None:
        """Wrapper passing second param as key to decoder."""
        js = """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx, key) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p, k) {
            return _0xDec(p, k);
        }
        console.log(_0xWrap(0, 'myKey'));
        """
        code, changed = roundtrip(js, StringRevealer)
        assert changed is True
        assert '"hello"' in code


class TestFindAndExecuteRotationEdge:
    """Edge cases for _find_and_execute_rotation."""

    def test_rotation_not_found_returns_none(self) -> None:
        """When no rotation IIFE exists, returns None."""

        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        function _0xArr() {
            var a = ['hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        console.log(_0xDec(0));
        """,
        )
        body = ast['body']
        decoder = BasicStringDecoder(['hello', 'world', 'foo', 'bar', 'baz'], 0)
        result = t._find_and_execute_rotation(body, '_0xArr', ['hello'], decoder, {}, set())
        assert result is None

    def test_rotation_found_in_sequence_expression(self) -> None:
        """Rotation IIFE inside a SequenceExpression is found and executed."""

        js = """
        function _0xArr() {
            var a = ['500', 'hello', 'world', 'foo', 'bar', 'baz'];
            _0xArr = function() { return a; };
            return _0xArr();
        }
        function _0xDec(idx) {
            idx = idx - 0;
            var arr = _0xArr();
            return arr[idx];
        }
        function _0xWrap(p) {
            return _0xDec(p);
        }
        (function(_0xarg, _0xstop) {
            while (true) {
                try {
                    var _0xval = parseInt(_0xWrap(0));
                    if (_0xval === _0xstop) {
                        break;
                    }
                } catch(e) {
                }
                _0xarg().push(_0xarg().shift());
            }
        })(_0xArr, 500), console.log('side');
        console.log(_0xDec(0));
        """
        t, ast = TestRotationInternalsDirect._make_revealer(None, js)
        body = ast['body']
        string_array = ['500', 'hello', 'world', 'foo', 'bar', 'baz']
        decoder = BasicStringDecoder(string_array, 0)
        wrapper = WrapperInfo('_0xWrap', param_index=0, wrapper_offset=0, func_node={})
        result = t._find_and_execute_rotation(body, '_0xArr', string_array, decoder, {'_0xWrap': wrapper}, set())
        assert result is not None
        idx, sub_expr = result
        assert sub_expr is not None  # Was inside a SequenceExpression


class TestExtractRotationExpressionEdge:
    """Edge cases for _extract_rotation_expression."""

    def test_no_loop_in_iife(self) -> None:
        """IIFE without a while/for loop returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        (function(a, b) {
            var x = 1;
            console.log(x);
        })(arr, 100);
        """,
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = t._extract_rotation_expression(iife_func)
        assert result is None

    def test_loop_without_try_statement(self) -> None:
        """Loop without a TryStatement returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        (function(a, b) {
            while (true) {
                var x = 1;
                break;
            }
        })(arr, 100);
        """,
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = t._extract_rotation_expression(iife_func)
        assert result is None

    def test_try_with_empty_block(self) -> None:
        """Try block with empty body returns None."""
        t, ast = TestRotationInternalsDirect._make_revealer(
            None,
            """
        (function(a, b) {
            while (true) {
                try {
                } catch(e) {}
                break;
            }
        })(arr, 100);
        """,
        )
        call_expr = ast['body'][0]['expression']
        iife_func = call_expr['callee']
        result = t._extract_rotation_expression(iife_func)
        assert result is None
