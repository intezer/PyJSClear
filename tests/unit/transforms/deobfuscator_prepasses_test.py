"""Tests for deobfuscator pre-pass integration (encoding detection, large file optimization)."""

from pyjsclear.deobfuscator import Deobfuscator
from pyjsclear.deobfuscator import _count_nodes


class TestLargeFileOptimization:
    def test_small_file_uses_full_pipeline(self):
        code = 'var x = 1;'
        d = Deobfuscator(code)
        result = d.execute()
        assert isinstance(result, str)

    def test_returns_original_on_no_change(self):
        code = 'var x = 1;'
        d = Deobfuscator(code)
        result = d.execute()
        assert result == code


class TestCountNodes:
    def test_count_simple_ast(self):
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        count = _count_nodes(ast)
        assert count > 0
