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
# Coercion strings
# ---------------------------------------------------------------------------
_FALSE_STR = "false"
_TRUE_STR = "true"
_OBJECT_STR = "[object Object]"
_UNDEFINED_STR = "undefined"


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
        return _decode_jjencode(code)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# String-aware semicolon splitter
# ---------------------------------------------------------------------------

def _split_statements(code):
    """Split code on statement-level semicolons (outside quotes)."""
    stmts = []
    in_str = False
    prev_esc = False
    start = 0

    for i, ch in enumerate(code):
        if ch == '"' and not prev_esc:
            in_str = not in_str
        prev_esc = (ch == '\\' and not prev_esc)
        if ch == ';' and not in_str:
            stmts.append(code[start:i])
            start = i + 1

    if start < len(code):
        stmts.append(code[start:])

    return stmts


# ---------------------------------------------------------------------------
# Symbol table parser
# ---------------------------------------------------------------------------

def _parse_symbol_table(stmt):
    """Parse statement 1: $={___:++$, $$$$:(![]+"")[$], ...}

    Returns dict mapping property names to their resolved values.
    """
    brace_start = stmt.index('{')
    brace_end = _find_matching_brace(stmt, brace_start)
    inner = stmt[brace_start + 1:brace_end]

    entries = _split_top_level(inner, ',')

    table = {}
    counter = -1

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        colon_idx = entry.index(':')
        key = entry[:colon_idx].strip()
        value_expr = entry[colon_idx + 1:].strip()

        if value_expr == '++$':
            counter += 1
            table[key] = counter
        elif value_expr.startswith('(![]+"")'):
            idx = _extract_bracket_ref(value_expr, table, counter)
            if isinstance(idx, int) and 0 <= idx < len(_FALSE_STR):
                table[key] = _FALSE_STR[idx]
            else:
                table[key] = idx
        elif value_expr.startswith('({}+"")'):
            idx = _extract_bracket_ref(value_expr, table, counter)
            if isinstance(idx, int) and 0 <= idx < len(_OBJECT_STR):
                table[key] = _OBJECT_STR[idx]
            else:
                table[key] = idx
        elif value_expr.startswith('($[$]+"")'):
            idx = _extract_bracket_ref(value_expr, table, counter)
            if isinstance(idx, int) and 0 <= idx < len(_UNDEFINED_STR):
                table[key] = _UNDEFINED_STR[idx]
            else:
                table[key] = idx
        elif value_expr.startswith('(!""+"")'):
            idx = _extract_bracket_ref(value_expr, table, counter)
            if isinstance(idx, int) and 0 <= idx < len(_TRUE_STR):
                table[key] = _TRUE_STR[idx]
            else:
                table[key] = idx
        else:
            table[key] = counter

    return table, counter


def _extract_bracket_ref(expr, table, current_counter):
    """Extract the index from expressions like (![]+"")[$]."""
    bracket_start = expr.rfind('[')
    bracket_end = expr.rfind(']')
    if bracket_start < 0 or bracket_end < 0:
        return current_counter

    ref = expr[bracket_start + 1:bracket_end].strip()
    if ref == '$':
        return current_counter

    if ref.startswith('$.'):
        key = ref[2:]
        val = table.get(key)
        if isinstance(val, int):
            return val

    return current_counter


def _find_matching_brace(code, start):
    """Find matching closing brace."""
    depth = 0
    in_str = False
    prev_esc = False
    for i in range(start, len(code)):
        ch = code[i]
        if ch == '"' and not prev_esc:
            in_str = not in_str
        prev_esc = (ch == '\\' and not prev_esc)
        if not in_str:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i
    return len(code) - 1


def _split_top_level(code, sep):
    """Split on separator at depth 0, respecting strings and brackets."""
    parts = []
    depth = 0
    in_str = False
    prev_esc = False
    start = 0

    for i, ch in enumerate(code):
        if ch == '"' and not prev_esc:
            in_str = not in_str
        prev_esc = (ch == '\\' and not prev_esc)
        if not in_str:
            if ch in ('{', '[', '('):
                depth += 1
            elif ch in ('}', ']', ')'):
                depth -= 1
            elif ch == sep and depth == 0:
                parts.append(code[start:i])
                start = i + 1

    if start < len(code):
        parts.append(code[start:])

    return parts


