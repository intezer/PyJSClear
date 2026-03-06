"""Unit tests for DeadBranchRemover transform and _is_truthy_literal helper."""

import pytest

from pyjsclear.transforms.dead_branch import DeadBranchRemover, _is_truthy_literal
from tests.unit.conftest import normalize, parse_expr, roundtrip


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
