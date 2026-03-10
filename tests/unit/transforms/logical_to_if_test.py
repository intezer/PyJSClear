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


class TestCoverageGaps:
    """Tests targeting uncovered lines in logical_to_if.py."""

    def test_non_dict_child_in_transform_bodies(self):
        """Line 36: _transform_bodies with non-dict child (skipped)."""
        # A simple literal expression; the AST will contain non-dict children
        # (e.g., string values) which should be safely skipped.
        code = 'var x = 1;'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False

    def test_non_dict_expression_in_expression_statement(self):
        """Line 76: ExpressionStatement with non-dict expression."""
        # This is hard to trigger from valid JS since esprima always gives dicts,
        # but we can test the boundary by verifying normal code doesn't crash.
        code = ';'  # Empty statement — not ExpressionStatement
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False

    def test_return_non_sequence_non_logical(self):
        """Line 98: Return statement with a plain expression (not sequence, not logical)."""
        code = 'function f() { return 42; }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False
        assert '42' in result

    def test_return_non_dict_argument(self):
        """Line 88: Return with null argument (return;)."""
        code = 'function f() { return; }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False

    def test_return_single_element_sequence(self):
        """Line 104: Return with single-element sequence (len <= 1) returns None."""
        # Manually constructing is tricky; a single-element SequenceExpression
        # is unusual. We test via the AST directly.
        from pyjsclear.parser import parse
        from pyjsclear.generator import generate

        ast = parse('function f() { return a; }')
        # Manually make the return argument a SequenceExpression with 1 element
        ret_stmt = ast['body'][0]['body']['body'][0]
        ret_stmt['argument'] = {
            'type': 'SequenceExpression',
            'expressions': [{'type': 'Identifier', 'name': 'a'}],
        }
        t = LogicalToIf(ast)
        changed = t.execute()
        assert changed is False

    def test_return_sequence_with_logical_items(self):
        """Lines 108-111: Return sequence containing LogicalExpression items."""
        code = 'function f() { return a && b(), c; }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is True
        # The logical expression a && b() inside the sequence should be converted to if
        assert 'if' in result
        assert 'return c' in normalize(result)

    def test_return_logical_right_not_sequence(self):
        """Line 120: Return logical where right side is not a SequenceExpression."""
        code = 'function f() { return a || b; }'
        result, changed = roundtrip(code, LogicalToIf)
        assert changed is False

    def test_return_logical_right_sequence_single_element(self):
        """Line 123: Return logical where right side is sequence with <=1 elements."""
        from pyjsclear.parser import parse
        from pyjsclear.generator import generate

        ast = parse('function f() { return a || b; }')
        ret_stmt = ast['body'][0]['body']['body'][0]
        ret_stmt['argument'] = {
            'type': 'LogicalExpression',
            'operator': '||',
            'left': {'type': 'Identifier', 'name': 'a'},
            'right': {
                'type': 'SequenceExpression',
                'expressions': [{'type': 'Identifier', 'name': 'b'}],
            },
        }
        t = LogicalToIf(ast)
        changed = t.execute()
        assert changed is False

    def test_nullish_coalescing_not_converted(self):
        """Lines 147-148: _logical_to_if with unknown operator (e.g. '??') returns None."""
        from pyjsclear.parser import parse
        from pyjsclear.generator import generate

        ast = parse('a ?? b();')
        # Esprima may not parse ?? as LogicalExpression, so force it
        expr_stmt = ast['body'][0]
        expr_stmt['expression'] = {
            'type': 'LogicalExpression',
            'operator': '??',
            'left': {'type': 'Identifier', 'name': 'a'},
            'right': {'type': 'CallExpression', 'callee': {'type': 'Identifier', 'name': 'b'}, 'arguments': []},
        }
        t = LogicalToIf(ast)
        changed = t.execute()
        assert changed is False

    def test_expression_stmt_non_dict_expression(self):
        """Line 75: ExpressionStatement with non-dict expression returns None."""
        from pyjsclear.parser import parse

        ast = parse('a();')
        ast['body'][0]['expression'] = 42
        t = LogicalToIf(ast)
        changed = t.execute()
        assert not changed
