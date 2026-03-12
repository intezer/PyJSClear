"""Tests for the no-op call remover transform."""

from pyjsclear.transforms.noop_calls import NoopCallRemover
from tests.unit.conftest import roundtrip


class TestNoopCallRemover:
    """Tests for removing calls to no-op methods."""

    def test_removes_call_to_empty_method(self):
        code = '''
        const C = class { static noop() {} };
        C.noop();
        console.log("kept");
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is True
        assert 'C.noop()' not in result
        assert 'kept' in result

    def test_removes_call_to_return_only_method(self):
        code = '''
        const C = class { static noop() { return; } };
        C.noop("ignored");
        console.log("kept");
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is True
        assert 'noop' not in result or 'static noop' in result
        assert 'kept' in result

    def test_preserves_method_with_body(self):
        code = '''
        const C = class { static doWork() { console.log("work"); } };
        C.doWork();
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is False

    def test_preserves_method_returning_value(self):
        code = '''
        const C = class { static getValue() { return 42; } };
        var x = C.getValue();
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is False

    def test_no_methods_returns_false(self):
        result, changed = roundtrip('var x = 1;', NoopCallRemover)
        assert changed is False

    def test_removes_chained_call(self):
        code = '''
        const C = class { static noop() { return; } };
        a.b.noop("test");
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is True

    def test_preserves_async_noop(self):
        """Async methods return promises — don't remove their calls."""
        code = '''
        const C = class { static async noop() { return; } };
        await C.noop();
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is False

    def test_preserves_non_expression_call(self):
        """Only removes expression statements, not calls used as values."""
        code = '''
        const C = class { static noop() {} };
        var x = C.noop();
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is False

    def test_removes_multiple_calls(self):
        code = '''
        const C = class { static noop() { return; } };
        C.noop("a");
        C.noop("b");
        C.noop("c");
        console.log("kept");
        '''
        result, changed = roundtrip(code, NoopCallRemover)
        assert changed is True
        assert result.count('noop') <= 1  # only the definition
        assert 'kept' in result
