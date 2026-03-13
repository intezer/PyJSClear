"""Tests for the unreachable code remover transform."""

from pyjsclear.transforms.unreachable_code import UnreachableCodeRemover
from tests.unit.conftest import roundtrip


class TestUnreachableCodeRemover:
    """Tests for removing unreachable statements after terminators."""

    def test_removes_after_return(self) -> None:
        code = 'function f() { return 1; console.log("dead"); }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is True
        assert 'dead' not in result
        assert 'return 1' in result

    def test_removes_after_throw(self) -> None:
        code = 'function f() { throw new Error(); var x = 1; }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is True
        assert 'var x' not in result

    def test_removes_after_break(self) -> None:
        code = 'for(;;) { break; console.log("dead"); }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is True
        assert 'dead' not in result

    def test_removes_after_continue(self) -> None:
        code = 'for(;;) { continue; console.log("dead"); }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is True
        assert 'dead' not in result

    def test_preserves_reachable_code(self) -> None:
        code = 'function f() { var x = 1; return x; }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is False

    def test_no_terminator_returns_false(self) -> None:
        result, changed = roundtrip('var x = 1; var y = 2;', UnreachableCodeRemover)
        assert changed is False

    def test_removes_multiple_after_return(self) -> None:
        code = 'function f() { return; var a = 1; var b = 2; var c = 3; }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is True
        assert 'var a' not in result
        assert 'var b' not in result
        assert 'var c' not in result

    def test_handles_nested_blocks(self) -> None:
        code = 'function f() { if (x) { return; var dead = 1; } var live = 2; }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is True
        assert 'dead' not in result
        assert 'live' in result

    def test_return_at_end_no_change(self) -> None:
        code = 'function f() { var x = 1; return x; }'
        result, changed = roundtrip(code, UnreachableCodeRemover)
        assert changed is False
