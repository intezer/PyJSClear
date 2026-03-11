"""Tests for the DeadExpressionRemover transform."""

from pyjsclear.transforms.dead_expressions import DeadExpressionRemover
from tests.unit.conftest import roundtrip


class TestRemoveNumericLiterals:
    """Tests for removing standalone numeric literal statements."""

    def test_removes_zero(self):
        code, changed = roundtrip('0;', DeadExpressionRemover)
        assert changed is True
        assert code.strip() == ''

    def test_removes_integer(self):
        code, changed = roundtrip('42;', DeadExpressionRemover)
        assert changed is True

    def test_removes_float(self):
        code, changed = roundtrip('3.14;', DeadExpressionRemover)
        assert changed is True

    def test_removes_negative_via_unary(self):
        """UnaryExpression -1 is NOT a Literal, so it should be kept."""
        code, changed = roundtrip('-1;', DeadExpressionRemover)
        assert changed is False
        assert '-1' in code


class TestPreservesNonNumeric:
    """Tests for keeping non-numeric expression statements."""

    def test_preserves_string_literal(self):
        code, changed = roundtrip('"use strict";', DeadExpressionRemover)
        assert changed is False
        assert 'use strict' in code

    def test_preserves_boolean_true(self):
        code, changed = roundtrip('true;', DeadExpressionRemover)
        assert changed is False
        assert 'true' in code

    def test_preserves_boolean_false(self):
        code, changed = roundtrip('false;', DeadExpressionRemover)
        assert changed is False
        assert 'false' in code

    def test_preserves_null(self):
        code, changed = roundtrip('null;', DeadExpressionRemover)
        assert changed is False

    def test_preserves_function_call(self):
        code, changed = roundtrip('foo();', DeadExpressionRemover)
        assert changed is False
        assert 'foo()' in code

    def test_preserves_assignment(self):
        code, changed = roundtrip('x = 1;', DeadExpressionRemover)
        assert changed is False


class TestMixedStatements:
    """Tests with mixed statement types."""

    def test_removes_only_numeric_from_block(self):
        code, changed = roundtrip('0; foo(); 1;', DeadExpressionRemover)
        assert changed is True
        assert 'foo()' in code
        assert '0' not in code.replace('foo()', '')

    def test_no_change_when_no_numeric_statements(self):
        code, changed = roundtrip('var x = 1; foo(); "str";', DeadExpressionRemover)
        assert changed is False
