import pytest

from pyjsclear.transforms.logical_to_if import LogicalToIf
from tests.unit.conftest import normalize, roundtrip


class TestLogicalAndToIf:
    def test_and_converts_to_if(self):
        code = 'a && b();'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('if (a) { b(); }')

    def test_and_with_sequence_in_right(self):
        code = 'a && (b(), c());'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('if (a) { b(); c(); }')


class TestLogicalOrToIf:
    def test_or_converts_to_negated_if(self):
        code = 'a || b();'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('if (!a) { b(); }')

    def test_or_with_sequence_in_right(self):
        code = 'a || (b(), c());'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('if (!a) { b(); c(); }')


class TestTernaryToIfElse:
    def test_ternary_converts_to_if_else(self):
        code = 'a ? b() : c();'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('if (a) { b(); } else { c(); }')

    def test_ternary_with_sequences(self):
        code = 'a ? (b(), c()) : (d(), e());'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('if (a) { b(); c(); } else { d(); e(); }')


class TestReturnSequence:
    def test_return_sequence_splits(self):
        code = 'function f() { return a(), b(), c; }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('function f() { a(); b(); return c; }')

    def test_return_two_element_sequence(self):
        code = 'function f() { return a(), b; }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('function f() { a(); return b; }')


class TestReturnLogical:
    def test_return_or_with_sequence(self):
        code = 'function f() { return a || (b(), c); }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('function f() { if (!a) { b(); } return c; }')

    def test_return_and_with_sequence(self):
        code = 'function f() { return a && (b(), c); }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('function f() { if (a) { b(); } return c; }')


class TestNoChange:
    def test_plain_call_expression_unchanged(self):
        code = 'b();'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False
        assert normalize(result) == normalize('b();')

    def test_assignment_unchanged(self):
        code = 'a = 1;'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False
        assert normalize(result) == normalize('a = 1;')

    def test_empty_program(self):
        code = ''
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False


class TestNestedInFunctionBody:
    def test_logical_inside_function(self):
        code = 'function f() { a && b(); }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('function f() { if (a) { b(); } }')

    def test_logical_inside_arrow_function(self):
        code = 'var f = () => { a || b(); };'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('var f = () => { if (!a) { b(); } };')

    def test_multiple_logicals_in_body(self):
        code = 'function f() { a && b(); c || d(); }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        assert normalize(result) == normalize('function f() { if (a) { b(); } if (!c) { d(); } }')
