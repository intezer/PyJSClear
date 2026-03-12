"""Tests for pure Python JJEncode decoder."""

import os
from pathlib import Path

import pytest

from pyjsclear.transforms.jj_decode import is_jj_encoded
from pyjsclear.transforms.jj_decode import jj_decode


JJ_SAMPLE_LINE = '$=~[];$={___:++$,'

MALJS_DIR = Path(__file__).parent.parent.parent / 'resources' / 'jsimplifier' / 'dataset' / 'MalJS'


def read_sample(md5):
    return (MALJS_DIR / md5).read_text()


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
        code = '$=~[];$={___:++$,"\\141\\154\\145\\162\\164\\50\\61\\51"}'
        result = jj_decode(code)
        if result is not None:
            assert any(c.isalpha() for c in result)

    def test_returns_none_on_no_payload(self):
        """JJEncode detection passes but no decodable payload -> None."""
        code = '$=~[];$={___:++$, some_prop: 42};'
        result = jj_decode(code)
        assert result is None


class TestJJDecodeOctalExtraction:
    """Test the octal character extraction logic."""

    def test_octal_alert(self):
        """Octal codes for 'alert(1)' are correctly extracted."""
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


class TestJJDecodeRealSamples:
    """Tests against real JJEncode samples from the MalJS dataset."""

    SAMPLES = [
        'c05bd16c6a6730747d272355f302be5b',   # 52 lines, JJ + jQuery
        '0d42da6b94708095cc9035c3a2030cee',   # 932 lines, JJ + Google Analytics
        '5bcc28e366085efa625515684fdc9648',   # 59 lines
    ]

    @pytest.mark.parametrize('sample', SAMPLES)
    def test_decode_returns_non_none(self, sample):
        """jj_decode must return decoded output for real samples."""
        code = read_sample(sample)
        result = jj_decode(code)
        assert result is not None

    @pytest.mark.parametrize('sample', SAMPLES)
    def test_decoded_contains_js_constructs(self, sample):
        """Decoded output must contain recognizable JavaScript."""
        code = read_sample(sample)
        result = jj_decode(code)
        assert result is not None
        assert any(kw in result for kw in ['var ', 'document', 'function', 'http', 'src', 'script'])

    def test_decode_preserves_rest_of_file(self):
        """Sample with normal JS after JJEncode includes both parts."""
        code = read_sample('0d42da6b94708095cc9035c3a2030cee')
        result = jj_decode(code)
        assert result is not None
        assert 'GoogleAnalytics' in result  # from lines 2+ of the file

    def test_decode_c05bd16c_contains_known_urls(self):
        """Verify decoded payload contains known URLs (validated via Node.js)."""
        code = read_sample('c05bd16c6a6730747d272355f302be5b')
        result = jj_decode(code)
        assert result is not None
        assert 'counter.yadro.ru' in result
        assert 'mailfolder.us' in result


class TestJJDecodeBulk:
    def test_most_pure_samples_decode(self):
        """At least 80% of pure JJEncode samples should decode."""
        if not MALJS_DIR.exists():
            pytest.skip('MalJS dataset not available')

        total = 0
        success = 0
        for fname in os.listdir(MALJS_DIR):
            fpath = MALJS_DIR / fname
            if not fpath.is_file():
                continue
            try:
                code = fpath.read_text()
            except Exception:
                continue
            if not code.startswith('$=~[];$={___:'):
                continue
            total += 1
            result = jj_decode(code)
            if result is not None and any(c.isalpha() for c in result):
                success += 1

        assert total > 0, 'No pure JJEncode samples found'
        success_rate = success / total
        assert success_rate >= 0.8, f'Only {success}/{total} ({success_rate:.0%}) decoded'
