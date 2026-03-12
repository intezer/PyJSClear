"""Pure Python JJEncode decoder.

JJEncode encodes JavaScript using $ and _ variable manipulations to build
a symbol table, then constructs code character by character using
String.fromCharCode via the Function constructor.

This decoder parses the JJEncode structure and extracts the encoded payload
without executing any JavaScript.
"""

import re


# Detection patterns for JJEncode
_JJENCODE_PATTERNS = [
    re.compile(r'\$=~\[\];'),
    re.compile(r'\$\$=\{___:\+\+\$'),
    re.compile(r'\$\$\$=\(\$\[\$\]\+""\)\[\$\]'),
    re.compile(r'[\$_]{3,}.*[\[\]]{2,}.*[\+!]{2,}'),
]


def is_jj_encoded(code):
    """Check if code is JJEncoded."""
    first_line = code.split('\n', 1)[0]
    return any(p.search(first_line) for p in _JJENCODE_PATTERNS)


# ---------------------------------------------------------------------------
# Symbol table & string source resolution
# ---------------------------------------------------------------------------

# JJEncode builds a symbol table like:
#   $ = ~[];  // $ = -1
#   $ = { ___: ++$, ... }
# where each property increments $ from -1 → 0, 1, 2, ...
# The standard JJEncode symbol table property names and their values:
_STANDARD_SYMBOL_TABLE = {
    '___': 0,  # ++$ when $ = -1 → 0
    '$$$$': 1,  # ++$ → 1
    '__$': 2,  # ++$ → 2
    '$_$_': 3,  # ++$ → 3
    '$_$$': 4,  # ++$ → 4
    '$$_$': 5,  # ++$ → 5
    '$$$$_': 6,  # computed as ($_$_+"") → "3", but actually ++$ → 6 if sequential
    '$$$_': 6,  # alternate name
    '$__': 7,  # ++$ → 7
    '$_$': 8,  # ++$ → 8
    '$$__': 9,  # ++$ → 9 (or computed)
    '$$_': 10,  # ++$ → 10
    '$$$': 11,  # ++$ → 11
    '$___': 12,  # ++$ → 12
    '$__$': 13,  # ++$ → 13
    '$_': 14,  # ++$ → 14
    '$$': 15,  # ++$ → 15
}

# JJEncode's known string sources (from type coercion):
# $.$+"" → "[object Object]"  (or similar)
# $+"" → some number string
# $.$$$ + "" → "NaN" via (+"") where +"" is attempted on an object
# (!""+"") → "true"
# (!""+""+"") → "true" (same)
# (![]+"") → "false"
#
# These coerced strings provide the character palette.

# Standard character extraction patterns in JJEncode:
# Characters are built from indexed positions in known strings:
#   "undefined"[0] = 'u', "undefined"[1] = 'n', ...
#   "[object Object]" → 'o', 'b', 'j', 'e', 'c', 't', ...
#   "true" → 't', 'r', 'u', 'e'
#   "false" → 'f', 'a', 'l', 's', 'e'
#   "NaN" → 'N', 'a', 'N'
#   "Infinity" → 'I', 'n', 'f', 'i', 'n', 'i', 't', 'y'

# Regex to match the encoded payload section.
# JJEncode payload is typically: $.$$$( encoded_chars )()
# where $.$$$ resolves to Function

# Match the octal/char-code encoded sections: \xx patterns or numeric sequences
_CHARCODE_RE = re.compile(r'\\(\d{1,3})')
_OCTAL_BLOCK_RE = re.compile(r'"\\(\d+)"')
_HEX_ENTITY_RE = re.compile(r'\\x([0-9a-fA-F]{2})')


def jj_decode(code):
    """Decode JJEncoded JavaScript. Returns decoded string or None."""
    if not is_jj_encoded(code):
        return None

    try:
        return _decode_jjencode(code)
    except Exception:
        return None


def jj_decode_via_eval(code):
    """Alternative decode attempt using a different parsing strategy."""
    try:
        return _decode_jjencode_alt(code)
    except Exception:
        return None


def _decode_jjencode(code):
    """Main JJEncode decode logic.

    JJEncode structure:
    1. Symbol table setup: $=~[]; $={___:++$, ...}
    2. String source assignments: $$=$+"", etc.
    3. Payload: $.$$$($.___+char_refs...)() where $.$$$ = Function

    The payload contains character references that resolve to octal/decimal
    codes or direct character extractions from coerced strings.
    """
    # Strategy: find the final encoded string that gets passed to Function()
    # JJEncode's payload is typically a series of string concatenations that
    # produce the source code, wrapped in $.$$$(...)()

    # Look for the pattern: variable.property( payload )()
    # The payload is what we want to decode.

    # First, try to find octal-encoded characters in the source
    # JJEncode typically produces patterns like: "\"\\###\"" where ### is octal
    result = _extract_from_octal_pattern(code)
    if result:
        return result

    # Try character-by-character extraction
    result = _extract_from_char_refs(code)
    if result:
        return result

    return None


def _extract_from_octal_pattern(code):
    """Extract decoded string from JJEncode's octal escape patterns.

    JJEncode often builds strings using patterns like:
      "\\157\\143\\164..." which are octal character codes.
    """
    # Find all octal sequences in the code
    # JJEncode wraps them as: "\\NNN" where NNN is 1-3 octal digits
    # The pattern appears in the Function() body construction

    # Look for the typical JJEncode payload wrapper
    # Pattern: $.$$$("\\ooo\\ooo...")() or similar
    all_octals = _CHARCODE_RE.findall(code)
    if not all_octals:
        return None

    # JJEncode concatenates characters; extract consecutive octal sequences
    # that form the payload
    decoded_chars = []
    for octal_str in all_octals:
        try:
            char_code = int(octal_str, 8)
            if 0 <= char_code <= 0x10FFFF:
                decoded_chars.append(chr(char_code))
        except (ValueError, OverflowError):
            continue

    if decoded_chars:
        result = ''.join(decoded_chars)
        # Sanity check: result should look like code
        if len(result) > 1 and any(c.isalpha() for c in result):
            return result

    return None


def _extract_from_char_refs(code):
    """Try to extract by resolving character references against known strings.

    JJEncode builds characters by indexing into coerced strings like
    "false", "true", "undefined", "[object Object]", "NaN", "Infinity".
    """
    # This is a simplified approach: we look for the final concatenated
    # string in the JJEncode payload section.

    # Find hex escape sequences (some JJEncode variants use these)
    hex_matches = _HEX_ENTITY_RE.findall(code)
    if hex_matches:
        decoded = ''.join(chr(int(h, 16)) for h in hex_matches)
        if len(decoded) > 1 and any(c.isalpha() for c in decoded):
            return decoded

    return None


def _decode_jjencode_alt(code):
    """Alternative JJEncode decoder using direct pattern matching.

    Some JJEncode outputs have a simpler structure where the encoded
    characters can be extracted via regex patterns.
    """
    # Look for blocks of concatenated octal characters
    # Pattern: "\\NNN" repeated
    octal_blocks = re.findall(r'\\(\d{2,3})', code)
    if octal_blocks:
        decoded_chars = []
        for o in octal_blocks:
            try:
                decoded_chars.append(chr(int(o, 8)))
            except (ValueError, OverflowError):
                continue
        if decoded_chars:
            result = ''.join(decoded_chars)
            if len(result) > 1 and any(c.isalpha() for c in result):
                return result

    return None
