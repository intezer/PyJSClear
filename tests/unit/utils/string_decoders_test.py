"""Comprehensive tests for pyjsclear.utils.string_decoders."""

import pytest

from pyjsclear.utils.string_decoders import (
    Base64StringDecoder,
    BasicStringDecoder,
    DecoderType,
    Rc4StringDecoder,
    StringDecoder,
    base64_transform,
)


# ---------------------------------------------------------------------------
# DecoderType enum
# ---------------------------------------------------------------------------

class TestDecoderType:
    def test_basic_value(self):
        assert DecoderType.BASIC.value == 'basic'

    def test_base64_value(self):
        assert DecoderType.BASE_64.value == 'base64'

    def test_rc4_value(self):
        assert DecoderType.RC4.value == 'rc4'

    def test_enum_members(self):
        assert set(DecoderType) == {DecoderType.BASIC, DecoderType.BASE_64, DecoderType.RC4}

    def test_lookup_by_value(self):
        assert DecoderType('basic') is DecoderType.BASIC
        assert DecoderType('base64') is DecoderType.BASE_64
        assert DecoderType('rc4') is DecoderType.RC4


# ---------------------------------------------------------------------------
# base64_transform  (custom alphabet: lowercase first, then uppercase)
# ---------------------------------------------------------------------------

class TestBase64Transform:
    def test_empty_string(self):
        assert base64_transform('') == ''

    def test_non_standard_alphabet(self):
        """Standard base64 'aGVsbG8=' decodes to 'hello', but the custom
        alphabet reverses case mapping so the result must differ."""
        result = base64_transform('aGVsbG8=')
        assert result != 'hello'

    def test_decode_known_4char_group(self):
        # 'abcd' -> indices 0,1,2,3 in custom alphabet
        assert base64_transform('abcd') == '\x00\x04 '

    def test_decode_uppercase_group(self):
        # 'ABCD' -> indices 26,27,28,29
        result = base64_transform('ABCD')
        assert result[0] == '\x1a'
        assert result[1] == 'm'
        assert len(result) == 3

    def test_decode_mixed_case(self):
        assert base64_transform('aBcD') == "\x00l'"

    def test_decode_two_groups(self):
        # 8 chars = two 4-char groups = 6 decoded bytes
        assert base64_transform('abcdefgh') == '\x00\x04 \x04\x14a'

    def test_padding_double_equals(self):
        # 'ab==' has one meaningful 6-bit pair
        assert base64_transform('ab==') == '\x00\x08\x10'

    def test_padding_single_equals(self):
        assert base64_transform('abc=') == '\x00\x040'

    def test_invalid_chars_are_skipped(self):
        """Characters not in the alphabet should be silently ignored."""
        # '$' and '!' are not in the alphabet
        assert base64_transform('$ab!cd') == base64_transform('abcd')

    def test_returns_string(self):
        result = base64_transform('abcd')
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# StringDecoder base class
# ---------------------------------------------------------------------------

class TestStringDecoder:
    def test_get_string_raises_not_implemented(self):
        decoder = StringDecoder(['a', 'b'], 0)
        with pytest.raises(NotImplementedError):
            decoder.get_string(0)

    def test_type_property_is_basic(self):
        decoder = StringDecoder(['a'], 0)
        assert decoder.type == DecoderType.BASIC

    def test_get_string_for_rotation_raises_on_first_call(self):
        decoder = BasicStringDecoder(['hello'], 0)
        with pytest.raises(RuntimeError, match='First call'):
            decoder.get_string_for_rotation(0)

    def test_get_string_for_rotation_works_on_second_call(self):
        decoder = BasicStringDecoder(['hello', 'world'], 0)
        with pytest.raises(RuntimeError):
            decoder.get_string_for_rotation(0)
        # Second call should succeed
        assert decoder.get_string_for_rotation(0) == 'hello'

    def test_get_string_for_rotation_passes_args(self):
        decoder = BasicStringDecoder(['hello', 'world'], 0)
        # Exhaust first-call guard
        with pytest.raises(RuntimeError):
            decoder.get_string_for_rotation(0)
        # Second call with index 1
        assert decoder.get_string_for_rotation(1) == 'world'

    def test_is_first_call_flag(self):
        decoder = BasicStringDecoder(['x'], 0)
        assert decoder.is_first_call is True
        with pytest.raises(RuntimeError):
            decoder.get_string_for_rotation(0)
        assert decoder.is_first_call is False


