"""Tests for the NullishCoalescing transform."""

from pyjsclear.transforms.nullish_coalescing import NullishCoalescing
from tests.unit.conftest import roundtrip


class TestSimplePattern:
    """Tests for X !== null && X !== undefined ? X : default → X ?? default."""

    def test_basic_pattern(self):
        code, changed = roundtrip(
            'var y = x !== null && x !== undefined ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is True
        assert '??' in code
        assert 'x ?? fallback' in code

    def test_reversed_order(self):
        code, changed = roundtrip(
            'var y = x !== undefined && x !== null ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is True
        assert 'x ?? fallback' in code


class TestTempAssignmentPattern:
    """Tests for (_tmp = value) !== null && _tmp !== undefined ? _tmp : default."""

    def test_temp_var_pattern(self):
        code, changed = roundtrip(
            'var y = (_tmp = getValue()) !== null && _tmp !== undefined ? _tmp : fallback;',
            NullishCoalescing,
        )
        assert changed is True
        assert '??' in code
        assert 'getValue() ?? fallback' in code

    def test_temp_var_with_member_access(self):
        code, changed = roundtrip(
            'var y = (_tmp = obj.prop) !== null && _tmp !== undefined ? _tmp : fallback;',
            NullishCoalescing,
        )
        assert changed is True
        assert 'obj.prop ?? fallback' in code


class TestNoTransform:
    """Cases that should NOT trigger the transform."""

    def test_not_strict_inequality(self):
        """!= instead of !== should not match."""
        code, changed = roundtrip(
            'var y = x != null && x != undefined ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is False

    def test_or_instead_of_and(self):
        """|| instead of && should not match."""
        code, changed = roundtrip(
            'var y = x !== null || x !== undefined ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is False

    def test_different_variables(self):
        code, changed = roundtrip(
            'var y = x !== null && z !== undefined ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is False

    def test_consequent_not_matching_checked_var(self):
        code, changed = roundtrip(
            'var y = x !== null && x !== undefined ? other : fallback;',
            NullishCoalescing,
        )
        assert changed is False

    def test_checking_against_zero_not_null(self):
        code, changed = roundtrip(
            'var y = x !== 0 && x !== undefined ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is False

    def test_non_binary_left(self):
        """Left of && is not a BinaryExpression."""
        code, changed = roundtrip(
            'var y = foo() && x !== undefined ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is False

    def test_non_binary_right(self):
        """Right of && is not a BinaryExpression."""
        code, changed = roundtrip(
            'var y = x !== null && foo() ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is False


class TestYodaStyle:
    """Tests with null/undefined on the left side of comparison."""

    def test_null_on_left_undefined_on_left(self):
        """null !== X && undefined !== X ? X : fallback."""
        code, changed = roundtrip(
            'var y = null !== x && undefined !== x ? x : fallback;',
            NullishCoalescing,
        )
        assert changed is True
        assert 'x ?? fallback' in code
