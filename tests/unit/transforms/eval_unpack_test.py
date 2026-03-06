"""Tests for eval/packer unpacker."""

from pyjsclear.transforms.eval_unpack import _dean_edwards_unpack
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


class TestEvalUnpack:
    def test_unpack_packer(self):
        result = eval_unpack(PACKER_SAMPLE)
        assert result is not None
        assert 'GetParams' in result
        assert 'alert' in result