# ---------------------------------------------------------------------------
# BasicStringDecoder
# ---------------------------------------------------------------------------

class TestBasicStringDecoder:
    def test_type_property(self):
        decoder = BasicStringDecoder(['a'], 0)
        assert decoder.type == DecoderType.BASIC

    def test_zero_offset(self):
        arr = ['alpha', 'beta', 'gamma']
        decoder = BasicStringDecoder(arr, 0)
        assert decoder.get_string(0) == 'alpha'
        assert decoder.get_string(1) == 'beta'
        assert decoder.get_string(2) == 'gamma'

    def test_positive_offset(self):
        arr = ['a', 'b', 'c', 'd']
        decoder = BasicStringDecoder(arr, 2)
        # index 0 -> array[0+2] = 'c'
        assert decoder.get_string(0) == 'c'
        assert decoder.get_string(1) == 'd'

    def test_negative_offset(self):
        arr = ['a', 'b', 'c', 'd']
        decoder = BasicStringDecoder(arr, -2)
        # index 2 -> array[2-2] = 'a'
        assert decoder.get_string(2) == 'a'
        assert decoder.get_string(3) == 'b'

    def test_out_of_bounds_positive(self):
        arr = ['a', 'b']
        decoder = BasicStringDecoder(arr, 0)
        assert decoder.get_string(5) is None

    def test_out_of_bounds_negative(self):
        arr = ['a', 'b']
        decoder = BasicStringDecoder(arr, -5)
        assert decoder.get_string(0) is None

    def test_exact_boundary(self):
        arr = ['a', 'b', 'c']
        decoder = BasicStringDecoder(arr, 0)
        assert decoder.get_string(2) == 'c'  # last valid index
        assert decoder.get_string(3) is None  # one past end

    def test_negative_index_yields_negative_array_index(self):
        arr = ['a', 'b']
        decoder = BasicStringDecoder(arr, 0)
        # index -1 -> array[-1] which is < 0 -> returns None
        assert decoder.get_string(-1) is None

    def test_empty_array(self):
        decoder = BasicStringDecoder([], 0)
        assert decoder.get_string(0) is None

    def test_extra_args_are_ignored(self):
        decoder = BasicStringDecoder(['x'], 0)
        assert decoder.get_string(0, 'extra', 'args') == 'x'


# ---------------------------------------------------------------------------
# Base64StringDecoder
# ---------------------------------------------------------------------------

class TestBase64StringDecoder:
    def test_type_property(self):
        decoder = Base64StringDecoder(['x'], 0)
        assert decoder.type == DecoderType.BASE_64

    def test_decodes_value(self):
        # 'abcd' through base64_transform gives '\x00\x04 '
        decoder = Base64StringDecoder(['abcd'], 0)
        assert decoder.get_string(0) == '\x00\x04 '

    def test_with_offset(self):
        decoder = Base64StringDecoder(['SKIP', 'abcd'], 1)
        # index 0 -> array[0+1] = 'abcd'
        assert decoder.get_string(0) == base64_transform('abcd')

    def test_out_of_bounds_returns_none(self):
        decoder = Base64StringDecoder(['abcd'], 0)
        assert decoder.get_string(5) is None

    def test_negative_out_of_bounds_returns_none(self):
        decoder = Base64StringDecoder(['abcd'], -10)
        assert decoder.get_string(0) is None

    def test_caching(self):
        decoder = Base64StringDecoder(['abcd'], 0)
        result1 = decoder.get_string(0)
        result2 = decoder.get_string(0)
        assert result1 == result2
        # Verify value is actually in the cache
        assert 0 in decoder._cache
        assert decoder._cache[0] == result1

    def test_cache_is_used(self):
        decoder = Base64StringDecoder(['abcd'], 0)
        # First call populates cache
        decoder.get_string(0)
        # Modify cache to prove second call uses it
        decoder._cache[0] = 'CACHED'
        assert decoder.get_string(0) == 'CACHED'

    def test_multiple_indices(self):
        decoder = Base64StringDecoder(['abcd', 'ABCD'], 0)
        r0 = decoder.get_string(0)
        r1 = decoder.get_string(1)
        assert r0 == base64_transform('abcd')
        assert r1 == base64_transform('ABCD')
        assert r0 != r1

    def test_empty_encoded_string(self):
        decoder = Base64StringDecoder([''], 0)
        assert decoder.get_string(0) == ''

    def test_get_string_for_rotation(self):
        decoder = Base64StringDecoder(['abcd'], 0)
        with pytest.raises(RuntimeError):
            decoder.get_string_for_rotation(0)
        result = decoder.get_string_for_rotation(0)
        assert result == base64_transform('abcd')


