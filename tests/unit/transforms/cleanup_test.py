"""Tests for the cleanup transforms."""

from pyjsclear.transforms.cleanup import OptionalCatchBinding
from pyjsclear.transforms.cleanup import ReturnUndefinedCleanup
from pyjsclear.transforms.cleanup import VarToConst
from tests.unit.conftest import roundtrip


class TestOptionalCatchBinding:
    """Tests for removing unused catch parameters."""

    def test_unused_catch_param_removed(self):
        code = 'try { foo(); } catch (e) { bar(); }'
        result, changed = roundtrip(code, OptionalCatchBinding)
        assert changed is True
        assert 'catch {' in result
        assert 'catch (e)' not in result

    def test_used_catch_param_preserved(self):
        code = 'try { foo(); } catch (e) { console.log(e); }'
        result, changed = roundtrip(code, OptionalCatchBinding)
        assert changed is False
        assert 'catch (e)' in result

    def test_no_try_catch_returns_false(self):
        result, changed = roundtrip('var x = 1;', OptionalCatchBinding)
        assert changed is False

    def test_catch_without_param_unchanged(self):
        code = 'try { foo(); } catch { bar(); }'
        result, changed = roundtrip(code, OptionalCatchBinding)
        assert changed is False

    def test_nested_catch_unused(self):
        code = '''
        try {
            try { a(); } catch (inner) { b(); }
        } catch (outer) {
            c();
        }
        '''
        result, changed = roundtrip(code, OptionalCatchBinding)
        assert changed is True
        # Both inner and outer are unused
        assert 'catch (inner)' not in result
        assert 'catch (outer)' not in result

    def test_catch_param_used_in_nested_scope(self):
        code = '''
        try { foo(); } catch (e) {
            function handler() { return e.message; }
            handler();
        }
        '''
        result, changed = roundtrip(code, OptionalCatchBinding)
        assert changed is False
        assert 'catch (e)' in result


class TestReturnUndefinedCleanup:
    """Tests for simplifying return undefined to return."""

    def test_return_undefined_simplified(self):
        code = 'function f() { return undefined; }'
        result, changed = roundtrip(code, ReturnUndefinedCleanup)
        assert changed is True
        assert 'return;' in result
        assert 'return undefined' not in result

    def test_return_value_unchanged(self):
        code = 'function f() { return 42; }'
        result, changed = roundtrip(code, ReturnUndefinedCleanup)
        assert changed is False

    def test_bare_return_unchanged(self):
        code = 'function f() { return; }'
        result, changed = roundtrip(code, ReturnUndefinedCleanup)
        assert changed is False

    def test_no_returns_false(self):
        result, changed = roundtrip('var x = 1;', ReturnUndefinedCleanup)
        assert changed is False

    def test_multiple_return_undefined(self):
        code = '''
        function f() {
            if (x) { return undefined; }
            return undefined;
        }
        '''
        result, changed = roundtrip(code, ReturnUndefinedCleanup)
        assert changed is True
        assert 'return undefined' not in result


class TestVarToConst:
    """Tests for converting var to const when never reassigned."""

    def test_simple_var_to_const(self):
        code = 'function f() { var x = 1; return x; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is True
        assert 'const x = 1' in result
        assert 'var x' not in result

    def test_reassigned_var_stays_var(self):
        code = 'function f() { var x = 1; x = 2; return x; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is False
        assert 'var x' in result

    def test_no_init_stays_var(self):
        code = 'function f() { var x; x = 1; return x; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is False
        assert 'var x' in result

    def test_const_unchanged(self):
        code = 'function f() { const x = 1; return x; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is False

    def test_let_unchanged(self):
        code = 'function f() { let x = 1; return x; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is False

    def test_multi_declarator_not_converted(self):
        """var a=1, b=2 should not be converted (would need splitting)."""
        code = 'function f() { var a = 1, b = 2; return a + b; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is False

    def test_for_in_not_converted(self):
        code = 'function f(obj) { for (var k in obj) { console.log(k); } }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is False

    def test_var_in_if_block_not_converted(self):
        """var inside if-block is function-scoped but const would be block-scoped."""
        code = '''
        function f(cond) {
            if (cond) { var x = 1; }
            return x;
        }
        '''
        result, changed = roundtrip(code, VarToConst)
        assert changed is False
        assert 'var x' in result

    def test_var_in_try_block_not_converted(self):
        code = '''
        function f() {
            try { var x = 1; } catch (e) {}
            return x;
        }
        '''
        result, changed = roundtrip(code, VarToConst)
        assert changed is False
        assert 'var x' in result

    def test_var_in_for_body_not_converted(self):
        code = '''
        function f() {
            for (var i = 0; i < 1; i++) { var x = 1; }
            return x;
        }
        '''
        result, changed = roundtrip(code, VarToConst)
        assert changed is False

    def test_var_hoisted_reference_before_decl(self):
        """Reference before var declaration relies on hoisting — can't use const."""
        code = '''
        function f() {
            console.log(x);
            if (true) { var x = 1; }
        }
        '''
        result, changed = roundtrip(code, VarToConst)
        assert changed is False

    def test_var_in_switch_case_not_converted(self):
        """var inside switch case block is not at function scope."""
        code = '''
        function f(x) {
            switch (x) {
                case 1: var y = 10; break;
            }
            return y;
        }
        '''
        result, changed = roundtrip(code, VarToConst)
        assert changed is False
        assert 'var y' in result

    def test_class_assigned_to_var(self):
        code = 'function f() { var C = class {}; return C; }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is True
        assert 'const C = class' in result

    def test_function_assigned_to_var(self):
        code = 'function f() { var g = function() { return 1; }; return g(); }'
        result, changed = roundtrip(code, VarToConst)
        assert changed is True
        assert 'const g = function' in result
