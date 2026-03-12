"""Tests for the cleanup transforms."""

from pyjsclear.transforms.cleanup import EmptyIfRemover
from pyjsclear.transforms.cleanup import LetToConst
from pyjsclear.transforms.cleanup import OptionalCatchBinding
from pyjsclear.transforms.cleanup import ReturnUndefinedCleanup
from pyjsclear.transforms.cleanup import TrailingReturnRemover
from pyjsclear.transforms.cleanup import VarToConst
from tests.unit.conftest import roundtrip


class TestEmptyIfRemover:
    """Tests for removing empty if statements."""

    def test_removes_empty_if_no_else(self):
        code = 'if (x < 0) {} console.log("kept");'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is True
        assert 'if' not in result
        assert 'kept' in result

    def test_removes_empty_if_identifier_test(self):
        code = 'if (flag) {} console.log("kept");'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is True
        assert 'if' not in result

    def test_flips_empty_if_with_else(self):
        code = 'if (x) {} else { console.log("alt"); }'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is True
        assert '!x' in result or '! x' in result
        assert 'alt' in result
        assert 'else' not in result

    def test_preserves_non_empty_if(self):
        code = 'if (x) { console.log("body"); }'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is False
        assert 'body' in result

    def test_preserves_if_with_side_effect_test(self):
        """Don't remove if(foo()) {} — the call has side effects."""
        code = 'if (foo()) {} console.log("kept");'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is False
        assert 'foo()' in result

    def test_no_if_returns_false(self):
        result, changed = roundtrip('var x = 1;', EmptyIfRemover)
        assert changed is False

    def test_removes_member_expression_test(self):
        code = 'if (a.b) {} console.log("kept");'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is True
        assert 'if' not in result

    def test_preserves_assignment_in_test(self):
        """Don't remove if(x = foo()) {} — assignment is a side effect."""
        code = 'if (x = 1) {} console.log("kept");'
        result, changed = roundtrip(code, EmptyIfRemover)
        assert changed is False


class TestTrailingReturnRemover:
    """Tests for removing trailing return; at end of functions."""

    def test_removes_trailing_return(self):
        code = 'function f() { console.log("hi"); return; }'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is True
        assert 'return' not in result
        assert 'hi' in result

    def test_preserves_return_with_value(self):
        code = 'function f() { return 42; }'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is False
        assert 'return 42' in result

    def test_preserves_non_trailing_return(self):
        code = 'function f() { return; console.log("dead"); }'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is False

    def test_removes_from_arrow_function(self):
        code = 'const f = () => { console.log("hi"); return; };'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is True
        assert 'return' not in result

    def test_removes_from_method(self):
        code = 'const C = class { foo() { this.x = 1; return; } };'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is True
        assert 'return' not in result

    def test_preserves_arrow_expression_body(self):
        code = 'const f = () => 42;'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is False

    def test_no_functions_returns_false(self):
        result, changed = roundtrip('var x = 1;', TrailingReturnRemover)
        assert changed is False

    def test_empty_function_unchanged(self):
        code = 'function f() {}'
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is False

    def test_removes_from_nested_functions(self):
        code = '''
        function f() {
            function g() { console.log("inner"); return; }
            g();
            return;
        }
        '''
        result, changed = roundtrip(code, TrailingReturnRemover)
        assert changed is True
        assert 'return' not in result


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


class TestLetToConst:
    """Tests for converting let to const when never reassigned."""

    def test_simple_let_to_const(self):
        code = 'function f() { let x = 1; return x; }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is True
        assert 'const x = 1' in result
        assert 'let x' not in result

    def test_reassigned_let_stays_let(self):
        code = 'function f() { let x = 1; x = 2; return x; }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is False
        assert 'let x' in result

    def test_no_init_stays_let(self):
        code = 'function f() { let x; x = 1; return x; }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is False
        assert 'let x' in result

    def test_const_unchanged(self):
        code = 'function f() { const x = 1; return x; }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is False

    def test_var_unchanged(self):
        code = 'function f() { var x = 1; return x; }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is False

    def test_let_in_block(self):
        """let inside if-block should still be converted (both block-scoped)."""
        code = '''
        function f(cond) {
            if (cond) { let x = 1; console.log(x); }
        }
        '''
        result, changed = roundtrip(code, LetToConst)
        assert changed is True
        assert 'const x = 1' in result

    def test_let_in_for_loop_body(self):
        code = 'function f() { for (let i = 0; i < 1; i++) { let x = 1; console.log(x); } }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is True
        assert 'const x = 1' in result

    def test_loop_counter_stays_let(self):
        code = 'function f() { for (let i = 0; i < 10; i++) { console.log(i); } }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is False
        assert 'let i' in result

    def test_multi_declarator_not_converted(self):
        code = 'function f() { let a = 1, b = 2; return a + b; }'
        result, changed = roundtrip(code, LetToConst)
        assert changed is False

    def test_no_lets_returns_false(self):
        result, changed = roundtrip('var x = 1;', LetToConst)
        assert changed is False
