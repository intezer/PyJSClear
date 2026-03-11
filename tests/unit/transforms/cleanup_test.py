"""Tests for the cleanup transforms."""

from pyjsclear.transforms.cleanup import OptionalCatchBinding
from pyjsclear.transforms.cleanup import ReturnUndefinedCleanup
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
