import pytest

from pyjsclear.transforms.object_simplifier import ObjectSimplifier
from tests.unit.conftest import normalize, roundtrip


class TestLiteralPropertyAccess:
    """Tests for inlining literal property accesses from proxy objects."""

    def test_numeric_property(self):
        code, changed = roundtrip("const o = {x: 1}; y(o.x);", ObjectSimplifier)
        assert changed is True
        assert "y(1)" in code
        assert "o.x" not in code

    def test_string_property(self):
        code, changed = roundtrip('const o = {s: "hello"}; y(o.s);', ObjectSimplifier)
        assert changed is True
        assert "hello" in code
        assert "o.s" not in code

    def test_computed_string_access(self):
        code, changed = roundtrip('const o = {x: 1}; y(o["x"]);', ObjectSimplifier)
        assert changed is True
        assert "y(1)" in code
        assert 'o["x"]' not in code


class TestFunctionPropertyCall:
    """Tests for inlining function property calls."""

    def test_simple_function_inline(self):
        code, changed = roundtrip(
            "const o = {f: function(a) { return a; }}; o.f(1);",
            ObjectSimplifier,
        )
        assert changed is True
        assert "o.f" not in code

    def test_multi_param_function_inline(self):
        code, changed = roundtrip(
            "const o = {f: function(a, b) { return a + b; }}; o.f(1, 2);",
            ObjectSimplifier,
        )
        assert changed is True
        assert "1 + 2" in code
        assert "o.f" not in code


class TestPropertyAssignmentPreventsInlining:
    """Tests that property assignment on the object prevents inlining."""

    def test_assignment_blocks_inlining(self):
        code, changed = roundtrip(
            "const o = {x: 1}; o.x = 2; y(o.x);", ObjectSimplifier
        )
        assert changed is False
        assert "o.x" in code


class TestNonConstantBinding:
    """Tests that non-constant bindings are not inlined."""

    def test_var_reassigned_no_inline(self):
        code, changed = roundtrip(
            "var o = {x: 1}; o = {}; y(o.x);", ObjectSimplifier
        )
        assert changed is False
        assert "o.x" in code


class TestLetBindingConstant:
    """Let binding without reassignment is treated as constant and inlined."""

    def test_let_without_reassignment_inlines(self):
        code, changed = roundtrip("let o = {x: 1}; y(o.x);", ObjectSimplifier)
        assert changed is True
        assert "y(1)" in code


class TestNonProxyObject:
    """Tests that objects with non-literal, non-function values are skipped."""

    def test_object_with_identifier_value_skipped(self):
        code, changed = roundtrip(
            "const o = {x: someVar}; y(o.x);", ObjectSimplifier
        )
        assert changed is False
        assert "o.x" in code

    def test_object_with_call_expression_value_skipped(self):
        code, changed = roundtrip(
            "const o = {x: foo()}; y(o.x);", ObjectSimplifier
        )
        assert changed is False
        assert "o.x" in code


class TestNoProxyObjects:
    """Tests that the transform returns False when there is nothing to do."""

    def test_no_objects_returns_false(self):
        code, changed = roundtrip("var x = 1; y(x);", ObjectSimplifier)
        assert changed is False

    def test_empty_object_returns_false(self):
        code, changed = roundtrip("const o = {}; y(o);", ObjectSimplifier)
        assert changed is False
