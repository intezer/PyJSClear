"""Tests for the OptionalChaining transform."""

from pyjsclear.generator import generate
from pyjsclear.parser import parse
from pyjsclear.transforms.optional_chaining import OptionalChaining
from pyjsclear.transforms.optional_chaining import _nodes_match
from pyjsclear.utils.ast_helpers import is_null_literal
from pyjsclear.utils.ast_helpers import is_undefined
from tests.unit.conftest import roundtrip


class TestSimplePattern:
    """Tests for X === null || X === undefined ? undefined : X.prop → X?.prop."""

    def test_basic_member_access(self) -> None:
        code, changed = roundtrip(
            'var y = x === null || x === undefined ? undefined : x.foo;',
            OptionalChaining,
        )
        assert changed is True
        assert 'x?.foo' in code

    def test_computed_member_access(self) -> None:
        code, changed = roundtrip(
            'var y = x === null || x === undefined ? undefined : x["foo"];',
            OptionalChaining,
        )
        assert changed is True
        assert '?.["foo"]' in code

    def test_reversed_null_undefined(self) -> None:
        code, changed = roundtrip(
            'var y = x === undefined || x === null ? undefined : x.foo;',
            OptionalChaining,
        )
        assert changed is True
        assert 'x?.foo' in code

    def test_void_0_as_undefined(self) -> None:
        code, changed = roundtrip(
            'var y = x === null || x === void 0 ? void 0 : x.foo;',
            OptionalChaining,
        )
        assert changed is True
        assert 'x?.foo' in code


class TestTempAssignmentPattern:
    """Tests for (_tmp = expr) === null || _tmp === undefined ? undefined : _tmp.prop."""

    def test_temp_var_member(self) -> None:
        code, changed = roundtrip(
            'var y = (_tmp = obj.prop) === null || _tmp === undefined ? undefined : _tmp.nested;',
            OptionalChaining,
        )
        assert changed is True
        assert 'obj.prop?.nested' in code

    def test_temp_var_eliminates_temp(self) -> None:
        """The temp variable should not appear in the output."""
        code, changed = roundtrip(
            'var y = (_tmp = obj.a) === null || _tmp === undefined ? undefined : _tmp.b;',
            OptionalChaining,
        )
        assert changed is True
        assert '_tmp' not in code


class TestNoTransform:
    """Cases that should NOT trigger the transform."""

    def test_consequent_not_undefined(self) -> None:
        code, changed = roundtrip(
            'var y = x === null || x === undefined ? 0 : x.foo;',
            OptionalChaining,
        )
        assert changed is False

    def test_different_variables_in_checks(self) -> None:
        code, changed = roundtrip(
            'var y = x === null || z === undefined ? undefined : x.foo;',
            OptionalChaining,
        )
        assert changed is False

    def test_alternate_is_plain_identifier(self) -> None:
        """x?.  would require the alternate to be a member/call, not just x."""
        code, changed = roundtrip(
            'var y = x === null || x === undefined ? undefined : x;',
            OptionalChaining,
        )
        assert changed is False

    def test_and_operator_not_or(self) -> None:
        """&& instead of || should not match (that's the nullish coalescing pattern)."""
        code, changed = roundtrip(
            'var y = x === null && x === undefined ? undefined : x.foo;',
            OptionalChaining,
        )
        assert changed is False

    def test_not_equality_check(self) -> None:
        """!== instead of === should not match."""
        code, changed = roundtrip(
            'var y = x !== null || x !== undefined ? undefined : x.foo;',
            OptionalChaining,
        )
        assert changed is False


class TestOptionalCall:
    """Tests for X === null || X === undefined ? undefined : X() → X?.()."""

    def test_optional_call(self) -> None:
        code, changed = roundtrip(
            'var y = fn === null || fn === undefined ? undefined : fn();',
            OptionalChaining,
        )
        assert changed is True
        assert 'fn?.()' in code

    def test_optional_call_with_args(self) -> None:
        code, changed = roundtrip(
            'var y = fn === null || fn === undefined ? undefined : fn(1, 2);',
            OptionalChaining,
        )
        assert changed is True
        assert '?.' in code


class TestYodaStyle:
    """Tests for null/undefined on the left side of comparison."""

    def test_null_on_left(self) -> None:
        """null === x || undefined === x ? undefined : x.foo → x?.foo."""
        code, changed = roundtrip(
            'var y = null === x || undefined === x ? undefined : x.foo;',
            OptionalChaining,
        )
        assert changed is True
        assert 'x?.foo' in code

    def test_void_0_on_consequent(self) -> None:
        """void 0 as consequent should be recognized as undefined."""
        code, changed = roundtrip(
            'var y = x === null || x === void 0 ? void 0 : x.foo;',
            OptionalChaining,
        )
        assert changed is True


class TestHelperFunctions:
    """Direct tests for helper functions to cover edge cases."""

    def test_is_undefined_with_non_dict(self) -> None:
        assert is_undefined(None) is False
        assert is_undefined('string') is False

    def test_is_undefined_with_void_0(self) -> None:
        node = {
            'type': 'UnaryExpression',
            'operator': 'void',
            'argument': {'type': 'Literal', 'value': 0},
        }
        assert is_undefined(node) is True

    def test_is_undefined_with_void_non_zero(self) -> None:
        node = {
            'type': 'UnaryExpression',
            'operator': 'void',
            'argument': {'type': 'Literal', 'value': 1},
        }
        assert is_undefined(node) is False

    def test_is_null_literal_true(self) -> None:
        assert is_null_literal({'type': 'Literal', 'value': None, 'raw': 'null'}) is True

    def test_is_null_literal_false(self) -> None:
        assert is_null_literal({'type': 'Literal', 'value': 0}) is False
        assert is_null_literal(None) is False

    def test_nodes_match_non_dict(self) -> None:
        assert _nodes_match(None, None) is False
        assert _nodes_match({}, None) is False

    def test_nodes_match_different_types(self) -> None:
        a = {'type': 'Identifier', 'name': 'x'}
        b = {'type': 'Literal', 'value': 1}
        assert _nodes_match(a, b) is False

    def test_nodes_match_member_expression(self) -> None:
        a = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'prop'},
            'computed': False,
        }
        b = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'prop'},
            'computed': False,
        }
        assert _nodes_match(a, b) is True

    def test_nodes_match_unknown_type_returns_false(self) -> None:
        a = {'type': 'CallExpression'}
        b = {'type': 'CallExpression'}
        assert _nodes_match(a, b) is False


class TestGeneratorOutput:
    """Tests that ?. roundtrips through parse → generate correctly."""

    def test_optional_member_roundtrip(self) -> None:
        code = 'var x = a?.b;'
        result = generate(parse(code))
        assert 'a?.b' in result

    def test_optional_computed_roundtrip(self) -> None:
        code = 'var x = a?.[0];'
        result = generate(parse(code))
        assert 'a?.[0]' in result

    def test_optional_call_roundtrip(self) -> None:
        code = 'var x = fn?.();'
        result = generate(parse(code))
        assert 'fn?.()' in result

    def test_chained_optional(self) -> None:
        code = 'var x = a?.b?.c;'
        result = generate(parse(code))
        assert 'a?.b?.c' in result
