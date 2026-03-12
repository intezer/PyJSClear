"""Tests for the ElseIfFlattener transform."""

from pyjsclear.transforms.else_if_flatten import ElseIfFlattener
from tests.unit.conftest import normalize
from tests.unit.conftest import roundtrip


class TestBasicFlatten:
    """Tests for else { if } → else if conversion."""

    def test_simple_else_if(self):
        code, changed = roundtrip(
            'if (a) { x(); } else { if (b) { y(); } }',
            ElseIfFlattener,
        )
        assert changed is True
        assert 'else if (b)' in code

    def test_else_if_with_else(self):
        code, changed = roundtrip(
            'if (a) { x(); } else { if (b) { y(); } else { z(); } }',
            ElseIfFlattener,
        )
        assert changed is True
        assert 'else if (b)' in code
        assert 'else {' in code  # inner else preserved

    def test_deeply_nested_flattens(self):
        code, changed = roundtrip(
            'if (a) { x(); } else { if (b) { y(); } else { if (c) { z(); } } }',
            ElseIfFlattener,
        )
        assert changed is True
        assert 'else if (b)' in code
        assert 'else if (c)' in code


class TestNoFlatten:
    """Tests where flattening should NOT occur."""

    def test_no_else(self):
        code, changed = roundtrip('if (a) { x(); }', ElseIfFlattener)
        assert changed is False

    def test_else_is_not_block(self):
        """Direct else-if (no wrapping block) — already flat."""
        code, changed = roundtrip(
            'if (a) { x(); } else if (b) { y(); }',
            ElseIfFlattener,
        )
        assert changed is False

    def test_else_block_has_multiple_statements(self):
        """Block with multiple statements should not be flattened."""
        code, changed = roundtrip(
            'if (a) { x(); } else { foo(); if (b) { y(); } }',
            ElseIfFlattener,
        )
        assert changed is False

    def test_else_block_has_non_if_single_statement(self):
        code, changed = roundtrip(
            'if (a) { x(); } else { foo(); }',
            ElseIfFlattener,
        )
        assert changed is False
