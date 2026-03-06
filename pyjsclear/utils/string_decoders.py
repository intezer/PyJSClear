"""String decoder implementations for obfuscator.io patterns."""

from enum import Enum
from urllib.parse import unquote


class DecoderType(Enum):
    BASIC = 'basic'
    BASE_64 = 'base64'
    RC4 = 'rc4'


_BASE_64_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/='


def base64_transform(s):
    """Decode obfuscator.io's custom base64 encoding."""
    # Decode 4 base64 chars into 3 bytes using 6-bit groups.
    # d accumulates bits; every non-first char in a group yields a byte
    # via right-shift with mask derived from position within the group.
    a = ''
    c = 0
    d = 0
    for ch in s:
        e = _BASE_64_ALPHABET.find(ch)
        if e != -1:
            d = d * 64 + e if (c % 4) else e
            if c % 4:
                a += chr(255 & (d >> ((-2 * c) & 6)))
            c += 1
    # Percent-encode each byte then URI-decode for UTF-8 support
    encoded = ''.join(f'%{ord(ch):02x}' for ch in a)
    try:
        return unquote(encoded)
    except Exception:
        return a


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
        idx = index + self.index_offset
        if 0 <= idx < len(self.string_array):
            return self.string_array[idx]
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
        idx = index + self.index_offset
        if not (0 <= idx < len(self.string_array)):
            return None
        decoded = base64_transform(self.string_array[idx])
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
        idx = index + self.index_offset
        if not (0 <= idx < len(self.string_array)):
            return None
        encoded = self.string_array[idx]
        decoded = self._rc4_decode(encoded, key)
        self._cache[cache_key] = decoded
        return decoded

    def _rc4_decode(self, s, key):
        """RC4 decryption with base64 pre-processing."""
        s = base64_transform(s)
        # KSA
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + ord(key[i % len(key)])) % 256
            S[i], S[j] = S[j], S[i]
        # PRGA
        i = 0
        j = 0
        decoded = []
        for y in range(len(s)):
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            decoded.append(chr(ord(s[y]) ^ S[(S[i] + S[j]) % 256]))
        return ''.join(decoded)
