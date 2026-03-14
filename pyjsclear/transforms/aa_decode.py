"""Pure Python AAEncode decoder.

AAEncode (by Yosuke Hasegawa) encodes JavaScript into Japanese-style
emoticon characters using fullwidth/halfwidth katakana and special symbols.
Each source character is represented as an octal or hex escape built from
emoticon digit expressions, separated by a backslash-like marker.

This decoder performs iterative string replacements to recover the digit
sequences, then converts octal/hex values back to characters.
"""

import re


# Characteristic pattern present in all AAEncoded output.
_SIGNATURE = '\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]'

# Separator between encoded characters (represents the escape character).
_SEPARATOR = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+'

# Unicode hex marker using U+FF70 (halfwidth katakana-hiragana prolonged sound mark).
_UNICODE_MARKER = '(o\uff9f\uff70\uff9fo)'

# Sentinel used to track unicode marker positions after replacement.
_HEX_SENTINEL = '\x01'

_HEX_CHARS = set('0123456789abcdefABCDEF')

# Replacement rules: longer/more specific patterns first to avoid partial matches.
# All patterns use U+FF70 to match real AAEncode output.
_REPLACEMENTS: list[tuple[str, str]] = [
    ('(o\uff9f\uff70\uff9fo)', _HEX_SENTINEL),
    ('((\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))', '5'),
    ('((\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f))', '4'),
    ('((\uff9f\uff70\uff9f) + (o^_^o))', '3'),
    ('((\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))', '2'),
    ('((o^_^o) - (\uff9f\u0398\uff9f))', '2'),
    ('((o^_^o) + (o^_^o))', '6'),
    ('(\uff9f\uff70\uff9f)', '1'),
    ('(\uff9f\u0398\uff9f)', '1'),
    ('(c^_^o)', '0'),
    ('(o^_^o)', '3'),
]

# Trailing execution wrappers that mark the end of the data region.
_TAIL_PATTERNS: list[str] = [
    '(\uff9f\u0414\uff9f)[\'_\']',
    '(\uff9f\u0414\uff9f)["_"]',
]

_NON_HEX_PATTERN = re.compile(r'[^0-9a-fA-F]')


def is_aa_encoded(code: str) -> bool:
    """Return True if code contains the AAEncode execution signature."""
    if not isinstance(code, str):
        return False
    return _SIGNATURE in code


def aa_decode(code: str) -> str | None:
    """Decode AAEncoded JavaScript, returning the source string or None on failure."""
    if not isinstance(code, str) or not is_aa_encoded(code):
        return None

    try:
        return _decode_impl(code)
    except Exception:
        return None


def _decode_impl(code: str) -> str | None:
    """Core decoding: isolate data section, replace emoticons with digits, convert to chars."""
    data = _extract_data_region(code)
    if data is None:
        return None

    # Apply emoticon-to-digit replacements.
    for original_pattern, replacement in _REPLACEMENTS:
        data = data.replace(original_pattern, replacement)

    # Split on separator to get individual character segments.
    segments = data.split(_SEPARATOR)

    result_characters = _decode_segments(segments)
    if not result_characters:
        return None

    return ''.join(result_characters)


def _extract_data_region(code: str) -> str | None:
    """Extract the encoded payload between the first separator and the trailing wrapper."""
    separator_index = code.find(_SEPARATOR)
    if separator_index == -1:
        return None

    data = code[separator_index:]
    for tail_pattern in _TAIL_PATTERNS:
        tail_position = data.rfind(tail_pattern)
        if tail_position != -1:
            return data[:tail_position]

    return data


def _decode_segments(segments: list[str]) -> list[str]:
    """Convert digit-string segments into decoded characters."""
    result_characters: list[str] = []
    for segment in segments:
        decoded_character = _decode_single_segment(segment.strip())
        if decoded_character is not None:
            result_characters.append(decoded_character)
    return result_characters


def _decode_single_segment(segment: str) -> str | None:
    """Decode one segment into a character, or return None if unparseable."""
    if not segment:
        return None

    is_hex = _HEX_SENTINEL in segment

    # Remove hex sentinel and operator/whitespace noise.
    cleaned_digits = segment.replace(_HEX_SENTINEL, '')
    cleaned_digits = cleaned_digits.replace('+', '').replace(' ', '').strip()

    if not cleaned_digits:
        return None

    # If non-digit residue remains, strip it.
    if not _is_valid_digit_string(cleaned_digits, is_hex):
        cleaned_digits = _NON_HEX_PATTERN.sub('', cleaned_digits)
        if not cleaned_digits:
            return None

    try:
        base = 16 if is_hex else 8
        return chr(int(cleaned_digits, base))
    except (ValueError, OverflowError):
        return None


def _is_valid_digit_string(value: str, allow_hex: bool) -> bool:
    """Check whether value contains only valid digit characters for the given base."""
    if allow_hex:
        return all(character in _HEX_CHARS for character in value)
    return value.isdigit()
