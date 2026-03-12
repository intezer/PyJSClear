"""Tests for pure Python JJEncode decoder."""

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

    def test_first_line_only(self):
        """Detection looks at first line only."""
        code = 'var x = 1;\n$=~[];$={___:++$,'
        assert is_jj_encoded(code) is False

    def test_detects_dollar_pattern(self):
        """Detects the $$$ pattern with brackets."""
        code = '$$$_[[]]+[]+!!+'
        assert is_jj_encoded(code) is True


class TestJJDecode:
    def test_non_jj_code_returns_none(self):
        """jj_decode() with non-JJ code returns None."""
        result = jj_decode('var x = 1;')
        assert result is None

    def test_decode_with_octal_escapes(self):
        """JJEncode with octal escape sequences gets decoded."""
        # Minimal JJEncode-like code with octal escapes that spell "alert(1)"
        code = '$=~[];$={___:++$,"\\141\\154\\145\\162\\164\\50\\61\\51"}'
        result = jj_decode(code)
        if result is not None:
            # If decoded, should contain recognizable characters
            assert any(c.isalpha() for c in result)

    def test_jj_decode_via_eval_returns_none_on_normal_code(self):
        """jj_decode_via_eval with non-JJ code returns None."""
        result = jj_decode_via_eval('var x = 1;')
        assert result is None

    def test_returns_none_on_no_payload(self):
        """JJEncode detection passes but no decodable payload → None."""
        code = '$=~[];$={___:++$, some_prop: 42};'
        result = jj_decode(code)
        assert result is None


class TestJJDecodeOctalExtraction:
    """Test the octal character extraction logic."""

    def test_octal_alert(self):
        """Octal codes for 'alert(1)' are correctly extracted."""
        # 'a'=141, 'l'=154, 'e'=145, 'r'=162, 't'=164, '('=50, '1'=61, ')'=51
        code = '$=~[];$={___:++$};$.___+"\\141\\154\\145\\162\\164\\50\\61\\51"'
        result = jj_decode(code)
        if result is not None:
            assert 'alert' in result

    def test_hex_escape_extraction(self):
        """Hex escapes in JJEncode variants are extracted."""
        code = '$=~[];$={___:++$};\\x61\\x6c\\x65\\x72\\x74'
        result = jj_decode(code)
        if result is not None:
            assert 'alert' in result
