"""Unit tests for the JJEncode decoder."""

import os

import pytest

from pyjsclear.transforms.jj_decode import is_jj_encoded
from pyjsclear.transforms.jj_decode import jj_decode


# Path to real JJEncode samples
_MALJS_DIR = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    'resources',
    'jsimplifier',
    'dataset',
    'MalJS',
)


class TestIsJJEncoded:
    """Detection tests."""

    def test_positive_dollar_sign(self):
        assert is_jj_encoded('$=~[];$={___:++$};') is True

    def test_positive_custom_varname(self):
        assert is_jj_encoded('myVar=~[];myVar={___:++myVar};') is True

    def test_negative_plain_js(self):
        assert is_jj_encoded('var x = 1;') is False

    def test_negative_empty(self):
        assert is_jj_encoded('') is False

    def test_negative_none_like(self):
        assert is_jj_encoded('   ') is False

    def test_negative_jsfuck(self):
        assert is_jj_encoded('[][(![]+[])]') is False


class TestJJDecode:
    """Decoding tests."""

    def test_empty_returns_none(self):
        assert jj_decode('') is None

    def test_plain_js_returns_none(self):
        assert jj_decode('var x = 1;') is None

    def test_none_input_returns_none(self):
        assert jj_decode(None) is None

    def test_real_sample_7b6c(self):
        """Decode the JJEncode line from the 7b6c... sample."""
        sample_path = os.path.join(_MALJS_DIR, '7b6c66c42548b964c11cbaf37e9be12d')
        if not os.path.isfile(sample_path):
            pytest.skip('Sample file not available')

        with open(sample_path) as f:
            lines = f.readlines()

        jj_line = lines[23]  # line 24 (0-indexed: 23)
        result = jj_decode(jj_line)
        assert result is not None
        # The decoded output should contain document.write
        assert 'document.write' in result or 'document.writeln' in result

    def test_real_sample_7b6c_contains_script_tag(self):
        """Decoded output should contain a script tag reference."""
        sample_path = os.path.join(_MALJS_DIR, '7b6c66c42548b964c11cbaf37e9be12d')
        if not os.path.isfile(sample_path):
            pytest.skip('Sample file not available')

        with open(sample_path) as f:
            lines = f.readlines()

        jj_line = lines[23]
        result = jj_decode(jj_line)
        assert result is not None
        assert '<script' in result.lower() or 'script' in result.lower()
