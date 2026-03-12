"""Tests for transform interaction edge cases.

These tests verify that transforms work correctly when composed together,
catching bugs that wouldn't appear in isolation.
"""

from pyjsclear import deobfuscate
from pyjsclear.deobfuscator import Deobfuscator
from pyjsclear.generator import generate
from pyjsclear.parser import parse
from pyjsclear.transforms.dead_expressions import DeadExpressionRemover
from pyjsclear.transforms.expression_simplifier import ExpressionSimplifier
from pyjsclear.transforms.nullish_coalescing import NullishCoalescing
from pyjsclear.transforms.optional_chaining import OptionalChaining
from pyjsclear.transforms.property_simplifier import PropertySimplifier
from pyjsclear.transforms.proxy_functions import ProxyFunctionInliner
from pyjsclear.transforms.sequence_splitter import SequenceSplitter


class TestSequenceSplitterThenDeadExpressions:
    """SequenceSplitter produces `0; fn();` — DeadExpressions cleans up `0;`."""

    def test_comma_zero_pattern(self):
        code = '(0, fn)();'
        ast = parse(code)
        SequenceSplitter(ast).execute()
        DeadExpressionRemover(ast).execute()
        result = generate(ast)
        assert '0;' not in result
        assert 'fn()' in result

    def test_comma_zero_in_member(self):
        code = '(0, obj.method)();'
        ast = parse(code)
        SequenceSplitter(ast).execute()
        DeadExpressionRemover(ast).execute()
        result = generate(ast)
        assert '0;' not in result


class TestNullishThenOptionalChaining:
    """NullishCoalescing and OptionalChaining should not interfere."""

    def test_both_patterns_in_same_code(self):
        code = '''
        var a = x !== null && x !== undefined ? x : fallback;
        var b = y === null || y === undefined ? undefined : y.prop;
        '''
        ast = parse(code)
        NullishCoalescing(ast).execute()
        OptionalChaining(ast).execute()
        result = generate(ast)
        assert '??' in result
        assert '?.' in result

    def test_nullish_does_not_eat_optional_chaining_pattern(self):
        """The || pattern should not be mistakenly matched by NullishCoalescing."""
        code = 'var y = x === null || x === undefined ? undefined : x.foo;'
        ast = parse(code)
        NullishCoalescing(ast).execute()
        result = generate(ast)
        # NullishCoalescing uses &&, not ||, so this should not match
        assert '??' not in result


class TestProxyInlinerGuard:
    """Proxy inliner should not blow up helper functions."""

    def test_conditional_helper_not_inlined_when_many_calls(self):
        """A function with a conditional body called >3 times should not be inlined."""
        code = '''
        function helper(x, y) {
            return typeof x === "object" ? x[y] : {};
        }
        var a = helper(obj1, "a");
        var b = helper(obj2, "b");
        var c = helper(obj3, "c");
        var d = helper(obj4, "d");
        '''
        ast = parse(code)
        ProxyFunctionInliner(ast).execute()
        result = generate(ast)
        # helper should still exist as a function, not be inlined
        assert 'function helper' in result
        assert 'helper(obj1' in result

    def test_simple_proxy_still_inlined(self):
        """Simple proxy functions (no conditional) should still be inlined."""
        code = '''
        function add(a, b) { return a + b; }
        var x = add(1, 2);
        '''
        ast = parse(code)
        changed = ProxyFunctionInliner(ast).execute()
        result = generate(ast)
        assert changed is True
        assert '1 + 2' in result


class TestPropertySimplifierThenExpressionSimplifier:
    """PropertySimplifier runs before ExpressionSimplifier in the pipeline."""

    def test_bracket_to_dot_then_no_regression(self):
        """Converting brackets shouldn't break ExpressionSimplifier."""
        code = 'var x = obj["foo"]; var y = 1 + 2;'
        ast = parse(code)
        PropertySimplifier(ast).execute()
        ExpressionSimplifier(ast).execute()
        result = generate(ast)
        assert 'obj.foo' in result
        assert '3' in result


class TestFullPipelineSmoke:
    """Smoke tests running the full Deobfuscator pipeline on small inputs."""

    def test_simple_code_roundtrip(self):
        result = deobfuscate('var x = 1;')
        assert result == 'const x = 1;'

    def test_constant_folding_in_pipeline(self):
        result = deobfuscate('var x = 1 + 2;')
        assert '3' in result

    def test_dead_branch_in_pipeline(self):
        result = deobfuscate('if (true) { foo(); } else { bar(); }')
        assert 'foo()' in result
        assert 'bar()' not in result

    def test_property_simplifier_in_pipeline(self):
        result = deobfuscate('obj["foo"];')
        assert 'obj.foo' in result

    def test_pipeline_does_not_crash_on_empty(self):
        result = deobfuscate('')
        assert result == ''

    def test_pipeline_does_not_crash_on_syntax_error(self):
        result = deobfuscate('not valid {{ js;')
        assert isinstance(result, str)