# ---------------------------------------------------------------------------
# Payload evaluation (token-by-token)
# ---------------------------------------------------------------------------

def _eval_payload_parts(payload_inner, table):
    """Evaluate a JJEncode payload by splitting on + and resolving each part.

    Each part is either:
    - A string literal like backslash-quote or double-backslash
    - A property reference like $.__$ (resolves to number or char)
    - A coercion expression like (![]+\"\")[$.key]
    """
    parts = _split_top_level(payload_inner, '+')
    result = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        val = _resolve_part(part, table)
        if val is not None:
            result.append(str(val))

    return ''.join(result)


def _resolve_part(part, table):
    """Resolve a single payload part to its string value."""
    # String literal: "..." (including escaped content)
    if part.startswith('"') and part.endswith('"'):
        return _unescape_js_string_literal(part[1:-1])

    # Property reference: $.key
    if part.startswith('$.'):
        key = part[2:]
        val = table.get(key)
        if val is not None:
            return val

    # Coercion + indexing: (![]+"")[$.key] etc.
    coercion_match = re.match(
        r'\((!?\[\]|!?""|!\$|\{\}|\$\[\$\])\+""\)\[([^\]]+)\]',
        part
    )
    if coercion_match:
        coerce_expr = coercion_match.group(1)
        idx_expr = coercion_match.group(2).strip()

        base_str = _coerce_to_string(coerce_expr)
        if base_str is not None:
            idx = _resolve_part(idx_expr, table)
            if isinstance(idx, int) and 0 <= idx < len(base_str):
                return base_str[idx]

    # Nested: ((!$)+"")[$.key]
    nested_match = re.match(r'\(\(!?\$\)\+""\)\[([^\]]+)\]', part)
    if nested_match:
        idx_expr = nested_match.group(1).strip()
        idx = _resolve_part(idx_expr, table)
        if isinstance(idx, int) and 0 <= idx < len(_FALSE_STR):
            return _FALSE_STR[idx]

    # Parenthesized expression
    if part.startswith('(') and part.endswith(')'):
        return _resolve_part(part[1:-1], table)

    return None


def _coerce_to_string(expr):
    """Map coercion sub-expression to its string result."""
    if expr == '![]':
        return _FALSE_STR
    if expr == '!""' or expr == "!''":
        return _TRUE_STR
    if expr == '{}':
        return _OBJECT_STR
    if expr == '$[$]':
        return _UNDEFINED_STR
    if expr == '!$':
        return _FALSE_STR
    return None


def _unescape_js_string_literal(s):
    """Unescape a JS string literal content (handles \\\\ → \\ and \\\" → \")."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_ch = s[i + 1]
            if next_ch == '\\':
                result.append('\\')
                i += 2
            elif next_ch == '"':
                result.append('"')
                i += 2
            elif next_ch == "'":
                result.append("'")
                i += 2
            elif next_ch == 'n':
                result.append('\n')
                i += 2
            elif next_ch == 'r':
                result.append('\r')
                i += 2
            elif next_ch == 't':
                result.append('\t')
                i += 2
            else:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


# ---------------------------------------------------------------------------
# JS escape processing (for the final decoded body)
# ---------------------------------------------------------------------------

def _process_js_escapes(s):
    """Process JavaScript string escape sequences (octal, hex, unicode)."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_ch = s[i + 1]
            if next_ch == 'n':
                result.append('\n')
                i += 2
            elif next_ch == 'r':
                result.append('\r')
                i += 2
            elif next_ch == 't':
                result.append('\t')
                i += 2
            elif next_ch == '\\':
                result.append('\\')
                i += 2
            elif next_ch == '"':
                result.append('"')
                i += 2
            elif next_ch == "'":
                result.append("'")
                i += 2
            elif next_ch == 'x' and i + 3 < len(s):
                hex_str = s[i + 2:i + 4]
                try:
                    result.append(chr(int(hex_str, 16)))
                    i += 4
                except ValueError:
                    result.append(s[i])
                    i += 1
            elif next_ch == 'u' and i + 5 < len(s):
                hex_str = s[i + 2:i + 6]
                try:
                    result.append(chr(int(hex_str, 16)))
                    i += 6
                except ValueError:
                    result.append(s[i])
                    i += 1
            elif next_ch.isdigit():
                j = i + 1
                while j < len(s) and j < i + 4 and s[j].isdigit():
                    j += 1
                octal_str = s[i + 1:j]
                try:
                    code = int(octal_str, 8)
                    result.append(chr(code))
                except (ValueError, OverflowError):
                    result.append(s[i])
                    i += 1
                    continue
                i = j
            else:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1

    return ''.join(result)


