"""String decoder implementations for obfuscator.io patterns."""

from enum import Enum
from urllib.parse import unquote


class DecoderType(Enum):
    BASIC = 'basic'
    BASE_64 = 'base64'
    RC4 = 'rc4'


_BASE_64_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/='


def base64_transform(encoded_string):
    """Decode obfuscator.io's custom base64 encoding."""
    # Decode 4 base64 chars into 3 bytes using 6-bit groups.
    # bit_buffer accumulates bits; every non-first char in a group yields a byte
    # via right-shift with mask derived from position within the group.
    decoded_chars = ''
    bit_count = 0
    bit_buffer = 0
    for ch in encoded_string:
        char_index = _BASE_64_ALPHABET.find(ch)
        if char_index != -1:
            bit_buffer = bit_buffer * 64 + char_index if (bit_count % 4) else char_index
            if bit_count % 4:
                decoded_chars += chr(255 & (bit_buffer >> ((-2 * bit_count) & 6)))
            bit_count += 1
    # Percent-encode each byte then URI-decode for UTF-8 support
    percent_encoded = ''.join(f'%{ord(ch):02x}' for ch in decoded_chars)
    try:
        return unquote(percent_encoded)
    except Exception:
        return decoded_chars


class StringDecoder:
    """Base string decoder."""

    def __init__(self, string_array, index_offset):
        self.string_array = string_array
        self.index_offset = index_offset
        self.is_first_call = True

    @property
    def type(self):
        return DecoderType.BASIC

    def get_string(self, index, *args):
        raise NotImplementedError

    def get_string_for_rotation(self, index, *args, **kwargs):
        if self.is_first_call:
            self.is_first_call = False
            raise RuntimeError('First call')
        return self.get_string(index, *args, **kwargs)


class BasicStringDecoder(StringDecoder):
    """Simple array index + offset decoder."""

    @property
    def type(self):
        return DecoderType.BASIC

    def get_string(self, index, *args):
        array_index = index + self.index_offset
        if 0 <= array_index < len(self.string_array):
            return self.string_array[array_index]
        return None


class Base64StringDecoder(StringDecoder):
    """Base64 string decoder."""

    def __init__(self, string_array, index_offset):
        super().__init__(string_array, index_offset)
        self._cache = {}

    @property
    def type(self):
        return DecoderType.BASE_64

    def get_string(self, index, *args):
        if index in self._cache:
            return self._cache[index]
        array_index = index + self.index_offset
        if not (0 <= array_index < len(self.string_array)):
            return None
        decoded = base64_transform(self.string_array[array_index])
        self._cache[index] = decoded
        return decoded


class Rc4StringDecoder(StringDecoder):
    """RC4 string decoder."""

    def __init__(self, string_array, index_offset):
        super().__init__(string_array, index_offset)
        self._cache = {}

    @property
    def type(self):
        return DecoderType.RC4

    def get_string(self, index, key=None):
        if key is None:
            return None
        # Include key in cache to avoid collisions with different RC4 keys
        cache_key = (index, key)
        if cache_key in self._cache:
            return self._cache[cache_key]
        array_index = index + self.index_offset
        if not (0 <= array_index < len(self.string_array)):
            return None
        encoded = self.string_array[array_index]
        decoded = self._rc4_decode(encoded, key)
        self._cache[cache_key] = decoded
        return decoded

    def _rc4_decode(self, encoded_string, key):
        """RC4 decryption with base64 pre-processing."""
        encoded_string = base64_transform(encoded_string)
        # KSA
        state_box = list(range(256))
        j = 0
        for i in range(256):
            j = (j + state_box[i] + ord(key[i % len(key)])) % 256
            state_box[i], state_box[j] = state_box[j], state_box[i]
        # PRGA
        i = 0
        j = 0
        decoded = []
        for position in range(len(encoded_string)):
            i = (i + 1) % 256
            j = (j + state_box[i]) % 256
            state_box[i], state_box[j] = state_box[j], state_box[i]
            decoded.append(chr(ord(encoded_string[position]) ^ state_box[(state_box[i] + state_box[j]) % 256]))
        return ''.join(decoded)
