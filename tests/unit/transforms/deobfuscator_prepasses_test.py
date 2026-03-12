"""Tests for deobfuscator pre-pass integration (encoding detection, large file optimization)."""

from unittest.mock import patch

from pyjsclear.deobfuscator import Deobfuscator
from pyjsclear.deobfuscator import _count_nodes


class TestLargeFileOptimization:
    def test_returns_original_on_no_change(self):
        code = 'const x = 1;'
        d = Deobfuscator(code)
        result = d.execute()
        assert result == code


class TestCountNodes:
    def test_count_simple_ast(self):
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        count = _count_nodes(ast)
        assert count > 0


class TestJSFuckPrePass:
    """Test JSFuck pre-pass integration in deobfuscator."""

    @patch('pyjsclear.deobfuscator.is_jsfuck', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.jsfuck_decode', return_value='var y = 2;')
    def test_jsfuck_pre_pass(self, mock_decode, mock_detect):
        """JSFuck pre-pass: detected and decoded."""
        code = 'some jsfuck stuff'
        result = Deobfuscator(code).execute()
        mock_decode.assert_called_once_with(code)
        assert 'y' in result or 'var' in result

    @patch('pyjsclear.deobfuscator.is_jsfuck', return_value=True)
    @patch('pyjsclear.deobfuscator.jsfuck_decode', return_value=None)
    @patch('pyjsclear.deobfuscator.is_aa_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_jj_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_eval_packed', return_value=False)
    def test_jsfuck_decode_failure_continues(self, *mocks):
        """When JSFuck decode fails, pipeline continues normally."""
        code = 'var x = 1;'
        result = Deobfuscator(code).execute()
        # Should still produce a result (original or transformed)
        assert result is not None


class TestJJEncodePrePass:
    """Test JJEncode pre-pass integration in deobfuscator."""

    @patch('pyjsclear.deobfuscator.is_jsfuck', return_value=False)
    @patch('pyjsclear.deobfuscator.is_aa_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_jj_encoded', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.jj_decode', return_value='var z = 3;')
    def test_jj_encode_pre_pass(self, mock_decode, mock_detect, mock_aa, mock_jsfuck):
        """JJEncode pre-pass: detected and decoded."""
        code = 'some jj encoded stuff'
        result = Deobfuscator(code).execute()
        mock_decode.assert_called_once_with(code)
        assert 'z' in result or 'var' in result

    @patch('pyjsclear.deobfuscator.is_jsfuck', return_value=False)
    @patch('pyjsclear.deobfuscator.is_aa_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_jj_encoded', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.jj_decode', return_value=None)
    @patch('pyjsclear.deobfuscator.jj_decode_via_eval', return_value='var w = 4;')
    def test_jj_encode_fallback_to_eval(self, mock_eval, mock_decode, mock_detect, mock_aa, mock_jsfuck):
        """JJEncode falls back to jj_decode_via_eval when jj_decode returns None."""
        code = 'some jj encoded stuff'
        result = Deobfuscator(code).execute()
        mock_eval.assert_called_once_with(code)
        assert 'w' in result or 'var' in result
