"""AAEncode decoder.

AAEncode encodes JavaScript using Japanese-style emoticons.
This decoder reverses the encoding by replacing emoticon patterns
with their numeric values, then converting octal/hex to characters.
"""

import re


# The 16 AAEncode symbol table entries (indices 0-15)
_AA_SYMBOLS = [
    '(c^_^o)',
    '(\uff9f\u0398\uff9f)',
    '((o^_^o) - (\uff9f\u0398\uff9f))',
    '(o^_^o)',
    '(\uff9f\uff70\uff9f)',
    '((\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))',
    '((o^_^o) +(o^_^o))',
    '((\uff9f\uff70\uff9f) + (o^_^o))',
    '((\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f))',
    '((\uff9f\uff70\uff9f) + (\uff9f\uff70\uff9f) + (\uff9f\u0398\uff9f))',
    '(\uff9f\u0414\uff9f) .\uff9f\u03c9\uff9f\uff89',
    '(\uff9f\u0414\uff9f) .\uff9f\u0398\uff9f\uff89',
    "(\uff9f\u0414\uff9f) ['c']",
    '(\uff9f\u0414\uff9f) .\uff9f\uff70\uff9f\uff89',
    '(\uff9f\u0414\uff9f) .\uff9f\u0414\uff9f\uff89',
    '(\uff9f\u0414\uff9f) [\uff9f\u0398\uff9f]',
]

# Detection pattern: AAEncoded code contains these characteristic markers
_AA_DETECT_RE = re.compile(r'\(\uff9f\u0414\uff9f\)\s*\[\uff9f\u03b5\uff9f\]')  # (ﾟДﾟ)[ﾟεﾟ]

# Unicode marker for hex characters (code points > 127)
_UNICODE_MARKER = '(o\uff9f\uff70\uff9fo)+ '


def is_aa_encoded(code):
    """Check if code is AAEncoded."""
    return bool(_AA_DETECT_RE.search(code))


def aa_decode(code):
    """Decode AAEncoded JavaScript. Returns decoded string or None on failure."""
    if not is_aa_encoded(code):
        return None

    try:
        text = code
        # Replace each symbol with its numeric value
        for i, symbol in enumerate(_AA_SYMBOLS):
            search = symbol + '+ '
            replacement = str(i) if i <= 7 else format(i, 'x')
            text = text.replace(search, replacement)

        # Remove the trailing execution wrapper
        text = text.replace("(\uff9f\u0414\uff9f)[\uff9fo\uff9f]) (\uff9f\u0398\uff9f)) ('_');", '')
        text = text.replace(
            "(\uff9f\u0414\uff9f)[\uff9fo\uff9f])(\uff9f\u0398\uff9f))((\uff9f\u0398\uff9f)+(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+((\uff9f\uff70\uff9f)+(\uff9f\u0398\uff9f))+(\uff9f\u0398\uff9f)+(\uff9f\u0414\uff9f)[\uff9fo\uff9f]);",
            '',
        )

        # Split on the escape marker
        parts = text.split('(\uff9f\u0414\uff9f)[\uff9f\u03b5\uff9f]+')

        result = ''
        for part in parts[1:]:  # Skip the preamble
            part = part.strip()
            if not part:
                continue
            if part.startswith(_UNICODE_MARKER):
                # Unicode character: parse as hex
                hex_str = part[len(_UNICODE_MARKER) :].strip().rstrip('+').strip()
                result += chr(int(hex_str, 16))
            else:
                # ASCII character: parse as octal
                octal_str = part.strip().rstrip('+').strip()
                if octal_str:
                    result += chr(int(octal_str, 8))

        return result if result else None
    except (ValueError, IndexError):
        return None
