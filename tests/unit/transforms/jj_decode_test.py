"""Tests for JJEncode decoder."""

from pyjsclear.transforms.jj_decode import is_jj_encoded


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
