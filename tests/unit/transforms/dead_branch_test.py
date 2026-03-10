"""Unit tests for DeadBranchRemover transform and _is_truthy_literal helper."""

import pytest

from pyjsclear.transforms.dead_branch import DeadBranchRemover
from pyjsclear.transforms.dead_branch import _is_truthy_literal
from tests.unit.conftest import normalize
from tests.unit.conftest import parse_expr
from tests.unit.conftest import roundtrip


# ---------------------------------------------------------------------------
# _is_truthy_literal helper tests
# ---------------------------------------------------------------------------


class TestIsTruthyLiteral:
    def test_null_is_falsy(self):
        node = {'type': 'Literal', 'value': None}
        assert _is_truthy_literal(node) is False

    def test_true_is_truthy(self):
        node = {'type': 'Literal', 'value': True}
        assert _is_truthy_literal(node) is True

    def test_false_is_falsy(self):
        node = {'type': 'Literal', 'value': False}
        assert _is_truthy_literal(node) is False

    def test_nonzero_number_is_truthy(self):
        node = {'type': 'Literal', 'value': 1}
        assert _is_truthy_literal(node) is True

    def test_zero_is_falsy(self):
        node = {'type': 'Literal', 'value': 0}
        assert _is_truthy_literal(node) is False

    def test_nonempty_string_is_truthy(self):
        node = {'type': 'Literal', 'value': 'a'}
        assert _is_truthy_literal(node) is True

    def test_empty_string_is_falsy(self):
        node = {'type': 'Literal', 'value': ''}
        assert _is_truthy_literal(node) is False

    def test_not_false_is_truthy(self):
        node = {
            'type': 'UnaryExpression',
            'operator': '!',
            'argument': {'type': 'Literal', 'value': False},
        }
        assert _is_truthy_literal(node) is True

    def test_not_true_is_falsy(self):
        node = {
            'type': 'UnaryExpression',
            'operator': '!',
            'argument': {'type': 'Literal', 'value': True},
        }
        assert _is_truthy_literal(node) is False

    def test_not_zero_is_truthy(self):
        node = {
            'type': 'UnaryExpression',
            'operator': '!',
            'argument': {'type': 'Literal', 'value': 0},
        }
        assert _is_truthy_literal(node) is True

    def test_empty_array_is_truthy(self):
        node = {'type': 'ArrayExpression', 'elements': []}
        assert _is_truthy_literal(node) is True

    def test_empty_object_is_truthy(self):
        node = {'type': 'ObjectExpression', 'properties': []}
        assert _is_truthy_literal(node) is True

    def test_non_empty_array_is_unknown(self):
        node = {'type': 'ArrayExpression', 'elements': [{'type': 'Literal', 'value': 1}]}
        assert _is_truthy_literal(node) is None

    def test_identifier_is_unknown(self):
        node = {'type': 'Identifier', 'name': 'x'}
        assert _is_truthy_literal(node) is None

    def test_non_dict_returns_none(self):
        assert _is_truthy_literal(None) is None
        assert _is_truthy_literal(42) is None

    def test_unary_non_bang_is_unknown(self):
        node = {
            'type': 'UnaryExpression',
            'operator': '-',
            'argument': {'type': 'Literal', 'value': 1},
        }
        assert _is_truthy_literal(node) is None


# ---------------------------------------------------------------------------
# DeadBranchRemover transform roundtrip tests
# ---------------------------------------------------------------------------


