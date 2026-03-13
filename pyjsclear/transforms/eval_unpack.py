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


def is_eval_packed(code: str) -> bool:
    """Check if code uses eval packing."""
    return bool(_PACKER_RE.search(code) or _PACKER_RE2.search(code) or _EVAL_RE.search(code.lstrip()))


def _dean_edwards_unpack(packed: str, radix: int, count: int, keywords: list[str]) -> str:
    """Pure Python implementation of Dean Edwards unpacker."""

    # Build the replacement function
    def base_encode(value: int) -> str:
        prefix = '' if value < radix else base_encode(int(value / radix))
        remainder = value % radix
        if remainder > 35:
            return prefix + chr(remainder + 29)
        return prefix + ('0123456789abcdefghijklmnopqrstuvwxyz'[remainder] if remainder < 36 else chr(remainder + 29))

    # Build dictionary
    lookup = {}
    while count > 0:
        count -= 1
        key = base_encode(count)
        lookup[key] = keywords[count] if count < len(keywords) and keywords[count] else key

    # Replace tokens in packed string
    def replacer(token_match: re.Match) -> str:
        token = token_match.group(0)
        return lookup.get(token, token)

    return re.sub(r'\b\w+\b', replacer, packed)


def eval_unpack(code: str) -> str | None:
    """Unpack eval-packed JavaScript. Returns unpacked code or None."""
    return _try_dean_edwards(code)


def _try_dean_edwards(code: str) -> str | None:
    """Try to unpack Dean Edwards packer format."""
    for pattern in [_PACKER_RE, _PACKER_RE2]:
        pattern_match = pattern.search(code)
        if not pattern_match:
            continue

        packed = pattern_match.group(1)
        radix = int(pattern_match.group(2))
        count = int(pattern_match.group(3))
        keywords = pattern_match.group(4).split('|')

        # Unescape the packed string
        packed = packed.replace("\\'", "'").replace('\\\\', '\\')

        try:
            return _dean_edwards_unpack(packed, radix, count, keywords)
        except Exception:
            continue
    return None
