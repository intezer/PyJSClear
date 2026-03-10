"""Tests for JJEncode decoder."""

import subprocess
from unittest.mock import MagicMock
from unittest.mock import patch

from pyjsclear.transforms.jj_decode import _run_with_function_intercept
from pyjsclear.transforms.jj_decode import is_jj_encoded
from pyjsclear.transforms.jj_decode import jj_decode
from pyjsclear.transforms.jj_decode import jj_decode_via_eval


JJ_SAMPLE_LINE = '$=~[];$={___:++$,'


class TestJJDetection:
    def test_detects_jj_encoded(self):
        assert is_jj_encoded(JJ_SAMPLE_LINE) is True

    def test_detects_variant(self):
        assert is_jj_encoded('$$={___:++$,') is True

    def test_rejects_normal_js(self):
        assert is_jj_encoded('var x = 1;') is False

    def test_rejects_empty(self):
        assert is_jj_encoded('') is False


class TestJJDecode:
    def test_non_jj_code_returns_none(self):
        """jj_decode() with non-JJ code returns None (lines 32-33)."""
        result = jj_decode('var x = 1;')
        assert result is None

    @patch('pyjsclear.transforms.jj_decode.shutil.which', return_value=None)
    def test_jj_code_no_node_returns_none(self, mock_which):
        """jj_decode() with JJ code but no Node.js returns None (line 34)."""
        jj_code = '$=~[];$={___:++$, alert(1)}'
        result = jj_decode(jj_code)
        assert result is None

    @patch('pyjsclear.transforms.jj_decode._run_with_function_intercept', return_value='alert(1)')
    def test_jj_decode_via_eval_delegates(self, mock_run):
        """jj_decode_via_eval() calls _run_with_function_intercept (line 39)."""
        result = jj_decode_via_eval('some code')
        mock_run.assert_called_once_with('some code')
        assert result == 'alert(1)'


class TestRunWithFunctionIntercept:
    @patch('pyjsclear.transforms.jj_decode.shutil.which', return_value=None)
    def test_no_node_returns_none(self, mock_which):
        """When node is not found, returns None (lines 44-46)."""
        result = _run_with_function_intercept('some code')
        assert result is None

    @patch('pyjsclear.transforms.jj_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jj_decode.subprocess.run')
    def test_successful_execution(self, mock_run, mock_which):
        """Successful execution returns stdout (lines 75-87)."""
        mock_result = MagicMock()
        mock_result.stdout = 'alert(1)\n'
        mock_run.return_value = mock_result
        result = _run_with_function_intercept('$=~[];')
        assert result == 'alert(1)'
        mock_run.assert_called_once()

    @patch('pyjsclear.transforms.jj_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jj_decode.subprocess.run')
    def test_empty_output_returns_none(self, mock_run, mock_which):
        """Empty stdout returns None (line 87)."""
        mock_result = MagicMock()
        mock_result.stdout = '   '
        mock_run.return_value = mock_result
        result = _run_with_function_intercept('$=~[];')
        assert result is None

    @patch('pyjsclear.transforms.jj_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jj_decode.subprocess.run', side_effect=subprocess.TimeoutExpired('node', 5))
    def test_timeout_returns_none(self, mock_run, mock_which):
        """Timeout returns None (line 90-91)."""
        result = _run_with_function_intercept('$=~[];')
        assert result is None

    @patch('pyjsclear.transforms.jj_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jj_decode.subprocess.run', side_effect=OSError('error'))
    def test_os_error_returns_none(self, mock_run, mock_which):
        """OSError returns None (line 90-91)."""
        result = _run_with_function_intercept('$=~[];')
        assert result is None
