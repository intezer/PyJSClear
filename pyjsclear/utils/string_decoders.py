"""String decoder implementations for obfuscator.io patterns."""

from enum import StrEnum


class DecoderType(StrEnum):
    """Supported obfuscator.io string encoding types."""

    BASIC = 'basic'
    BASE_64 = 'base64'
    RC4 = 'rc4'


_BASE_64_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/='


def base64_transform(encoded_string: str) -> str:
    """Decode obfuscator.io's custom base64 encoding to a UTF-8 string."""
    # Decode 4 base64 chars into 3 bytes using 6-bit groups.
    # bit_buffer accumulates bits; every non-first char in a group yields a byte
    # via right-shift with mask derived from position within the group.
    decoded_chars = ''
    bit_count = 0
    bit_buffer = 0
    for character in encoded_string:
        char_index = _BASE_64_ALPHABET.find(character)
        if char_index == -1:
            continue
        bit_buffer = bit_buffer * 64 + char_index if (bit_count % 4) else char_index
        if bit_count % 4:
            decoded_chars += chr(255 & (bit_buffer >> ((-2 * (bit_count + 1)) & 6)))
        bit_count += 1
    # Convert to raw bytes then decode as UTF-8 (matching JS decodeURIComponent)
    try:
        raw_bytes = bytes(ord(character) for character in decoded_chars)
        return raw_bytes.decode('utf-8')
    except (UnicodeDecodeError, ValueError):
        return decoded_chars


class StringDecoder:
    """Abstract base class for obfuscator.io string decoders."""

    def __init__(self, string_array: list[str], index_offset: int) -> None:
        self.string_array = string_array
        self.index_offset = index_offset
        self.is_first_call = True

    @property
    def type(self) -> DecoderType:
        """Return the decoder type identifier."""
        return DecoderType.BASIC

    def get_string(self, index: int, *args: object) -> str | None:
        """Retrieve and decode the string at the given index."""
        raise NotImplementedError

    def get_string_for_rotation(self, index: int, *args: object, **kwargs: object) -> str | None:
        """Retrieve a string, raising on first call to trigger array rotation."""
        if self.is_first_call:
            self.is_first_call = False
            raise RuntimeError('First call')
        return self.get_string(index, *args, **kwargs)


class BasicStringDecoder(StringDecoder):
    """Decoder that resolves strings by simple array index plus offset."""

    @property
    def type(self) -> DecoderType:
        """Return the decoder type identifier."""
        return DecoderType.BASIC

    def get_string(self, index: int, *args: object) -> str | None:
        """Retrieve the string at the offset-adjusted index."""
        array_index = index + self.index_offset
        if 0 <= array_index < len(self.string_array):
            return self.string_array[array_index]
        return None


class Base64StringDecoder(StringDecoder):
    """Decoder that applies custom base64 decoding after index lookup."""

    def __init__(self, string_array: list[str], index_offset: int) -> None:
        super().__init__(string_array, index_offset)
        self._cache: dict[int, str] = {}

    @property
    def type(self) -> DecoderType:
        """Return the decoder type identifier."""
        return DecoderType.BASE_64

    def get_string(self, index: int, *args: object) -> str | None:
        """Retrieve and base64-decode the string at the given index."""
        if index in self._cache:
            return self._cache[index]
        array_index = index + self.index_offset
        if not (0 <= array_index < len(self.string_array)):
            return None
        decoded = base64_transform(self.string_array[array_index])
        self._cache[index] = decoded
        return decoded


class Rc4StringDecoder(StringDecoder):
    """Decoder that applies RC4 decryption (with base64 pre-processing) after index lookup."""

    def __init__(self, string_array: list[str], index_offset: int) -> None:
        super().__init__(string_array, index_offset)
        self._cache: dict[tuple[int, str], str] = {}

    @property
    def type(self) -> DecoderType:
        """Return the decoder type identifier."""
        return DecoderType.RC4

    def get_string(self, index: int, key: str | None = None) -> str | None:
        """Retrieve and RC4-decrypt the string at the given index using the provided key."""
        if not key:
            return None
        cache_key = (index, key)
        if cache_key in self._cache:
            return self._cache[cache_key]
        array_index = index + self.index_offset
        if not (0 <= array_index < len(self.string_array)):
            return None
        encoded = self.string_array[array_index]
        decoded = _rc4_decode(encoded, key)
        self._cache[cache_key] = decoded
        return decoded


def _rc4_decode(encoded_string: str, key: str) -> str:
    """Decrypt an RC4-encoded string after base64 pre-processing."""
    base64_decoded = base64_transform(encoded_string)
    state_box = _rc4_key_schedule(key)
    return _rc4_prga_decrypt(state_box, base64_decoded)


def _rc4_key_schedule(key: str) -> list[int]:
    """Perform RC4 Key Scheduling Algorithm (KSA)."""
    state_box = list(range(256))
    swap_index = 0
    for index in range(256):
        swap_index = (swap_index + state_box[index] + ord(key[index % len(key)])) % 256
        state_box[index], state_box[swap_index] = state_box[swap_index], state_box[index]
    return state_box


def _rc4_prga_decrypt(state_box: list[int], encoded_string: str) -> str:
    """Perform RC4 Pseudo-Random Generation Algorithm (PRGA) to decrypt the string."""
    state_index = 0
    swap_index = 0
    decoded = []
    for character in encoded_string:
        state_index = (state_index + 1) % 256
        swap_index = (swap_index + state_box[state_index]) % 256
        state_box[state_index], state_box[swap_index] = state_box[swap_index], state_box[state_index]
        keystream_byte = state_box[(state_box[state_index] + state_box[swap_index]) % 256]
        decoded.append(chr(ord(character) ^ keystream_byte))
    return ''.join(decoded)