# ---------------------------------------------------------------------------
# Main decode
# ---------------------------------------------------------------------------

def _build_standard_table(table):
    """Set the derived string properties from the standard JJEncode setup.

    Verified from Node.js eval on real samples. All JJEncode samples use
    identical setup producing these values.
    """
    # Derived characters from coercion strings:
    table['$_'] = 'constructor'
    table['_$'] = 'o'
    table['__'] = 't'
    table['_'] = 'u'
    table['$$'] = 'return'
    table['$'] = 'Function'  # Sentinel


def _extract_payload_content(stmt):
    """Extract the inner content from $.$($.$(CONTENT)())().

    Handles nested parentheses and string literals properly.
    """
    # Must start with $.$($.$(
    if not stmt.startswith('$.$($.$('):
        return stmt

    # Skip the prefix '$.$($.$(', find matching ) for the inner $.$(
    start = 8  # len('$.$($.$(')
    content_start = start

    # Find the matching ) for the inner $.$( call
    # We need to track depth, starting at depth 1 (we're inside the inner paren)
    depth = 1
    in_str = False
    prev_esc = False
    i = content_start

    while i < len(stmt) and depth > 0:
        ch = stmt[i]
        if ch == '"' and not prev_esc:
            in_str = not in_str
        prev_esc = (ch == '\\' and not prev_esc)
        if not in_str:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
        i += 1

    # i is now just past the matching ) for inner $.$(
    # The content is from content_start to i-1 (the closing paren)
    content = stmt[content_start:i - 1]
    return content


def _decode_jjencode(code):
    """Main JJEncode decode logic.

    JJEncode has exactly 6 statement-level semicolons:
    0: $=~[]           - init $ to -1
    1: $={___:++$,...}  - symbol table
    2: $.$_=(...)       - builds "constructor"
    3: $.$$=(...)       - builds "return"
    4: $.$=($.___)[$.$_][$.$_]  - gets Function
    5: $.$($.$(...)())()  - payload
    """
    lines = code.split('\n')
    first_line = lines[0]
    rest = '\n'.join(lines[1:]) if len(lines) > 1 else ''

    stmts = _split_statements(first_line)
    if len(stmts) < 6:
        return None

    # Parse symbol table
    table, _counter = _parse_symbol_table(stmts[1])
    _build_standard_table(table)

    # Extract payload from statement 5
    payload_stmt = stmts[5].strip()

    # Strip wrapper: $.$($.$(  <content>  )())()
    # Structure: $.$(  $.$(  CONTENT  )  ()  )  ()
    inner = payload_stmt.rstrip('; ')
    inner = _extract_payload_content(inner)

    # Now inner is: $.$$+"\""+ ... +"\""
    # Evaluate the concatenation
    body = _eval_payload_parts(inner, table)

    # body should be: return"<escaped_content>"
    if not body.startswith('return'):
        return None

    body = body[6:]  # Remove "return"

    # Strip surrounding quotes
    if body.startswith('"') and body.endswith('"'):
        body = body[1:-1]
    elif body.startswith("'") and body.endswith("'"):
        body = body[1:-1]

    # Process JS escapes (octals like \156 → 'n')
    decoded = _process_js_escapes(body)

    if not decoded or not any(c.isalpha() for c in decoded):
        return None

    # Combine with rest of file
    if rest.strip():
        return decoded + '\n' + rest
    return decoded
