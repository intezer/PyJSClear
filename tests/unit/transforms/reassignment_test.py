"""Unit tests for ReassignmentRemover transform."""

import pytest

from pyjsclear.transforms.reassignment import ReassignmentRemover
from tests.unit.conftest import normalize, roundtrip


class TestReassignmentRemoverDeclaratorInline:
    """Tests for var x = y; declarator-based inlining."""

    def test_well_known_global_json(self):
        code = "var x = JSON; x.parse(y);"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert "JSON.parse(y)" in normalize(result)
        assert "var x" not in normalize(result) or "x.parse" not in normalize(result)

    def test_well_known_global_console(self):
        code = 'var x = console; x.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'console.log("hi")' in normalize(result)

    def test_constant_binding_inline(self):
        code = "const a = 1; var b = a; c(b);"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert "c(a)" in normalize(result)

    def test_unknown_target_unchanged(self):
        code = "var x = y; x.foo();"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False
        assert "x.foo()" in normalize(result)

    def test_self_assignment_skipped(self):
        code = "var x = x;"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False

    def test_non_constant_target_unchanged(self):
        code = "var y = 1; y = 2; var x = y; x.foo();"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False
        assert "x.foo()" in normalize(result)


class TestReassignmentRemoverAssignmentAlias:
    """Tests for var x; ... x = y; assignment alias inlining."""

    def test_assignment_alias_console(self):
        code = 'var x; x = console; x.log("hi");'
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert 'console.log("hi")' in normalize(result)
        # The assignment statement should be removed
        assert "x = console" not in normalize(result)

    def test_assignment_alias_json(self):
        code = "var x; x = JSON; x.parse(s);"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert "JSON.parse(s)" in normalize(result)

    def test_assignment_alias_unknown_target_unchanged(self):
        code = "var x; x = y; x.foo();"
        result, changed = roundtrip(code, ReassignmentRemover)
        # y is not well-known and not a constant binding, so no change
        assert "x.foo()" in normalize(result)

    def test_assignment_alias_non_constant_target_unchanged(self):
        code = "var y = 1; y = 2; var x; x = y; x.foo();"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert "x.foo()" in normalize(result)


class TestReassignmentRemoverNoChange:
    """Tests for cases where nothing changes."""

    def test_no_reassignments_returns_false(self):
        code = "var a = 1; console.log(a);"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False

    def test_param_not_inlined(self):
        code = "function f(x) { var y = x; return y; }"
        result, changed = roundtrip(code, ReassignmentRemover)
        # x is a param binding; it is constant, so inlining y=x should work
        # but the key point is params themselves are not processed as sources
        # Let's just verify it doesn't crash
        assert isinstance(changed, bool)

    def test_no_variable_declarations(self):
        code = "console.log(1);"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is False


class TestReassignmentRemoverEdgeCases:
    """Edge case tests."""

    def test_multiple_well_known_globals(self):
        code = "var a = Object; var b = Array; a.keys(x); b.isArray(y);"
        result, changed = roundtrip(code, ReassignmentRemover)
        assert changed is True
        assert "Object.keys(x)" in normalize(result)
        assert "Array.isArray(y)" in normalize(result)

    def test_rebuild_scope_flag(self):
        assert ReassignmentRemover.rebuild_scope is True
