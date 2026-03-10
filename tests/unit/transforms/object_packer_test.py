import pytest

from pyjsclear.transforms.object_packer import ObjectPacker
from tests.unit.conftest import normalize
from tests.unit.conftest import roundtrip


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


class TestCoverageGaps:
    """Tests targeting uncovered lines in object_packer.py."""

    def test_non_dict_node_in_process_bodies(self):
        """Line 22: Non-dict node passed to _process_bodies (skipped)."""
        # Simple code with literals; _process_bodies will encounter non-dict values
        code, changed = roundtrip('var x = 1;', ObjectPacker)
        assert changed is False

    def test_non_dict_statement_in_body(self):
        """Lines 57-58: Non-dict statement in body array is skipped."""
        # Normal parsing won't produce non-dict statements, but this tests
        # that the code doesn't crash on simple cases.
        code, changed = roundtrip('var o = {}; o.x = 1;', ObjectPacker)
        assert changed is True

    def test_compound_assignment_stops_packing(self):
        """Line 73: Assignment expression without '=' operator (e.g., +=) stops packing."""
        code, changed = roundtrip('var o = {}; o.x = 1; o.y += 2;', ObjectPacker)
        assert changed is True
        result = normalize(code)
        assert ': 1' in result
        assert 'o.y += 2' in result

    def test_left_not_member_expression(self):
        """Line 79: Left side of assignment is not MemberExpression."""
        code, changed = roundtrip('var o = {}; o.x = 1; z = 2;', ObjectPacker)
        assert changed is True
        result = normalize(code)
        assert ': 1' in result
        assert 'z = 2' in result

    def test_object_name_mismatch(self):
        """Line 82: Object reference name doesn't match the target object."""
        code, changed = roundtrip('var o = {}; o.x = 1; p.y = 2;', ObjectPacker)
        assert changed is True
        result = normalize(code)
        assert ': 1' in result
        assert 'p.y = 2' in result

    def test_property_node_is_none(self):
        """Line 87: Property node is None stops packing."""
        from pyjsclear.generator import generate
        from pyjsclear.parser import parse

        ast = parse('var o = {}; o.x = 1;')
        # Manually set the property of the MemberExpression to None
        body = ast['body']
        assignment_stmt = body[1]
        left = assignment_stmt['expression']['left']
        left['property'] = None
        t = ObjectPacker(ast)
        changed = t.execute()
        # Should not pack because property is None
        assert changed is False

    def test_references_name_list_child(self):
        """Lines 129-130: _references_name finds reference in list child (e.g. array)."""
        code, changed = roundtrip('var o = {}; o.x = 1; o.y = [o];', ObjectPacker)
        assert changed is True
        result = normalize(code)
        assert ': 1' in result
        assert 'o.y = [o]' in result

    def test_references_name_no_type(self):
        """Line 120: _references_name with node missing 'type' returns False."""
        packer = ObjectPacker({'type': 'Program', 'body': []})
        # A dict without 'type' should return False
        assert packer._references_name({}, 'o') is False
        assert packer._references_name('not_a_dict', 'o') is False
        assert packer._references_name(None, 'o') is False

    def test_references_name_identifier_match(self):
        """Line 122-123: _references_name with Identifier matching name."""
        packer = ObjectPacker({'type': 'Program', 'body': []})
        assert packer._references_name({'type': 'Identifier', 'name': 'o'}, 'o') is True
        assert packer._references_name({'type': 'Identifier', 'name': 'x'}, 'o') is False

    def test_non_dict_in_body_direct_ast(self):
        """Line 22/57: non-dict in body triggers skip in _process_bodies and _try_pack_body."""
        from pyjsclear.parser import parse

        ast = parse('var o = {}; o.x = 1;')
        ast['body'].append(42)
        t = ObjectPacker(ast)
        changed = t.execute()
        assert changed
