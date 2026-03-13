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


def is_jj_encoded(code: str) -> bool:
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

# Single-char JS escape sequences
_SINGLE_CHAR_ESCAPES: dict[str, str] = {
    'n': '\n', 'r': '\r', 't': '\t',
    '\\': '\\', "'": "'", '"': '"',
    '/': '/', 'b': '\b', 'f': '\f',
}


def _split_at_depth_zero(text: str, delimiter: str) -> list[str]:
    """Split *text* on *delimiter* only when bracket/paren depth is 0
    and not inside a string literal.  All logic is iterative."""
    parts = []
    current = []
    depth = 0
    index = 0
    in_string = None
    while index < len(text):
        character = text[index]

        if in_string is not None:
            current.append(character)
            if character == '\\' and index + 1 < len(text):
                index += 1
                current.append(text[index])
            elif character == in_string:
                in_string = None
            index += 1
            continue

        if character in ('"', "'"):
            in_string = character
            current.append(character)
            index += 1
            continue

        if character in ('(', '[', '{'):
            depth += 1
            current.append(character)
            index += 1
            continue

        if character in (')', ']', '}'):
            depth -= 1
            current.append(character)
            index += 1
            continue

        if depth == 0 and text[index:index + len(delimiter)] == delimiter:
            parts.append(''.join(current))
            current = []
            index += len(delimiter)
            continue

        current.append(character)
        index += 1

    parts.append(''.join(current))
    return parts


def _find_matching_close(text: str, start: int, open_character: str, close_character: str) -> int:
    """Return index of *close_character* matching *open_character* at *start*.
    Iterative, respects strings."""
    depth = 0
    in_string = None
    index = start
    while index < len(text):
        character = text[index]
        if in_string is not None:
            if character == '\\' and index + 1 < len(text):
                index += 2
                continue
            if character == in_string:
                in_string = None
            index += 1
            continue
        if character in ('"', "'"):
            in_string = character
        elif character == open_character:
            depth += 1
        elif character == close_character:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return -1


# ---------------------------------------------------------------------------
# Symbol table parser
# ---------------------------------------------------------------------------


def _parse_symbol_table(stmt: str, varname: str) -> dict[str, int | str] | None:
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

    table: dict[str, int | str] = {}
    counter = -1  # ~[] = -1

    entries = _split_at_depth_zero(body, ',')
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        colon_index = entry.find(':')
        if colon_index == -1:
            continue
        key = entry[:colon_index].strip()
        value_expr = entry[colon_index + 1:].strip()

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
            scan = bracket_end
            while scan >= 0:
                if value_expr[scan] == ']':
                    depth += 1
                elif value_expr[scan] == '[':
                    depth -= 1
                    if depth == 0:
                        bracket_start = scan
                        break
                scan -= 1
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


def _eval_coercion(expr: str, varname: str) -> str | None:
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
    if expr in ('!""', "!''"):
        return 'true'
    if expr == '{}':
        return _OBJECT_STR
    # VARNAME[VARNAME] -> undefined
    if expr == varname + '[' + varname + ']':
        return 'undefined'
    # (!VARNAME) where VARNAME is object -> false
    if expr in ('!' + varname, '(!' + varname + ')'):
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


def _eval_expr(expr: str, table: dict[str, int | str], varname: str, depth: int = 0) -> str | None:
    """Evaluate a JJEncode expression to a string value.

    Handles symbol-table references, string literals, coercion
    expressions with indexing, sub-assignments, and concatenation.
    Returns the resolved string or None.
    """
    if depth > _MAX_EVAL_DEPTH:
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

            val = _eval_inner(inner, table, varname, depth + 1)
            if not rest:
                return val
            # Check for [index] after the paren
            if rest.startswith('[') and rest.endswith(']'):
                if val is None:
                    return None
                index_expr = rest[1:-1].strip()
                idx = _resolve_int(index_expr, table, varname)
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
            index_expr = expr[bracket_pos + 1:-1]
            idx = _resolve_int(index_expr, table, varname)
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
            for token in tokens:
                token_val = _eval_expr(token, table, varname, depth + 1)
                if token_val is None:
                    return None
                parts.append(token_val)
            return ''.join(parts)

    return None


def _eval_inner(inner: str, table: dict[str, int | str], varname: str, depth: int = 0) -> str | None:
    """Evaluate the inside of a parenthesised expression.
    Handles sub-assignments and simple expressions."""
    if depth > _MAX_EVAL_DEPTH:
        return None

    prefix = varname + '.'

    # Sub-assignment: VARNAME.KEY=EXPR
    if inner.startswith(prefix):
        eq_pos = _find_top_level_eq(inner)
        if eq_pos is not None:
            key = inner[len(prefix):eq_pos]
            rhs = inner[eq_pos + 1:]
            val = _eval_expr(rhs, table, varname, depth + 1)
            if val is not None:
                table[key] = val
                return val

    # Coercion expression like !$+"" or ![]+"", etc.
    coercion_str = _eval_coercion(inner, varname)
    if coercion_str is not None:
        return coercion_str

    # Just a nested expression
    return _eval_expr(inner, table, varname, depth + 1)


