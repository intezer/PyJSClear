"""Tests for the dead object property remover transform."""

from pyjsclear.transforms.dead_object_props import DeadObjectPropRemover
from tests.unit.conftest import roundtrip


class TestDeadObjectPropRemover:
    """Tests for removing dead object property assignments."""

    def test_removes_dead_prop(self):
        code = 'var v = {}; v.FOO = "bar";'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True
        assert 'v.FOO' not in result
        assert 'bar' not in result

    def test_preserves_read_prop(self):
        code = 'var v = {}; v.FOO = "bar"; console.log(v.FOO);'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_multiple_dead_props(self):
        code = 'var v = {}; v.A = 1; v.B = 2; v.C = 3;'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True
        assert 'v.A' not in result
        assert 'v.B' not in result
        assert 'v.C' not in result

    def test_mixed_dead_and_live(self):
        code = 'var v = {}; v.A = 1; v.B = 2; console.log(v.A);'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True
        assert 'v.A' in result  # read, so preserved
        assert 'v.B' not in result  # dead

    def test_no_dead_props_returns_false(self):
        result, changed = roundtrip('var x = 1;', DeadObjectPropRemover)
        assert changed is False

    def test_skips_computed_access(self):
        code = 'var v = {}; v["FOO"] = "bar";'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_preserves_call_rhs(self):
        """Don't remove if RHS has side effects (function call)."""
        code = 'var v = {}; v.FOO = doSomething();'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_preserves_new_rhs(self):
        """Don't remove if RHS is a constructor call."""
        code = 'var v = {}; v.FOO = new Foo();'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_removes_with_identifier_rhs(self):
        """Identifier RHS is side-effect-free."""
        code = 'var v = {}; v.FOO = x;'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True
        assert 'v.FOO' not in result

    def test_removes_with_member_rhs(self):
        """MemberExpression RHS is side-effect-free."""
        code = 'var v = {}; v.FOO = a.b;'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True
        assert 'v.FOO' not in result

    def test_removes_with_unary_rhs(self):
        code = 'var v = {}; v.FOO = -1;'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True

    def test_removes_with_array_rhs(self):
        code = 'var v = {}; v.FOO = [1, 2, 3];'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True

    def test_preserves_array_rhs_with_call(self):
        code = 'var v = {}; v.FOO = [fn()];'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_multiple_objects(self):
        code = 'var a = {}, b = {}; a.X = 1; b.Y = 2; console.log(a.X);'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is True
        assert 'a.X' in result
        assert 'b.Y' not in result

    def test_preserves_escaped_via_assignment(self):
        """Properties on objects assigned to exports are preserved."""
        code = 'var v = {}; r.exports = v; v.FOO = "bar";'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_preserves_escaped_via_call(self):
        """Properties on objects passed as function args are preserved."""
        code = 'var v = {}; fn(v); v.FOO = "bar";'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_preserves_global_object(self):
        """Properties on global objects like module are preserved."""
        code = 'module.exports = x;'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        assert changed is False

    def test_chained_member_preserves_base(self):
        """v.A.B = 1 reads v.A (as object), so v.A is preserved."""
        code = 'var v = {}; v.A = {}; v.A.B = 1;'
        result, changed = roundtrip(code, DeadObjectPropRemover)
        # v.A appears as both write and read (object of v.A.B), so it's preserved
        assert changed is False
