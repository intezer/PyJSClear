"""Pure Python AAEncode decoder.

AAEncode (by Yosuke Hasegawa) encodes JavaScript into Japanese-style
emoticon characters using fullwidth/halfwidth katakana and special symbols.
Each source character is represented as an octal or hex escape built from
emoticon digit expressions, separated by a backslash-like marker.

This decoder performs iterative string replacements to recover the digit
sequences, then converts octal/hex values back to characters.
"""

import re

# Characteristic pattern present in all AAEncoded output — the execution call.
_SIGNATURE = '\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]'

# Separator between encoded characters (represents the escape character "\").
_SEPARATOR = '(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+'

# Unicode hex marker — when present before a segment, the value is hex (\uXXXX).
_UNICODE_MARKER = '(o\uff9f\u30fc\uff9fo)'

# Sentinel used to track unicode marker positions after replacement.
_HEX_SENTINEL = '\x01'

# Replacement rules: longer/more specific patterns first to avoid partial matches.
_REPLACEMENTS = [
    ('(o\uff9f\u30fc\uff9fo)',                                      _HEX_SENTINEL),
    ('((\uff9f\u30fc\uff9f) + (\uff9f\u30fc\uff9f) + (\uff9f\u0398\uff9f))', '5'),
    ('((\uff9f\u30fc\uff9f) + (\uff9f\u30fc\uff9f))',              '4'),
    ('((\uff9f\u30fc\uff9f) + (o^_^o))',                            '3'),
    ('((\uff9f\u30fc\uff9f) + (\uff9f\u0398\uff9f))',              '2'),
    ('((o^_^o) - (\uff9f\u0398\uff9f))',                            '2'),
    ('((o^_^o) + (o^_^o))',                                          '6'),
    ('(\uff9f\u30fc\uff9f)',                                        '1'),
    ('(\uff9f\u0398\uff9f)',                                        '1'),
    ('(c^_^o)',                                                      '0'),
    ('(o^_^o)',                                                      '3'),
]


def is_aa_encoded(code):
    """Check if *code* looks like AAEncoded JavaScript.

    Returns True when the characteristic execution pattern is found.
    """
    if not isinstance(code, str):
        return False
    return _SIGNATURE in code


def aa_decode(code):
    """Decode AAEncoded JavaScript.

    Returns the decoded source string, or ``None`` on any failure.
    All processing is iterative (no recursion).
    """
    if not isinstance(code, str) or not is_aa_encoded(code):
        return None

    try:
        return _decode_impl(code)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _decode_impl(code):
    """Core decoding logic."""
    # 1. Isolate the data section.
    #    AAEncode wraps data inside an execution pattern.  The encoded payload
    #    is the series of segments joined by the separator, ending with a
    #    final execution call like  (ﾟДﾟ)['_']  or  )('_');
    #    We look for the *first* separator occurrence and take everything from
    #    there up to the trailing execution wrapper.

    # Find the data region: everything after the initial variable setup and
    # before the trailing execution portion.
    # The data starts at the first separator token.
    sep_idx = code.find(_SEPARATOR)
    if sep_idx == -1:
        return None

    # The trailing execution wrapper varies but typically looks like:
    #   (ﾟДﾟ)['_'](ﾟΘﾟ)   or   )('_');
    # We strip from the last occurrence of  (ﾟДﾟ)['_']  onward.
    tail_patterns = [
        "(\uff9f\u0414\uff9f)['_']",
        '(\uff9f\u0414\uff9f)["_"]',
    ]
    data = code[sep_idx:]
    for pat in tail_patterns:
        tail_pos = data.rfind(pat)
        if tail_pos != -1:
            data = data[:tail_pos]
            break

    # 2. Apply emoticon-to-digit replacements.
    for old, new in _REPLACEMENTS:
        data = data.replace(old, new)

    # 3. Split on the separator to get individual character segments.
    segments = data.split(_SEPARATOR)

    # The first element is the leading separator itself (empty or noise) — skip it.
    # Actually, since we started data *at* the first separator, the split
    # produces an empty first element.  Handle gracefully.

    result_chars = []
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        # Determine hex vs octal mode.
        is_hex = _HEX_SENTINEL in segment

        # Remove hex sentinel and any remaining operator/whitespace noise.
        cleaned = segment.replace(_HEX_SENTINEL, '')
        cleaned = cleaned.replace('+', '').replace(' ', '').strip()

        if not cleaned:
            continue

        # cleaned should now be a string of digit characters.
        if not cleaned.isdigit() and not (is_hex and all(c in '0123456789abcdefABCDEF' for c in cleaned)):
            # If we still have non-digit residue, try harder: keep only digits.
            cleaned = re.sub(r'[^0-9a-fA-F]', '', cleaned)
            if not cleaned:
                continue

        try:
            if is_hex:
                result_chars.append(chr(int(cleaned, 16)))
            else:
                result_chars.append(chr(int(cleaned, 8)))
        except (ValueError, OverflowError):
            continue

    if not result_chars:
        return None

    return ''.join(result_chars)
