import pytest

from pyjsclear.transforms.object_packer import ObjectPacker
from tests.unit.conftest import normalize, roundtrip


class TestBasicPacking:
    """Tests for consolidating sequential assignments into object literals."""

    def test_basic_packing(self):
        code, changed = roundtrip('var o = {}; o.x = 1; o.y = "hello";', ObjectPacker)
        assert changed is True
        result = normalize(code)
        # Keys may be quoted ('x') or unquoted (x) depending on generator
        assert '1' in result
        assert '"hello"' in result
        # The separate assignment statements should be gone
        assert 'o.x =' not in result
        assert 'o.y =' not in result

    def test_empty_object_no_assignments(self):
        code, changed = roundtrip('var o = {};', ObjectPacker)
        assert changed is False
        assert 'var o = {}' in normalize(code)

    def test_stop_at_self_reference(self):
        code, changed = roundtrip('var o = {}; o.x = 1; o.y = o.x;', ObjectPacker)
        assert changed is True
        result = normalize(code)
        # x should be packed into the literal (key may be quoted)
        assert ': 1' in result
        # y = o.x is self-referential, so it remains as a separate statement
        assert 'o.y = o.x' in result

    def test_stop_at_non_assignment(self):
        code, changed = roundtrip('var o = {}; o.x = 1; foo(); o.y = 2;', ObjectPacker)
        assert changed is True
        result = normalize(code)
        # x should be packed (key may be quoted)
        assert ': 1' in result
        # foo() interrupts packing, so y remains separate
        assert 'o.y = 2' in result
        assert 'foo()' in result

    def test_computed_property(self):
        code, changed = roundtrip('var o = {}; o["x"] = 1;', ObjectPacker)
        assert changed is True
        result = normalize(code)
        # The assignment statement should be removed (packed into literal)
        assert 'o["x"] = 1' not in result
        assert 'o.x = 1' not in result


class TestNoPacking:
    """Tests for cases where packing should not occur."""

    def test_non_empty_initial_object(self):
        code, changed = roundtrip('var o = { a: 1 }; o.x = 2;', ObjectPacker)
        assert changed is False
        result = normalize(code)
        assert 'o.x = 2' in result

    def test_no_packable_patterns(self):
        code, changed = roundtrip('var x = 1; var y = 2;', ObjectPacker)
        assert changed is False

    def test_no_packable_patterns_non_object(self):
        code, changed = roundtrip('var o = 5; o.x = 1;', ObjectPacker)
        assert changed is False


class TestNestedBodies:
    """Tests for recursive processing of nested bodies."""

    def test_nested_function_body(self):
        code, changed = roundtrip('function f() { var o = {}; o.x = 1; o.y = 2; }', ObjectPacker)
        assert changed is True
        result = normalize(code)
        # Both properties should be packed; assignments should be gone
        assert 'o.x =' not in result
        assert 'o.y =' not in result
        # The packed object should contain both values
        assert ': 1' in result
        assert ': 2' in result
