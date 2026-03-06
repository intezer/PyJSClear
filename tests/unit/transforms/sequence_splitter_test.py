import pytest

from pyjsclear.transforms.sequence_splitter import SequenceSplitter
from tests.unit.conftest import normalize, roundtrip


class TestSequenceSplittingInExpressionStatements:
    def test_splits_sequence_into_separate_statements(self):
        code = '(a(), b(), c());'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('a(); b(); c();')

    def test_splits_two_element_sequence(self):
        code = '(a(), b());'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('a(); b();')


class TestMultiVarSplitting:
    def test_splits_multi_declarator_var(self):
        code = 'var a = 1, b = 2;'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('var a = 1; var b = 2;')

    def test_splits_three_declarators(self):
        code = 'var a = 1, b = 2, c = 3;'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('var a = 1; var b = 2; var c = 3;')

    def test_preserves_kind_let(self):
        code = 'let a = 1, b = 2;'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('let a = 1; let b = 2;')

    def test_preserves_kind_const(self):
        code = 'const a = 1, b = 2;'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('const a = 1; const b = 2;')


class TestSingleDeclaratorSequenceInitSplitting:
    def test_splits_sequence_in_var_init(self):
        code = 'var x = (a, b, expr());'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('a; b; var x = expr();')

    def test_splits_two_element_sequence_in_init(self):
        code = 'var x = (a, expr());'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('a; var x = expr();')


class TestIndirectCallPrefixExtraction:
    def test_extracts_zero_prefix(self):
        code = '(0, fn)(args);'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('0; fn(args);')

    def test_extracts_multiple_prefixes(self):
        code = '(0, 1, fn)(args);'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('0; 1; fn(args);')


class TestBodyNormalization:
    def test_if_body_normalized_to_block(self):
        code = 'if (x) y();'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('if (x) { y(); }')

    def test_while_body_normalized_to_block(self):
        code = 'while (x) y();'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('while (x) { y(); }')

    def test_for_body_normalized_to_block(self):
        code = 'for (;;) y();'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('for (; ; ) { y(); }')


class TestIfBranchNormalization:
    def test_consequent_normalized(self):
        code = 'if (x) y();'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('if (x) { y(); }')

    def test_alternate_normalized(self):
        code = 'if (x) { y(); } else z();'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('if (x) { y(); } else { z(); }')

    def test_else_if_not_wrapped(self):
        code = 'if (x) { y(); } else if (z) { w(); }'
        result, changed = roundtrip(code, SequenceSplitter)
        # else-if should not be wrapped in a block
        assert normalize(result) == normalize('if (x) { y(); } else if (z) { w(); }')


class TestNoChangeWhenNothingToSplit:
    def test_single_expression_statement(self):
        code = 'a();'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is False
        assert normalize(result) == normalize('a();')

    def test_single_var_declaration(self):
        code = 'var a = 1;'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is False
        assert normalize(result) == normalize('var a = 1;')

    def test_already_block_if(self):
        code = 'if (x) { y(); }'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is False
        assert normalize(result) == normalize('if (x) { y(); }')

    def test_empty_program(self):
        code = ''
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is False


class TestAwaitWrappedSequenceSplitting:
    def test_splits_await_sequence_in_var_init(self):
        code = 'async function f() { var x = await (a, b, expr()); }'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('async function f() { a; b; var x = await expr(); }')

    def test_splits_await_two_element_sequence(self):
        code = 'async function f() { var x = await (a, expr()); }'
        result, changed = roundtrip(code, SequenceSplitter)
        assert changed is True
        assert normalize(result) == normalize('async function f() { a; var x = await expr(); }')
