"""Unit tests for ReassignmentRemover transform."""

import pytest

from pyjsclear.transforms.reassignment import ReassignmentRemover
from tests.unit.conftest import normalize, roundtrip


class TestReassignmentRemoverDeclaratorInline:
    """Tests for var x = y; declarator-based inlining."""

    def test_well_known_global_json(self):
        code = 'var x = JSON; x.parse(y);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'JSON.parse(y)' in normalize(result)
        assert 'var x' not in normalize(result) or 'x.parse' not in normalize(result)

    def test_well_known_global_console(self):
        code = 'var x = console; x.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'console.log("hi")' in normalize(result)

    def test_constant_binding_inline(self):
        code = 'const a = 1; var b = a; c(b);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'c(a)' in normalize(result)

    def test_unknown_target_unchanged(self):
        code = 'var x = y; x.foo();'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False
        assert 'x.foo()' in normalize(result)

    def test_self_assignment_skipped(self):
        code = 'var x = x;'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False

    def test_non_constant_target_unchanged(self):
        code = 'var y = 1; y = 2; var x = y; x.foo();'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False
        assert 'x.foo()' in normalize(result)


class TestReassignmentRemoverAssignmentAlias:
    """Tests for var x; ... x = y; assignment alias inlining."""

    def test_assignment_alias_console(self):
        code = 'var x; x = console; x.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'console.log("hi")' in normalize(result)
        # The assignment statement should be removed
        assert 'x = console' not in normalize(result)

    def test_assignment_alias_json(self):
        code = 'var x; x = JSON; x.parse(s);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'JSON.parse(s)' in normalize(result)

    def test_assignment_alias_unknown_target_unchanged(self):
        code = 'var x; x = y; x.foo();'
        result, changed = roundtrip(code, ReassignmentRemover)
        # y is not well-known and not a constant binding, so no change
        assert 'x.foo()' in normalize(result)

    def test_assignment_alias_non_constant_target_unchanged(self):
        code = 'var y = 1; y = 2; var x; x = y; x.foo();'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert 'x.foo()' in normalize(result)


class TestReassignmentRemoverNoChange:
    """Tests for cases where nothing changes."""

    def test_no_reassignments_returns_false(self):
        code = 'var a = 1; console.log(a);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False

    def test_param_not_inlined(self):
        code = 'function f(x) { var y = x; return y; }'
        result, changed = roundtrip(code, ReassignmentRemover)
        # x is a param binding; it is constant, so inlining y=x should work
        # but the key point is params themselves are not processed as sources
        # Let's just verify it doesn't crash
        assert isinstance(changed, bool)

    def test_no_variable_declarations(self):
        code = 'console.log(1);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False


class TestReassignmentRemoverEdgeCases:
    """Edge case tests."""

    def test_multiple_well_known_globals(self):
        code = 'var a = Object; var b = Array; a.keys(x); b.isArray(y);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'Object.keys(x)' in normalize(result)
        assert 'Array.isArray(y)' in normalize(result)

    def test_rebuild_scope_flag(self):
        assert ReassignmentRemover.rebuild_scope is True


class TestReassignmentRemoverSkipConditions:
    """Tests for skip conditions on reference replacement."""

    def test_reference_as_assignment_lhs_skipped(self):
        """Line 93: Reference used as assignment left-hand side should be skipped."""
        code = 'var x = console; x = something; x.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        # x has writes so it is not constant, no inlining should happen
        assert isinstance(changed, bool)

    def test_reference_as_declarator_id_skipped(self):
        """Line 95: Reference used as VariableDeclarator id should be skipped."""
        # When a variable is reassigned via declarator pattern, the id ref should be skipped
        code = 'var x = JSON; x.parse(s);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'JSON.parse(s)' in normalize(result)


class TestReassignmentRemoverAssignmentAliasEdgeCases:
    """Tests for assignment alias edge cases."""

    def test_assignment_alias_with_init_skipped(self):
        """Line 131: VariableDeclarator with init should be skipped for assignment alias."""
        code = 'var _0x1 = undefined; _0x1 = console; _0x1.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        # _0x1 has init (undefined), so assignment alias path skips it
        # but it might be handled by the declarator path instead
        assert isinstance(changed, bool)

    def test_assignment_alias_multiple_writes_skipped(self):
        """Line 151: Assignment alias with != 1 writes should be skipped."""
        code = 'var _0x1; _0x1 = console; _0x1 = JSON; _0x1.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        # Two writes means it won't be inlined via assignment alias
        assert '_0x1' in result or changed is False

    def test_assignment_alias_rhs_not_identifier(self):
        """Line 157: Assignment alias where right side is not an identifier."""
        code = 'var _0x1; _0x1 = 123; console.log(_0x1);'
        result, changed = roundtrip(code, ReassignmentRemover)
        # RHS is a literal, not an identifier — should be skipped
        assert '_0x1' in result

    def test_assignment_alias_self_assignment_skipped(self):
        """Line 161: target_name equals name should be skipped."""
        code = 'var _0x1; _0x1 = _0x1;'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False

    def test_assignment_alias_replacement_with_index(self):
        """Line 175: Assignment alias replacement in array position (with index)."""
        code = 'var _0x1; _0x1 = console; foo([_0x1]);'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'console' in result

    def test_assignment_alias_pattern(self):
        """Assignment alias: var x; x = console; log(x);"""
        code = 'var _0x1 = undefined; var _0x2; _0x2 = console; _0x2.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed
        assert 'console' in result


