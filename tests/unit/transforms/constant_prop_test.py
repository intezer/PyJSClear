"""Unit tests for ConstantProp transform."""

import pytest

from pyjsclear.transforms.constant_prop import ConstantProp
from tests.unit.conftest import normalize, roundtrip


class TestConstantPropBasic:
    def test_const_numeric_propagated_and_removed(self):
        code, changed = roundtrip("const x = 5; y(x);", ConstantProp)
        assert changed is True
        assert normalize(code) == normalize("y(5);")

    def test_var_no_reassignment_propagated(self):
        code, changed = roundtrip('var x = "hello"; console.log(x);', ConstantProp)
        assert changed is True
        assert normalize(code) == normalize('console.log("hello");')

    def test_let_with_reassignment_unchanged(self):
        code, changed = roundtrip("let x = 1; x = 2; y(x);", ConstantProp)
        assert changed is False
        assert "x" in code

    def test_multiple_references_replaced(self):
        code, changed = roundtrip("const x = 5; x; x;", ConstantProp)
        assert changed is True
        assert "x" not in normalize(code).replace("5", "")
        # Declaration should be removed
        assert "const" not in code

    def test_function_scope_propagation(self):
        code, changed = roundtrip(
            "function f() { const a = true; return a; }", ConstantProp
        )
        assert changed is True
        assert normalize(code) == normalize("function f() { return true; }")

    def test_non_literal_init_no_propagation(self):
        code, changed = roundtrip("const x = foo(); y(x);", ConstantProp)
        assert changed is False
        assert "x" in code

    def test_null_literal_propagated(self):
        code, changed = roundtrip("const x = null; y(x);", ConstantProp)
        assert changed is True
        assert normalize(code) == normalize("y(null);")

    def test_no_constants_returns_false(self):
        code, changed = roundtrip("var x = foo(); y(x);", ConstantProp)
        assert changed is False
