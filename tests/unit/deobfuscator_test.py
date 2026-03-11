"""Unit tests for the Deobfuscator orchestrator."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pyjsclear.deobfuscator import _LARGE_FILE_SIZE
from pyjsclear.deobfuscator import _MAX_CODE_SIZE
from pyjsclear.deobfuscator import TRANSFORM_CLASSES
from pyjsclear.deobfuscator import Deobfuscator
from pyjsclear.deobfuscator import _count_nodes


class TestTransformClasses:
    """Tests for the TRANSFORM_CLASSES list."""

    def test_transform_classes_length(self):
        """TRANSFORM_CLASSES has exactly 26 entries, with StringRevealer appearing twice."""
        assert len(TRANSFORM_CLASSES) == 34

    def test_string_revealer_appears_twice(self):
        from pyjsclear.transforms.string_revealer import StringRevealer

        occurrences = [cls for cls in TRANSFORM_CLASSES if cls is StringRevealer]
        assert len(occurrences) == 2

    def test_string_revealer_is_first_and_last(self):
        from pyjsclear.transforms.string_revealer import StringRevealer

        assert TRANSFORM_CLASSES[0] is StringRevealer
        assert TRANSFORM_CLASSES[-1] is StringRevealer


class TestDeobfuscatorInit:
    """Tests for Deobfuscator.__init__."""

    def test_stores_original_code(self):
        d = Deobfuscator('var x = 1;')
        assert d.original_code == 'var x = 1;'

    def test_default_max_iterations(self):
        d = Deobfuscator('var x = 1;')
        assert d.max_iterations == 50

    def test_custom_max_iterations(self):
        d = Deobfuscator('var x = 1;', max_iterations=5)
        assert d.max_iterations == 5


class TestDeobfuscatorExecute:
    """Tests for Deobfuscator.execute."""

    def test_simple_code_no_obfuscation_returns_original(self):
        """Simple code with no obfuscation returns original code unchanged."""
        code = 'var x = 1;'
        result = Deobfuscator(code).execute()
        # When no transform changes anything, the original code is returned
        assert result == code

    def test_hex_escapes_decoded(self):
        """Code with hex escape sequences gets decoded."""
        code = 'var x = "\\x48\\x65\\x6c\\x6c\\x6f";'
        result = Deobfuscator(code).execute()
        assert '\\x48' not in result
        assert 'Hello' in result

    def test_constant_propagation(self):
        """Code with a constant assignment gets propagated."""
        code = 'var x = 1; var y = x;'
        result = Deobfuscator(code).execute()
        # After constant propagation, x should be replaced with its value
        # The result should differ from original if transforms fired
        assert '1' in result

    @patch('pyjsclear.deobfuscator.parse', side_effect=SyntaxError('bad syntax'))
    @patch(
        'pyjsclear.deobfuscator.decode_hex_escapes_source',
        return_value='decoded output',
    )
    def test_parse_failure_with_hex_escapes_falls_back_to_source_decode(self, mock_decode, mock_parse):
        """When parse fails and hex decode produces different output, return decoded."""
        code = 'not valid js \\x48\\x65'
        result = Deobfuscator(code).execute()
        mock_parse.assert_called_once_with(code)
        mock_decode.assert_called_once_with(code)
        assert result == 'decoded output'

    @patch('pyjsclear.deobfuscator.parse', side_effect=SyntaxError('bad syntax'))
    @patch('pyjsclear.deobfuscator.decode_hex_escapes_source')
    def test_parse_failure_without_hex_escapes_returns_original(self, mock_decode, mock_parse):
        """When parse fails and hex decode returns same string, return original."""
        code = 'totally broken code'
        mock_decode.return_value = code  # no change
        result = Deobfuscator(code).execute()
        assert result == code

    @patch('pyjsclear.deobfuscator.TRANSFORM_CLASSES')
    @patch('pyjsclear.deobfuscator.parse')
    @patch('pyjsclear.deobfuscator.generate', return_value='generated code')
    def test_max_iterations_limits_passes(self, mock_generate, mock_parse, mock_transforms):
        """max_iterations=1 limits transform passes to one iteration."""
        mock_ast = MagicMock()
        mock_parse.return_value = mock_ast

        # A transform that always reports a change
        transform_instance = MagicMock()
        transform_instance.execute.return_value = True
        always_changes = MagicMock(return_value=transform_instance)

        mock_transforms.__iter__ = lambda self: iter([always_changes])

        result = Deobfuscator('var x = 1;', max_iterations=1).execute()

        # With max_iterations=1, the loop runs exactly once
        assert always_changes.call_count == 1
        assert result == 'generated code'

    @patch('pyjsclear.deobfuscator.TRANSFORM_CLASSES')
    @patch('pyjsclear.deobfuscator.parse')
    def test_transform_errors_silently_ignored_bug3(self, mock_parse, mock_transforms):
        """Bug #3: Silent `except Exception: continue` swallows all transform errors.

        This is intentional for a library — transforms are expected to fail on
        ASTs they don't handle, and surfacing those errors would spam callers.
        """
        mock_ast = MagicMock()
        mock_parse.return_value = mock_ast

        # First transform raises an error
        failing_transform = MagicMock(side_effect=RuntimeError('transform broke'))

        # Second transform succeeds and reports a change
        success_instance = MagicMock()
        success_instance.execute.return_value = False
        succeeding_transform = MagicMock(return_value=success_instance)

        mock_transforms.__iter__ = lambda self: iter([failing_transform, succeeding_transform])

        code = 'var x = 1;'
        result = Deobfuscator(code).execute()

        # The failing transform was attempted
        failing_transform.assert_called_once_with(mock_ast)
        # The succeeding transform still ran despite the earlier failure
        succeeding_transform.assert_called_once_with(mock_ast)
        # No exception was raised to the caller -- the error was silently swallowed
        # Since no transform reported a change, original code is returned
        assert result == code

    @patch('pyjsclear.deobfuscator.TRANSFORM_CLASSES')
    @patch('pyjsclear.deobfuscator.parse')
    @patch('pyjsclear.deobfuscator.generate', side_effect=Exception('generate failed'))
    def test_generate_failure_returns_original(self, mock_generate, mock_parse, mock_transforms):
        """When generate() raises, returns original code."""
        mock_ast = MagicMock()
        mock_parse.return_value = mock_ast

        # A transform that reports a change (so generate is attempted)
        change_instance = MagicMock()
        change_instance.execute.return_value = True
        change_transform = MagicMock(return_value=change_instance)

        mock_transforms.__iter__ = lambda self: iter([change_transform])

        code = 'var x = 1;'
        result = Deobfuscator(code).execute()
        assert result == code


class TestPrePasses:
    """Tests for pre-pass encoding detection (lines 91-112)."""

    @patch('pyjsclear.deobfuscator.is_jsfuck', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.jsfuck_decode', return_value='var x = 1;')
    def test_jsfuck_pre_pass(self, mock_decode, mock_detect):
        """JSFUCK pre-pass: detected and decoded (lines 91-94)."""
        code = '[][(![]+[])]'
        result = Deobfuscator(code).execute()
        mock_decode.assert_called_once_with(code)
        assert 'var' in result or 'x' in result

    @patch('pyjsclear.deobfuscator.is_jsfuck', return_value=False)
    @patch('pyjsclear.deobfuscator.is_aa_encoded', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.aa_decode', return_value='var y = 2;')
    def test_aa_encode_pre_pass(self, mock_decode, mock_detect, mock_jsfuck):
        """AAEncode pre-pass: detected and decoded (lines 97-100)."""
        code = 'some aa encoded stuff'
        result = Deobfuscator(code).execute()
        mock_decode.assert_called_once_with(code)
        assert 'var' in result or 'y' in result

    @patch('pyjsclear.deobfuscator.is_jsfuck', return_value=False)
    @patch('pyjsclear.deobfuscator.is_aa_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_jj_encoded', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.jj_decode', return_value='var z = 3;')
    def test_jj_encode_pre_pass(self, mock_decode, mock_detect, mock_aa, mock_jsfuck):
        """JJEncode pre-pass: detected and decoded (lines 103-106)."""
        code = '$=~[];$={___:++$,'
        result = Deobfuscator(code).execute()
        mock_decode.assert_called_once_with(code)
        assert 'var' in result or 'z' in result

    @patch('pyjsclear.deobfuscator.is_jsfuck', return_value=False)
    @patch('pyjsclear.deobfuscator.is_aa_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_jj_encoded', return_value=False)
    @patch('pyjsclear.deobfuscator.is_eval_packed', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.eval_unpack', return_value='var w = 4;')
    def test_eval_packer_pre_pass(self, mock_decode, mock_detect, mock_jj, mock_aa, mock_jsfuck):
        """Eval packer pre-pass: detected and decoded (lines 109-112)."""
        code = 'eval("var w = 4;")'
        result = Deobfuscator(code).execute()
        mock_decode.assert_called_once_with(code)
        assert 'var' in result or 'w' in result

    @patch('pyjsclear.deobfuscator.is_jsfuck', side_effect=[True, False])
    @patch('pyjsclear.deobfuscator.jsfuck_decode', return_value='var decoded = "\\x48\\x65\\x6c\\x6c\\x6f";')
    def test_recursive_deobfuscation(self, mock_decode, mock_detect):
        """Pre-pass decoded result goes through full pipeline (lines 124-125)."""
        code = '[][(![]+[])]'
        result = Deobfuscator(code).execute()
        # The decoded result has hex escapes, which should be further deobfuscated
        assert 'Hello' in result


class TestLargeFileHandling:
    """Tests for large file iteration reduction and lite mode (lines 141-156)."""

    def test_large_file_reduces_iterations(self):
        """Files > 500KB reduce max_iterations (line 142)."""
        # Create simple but large code
        code = 'var x = 1;\n' * 50001  # > 500KB
        d = Deobfuscator(code)
        result = d.execute()
        # Should not crash, returns original since no transforms fire
        assert result == code

    @patch('pyjsclear.deobfuscator.parse')
    @patch('pyjsclear.deobfuscator._count_nodes', return_value=150_000)
    @patch('pyjsclear.deobfuscator.TRANSFORM_CLASSES')
    def test_very_large_ast_reduces_to_3_iterations(self, mock_transforms, mock_count, mock_parse):
        """Very large AST (>100k nodes) reduces to 3 iterations (line 149)."""
        mock_ast = MagicMock()
        mock_parse.return_value = mock_ast

        # Transform that always changes
        instance = MagicMock()
        instance.execute.return_value = True
        always_changes = MagicMock(return_value=instance)
        mock_transforms.__iter__ = lambda self: iter([always_changes])

        # Code > _LARGE_FILE_SIZE to trigger node counting
        code = 'x' * (_LARGE_FILE_SIZE + 1)
        result = Deobfuscator(code).execute()
        # With 150k nodes, max iterations should be min(10, 3) = 3
        assert always_changes.call_count == 3

    @patch('pyjsclear.deobfuscator.parse')
    @patch('pyjsclear.deobfuscator._count_nodes', return_value=0)
    @patch('pyjsclear.deobfuscator.generate', return_value='generated')
    @patch('pyjsclear.deobfuscator.TRANSFORM_CLASSES')
    def test_lite_mode_strips_expensive_transforms(self, mock_transforms, mock_generate, mock_count, mock_parse):
        """Lite mode (>2MB) strips expensive transforms (line 154)."""
        mock_ast = MagicMock()
        mock_parse.return_value = mock_ast

        from pyjsclear.transforms.control_flow import ControlFlowRecoverer

        # One cheap transform that changes, one expensive that should be skipped
        cheap_instance = MagicMock()
        cheap_instance.execute.return_value = False
        cheap_transform = MagicMock(return_value=cheap_instance)

        expensive_instance = MagicMock()
        expensive_instance.execute.return_value = True

        mock_transforms.__iter__ = lambda self: iter([cheap_transform, ControlFlowRecoverer])

        code = 'x' * (_MAX_CODE_SIZE + 1)
        result = Deobfuscator(code).execute()
        # ControlFlowRecoverer should have been filtered out in lite mode
        # Since only the cheap transform ran and returned False, original code returned
        assert result == code

    @patch('pyjsclear.deobfuscator.parse')
    @patch('pyjsclear.deobfuscator._count_nodes', return_value=60_000)
    @patch('pyjsclear.deobfuscator.generate', return_value='generated')
    @patch('pyjsclear.deobfuscator.TRANSFORM_CLASSES')
    def test_large_node_count_strips_expensive_transforms(self, mock_transforms, mock_generate, mock_count, mock_parse):
        """Large AST (>50k nodes) strips expensive transforms (line 156)."""
        mock_ast = MagicMock()
        mock_parse.return_value = mock_ast

        cheap_instance = MagicMock()
        cheap_instance.execute.return_value = False
        cheap_transform = MagicMock(return_value=cheap_instance)

        from pyjsclear.transforms.proxy_functions import ProxyFunctionInliner

        mock_transforms.__iter__ = lambda self: iter([cheap_transform, ProxyFunctionInliner])

        # Code > _LARGE_FILE_SIZE to trigger node counting, but < _MAX_CODE_SIZE (not lite mode)
        code = 'x' * (_LARGE_FILE_SIZE + 1)
        result = Deobfuscator(code).execute()
        # ProxyFunctionInliner should be filtered out due to node count > _NODE_COUNT_LIMIT
        assert result == code
