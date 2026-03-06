"""Unit tests for UnusedVariableRemover transform."""

import pytest

from pyjsclear.transforms.unused_vars import UnusedVariableRemover
from tests.unit.conftest import normalize, roundtrip


class TestUnusedVariableRemover:
    """Tests for removing unreferenced variables and functions."""

    def test_unreferenced_var_in_function_removed(self):
        code = "function f() { var x = 1; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "var x" not in result
        assert "function f" in result

    def test_referenced_var_in_function_kept(self):
        code = "function f() { var x = 1; return x; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var x = 1" in result
        assert "return x" in result

    def test_global_0x_prefixed_var_removed(self):
        code = "var _0xabc = 1;"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "_0xabc" not in result

    def test_global_normal_var_kept(self):
        code = "var foo = 1;"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var foo = 1" in result

    def test_side_effect_call_expression_kept(self):
        code = "function f() { var x = foo(); }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var x = foo()" in result

    def test_side_effect_new_expression_kept(self):
        code = "function f() { var x = new Foo(); }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var x = new Foo()" in result

    def test_side_effect_assignment_expression_kept(self):
        code = "function f() { var x = (a = 1); }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var x" in result

    def test_side_effect_update_expression_kept(self):
        code = "function f() { var x = a++; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var x" in result

    def test_global_0x_function_declaration_removed(self):
        code = "function _0xabc() {}"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "_0xabc" not in result

    def test_unreferenced_nested_function_removed(self):
        code = "function f() { function g() {} }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "function g" not in result
        assert "function f" in result

    def test_param_kept_even_if_unreferenced(self):
        code = "function f(x) { return 1; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "function f(x)" in result

    def test_multiple_declarators_remove_only_unreferenced(self):
        code = "function f() { var x = 1, y = 2; return x; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "x" in result
        assert "y" not in result

    def test_multiple_declarators_all_unreferenced(self):
        code = "function f() { var x = 1, y = 2; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "var" not in result

    def test_no_unused_returns_false(self):
        code = "function f(x) { return x; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False

    def test_var_with_no_init_removed(self):
        code = "function f() { var x; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "var x" not in result

    def test_global_normal_function_kept(self):
        code = "function foo() {}"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "function foo" in result

    def test_rebuild_scope_flag(self):
        assert UnusedVariableRemover.rebuild_scope is True

    def test_nested_side_effect_in_binary_kept(self):
        code = "function f() { var x = 1 + foo(); }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is False
        assert "var x" in result

    def test_pure_init_object_removed(self):
        code = "function f() { var x = {a: 1}; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "var x" not in result

    def test_pure_init_array_removed(self):
        code = "function f() { var x = [1, 2]; }"
        result, changed = roundtrip(code, UnusedVariableRemover)
        assert changed is True
        assert "var x" not in result
