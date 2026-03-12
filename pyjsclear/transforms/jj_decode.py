"""Pure Python JJEncode decoder.

JJEncode (by Yosuke Hasegawa) encodes JavaScript using only
$, _, +, !, (, ), [, ], {, }, ~, :, ;, comma, dot, quotes,
backslash, and = characters with a single global variable.

This decoder extracts the payload string without executing any code.
All logic is iterative (no recursion).

SPDX-License-Identifier: Apache-2.0
"""

import re


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def is_jj_encoded(code):
    """Return True if *code* looks like JJEncoded JavaScript.

    Checks for the ``VARNAME=~[]`` initialisation pattern that begins every
    JJEncode output.
    """
    if not code or not code.strip():
        return False
    stripped = code.strip()
    return bool(re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*~\s*\[\s*\]', stripped))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_OBJECT_STR = '[object Object]'


def _split_at_depth_zero(text, delimiter):
    """Split *text* on *delimiter* only when bracket/paren depth is 0
    and not inside a string literal.  All logic is iterative."""
    parts = []
    current = []
    depth = 0
    i = 0
    in_string = None
    while i < len(text):
        ch = text[i]

        if in_string is not None:
            current.append(ch)
            if ch == '\\' and i + 1 < len(text):
                i += 1
                current.append(text[i])
            elif ch == in_string:
                in_string = None
            i += 1
            continue

        if ch in ('"', "'"):
            in_string = ch
            current.append(ch)
            i += 1
            continue

        if ch in ('(', '[', '{'):
            depth += 1
            current.append(ch)
            i += 1
            continue

        if ch in (')', ']', '}'):
            depth -= 1
            current.append(ch)
            i += 1
            continue

        if depth == 0 and text[i:i + len(delimiter)] == delimiter:
            parts.append(''.join(current))
            current = []
            i += len(delimiter)
            continue

        current.append(ch)
        i += 1

    parts.append(''.join(current))
    return parts


def _find_matching_close(text, start, open_ch, close_ch):
    """Return index of *close_ch* matching *open_ch* at *start*.
    Iterative, respects strings."""
    depth = 0
    in_string = None
    i = start
    while i < len(text):
        ch = text[i]
        if in_string is not None:
            if ch == '\\' and i + 1 < len(text):
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


# ---------------------------------------------------------------------------
# Symbol table parser
# ---------------------------------------------------------------------------


def _parse_symbol_table(stmt, varname):
    """Parse the ``$={___:++$, ...}`` statement and return a dict
    mapping property names to their resolved values (ints or chars)."""
    prefix = varname + '='
    body = stmt.strip()
    if body.startswith(prefix):
        body = body[len(prefix):]

    body = body.strip()
    if body.startswith('{') and body.endswith('}'):
        body = body[1:-1]
    else:
        return None

    table = {}
    counter = -1  # ~[] = -1

    entries = _split_at_depth_zero(body, ',')
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        colon_idx = entry.find(':')
        if colon_idx == -1:
            continue
        key = entry[:colon_idx].strip()
        value_expr = entry[colon_idx + 1:].strip()

        if value_expr.startswith('++'):
            counter += 1
            table[key] = counter
        elif value_expr.startswith('(') or value_expr.startswith('!'):
            # Coercion+index: e.g. (![]+"")[$] or ($[$]+"")[$]
            # Find the outermost [...] at the end
            if not value_expr.endswith(']'):
                continue
            bracket_end = len(value_expr) - 1
            # Walk backwards to find matching [
            depth = 0
            bracket_start = -1
            j = bracket_end
            while j >= 0:
                if value_expr[j] == ']':
                    depth += 1
                elif value_expr[j] == '[':
                    depth -= 1
                    if depth == 0:
                        bracket_start = j
                        break
                j -= 1
            if bracket_start <= 0:
                continue

            coercion_part = value_expr[:bracket_start].strip()
            # The index is the current counter value
            idx = counter

            coercion_str = _eval_coercion(coercion_part, varname)
            if coercion_str is not None and 0 <= idx < len(coercion_str):
                table[key] = coercion_str[idx]
        else:
            try:
                table[key] = int(value_expr)
            except ValueError:
                pass

    return table


def _eval_coercion(expr, varname):
    """Evaluate a coercion expression to a string.

    Handles:  (![]+"")  -> "false",  (!""+"") -> "true",
    ({}+"") -> "[object Object]",  ($[$]+"") -> "undefined",
    ((!$)+"") -> "false".
    """
    expr = expr.strip()
    if expr.startswith('(') and expr.endswith(')'):
        expr = expr[1:-1].strip()
    # Strip +"" suffix
    for suffix in ('+""', "+''"):
        if expr.endswith(suffix):
            expr = expr[:len(expr) - len(suffix)].strip()
            break
    else:
        return None

    if expr == '![]':
        return 'false'
    if expr == '!""' or expr == "!''":
        return 'true'
    if expr == '{}':
        return _OBJECT_STR
    # VARNAME[VARNAME] -> undefined
    if expr == varname + '[' + varname + ']':
        return 'undefined'
    # (!VARNAME) where VARNAME is object -> false
    if expr == '!' + varname or expr == '(!' + varname + ')':
        return 'false'
    # General X[X] pattern
    if re.match(r'^([a-zA-Z_$][a-zA-Z0-9_$]*)\[\1\]$', expr):
        return 'undefined'
    # VARNAME.KEY where KEY is not in table -> undefined
    if re.match(r'^' + re.escape(varname) + r'\.[a-zA-Z_$][a-zA-Z0-9_$]*$', expr):
        return 'undefined'
    return None


# ---------------------------------------------------------------------------
# Expression evaluator for statements 2/3 and payload
# ---------------------------------------------------------------------------


_MAX_EVAL_DEPTH = 100


def _eval_expr(expr, table, varname, _depth=0):
    """Evaluate a JJEncode expression to a string value.

    Handles symbol-table references, string literals, coercion
    expressions with indexing, sub-assignments, and concatenation.
    Returns the resolved string or None.
    """
    if _depth > _MAX_EVAL_DEPTH:
        return None

    expr = expr.strip()
    if not expr:
        return None

    prefix = varname + '.'

    # String literal — decode JS escape sequences
    if len(expr) >= 2:
        if (expr[0] == '"' and expr[-1] == '"') or \
           (expr[0] == "'" and expr[-1] == "'"):
            return _decode_js_string_literal(expr[1:-1])

    # Bare varname — at this point it's the symbol table object
    if expr == varname:
        return _OBJECT_STR

    # Parenthesised expression possibly followed by [index]
    # Strip nested parens iteratively before delegating to _eval_inner
    if expr.startswith('('):
        close = _find_matching_close(expr, 0, '(', ')')
        if close != -1:
            inner = expr[1:close].strip()
            rest = expr[close + 1:].strip()

            # Iteratively unwrap pure parenthesised expressions: (((...expr...)))
            while inner.startswith('(') and not rest:
                inner_close = _find_matching_close(inner, 0, '(', ')')
                if inner_close == len(inner) - 1:
                    inner = inner[1:inner_close].strip()
                else:
                    break

            val = _eval_inner(inner, table, varname, _depth + 1)
            if not rest:
                return val
            # Check for [index] after the paren
            if rest.startswith('[') and rest.endswith(']'):
                if val is None:
                    return None
                idx_expr = rest[1:-1].strip()
                idx = _resolve_int(idx_expr, table, varname)
                if isinstance(val, str) and idx is not None and 0 <= idx < len(val):
                    return val[idx]
                return None
            return None

    # Symbol table reference: VARNAME.KEY
    if expr.startswith(prefix) and '+' not in expr and '[' not in expr and '=' not in expr:
        key = expr[len(prefix):]
        val = table.get(key)
        if val is not None:
            return str(val) if isinstance(val, int) else val
        return None

    # VARNAME.KEY[VARNAME.KEY2] — string indexing into a table value
    if expr.startswith(prefix) and '[' in expr and '=' not in expr:
        bracket_pos = expr.index('[')
        key = expr[len(prefix):bracket_pos]
        str_val = table.get(key)
        if isinstance(str_val, str) and expr.endswith(']'):
            idx_expr = expr[bracket_pos + 1:-1]
            idx = _resolve_int(idx_expr, table, varname)
            if idx is not None and 0 <= idx < len(str_val):
                return str_val[idx]
        return None

    # Coercion with index: (![]+"")[$._$_]
    if expr.endswith(']'):
        val = _eval_coercion_indexed(expr, table, varname)
        if val is not None:
            return val

    # Concatenation: expr + expr + ...
    if '+' in expr:
        tokens = _split_at_depth_zero(expr, '+')
        if len(tokens) > 1:
            parts = []
            for t in tokens:
                v = _eval_expr(t, table, varname, _depth + 1)
                if v is None:
                    return None
                parts.append(v)
            return ''.join(parts)

    return None


def _eval_inner(inner, table, varname, _depth=0):
    """Evaluate the inside of a parenthesised expression.
    Handles sub-assignments and simple expressions."""
    if _depth > _MAX_EVAL_DEPTH:
        return None

    prefix = varname + '.'

    # Sub-assignment: VARNAME.KEY=EXPR
    if inner.startswith(prefix):
        eq_pos = _find_top_level_eq(inner)
        if eq_pos is not None:
            key = inner[len(prefix):eq_pos]
            rhs = inner[eq_pos + 1:]
            val = _eval_expr(rhs, table, varname, _depth + 1)
            if val is not None:
                table[key] = val
                return val

    # Coercion expression like !$+"" or ![]+"", etc.
    coercion_str = _eval_coercion(inner, varname)
    if coercion_str is not None:
        return coercion_str

    # Just a nested expression
    return _eval_expr(inner, table, varname, _depth + 1)


def _find_top_level_eq(expr):
    """Find the position of the first ``=`` at depth 0 that is not ``==``."""
    depth = 0
    in_string = None
    i = 0
    while i < len(expr):
        ch = expr[i]
        if in_string is not None:
            if ch == '\\' and i + 1 < len(expr):
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
        elif ch in ('(', '[', '{'):
            depth += 1
        elif ch in (')', ']', '}'):
            depth -= 1
        elif ch == '=' and depth == 0:
            # Check not ==
            if i + 1 < len(expr) and expr[i + 1] == '=':
                i += 2
                continue
            return i
        i += 1
    return None


def _eval_coercion_indexed(expr, table, varname):
    """Handle ``(![]+"")[$._$_]`` — coercion string indexed by a
    symbol table reference."""
    if not expr.endswith(']'):
        return None

    bracket_end = len(expr) - 1
    depth = 0
    bracket_start = -1
    j = bracket_end
    while j >= 0:
        if expr[j] == ']':
            depth += 1
        elif expr[j] == '[':
            depth -= 1
            if depth == 0:
                bracket_start = j
                break
        j -= 1

    if bracket_start <= 0:
        return None

    coercion_part = expr[:bracket_start].strip()
    index_expr = expr[bracket_start + 1:bracket_end].strip()

    coercion_str = _eval_coercion(coercion_part, varname)
    if coercion_str is None:
        return None

    idx = _resolve_int(index_expr, table, varname)
    if idx is None:
        return None

    if 0 <= idx < len(coercion_str):
        return coercion_str[idx]
    return ''


def _resolve_int(expr, table, varname):
    """Resolve an expression to an integer."""
    expr = expr.strip()
    prefix = varname + '.'
    if expr.startswith(prefix):
        key = expr[len(prefix):]
        val = table.get(key)
        if isinstance(val, int):
            return val
        return None
    try:
        return int(expr)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Augment-statement parser (statements 2 and 3)
# ---------------------------------------------------------------------------


def _parse_augment_statement(stmt, table, varname):
    """Parse statements that build multi-character strings like
    "constructor" and "return" by concatenation, and store
    intermediate single-char sub-assignments into the table."""
    stmt = stmt.strip()
    prefix = varname + '.'

    # Find top-level = to split LHS and RHS
    eq_pos = _find_top_level_eq(stmt)
    if eq_pos is None:
        return
    lhs = stmt[:eq_pos].strip()
    rhs = stmt[eq_pos + 1:].strip()

    if not lhs.startswith(prefix):
        return
    top_key = lhs[len(prefix):]

    # Evaluate the RHS: it's a + concatenation of terms
    tokens = _split_at_depth_zero(rhs, '+')
    resolved = []
    for token in tokens:
        val = _eval_expr(token, table, varname)
        if val is not None:
            resolved.append(val)
        else:
            resolved.append('?')

    result = ''.join(resolved)
    table[top_key] = result


# ---------------------------------------------------------------------------
# Escape decoder
# ---------------------------------------------------------------------------


def _decode_js_string_literal(s):
    """Decode escapes in a JS string literal content (between quotes).

    Only handles \\\\ -> \\, \\\" -> \", \\' -> ', and leaves everything
    else (like \\1, \\x, \\u) as-is for later processing."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nch = s[i + 1]
            if nch in ('"', "'", '\\'):
                result.append(nch)
                i += 2
                continue
        result.append(s[i])
        i += 1
    return ''.join(result)


def _decode_escapes(s):
    """Decode octal (\\NNN), hex (\\xNN), unicode (\\uNNNN) escape
    sequences in a single left-to-right pass.  Also handles standard
    single-char escapes."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nch = s[i + 1]

            # Unicode escape \uNNNN
            if nch == 'u' and i + 5 < len(s):
                hex_str = s[i + 2:i + 6]
                try:
                    result.append(chr(int(hex_str, 16)))
                    i += 6
                    continue
                except ValueError:
                    pass

            # Hex escape \xNN
            if nch == 'x' and i + 3 < len(s):
                hex_str = s[i + 2:i + 4]
                try:
                    result.append(chr(int(hex_str, 16)))
                    i += 4
                    continue
                except ValueError:
                    pass

            # Octal escape \NNN (1-3 digits)
            if '0' <= nch <= '7':
                octal = ''
                j = i + 1
                while j < len(s) and j < i + 4 and '0' <= s[j] <= '7':
                    octal += s[j]
                    j += 1
                result.append(chr(int(octal, 8)))
                i = j
                continue

            # Standard single-char escapes
            _esc = {
                'n': '\n', 'r': '\r', 't': '\t',
                '\\': '\\', "'": "'", '"': '"',
                '/': '/', 'b': '\b', 'f': '\f',
            }
            if nch in _esc:
                result.append(_esc[nch])
                i += 2
                continue

            # Unknown escape — keep literal
            result.append(nch)
            i += 2
            continue

        result.append(s[i])
        i += 1

    return ''.join(result)


# ---------------------------------------------------------------------------
# Payload extractor
# ---------------------------------------------------------------------------


def _extract_payload_expression(stmt, varname):
    """Extract the inner concatenation expression from the payload
    statement ``$.$($.$(EXPR)())()``."""
    # Find VARNAME.$(VARNAME.$(
    inner_prefix = varname + '.$(' + varname + '.$('
    idx = stmt.find(inner_prefix)
    if idx == -1:
        return None

    start = idx + len(inner_prefix)

    # Find matching ) for the inner $.$(
    depth = 1
    in_string = None
    i = start
    while i < len(stmt):
        ch = stmt[i]
        if in_string is not None:
            if ch == '\\' and i + 1 < len(stmt):
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
            i += 1
            continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return stmt[start:i]
        i += 1

    return None


# ---------------------------------------------------------------------------
# Main decoder
# ---------------------------------------------------------------------------


def jj_decode(code):
    """Decode JJEncoded JavaScript.  Returns the decoded string, or
    ``None`` on any failure."""
    try:
        return _jj_decode_inner(code)
    except Exception:
        return None


def _jj_decode_inner(code):
    if not code or not code.strip():
        return None

    stripped = code.strip()

    m = re.match(r'^([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*~\s*\[\s*\]', stripped)
    if not m:
        return None
    varname = m.group(1)

    # Find the JJEncode line
    jj_line = None
    for line in stripped.splitlines():
        line = line.strip()
        if re.match(r'^' + re.escape(varname) + r'\s*=\s*~\s*\[\s*\]', line):
            jj_line = line
            break

    if jj_line is None:
        return None

    # Split into semicolon-delimited statements at depth 0
    stmts = _split_at_depth_zero(jj_line, ';')
    stmts = [s.strip() for s in stmts if s.strip()]

    if len(stmts) < 5:
        return None

    # Statement 0: VARNAME=~[]
    # Statement 1: VARNAME={...}  (symbol table)
    # Statement 2: VARNAME.$_=...  (builds "constructor")
    # Statement 3: VARNAME.$$=...  (builds "return")
    # Statement 4: VARNAME.$=...   (Function constructor)
    # Statement 5 (last): payload invocation

    # --- Parse symbol table ---
    symbol_table = _parse_symbol_table(stmts[1], varname)
    if symbol_table is None:
        return None

    # --- Parse statement 2 (constructor string + sub-assignments) ---
    _parse_augment_statement(stmts[2], symbol_table, varname)

    # --- Parse statement 3 (return string) ---
    _parse_augment_statement(stmts[3], symbol_table, varname)

    # --- Extract payload from the last statement ---
    payload_stmt = stmts[-1]
    inner = _extract_payload_expression(payload_stmt, varname)
    if inner is None:
        return None

    # Evaluate the payload concatenation
    tokens = _split_at_depth_zero(inner, '+')
    resolved = []
    for token in tokens:
        val = _eval_expr(token, symbol_table, varname)
        if val is None:
            return None
        resolved.append(val)

    payload_str = ''.join(resolved)

    # Result should be: return"..."
    if not payload_str.startswith('return'):
        return None
    payload_str = payload_str[len('return'):]

    # Strip surrounding quotes
    payload_str = payload_str.strip()
    if len(payload_str) >= 2 and payload_str[0] == '"' and payload_str[-1] == '"':
        payload_str = payload_str[1:-1]
    elif len(payload_str) >= 2 and payload_str[0] == "'" and payload_str[-1] == "'":
        payload_str = payload_str[1:-1]
    else:
        return None

    return _decode_escapes(payload_str)
