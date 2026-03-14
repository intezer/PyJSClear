"""Eval/packer unpacker.

Handles Dean Edwards packer (eval(function(p,a,c,k,e,d){...})) by
replacing eval with identity capture (pure Python).
"""

import re


_BASE36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'

# Dean Edwards packer pattern
_PACKER_RE = re.compile(
    r"""eval\(function\(p,a,c,k,e,[dr]\)\{"""
    r""".*?return p\}"""
    r"""\('(.*?)',\s*(\d+)\s*,\s*(\d+)\s*,\s*'(.*?)'\s*\.split\('\|'\)""",
    re.DOTALL,
)

# Simpler packer variant with single-quoted packed string
_PACKER_RE2 = re.compile(
    r"""eval\(function\s*\(p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\)\s*\{"""
    r"""[\s\S]*?return\s+p[\s\S]*?\}\s*\(\s*'((?:[^'\\]|\\.)*)'\s*,"""
    r"""\s*(\d+)\s*,\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*)'\s*\.split\s*\(\s*'\|'\s*\)""",
    re.DOTALL,
)

# Generic eval(...) pattern
_EVAL_RE = re.compile(r'^eval\s*\(', re.MULTILINE)


def is_eval_packed(code: str) -> bool:
    """Return True if code appears to use eval packing."""
    return bool(_PACKER_RE.search(code) or _PACKER_RE2.search(code) or _EVAL_RE.search(code.lstrip()))


def _base_encode(value: int, radix: int) -> str:
    """Encode an integer in the given radix using Dean Edwards' scheme."""
    prefix = '' if value < radix else _base_encode(int(value / radix), radix)
    remainder = value % radix
    if remainder > 35:
        return prefix + chr(remainder + 29)
    return prefix + _BASE36_ALPHABET[remainder]


def _dean_edwards_unpack(packed: str, radix: int, count: int, keywords: list[str]) -> str:
    """Unpack a Dean Edwards packed string using pure Python."""
    keyword_mapping: dict[str, str] = {}
    while count > 0:
        count -= 1
        encoded_key = _base_encode(count, radix)
        keyword_mapping[encoded_key] = keywords[count] if count < len(keywords) and keywords[count] else encoded_key

    def replacer(token_match: re.Match) -> str:
        """Replace a matched token with its keyword mapping."""
        token = token_match.group(0)
        return keyword_mapping.get(token, token)

    return re.sub(r'\b\w+\b', replacer, packed)


def eval_unpack(code: str) -> str | None:
    """Unpack eval-packed JavaScript. Returns unpacked code or None."""
    return _try_dean_edwards(code)


def _try_dean_edwards(code: str) -> str | None:
    """Attempt to unpack Dean Edwards packer format from code."""
    for pattern in [_PACKER_RE, _PACKER_RE2]:
        pattern_match = pattern.search(code)
        if not pattern_match:
            continue

        packed = pattern_match.group(1)
        radix = int(pattern_match.group(2))
        count = int(pattern_match.group(3))
        keywords = pattern_match.group(4).split('|')

        packed = packed.replace('\\\'', '\'').replace('\\\\', '\\')

        try:
            return _dean_edwards_unpack(packed, radix, count, keywords)
        except Exception:
            continue
    return None