# ---------------------------------------------------------------------------
# Rc4StringDecoder
# ---------------------------------------------------------------------------

class TestRc4StringDecoder:
    def test_type_property(self):
        decoder = Rc4StringDecoder(['x'], 0)
        assert decoder.type == DecoderType.RC4

    def test_key_none_returns_none(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        assert decoder.get_string(0) is None

    def test_key_none_explicit(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        assert decoder.get_string(0, key=None) is None

    def test_out_of_bounds_returns_none(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        assert decoder.get_string(5, key='k') is None

    def test_negative_out_of_bounds_returns_none(self):
        decoder = Rc4StringDecoder(['abcd'], -10)
        assert decoder.get_string(0, key='k') is None

    def test_decodes_with_key(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        result = decoder.get_string(0, key='k')
        assert result is not None
        assert isinstance(result, str)
        # Verified value from the implementation
        assert result == 'o\xe6\x80'

    def test_different_keys_give_different_results(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        r1 = decoder.get_string(0, key='testkey')
        r2 = decoder.get_string(0, key='otherkey')
        assert r1 != r2

    def test_caching_with_same_key(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        r1 = decoder.get_string(0, key='mykey')
        r2 = decoder.get_string(0, key='mykey')
        assert r1 == r2
        assert r1 is r2  # same cached object
        assert (0, 'mykey') in decoder._cache

    def test_cache_keyed_by_index_and_key(self):
        decoder = Rc4StringDecoder(['abcd', 'ABCD'], 0)
        r1 = decoder.get_string(0, key='k')
        r2 = decoder.get_string(1, key='k')
        assert (0, 'k') in decoder._cache
        assert (1, 'k') in decoder._cache
        assert r1 != r2

    def test_cache_is_used(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        decoder.get_string(0, key='k')
        decoder._cache[(0, 'k')] = 'CACHED'
        assert decoder.get_string(0, key='k') == 'CACHED'

    def test_with_offset(self):
        decoder = Rc4StringDecoder(['SKIP', 'abcd'], 1)
        result = decoder.get_string(0, key='k')
        assert result is not None

    def test_same_input_same_key_deterministic(self):
        """Same input and key always produce the same output."""
        dec1 = Rc4StringDecoder(['abcd'], 0)
        dec2 = Rc4StringDecoder(['abcd'], 0)
        assert dec1.get_string(0, key='k') == dec2.get_string(0, key='k')

    def test_get_string_for_rotation(self):
        decoder = Rc4StringDecoder(['abcd'], 0)
        with pytest.raises(RuntimeError):
            decoder.get_string_for_rotation(0, key='k')
        result = decoder.get_string_for_rotation(0, key='k')
        assert result is not None

    def test_empty_array(self):
        decoder = Rc4StringDecoder([], 0)
        assert decoder.get_string(0, key='k') is None


# ---------------------------------------------------------------------------
# Cross-decoder consistency
# ---------------------------------------------------------------------------

class TestCrossDecoder:
    def test_basic_does_not_decode(self):
        """BasicStringDecoder returns the raw string, not decoded."""
        arr = ['abcd']
        basic = BasicStringDecoder(arr, 0)
        b64 = Base64StringDecoder(arr, 0)
        # Basic returns raw, Base64 returns decoded -> they should differ
        assert basic.get_string(0) == 'abcd'
        assert b64.get_string(0) != 'abcd'

    def test_all_decoders_handle_empty_array(self):
        for cls in [BasicStringDecoder, Base64StringDecoder, Rc4StringDecoder]:
            decoder = cls([], 0)
            assert decoder.get_string(0) is None