def _find_top_level_eq(expr: str) -> int | None:
    """Find the position of the first ``=`` at depth 0 that is not ``==``."""
    depth = 0
    in_string = None
    index = 0
    while index < len(expr):
        character = expr[index]
        if in_string is not None:
            if character == '\\' and index + 1 < len(expr):
                index += 2
                continue
            if character == in_string:
                in_string = None
            index += 1
            continue
        if character in ('"', "'"):
            in_string = character
        elif character in ('(', '[', '{'):
            depth += 1
        elif character in (')', ']', '}'):
            depth -= 1
        elif character == '=' and depth == 0:
            # Check not ==
            if index + 1 < len(expr) and expr[index + 1] == '=':
                index += 2
                continue
            return index
        index += 1
    return None


def _eval_coercion_indexed(expr: str, table: dict[str, int | str], varname: str) -> str | None:
    """Handle ``(![]+"")[$._$_]`` — coercion string indexed by a
    symbol table reference."""
    if not expr.endswith(']'):
        return None

    bracket_end = len(expr) - 1
    depth = 0
    bracket_start = -1
    scan = bracket_end
    while scan >= 0:
        if expr[scan] == ']':
            depth += 1
        elif expr[scan] == '[':
            depth -= 1
            if depth == 0:
                bracket_start = scan
                break
        scan -= 1

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


def _resolve_int(expr: str, table: dict[str, int | str], varname: str) -> int | None:
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


def _parse_augment_statement(stmt: str, table: dict[str, int | str], varname: str) -> None:
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


def _decode_js_string_literal(content: str) -> str:
    """Decode escapes in a JS string literal content (between quotes).

    Only handles \\\\ -> \\, \\\" -> \", \\' -> ', and leaves everything
    else (like \\1, \\x, \\u) as-is for later processing."""
    result = []
    index = 0
    while index < len(content):
        if content[index] == '\\' and index + 1 < len(content):
            next_character = content[index + 1]
            if next_character in ('"', "'", '\\'):
                result.append(next_character)
                index += 2
                continue
        result.append(content[index])
        index += 1
    return ''.join(result)


def _decode_escapes(text: str) -> str:
    """Decode octal (\\NNN), hex (\\xNN), unicode (\\uNNNN) escape
    sequences in a single left-to-right pass.  Also handles standard
    single-char escapes."""
    result = []
    index = 0
    while index < len(text):
        if text[index] == '\\' and index + 1 < len(text):
            next_character = text[index + 1]

            # Unicode escape \uNNNN
            if next_character == 'u' and index + 5 < len(text):
                hex_str = text[index + 2:index + 6]
                try:
                    result.append(chr(int(hex_str, 16)))
                    index += 6
                    continue
                except ValueError:
                    pass

            # Hex escape \xNN
            if next_character == 'x' and index + 3 < len(text):
                hex_str = text[index + 2:index + 4]
                try:
                    result.append(chr(int(hex_str, 16)))
                    index += 4
                    continue
                except ValueError:
                    pass

            # Octal escape: JS allows \0-\377 (max value 255).
            # First digit 0-3: up to 3 total digits (\000-\377).
            # First digit 4-7: up to 2 total digits (\40-\77).
            if '0' <= next_character <= '7':
                max_digits = 3 if next_character <= '3' else 2
                octal = ''
                scan = index + 1
                while scan < len(text) and scan < index + 1 + max_digits and '0' <= text[scan] <= '7':
                    octal += text[scan]
                    scan += 1
                result.append(chr(int(octal, 8)))
                index = scan
                continue

            # Standard single-char escapes
            if next_character in _SINGLE_CHAR_ESCAPES:
                result.append(_SINGLE_CHAR_ESCAPES[next_character])
                index += 2
                continue

            # Unknown escape — keep literal
            result.append(next_character)
            index += 2
            continue

        result.append(text[index])
        index += 1

    return ''.join(result)


# ---------------------------------------------------------------------------
# Payload extractor
# ---------------------------------------------------------------------------


def _extract_payload_expression(stmt: str, varname: str) -> str | None:
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
    index = start
    while index < len(stmt):
        character = stmt[index]
        if in_string is not None:
            if character == '\\' and index + 1 < len(stmt):
                index += 2
                continue
            if character == in_string:
                in_string = None
            index += 1
            continue
        if character in ('"', "'"):
            in_string = character
            index += 1
            continue
        if character == '(':
            depth += 1
        elif character == ')':
            depth -= 1
            if depth == 0:
                return stmt[start:index]
        index += 1

    return None


# ---------------------------------------------------------------------------
# Main decoder
# ---------------------------------------------------------------------------


def jj_decode(code: str) -> str | None:
    """Decode JJEncoded JavaScript.  Returns the decoded string, or
    ``None`` on any failure."""
    try:
        return _jj_decode_inner(code)
    except (ValueError, TypeError, IndexError, KeyError, OverflowError,
            AttributeError, re.error):
        return None


def _jj_decode_inner(code: str) -> str | None:
    if not code or not code.strip():
        return None

    stripped = code.strip()

    match = re.match(r'^([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*~\s*\[\s*\]', stripped)
    if not match:
        return None
    varname = match.group(1)

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
    stmts = [statement.strip() for statement in stmts if statement.strip()]

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
