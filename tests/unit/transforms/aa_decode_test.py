"""Unit tests for the AAEncode decoder."""

import pytest

from pyjsclear.transforms.aa_decode import is_aa_encoded
from pyjsclear.transforms.aa_decode import aa_decode


class TestIsAAEncoded:
    """Detection tests."""

    def test_positive(self):
        code = 'ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ (ﾟДﾟ)[ﾟεﾟ]+something'
        assert is_aa_encoded(code) is True

    def test_negative_plain_js(self):
        assert is_aa_encoded('var x = 1;') is False

    def test_negative_empty(self):
        assert is_aa_encoded('') is False

    def test_negative_none(self):
        assert is_aa_encoded(None) is False

    def test_negative_jsfuck(self):
        assert is_aa_encoded('[][(![]+[])]') is False


class TestAADecode:
    """Decoding tests."""

    def test_empty_returns_none(self):
        assert aa_decode('') is None

    def test_plain_js_returns_none(self):
        assert aa_decode('var x = 1;') is None

    def test_none_returns_none(self):
        assert aa_decode(None) is None

    def test_synthetic_simple(self):
        """Synthetic AAEncode for 'Hi' (H=110 octal, i=151 octal).

        This builds a minimal AAEncoded payload that the decoder can parse.
        Note: real AAEncode uses U+FF70 (\uff70 halfwidth), NOT U+30FC (fullwidth).
        """
        # H = 0x48 = 110 octal, i = 0x69 = 151 octal
        # Digit 1 = (\uff9f\uff70\uff9f), Digit 0 = (c^_^o),
        # Digit 5 = ((\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))
        sep = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+'
        h_digits = '(\uff9f\uff70\uff9f)+(\uff9f\uff70\uff9f)+(c^_^o)'  # 1 1 0
        i_digits = (
            '(\uff9f\uff70\uff9f)+'
            '((\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))+'
            '(\uff9f\uff70\uff9f)'
        )  # 1 5 1

        data = sep + h_digits + sep + i_digits
        # Add execution wrapper with the signature
        code = data + "(\uff9f\u0414\uff9f)['_'](\uff9f\u0398\uff9f)"

        result = aa_decode(code)
        assert result is not None
        assert result == 'Hi'
