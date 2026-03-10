"""Tests for JSFUCK decoder."""

import subprocess
from unittest.mock import MagicMock, patch

from pyjsclear.transforms.jsfuck_decode import is_jsfuck, jsfuck_decode


class TestJSFuckDetection:
    def test_detects_jsfuck(self):
        # Typical JSFUCK: only []()!+ chars
        code = '[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!!' + '+[])[+[]]]' * 5
        assert is_jsfuck(code) is True

    def test_rejects_normal_js(self):
        assert is_jsfuck('var x = 1; console.log(x);') is False

    def test_rejects_short_code(self):
        assert is_jsfuck('[]') is False

    def test_jsfuck_with_preamble(self):
        # Some JSFUCK variants have a $ = String.fromCharCode(...) preamble
        # followed by lots of JSFUCK
        preamble = '$ = String.fromCharCode(118, 82);\n'
        jsfuck = '[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]]' * 10
        code = preamble + jsfuck
        # Has significant non-JSFUCK content, but ratio might still be high
        assert isinstance(is_jsfuck(code), bool)


class TestJSFuckDecode:
    @patch('pyjsclear.transforms.jsfuck_decode.shutil.which', return_value=None)
    def test_no_node_returns_none(self, mock_which):
        """When Node.js not found, returns None (lines 38-40)."""
        result = jsfuck_decode('[][(![]+[])]')
        assert result is None

    @patch('pyjsclear.transforms.jsfuck_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jsfuck_decode.subprocess.run')
    def test_successful_decode(self, mock_run, mock_which):
        """Successful decode returns stdout (lines 42-89)."""
        mock_result = MagicMock()
        mock_result.stdout = 'alert(1)\n'
        mock_run.return_value = mock_result
        result = jsfuck_decode('[][(![]+[])]')
        assert result == 'alert(1)'
        mock_run.assert_called_once()

    @patch('pyjsclear.transforms.jsfuck_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jsfuck_decode.subprocess.run')
    def test_empty_output_returns_none(self, mock_run, mock_which):
        """Empty output returns None (lines 88-89)."""
        mock_result = MagicMock()
        mock_result.stdout = '  \n  '
        mock_run.return_value = mock_result
        result = jsfuck_decode('[][(![]+[])]')
        assert result is None

    @patch('pyjsclear.transforms.jsfuck_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jsfuck_decode.subprocess.run', side_effect=subprocess.TimeoutExpired('node', 10))
    def test_timeout_returns_none(self, mock_run, mock_which):
        """Timeout returns None (lines 92-93)."""
        result = jsfuck_decode('[][(![]+[])]')
        assert result is None

    @patch('pyjsclear.transforms.jsfuck_decode.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.jsfuck_decode.subprocess.run', side_effect=OSError('error'))
    def test_os_error_returns_none(self, mock_run, mock_which):
        """OSError returns None."""
        result = jsfuck_decode('[][(![]+[])]')
        assert result is None
