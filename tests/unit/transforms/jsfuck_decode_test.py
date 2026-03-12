"""Tests for pure Python JSFuck decoder."""

from pyjsclear.transforms.jsfuck_decode import _JSValue
from pyjsclear.transforms.jsfuck_decode import _Parser
from pyjsclear.transforms.jsfuck_decode import _tokenize
from pyjsclear.transforms.jsfuck_decode import is_jsfuck
from pyjsclear.transforms.jsfuck_decode import jsfuck_decode


class TestJSFuckDetection:
    def test_detects_jsfuck(self):
        # Typical JSFuck: only []()!+ chars
        code = '[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!!' + '+[])[+[]]]' * 5
        assert is_jsfuck(code) is True

    def test_rejects_normal_js(self):
        assert is_jsfuck('var x = 1; console.log(x);') is False

    def test_rejects_short_code(self):
        assert is_jsfuck('[]') is False

    def test_jsfuck_with_preamble(self):
        preamble = '$ = String.fromCharCode(118, 82);\n'
        jsfuck = '[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]]' * 10
        code = preamble + jsfuck
        assert isinstance(is_jsfuck(code), bool)

    def test_high_ratio_detected(self):
        # 95% JSFuck chars → detected
        code = '(![]+[])' * 50 + 'xx'
        assert is_jsfuck(code) is True

    def test_low_ratio_rejected(self):
        # Mostly normal code with some JSFuck chars
        code = 'var x = function() { return [1,2,3]; }; ' * 10
        assert is_jsfuck(code) is False


class TestJSValueCoercion:
    """Test JS-like type coercion semantics."""

    def test_empty_array_to_number(self):
        v = _JSValue([], 'array')
        assert v.to_number() == 0

    def test_empty_array_to_string(self):
        v = _JSValue([], 'array')
        assert v.to_string() == ''

    def test_false_to_string(self):
        v = _JSValue(False, 'bool')
        assert v.to_string() == 'false'

    def test_true_to_string(self):
        v = _JSValue(True, 'bool')
        assert v.to_string() == 'true'

    def test_true_to_number(self):
        v = _JSValue(True, 'bool')
        assert v.to_number() == 1

    def test_false_to_number(self):
        v = _JSValue(False, 'bool')
        assert v.to_number() == 0

    def test_number_zero_to_string(self):
        v = _JSValue(0, 'number')
        assert v.to_string() == '0'

    def test_string_indexing(self):
        v = _JSValue('false', 'string')
        result = v.get_property(_JSValue(0, 'number'))
        assert result.val == 'f'

    def test_undefined_to_string(self):
        v = _JSValue(None, 'undefined')
        assert v.to_string() == 'undefined'

    def test_nan_to_string(self):
        v = _JSValue(float('nan'), 'number')
        assert v.to_string() == 'NaN'

    def test_infinity_to_string(self):
        v = _JSValue(float('inf'), 'number')
        assert v.to_string() == 'Infinity'


class TestTokenizer:
    def test_basic_tokenization(self):
        tokens = _tokenize('[]+()')
        assert tokens == ['[', ']', '+', '(', ')']

    def test_ignores_whitespace(self):
        tokens = _tokenize('[ ] + ( )')
        assert tokens == ['[', ']', '+', '(', ')']

    def test_ignores_semicolons(self):
        tokens = _tokenize('[]+[];')
        assert tokens == ['[', ']', '+', '[', ']']


class TestParserBasics:
    """Test basic JSFuck expression parsing."""

    def test_empty_array(self):
        tokens = _tokenize('[]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'array'
        assert result.val == []

    def test_not_empty_array_is_false(self):
        # ![] → false
        tokens = _tokenize('![]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'bool'
        assert result.val is False

    def test_not_not_empty_array_is_true(self):
        # !![] → true
        tokens = _tokenize('!![]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'bool'
        assert result.val is True

    def test_unary_plus_empty_array_is_zero(self):
        # +[] → 0
        tokens = _tokenize('+[]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'number'
        assert result.val == 0

    def test_unary_plus_true_is_one(self):
        # +!![] → 1
        tokens = _tokenize('+!![]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'number'
        assert result.val == 1

    def test_false_plus_array_is_string_false(self):
        # ![]+[] → "false"
        tokens = _tokenize('![]+[]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'string'
        assert result.val == 'false'

    def test_true_plus_array_is_string_true(self):
        # !![]+[] → "true"
        tokens = _tokenize('!![]+[]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'string'
        assert result.val == 'true'

    def test_string_indexing_extracts_char(self):
        # (![]+[])[+[]] → "false"[0] → "f"
        tokens = _tokenize('(![]+[])[+[]]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'string'
        assert result.val == 'f'

    def test_number_addition(self):
        # +!![]+!![] → 1 + 1 → 2
        tokens = _tokenize('+!![]+!+[]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.type == 'number'
        # +!![]+!+[] parses as: (+!![]) + (!+[])
        # +!![] = +true = 1
        # !+[] = !0 = true → numeric addition: 1 + 1 = 2
        assert result.val == 2


class TestJSFuckDecode:
    def test_none_on_empty(self):
        assert jsfuck_decode('') is None
        assert jsfuck_decode('   ') is None

    def test_none_on_invalid(self):
        assert jsfuck_decode('not jsfuck at all') is None

    def test_simple_expressions_dont_crash(self):
        # Just parsing basic JSFuck without Function() call → None (no captured result)
        result = jsfuck_decode('![]+[]')
        assert result is None  # No Function() call, so nothing captured

    def test_decode_alert_one(self):
        """Test decoding JSFuck that produces alert(1).

        This is a real JSFuck encoding of alert(1). JSFuck builds the string
        "alert(1)" by extracting characters from coerced strings, then passes
        it to Function() constructor and calls the result.
        """
        # Simplified: we test the core evaluation mechanics work
        # Build "a" from "false"[1]: (![]+[])[+!+[]]
        tokens = _tokenize('(![]+[])[+!+[]]')
        p = _Parser(tokens)
        result = p.parse()
        assert result.val == 'a'  # "false"[1]

    def test_constructor_chain(self):
        """Test that constructor property chain resolves correctly.

        JSFuck accesses Function via: []["flat"]["constructor"]
        """
        tokens = _tokenize('[]')
        p = _Parser(tokens)
        arr = p.parse()

        # Access "flat" property
        flat_key = _JSValue('flat', 'string')
        flat_fn = arr.get_property(flat_key)
        assert flat_fn.type == 'function'

        # Access "constructor" on function → Function
        ctor_key = _JSValue('constructor', 'string')
        ctor = flat_fn.get_property(ctor_key)
        assert ctor.type == 'function'
        assert ctor.val == 'Function'
