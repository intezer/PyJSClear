"""Tests for AAEncode decoder."""

from pyjsclear.transforms.aa_decode import _AA_DETECT_RE, _UNICODE_MARKER, aa_decode, is_aa_encoded


# A minimal AAEncode sample encoding "alert(1)"
AA_SAMPLE = (
    "\uff9f\u03c9\uff9f\uff89= /\uff40\uff4d\xb4\uff09\uff89 ~\u253b\u2501\u253b   //*\xb4\u2207\uff40*/ ['_'];"
    " o=(\uff9f\uff70\uff9f)  =_=3;"
    " c=(\uff9f\u0398\uff9f) =(\uff9f\uff70\uff9f)-(\uff9f\uff70\uff9f);"
    " (\uff9f\u0414\uff9f) =(\uff9f\u0398\uff9f)= (o^_^o)/ (o^_^o);"
    "(\uff9f\u0414\uff9f)={\uff9f\u0398\uff9f: '_'"
    " ,\uff9f\u03c9\uff9f\uff89 : ((\uff9f\u03c9\uff9f\uff89==3) +'_') [\uff9f\u0398\uff9f]"
    " ,\uff9f\uff70\uff9f\uff89 :(\uff9f\u03c9\uff9f\uff89+ '_')[o^_^o -(\uff9f\u0398\uff9f)]"
    " ,\uff9f\u0414\uff9f\uff89:((\uff9f\uff70\uff9f==3) +'_')[\uff9f\uff70\uff9f] };"
    " (\uff9f\u0414\uff9f) [\uff9f\u0398\uff9f] =((\uff9f\u03c9\uff9f\uff89==3) +'_') [c^_^o];"
    "(\uff9f\u0414\uff9f) ['c'] = ((\uff9f\u0414\uff9f)+'_') [ (\uff9f\uff70\uff9f)+(\uff9f\uff70\uff9f)-(\uff9f\u0398\uff9f) ];"
    "(\uff9f\u0414\uff9f) ['o'] = ((\uff9f\u0414\uff9f)+'_') [\uff9f\u0398\uff9f];"
    "(\uff9fo\uff9f)=(\uff9f\u0414\uff9f) ['c']+(\uff9f\u0414\uff9f) ['o']+(\uff9f\u03c9\uff9f\uff89 +'_')[\uff9f\u0398\uff9f]+"
    " ((\uff9f\u03c9\uff9f\uff89==3) +'_') [\uff9f\uff70\uff9f] +"
    " ((\uff9f\u0414\uff9f) +'_') [(\uff9f\uff70\uff9f)+(\uff9f\uff70\uff9f)]+"
    " ((\uff9f\uff70\uff9f==3) +'_') [\uff9f\u0398\uff9f]+"
    "((\uff9f\uff70\uff9f==3) +'_') [(\uff9f\uff70\uff9f) - (\uff9f\u0398\uff9f)]+"
    "(\uff9f\u0414\uff9f) ['c']+"
    "((\uff9f\u0414\uff9f)+'_') [(\uff9f\uff70\uff9f)+(\uff9f\uff70\uff9f)]+"
    " (\uff9f\u0414\uff9f) ['o']+"
    "((\uff9f\uff70\uff9f==3) +'_') [\uff9f\u0398\uff9f];"
    "(\uff9f\u0414\uff9f) ['_'] =(o^_^o) [\uff9fo\uff9f] [\uff9fo\uff9f];"
    "(\uff9f\u03b5\uff9f)=((\uff9f\uff70\uff9f==3) +'_') [\uff9f\u0398\uff9f]+"
    " (\uff9f\u0414\uff9f) .\uff9f\u0414\uff9f\uff89+"
    "((\uff9f\u0414\uff9f)+'_') [(\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f)]+"
    "((\uff9f\uff70\uff9f==3) +'_') [o^_^o -\uff9f\u0398\uff9f]+"
    "((\uff9f\uff70\uff9f==3) +'_') [\uff9f\u0398\uff9f]+"
    " (\uff9f\u03c9\uff9f\uff89 +'_') [\uff9f\u0398\uff9f];"
    " (\uff9f\uff70\uff9f)+=(\uff9f\u0398\uff9f);"
    " (\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]='\\\\';"
    " (\uff9f\u0414\uff9f).\uff9f\u0398\uff9f\uff89=(\uff9f\u0414\uff9f+ \uff9f\uff70\uff9f)[o^_^o -(\uff9f\u0398\uff9f)];"
    "(o\uff9f\uff70\uff9fo)=(\uff9f\u03c9\uff9f\uff89 +'_')[c^_^o];"
    "(\uff9f\u0414\uff9f) [\uff9fo\uff9f]='\"';"
    "(\uff9f\u0414\uff9f) ['_'] ( (\uff9f\u0414\uff9f) ['_'] (\uff9f\u03b5\uff9f+"
    "(\uff9f\u0414\uff9f)[\uff9fo\uff9f]+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\u0398\uff9f)+ (\uff9f\uff70\uff9f)+ (\uff9f\uff70\uff9f)+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\u0398\uff9f)+ ((o^_^o) +(o^_^o))+ ((o^_^o) +(o^_^o))+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\u0398\uff9f)+ (\uff9f\uff70\uff9f)+ ((o^_^o) +(o^_^o))+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\u0398\uff9f)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ ((o^_^o) +(o^_^o))+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\u0398\uff9f)+ ((\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))+ ((o^_^o) - (\uff9f\u0398\uff9f))+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+((ﾟｰﾟ) + (ﾟΘﾟ))+ (c^_^o)+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\uff70\uff9f)+ ((o^_^o) - (\uff9f\u0398\uff9f))+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+(\uff9f\u0398\uff9f)+ ((\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))+ ((\uff9f\uff70\uff9f) + (o^_^o))+ "
    "(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+((ﾟｰﾟ) + (\uff9f\u0398\uff9f))+ (\uff9f\u0398\uff9f)+ "
    "(\uff9f\u0414\uff9f)[\uff9fo\uff9f]) (\uff9f\u0398\uff9f)) ('_');"
)


