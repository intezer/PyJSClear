"""Eval/packer unpacker.

Handles Dean Edwards packer (eval(function(p,a,c,k,e,d){...})) by
replacing eval with identity capture (pure Python).
"""

import re


# Dean Edwards packer pattern
_PACKER_RE = re.compile(
    r"""eval\(function\(p,a,c,k,e,[dr]\)\{"""
    r""".*?return p\}"""
    r"""\('(.*?)',\s*(\d+)\s*,\s*(\d+)\s*,\s*'(.*?)'\s*\.split\('\|'\)""",
    re.DOTALL,
)

# Simpler packer pattern (single-quoted packed string)
_PACKER_RE2 = re.compile(
    r"""eval\(function\s*\(p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\)\s*\{"""
    r"""[\s\S]*?return\s+p[\s\S]*?\}\s*\(\s*'((?:[^'\\]|\\.)*)'\s*,"""
    r"""\s*(\d+)\s*,\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*)'\s*\.split\s*\(\s*'\|'\s*\)""",
    re.DOTALL,
)

# Generic eval(...) pattern
_EVAL_RE = re.compile(r'^eval\s*\(', re.MULTILINE)


def is_eval_packed(code):
    """Check if code uses eval packing."""
    return bool(_PACKER_RE.search(code) or _PACKER_RE2.search(code) or _EVAL_RE.search(code.lstrip()))


def _dean_edwards_unpack(packed, radix, count, keywords):
    """Pure Python implementation of Dean Edwards unpacker."""

    # Build the replacement function
    def base_encode(c):
        prefix = '' if c < radix else base_encode(int(c / radix))
        c = c % radix
        if c > 35:
            return prefix + chr(c + 29)
        return prefix + ('0123456789abcdefghijklmnopqrstuvwxyz'[c] if c < 36 else chr(c + 29))

    # Build dictionary
    lookup = {}
    while count > 0:
        count -= 1
        key = base_encode(count)
        lookup[key] = keywords[count] if count < len(keywords) and keywords[count] else key

    # Replace tokens in packed string
    def replacer(match):
        token = match.group(0)
        return lookup.get(token, token)

    return re.sub(r'\b\w+\b', replacer, packed)


def eval_unpack(code):
    """Unpack eval-packed JavaScript. Returns unpacked code or None."""
    return _try_dean_edwards(code)


def _try_dean_edwards(code):
    """Try to unpack Dean Edwards packer format."""
    for pattern in [_PACKER_RE, _PACKER_RE2]:
        m = pattern.search(code)
        if m:
            packed = m.group(1)
            radix = int(m.group(2))
            count = int(m.group(3))
            keywords_str = m.group(4)
            keywords = keywords_str.split('|')

            # Unescape the packed string
            packed = packed.replace("\\'", "'").replace('\\\\', '\\')

            try:
                return _dean_edwards_unpack(packed, radix, count, keywords)
            except Exception:
                continue
    return None