class TestDeadBranchRemover:
    def test_if_true_keeps_consequent(self):
        code, changed = roundtrip('if (true) { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' in normalize(code)
        assert 'if' not in normalize(code)

    def test_if_false_with_alternate_keeps_alternate(self):
        code, changed = roundtrip('if (false) { x(); } else { y(); }', DeadBranchRemover)
        assert changed is True
        assert 'y()' in normalize(code)
        assert 'x()' not in normalize(code)
        assert 'if' not in normalize(code)

    def test_if_false_no_alternate_removed(self):
        code, changed = roundtrip('if (false) { x(); }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'x()' not in normalized
        assert 'if' not in normalized

    def test_if_zero_is_falsy(self):
        code, changed = roundtrip('if (0) { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' not in normalize(code)

    def test_if_empty_string_is_falsy(self):
        code, changed = roundtrip('if ("") { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' not in normalize(code)

    def test_if_one_is_truthy(self):
        code, changed = roundtrip('if (1) { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' in normalize(code)
        assert 'if' not in normalize(code)

    def test_if_nonempty_string_is_truthy(self):
        code, changed = roundtrip('if ("a") { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' in normalize(code)
        assert 'if' not in normalize(code)

    def test_if_not_false_is_truthy(self):
        code, changed = roundtrip('if (!false) { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' in normalize(code)
        assert 'if' not in normalize(code)

    def test_ternary_true_keeps_consequent(self):
        code, changed = roundtrip('true ? a : b;', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'a' in normalized
        assert 'b' not in normalized

    def test_nested_not_zero_is_truthy(self):
        code, changed = roundtrip('if (!0) { x(); }', DeadBranchRemover)
        assert changed is True
        assert 'x()' in normalize(code)
        assert 'if' not in normalize(code)

    def test_non_literal_test_unchanged(self):
        code, changed = roundtrip('if (x) { y(); }', DeadBranchRemover)
        assert changed is False
        normalized = normalize(code)
        assert 'if' in normalized
        assert 'y()' in normalized


# ---------------------------------------------------------------------------
# Coverage gap tests
# ---------------------------------------------------------------------------


class TestEmptyArrayObjectTruthy:
    """Lines 24-25: Empty array [] and empty object {} are truthy."""

    def test_if_empty_array_truthy(self):
        code, changed = roundtrip('if ([]) { a(); }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'a()' in normalized
        assert 'if' not in normalized

    def test_if_empty_object_truthy(self):
        code, changed = roundtrip('if ({}) { a(); }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'a()' in normalized
        assert 'if' not in normalized


class TestUnwrapBlock:
    """Lines 39-43: _unwrap_block with single-statement block."""

    def test_if_true_single_statement_block_unwrapped(self):
        """if (true) { return x; } → return x;"""
        code, changed = roundtrip('function f() { if (true) { return x; } }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'return x;' in normalized
        assert 'if' not in normalized


class TestIfFalseRemoved:
    """Line 61: if (false) { a(); } with no else → REMOVE."""

    def test_if_null_no_else_removed(self):
        code, changed = roundtrip('if (null) { a(); }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'a()' not in normalized


class TestTernaryFalsy:
    """Ternary with falsy test keeps alternate."""

    def test_ternary_false(self):
        code, changed = roundtrip('false ? a : b;', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'b' in normalized
        assert 'a' not in normalized

    def test_ternary_zero(self):
        code, changed = roundtrip('0 ? a : b;', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'b' in normalized


class TestLiteralDefaultTruthy:
    """Lines 24-25: Literal with value that is not None/bool/int/float/str → True."""

    def test_regex_literal_truthy(self):
        # A Literal with a regex value (dict) hits the default case → True
        node = {'type': 'Literal', 'value': {'pattern': '.*', 'flags': ''}, 'regex': {'pattern': '.*', 'flags': ''}}
        result = _is_truthy_literal(node)
        assert result is True


class TestUnwrapBlockIntegration:
    """Lines 39-43: _unwrap_block is called when replacing if(true) with consequent."""

    def test_if_true_multi_statement_block_kept_as_block(self):
        """Multi-statement block is NOT unwrapped (len > 1)."""
        code, changed = roundtrip('function f() { if (true) { a(); b(); } }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'a()' in normalized
        assert 'b()' in normalized
        assert 'if' not in normalized


class TestConditionalExpressionUnknownTest:
    """Line 66: ConditionalExpression with non-literal test returns None (no change)."""

    def test_ternary_with_variable_test_unchanged(self):
        code, changed = roundtrip('var z = x ? a : b;', DeadBranchRemover)
        assert changed is False
        normalized = normalize(code)
        assert '?' in normalized


class TestIfFalseNoElseREMOVE:
    """Line 61: if(false) with no else triggers REMOVE sentinel."""

    def test_if_null_with_else(self):
        """if(null) with else → keeps else branch."""
        code, changed = roundtrip('if (null) { a(); } else { b(); }', DeadBranchRemover)
        assert changed is True
        normalized = normalize(code)
        assert 'a()' not in normalized
        assert 'b()' in normalized