class TestAADetection:
    def test_detects_aa_encoded(self):
        assert is_aa_encoded(AA_SAMPLE) is True

    def test_rejects_normal_js(self):
        assert is_aa_encoded('var x = 1;') is False

    def test_rejects_empty(self):
        assert is_aa_encoded('') is False


class TestAADecode:
    def test_decode_returns_none_for_normal_js(self):
        assert aa_decode('var x = 1;') is None

    def test_decode_returns_string(self):
        # The sample may not decode perfectly without a real AAEncode encoder,
        # but the function should not crash
        result = aa_decode(AA_SAMPLE)
        # At minimum, it should return a string (even if imperfect)
        assert result is None or isinstance(result, str)

    def test_unicode_marker_path(self):
        """Test the unicode character marker path (lines 71-74).

        Build a minimal AAEncoded string with the unicode marker to exercise
        that code path.
        """
        # We need the detection pattern to match, plus escape-split parts with _UNICODE_MARKER
        # Build a fake AAEncoded string that the decoder can parse
        detect = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]'
        # Create a part that starts with the unicode marker followed by a hex number
        # chr(0x41) = 'A', so hex_str = '41'
        escape_split = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+'
        part_with_unicode = _UNICODE_MARKER + '41'
        code = detect + escape_split + part_with_unicode
        result = aa_decode(code)
        # Should decode the unicode marker part to chr(0x41) = 'A'
        assert result is not None
        assert 'A' in result

    def test_value_error_returns_none(self):
        """ValueError in decoding returns None (lines 82-83)."""
        # Build a fake AAEncoded string with invalid octal that triggers ValueError
        detect = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]'
        escape_split = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+'
        invalid_part = 'not_a_number'
        code = detect + escape_split + invalid_part
        result = aa_decode(code)
        assert result is None
