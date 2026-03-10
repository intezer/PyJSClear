"""Tests for eval/packer unpacker."""

import subprocess
from unittest.mock import MagicMock
from unittest.mock import patch

from pyjsclear.transforms.eval_unpack import _dean_edwards_unpack
from pyjsclear.transforms.eval_unpack import _try_node_eval
from pyjsclear.transforms.eval_unpack import eval_unpack
from pyjsclear.transforms.eval_unpack import is_eval_packed


PACKER_SAMPLE = (
    "eval(function (p, a, c, k, e, d) {"
    "    e = function (c) {"
    "        return (c < a ? '' : e(parseInt(c / a))) + "
    "((c = c % a) > 35 ? String.fromCharCode(c + 29) : c.toString(36));"
    "    };"
    "    if (!''.replace(/^/, String)) {"
    "        while (c--)"
    "            d[e(c)] = k[c] || e(c);"
    "        k = [function (e) {"
    "                return d[e];"
    "            }];"
    "        e = function () {"
    "            return '\\\\w+';"
    "        };"
    "        c = 1;"
    "    }"
    "    ;"
    "    while (c--)"
    "        if (k[c])"
    "            p = p.replace(new RegExp('\\\\b' + e(c) + '\\\\b', 'g'), k[c]);"
    "    return p;"
    "}('4 0(){    7   \"8 5 1 3\";}9 6 =0();2(6);', 62, 10,"
    " 'GetParams|a|alert|example|function|is|params|return|this|var'.split('|'), 0, {}));"
)


class TestEvalDetection:
    def test_detects_packer(self):
        assert is_eval_packed(PACKER_SAMPLE) is True

    def test_detects_generic_eval(self):
        assert is_eval_packed('eval("alert(1)")') is True

    def test_rejects_normal_js(self):
        assert is_eval_packed('var x = 1;') is False


class TestDeanEdwardsUnpack:
    def test_basic_unpack(self):
        packed = '4 0(){    7   "8 5 1 3";}9 6 =0();2(6);'
        keywords = 'GetParams|a|alert|example|function|is|params|return|this|var'.split('|')
        result = _dean_edwards_unpack(packed, 62, 10, keywords)
        assert 'function' in result
        assert 'GetParams' in result
        assert 'alert' in result
        assert 'return' in result

    def test_unpack_preserves_structure(self):
        packed = '0("1")'
        keywords = ['alert', 'hello']
        result = _dean_edwards_unpack(packed, 62, 2, keywords)
        assert result == 'alert("hello")'


class TestBaseEncodeHighRadix:
    def test_base_encode_c_greater_than_35(self):
        """base_encode for c > 35 uses chr(c + 29) (line 47)."""
        # Radix 62: keyword index 36 should produce chr(36+29)=chr(65)='A'
        packed = 'A'
        keywords = [''] * 36 + ['replaced']
        result = _dean_edwards_unpack(packed, 62, 37, keywords)
        assert result == 'replaced'

    def test_base_encode_c_equals_36(self):
        """base_encode for c=36 produces 'A' which maps via chr(36+29)."""
        packed = 'A("hello")'
        keywords = [''] * 36 + ['myFunc']
        result = _dean_edwards_unpack(packed, 62, 37, keywords)
        assert 'myFunc' in result


class TestDeanEdwardsException:
    def test_exception_in_dean_edwards_falls_through(self):
        """Exception in Dean Edwards unpacking continues to next pattern (lines 92-94)."""
        # Craft code that matches _PACKER_RE but will cause an error in _dean_edwards_unpack
        code = "eval(function(p,a,c,k,e,d){" "return p" "}('0', 0, 0, ''.split('|'), 0, {}))"
        # This should not raise; it should return None or fall through
        result = eval_unpack(code)
        # Either returns None or falls through to _try_node_eval
        assert result is None or isinstance(result, str)


class TestEvalUnpack:
    def test_unpack_packer(self):
        result = eval_unpack(PACKER_SAMPLE)
        assert result is not None
        assert 'GetParams' in result
        assert 'alert' in result

    @patch('pyjsclear.transforms.eval_unpack._try_dean_edwards', return_value=None)
    @patch('pyjsclear.transforms.eval_unpack._try_node_eval', return_value='decoded_code')
    def test_falls_through_to_node_eval(self, mock_node, mock_dean):
        """eval_unpack falls through to _try_node_eval when Dean Edwards fails (line 73)."""
        result = eval_unpack('eval("alert(1)")')
        assert result == 'decoded_code'
        mock_node.assert_called_once()


class TestTryNodeEval:
    def test_no_eval_pattern_returns_none(self):
        """No eval pattern returns None (line 100-101)."""
        result = _try_node_eval('var x = 1;')
        assert result is None

    @patch('pyjsclear.transforms.eval_unpack.shutil.which', return_value=None)
    def test_no_node_returns_none(self, mock_which):
        """No node returns None (lines 103-105)."""
        result = _try_node_eval('eval("alert(1)")')
        assert result is None

    @patch('pyjsclear.transforms.eval_unpack.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.eval_unpack.subprocess.run')
    def test_successful_node_eval(self, mock_run, mock_which):
        """Successful mock subprocess returns decoded output (lines 117-129)."""
        mock_result = MagicMock()
        mock_result.stdout = 'alert(1)\n'
        mock_run.return_value = mock_result
        result = _try_node_eval('eval("alert(1)")')
        assert result == 'alert(1)'

    @patch('pyjsclear.transforms.eval_unpack.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.eval_unpack.subprocess.run')
    def test_empty_output_returns_none(self, mock_run, mock_which):
        """Empty output returns None (line 129)."""
        mock_result = MagicMock()
        mock_result.stdout = '  '
        mock_run.return_value = mock_result
        result = _try_node_eval('eval("alert(1)")')
        assert result is None

    @patch('pyjsclear.transforms.eval_unpack.shutil.which', return_value='/usr/bin/node')
    @patch('pyjsclear.transforms.eval_unpack.subprocess.run', side_effect=subprocess.TimeoutExpired('node', 5))
    def test_timeout_returns_none(self, mock_run, mock_which):
        """Timeout returns None (lines 132-133)."""
        result = _try_node_eval('eval("alert(1)")')
        assert result is None
