"""Pure Python JSFuck decoder.

JSFuck encodes JavaScript using only []()!+ characters.
It exploits JS type coercion to build strings and execute code via Function().
This decoder evaluates the JSFuck expression subset and captures the
string passed to Function().
"""

import re


# JSFuck uses only these characters (plus optional whitespace/semicolons)
_JSFUCK_RE = re.compile(r'^[\s\[\]\(\)!+;]+$')


def is_jsfuck(code):
    """Check if code is JSFuck-encoded.

    JSFuck code consists only of []()!+ characters (with optional whitespace/semicolons).
    We also require minimum length to avoid false positives.
    """
    stripped = code.strip()
    if len(stripped) < 100:
        return False
    jsfuck_chars = set('[]()!+ \t\n\r;')
    jsfuck_count = sum(1 for c in stripped if c in jsfuck_chars)
    return jsfuck_count / len(stripped) > 0.9


# ---------------------------------------------------------------------------
# JSValue: models a JavaScript value with JS-like coercion semantics
# ---------------------------------------------------------------------------


class _JSValue:
    """A JavaScript value with type coercion semantics."""

    __slots__ = ('val', 'type')

    def __init__(self, val, typ):
        self.val = val
        self.type = typ  # 'array', 'bool', 'number', 'string', 'undefined', 'object', 'function'

    # -- coercion helpers ---------------------------------------------------

    def to_number(self):
        match self.type:
            case 'number':
                return self.val
            case 'bool':
                return 1 if self.val else 0
            case 'string':
                s = self.val.strip()
                if s == '':
                    return 0
                try:
                    return int(s)
                except ValueError:
                    try:
                        return float(s)
                    except ValueError:
                        return float('nan')
            case 'array':
                if len(self.val) == 0:
                    return 0
                if len(self.val) == 1:
                    return _JSValue(self.val[0], _guess_type(self.val[0])).to_number()
                return float('nan')
            case 'undefined':
                return float('nan')
            case _:
                return float('nan')

    def to_string(self):
        match self.type:
            case 'string':
                return self.val
            case 'number':
                if isinstance(self.val, float):
                    if self.val != self.val:  # NaN
                        return 'NaN'
                    if self.val == float('inf'):
                        return 'Infinity'
                    if self.val == float('-inf'):
                        return '-Infinity'
                    if self.val == int(self.val):
                        return str(int(self.val))
                    return str(self.val)
                return str(self.val)
            case 'bool':
                return 'true' if self.val else 'false'
            case 'array':
                parts = []
                for item in self.val:
                    if item is None:
                        parts.append('')
                    elif isinstance(item, _JSValue):
                        parts.append(item.to_string())
                    else:
                        parts.append(_JSValue(item, _guess_type(item)).to_string())
                return ','.join(parts)
            case 'undefined':
                return 'undefined'
            case 'object':
                return '[object Object]'
            case _:
                return str(self.val)

    def to_bool(self):
        match self.type:
            case 'bool':
                return self.val
            case 'number':
                return self.val != 0 and self.val == self.val  # 0 and NaN are falsy
            case 'string':
                return len(self.val) > 0
            case 'array':
                return True  # arrays are always truthy in JS
            case 'undefined':
                return False
            case 'object':
                return True
            case _:
                return bool(self.val)

    def get_property(self, key):
        """Property access: self[key]."""
        key_str = key.to_string() if isinstance(key, _JSValue) else str(key)

        if self.type == 'string':
            # String indexing
            try:
                idx = int(key_str)
                if 0 <= idx < len(self.val):
                    return _JSValue(self.val[idx], 'string')
            except (ValueError, IndexError):
                pass
            # String properties
            if key_str == 'length':
                return _JSValue(len(self.val), 'number')
            if key_str == 'constructor':
                return _STRING_CONSTRUCTOR
            # String.prototype methods
            return _get_string_method(self, key_str)

        if self.type == 'array':
            try:
                idx = int(key_str)
                if 0 <= idx < len(self.val):
                    item = self.val[idx]
                    if isinstance(item, _JSValue):
                        return item
                    return _JSValue(item, _guess_type(item))
            except (ValueError, IndexError):
                pass
            if key_str == 'length':
                return _JSValue(len(self.val), 'number')
            if key_str == 'constructor':
                return _ARRAY_CONSTRUCTOR
            # Array methods that JSFuck commonly accesses
            if key_str in (
                'flat',
                'fill',
                'find',
                'filter',
                'entries',
                'concat',
                'join',
                'sort',
                'reverse',
                'slice',
                'map',
                'forEach',
                'reduce',
                'some',
                'every',
                'indexOf',
                'includes',
                'keys',
                'values',
                'at',
                'pop',
                'push',
                'shift',
                'unshift',
                'splice',
                'toString',
                'valueOf',
            ):
                return _JSValue(key_str, 'function')

        if self.type == 'number':
            if key_str == 'constructor':
                return _NUMBER_CONSTRUCTOR
            if key_str == 'toString':
                return _JSValue('toString', 'function')
            return _JSValue(None, 'undefined')

        if self.type == 'bool':
            if key_str == 'constructor':
                return _BOOLEAN_CONSTRUCTOR
            return _JSValue(None, 'undefined')

        if self.type == 'function':
            if key_str == 'constructor':
                return _FUNCTION_CONSTRUCTOR
            return _JSValue(None, 'undefined')

        if self.type == 'object':
            if key_str == 'constructor':
                return _OBJECT_CONSTRUCTOR
            return _JSValue(None, 'undefined')

        return _JSValue(None, 'undefined')

    def __repr__(self):
        return f'_JSValue({self.val!r}, {self.type!r})'


def _guess_type(val):
    if isinstance(val, bool):
        return 'bool'
    if isinstance(val, (int, float)):
        return 'number'
    if isinstance(val, str):
        return 'string'
    if isinstance(val, list):
        return 'array'
    if val is None:
        return 'undefined'
    return 'object'


def _get_string_method(string_val, method_name):
    """Return a callable _JSValue wrapping a string method."""
    if method_name in (
        'italics',
        'bold',
        'fontcolor',
        'fontsize',
        'big',
        'small',
        'strike',
        'sub',
        'sup',
        'link',
        'anchor',
        'charAt',
        'charCodeAt',
        'concat',
        'slice',
        'substring',
        'toLowerCase',
        'toUpperCase',
        'trim',
        'split',
        'replace',
        'indexOf',
        'includes',
        'repeat',
        'padStart',
        'padEnd',
        'toString',
        'valueOf',
        'at',
        'startsWith',
        'endsWith',
        'match',
        'search',
        'normalize',
        'flat',
    ):
        return _JSValue(method_name, 'function')
    return _JSValue(None, 'undefined')


# Sentinel constructors for property chain resolution
_STRING_CONSTRUCTOR = _JSValue('String', 'function')
_NUMBER_CONSTRUCTOR = _JSValue('Number', 'function')
_BOOLEAN_CONSTRUCTOR = _JSValue('Boolean', 'function')
_ARRAY_CONSTRUCTOR = _JSValue('Array', 'function')
_OBJECT_CONSTRUCTOR = _JSValue('Object', 'function')
_FUNCTION_CONSTRUCTOR = _JSValue('Function', 'function')

# Known constructor-of-constructor chain results
_CONSTRUCTOR_MAP = {
    'String': _STRING_CONSTRUCTOR,
    'Number': _NUMBER_CONSTRUCTOR,
    'Boolean': _BOOLEAN_CONSTRUCTOR,
    'Array': _ARRAY_CONSTRUCTOR,
    'Object': _OBJECT_CONSTRUCTOR,
    'Function': _FUNCTION_CONSTRUCTOR,
}


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


def _tokenize(code):
    """Tokenize JSFuck code into a list of characters/tokens."""
    tokens = []
    for ch in code:
        if ch in '[]()!+':
            tokens.append(ch)
        # Skip whitespace, semicolons
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser/evaluator
# ---------------------------------------------------------------------------


class _Parser:
    """Recursive descent parser for JSFuck expressions."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.captured = None  # Result from Function(body)()

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        if self.pos >= len(self.tokens):
            raise _ParseError('Unexpected end of input')
        tok = self.tokens[self.pos]
        if expected is not None and tok != expected:
            raise _ParseError(f'Expected {expected!r}, got {tok!r}')
        self.pos += 1
        return tok

    def parse(self):
        """Parse and evaluate the full expression."""
        result = self._expression()
        return result

    def _expression(self):
        """Parse addition: expr ('+' expr)*"""
        left = self._unary()

        while self.peek() == '+':
            self.consume('+')
            right = self._unary()
            left = self._js_add(left, right)

        return left

    def _unary(self):
        """Parse unary: [!+]* postfix"""
        ops = []
        while self.peek() in ('!', '+'):
            # + is unary only if the next token is not a postfix start
            # Actually in JSFuck, + before [ or ( or ! is always unary
            if self.peek() == '+':
                ops.append('+')
                self.consume('+')
            else:
                ops.append('!')
                self.consume('!')

        val = self._postfix()

        # Apply unary operators right to left
        for op in reversed(ops):
            if op == '!':
                val = _JSValue(not val.to_bool(), 'bool')
            elif op == '+':
                val = _JSValue(val.to_number(), 'number')

        return val

    def _postfix(self):
        """Parse postfix: primary ('[' expr ']')* ('(' args ')')*"""
        val = self._primary()
        receiver = None  # Track receiver for method calls

        while self.peek() in ('[', '('):
            if self.peek() == '[':
                self.consume('[')
                key = self._expression()
                self.consume(']')
                receiver = val  # val is the receiver of the property access
                val = val.get_property(key)
            elif self.peek() == '(':
                self.consume('(')
                args = self._arglist()
                self.consume(')')
                val = self._call(val, args, receiver)
                receiver = None

        return val

    def _primary(self):
        """Parse primary: '(' expr ')' | '[' elements ']'"""
        tok = self.peek()

        if tok == '(':
            self.consume('(')
            val = self._expression()
            self.consume(')')
            return val

        if tok == '[':
            self.consume('[')
            if self.peek() == ']':
                self.consume(']')
                return _JSValue([], 'array')
            elements = [self._expression()]
            while self.peek() not in (']', None):
                # JSFuck doesn't use commas, but handle them if present
                elements.append(self._expression())
            self.consume(']')
            return _JSValue(elements, 'array')

        raise _ParseError(f'Unexpected token: {tok!r} at pos {self.pos}')

    def _arglist(self):
        """Parse argument list (comma-separated or just one expression)."""
        if self.peek() == ')':
            return []
        args = [self._expression()]
        return args

    def _call(self, func, args, receiver=None):
        """Handle function call semantics."""
        # Function constructor: Function(body) returns a new function
        if func.type == 'function' and func.val == 'Function':
            if args:
                body = args[-1].to_string()
                # Return a callable that when invoked, captures the body
                return _JSValue(('__function_body__', body), 'function')

        # Calling a function created by Function(body)
        if func.type == 'function' and isinstance(func.val, tuple):
            if func.val[0] == '__function_body__':
                self.captured = func.val[1]
                return _JSValue(None, 'undefined')

        # Constructor property access — e.g., []["flat"]["constructor"]
        if func.type == 'function' and isinstance(func.val, str):
            name = func.val
            # Handle constructor-of-constructor chains
            if name in _CONSTRUCTOR_MAP:
                # Calling a constructor as function, e.g., String(x)
                if args:
                    return _JSValue(args[0].to_string(), 'string')
                return _JSValue('', 'string')

            # String methods
            if name == 'italics':
                return _JSValue('<i></i>', 'string')
            if name == 'fontcolor':
                return _JSValue('<font color="undefined"></font>', 'string')

            # toString with radix — e.g., (10)["toString"](36) → "a"
            if name == 'toString' and args and receiver is not None:
                radix = args[0].to_number()
                if isinstance(radix, (int, float)) and radix == int(radix):
                    radix = int(radix)
                    if 2 <= radix <= 36 and receiver.type == 'number':
                        num = receiver.to_number()
                        if isinstance(num, (int, float)) and num == int(num):
                            return _JSValue(_int_to_base(int(num), radix), 'string')

        return _JSValue(None, 'undefined')

    def _js_add(self, left, right):
        """JS + operator with type coercion."""
        # If either is a string, concatenate
        if left.type == 'string' or right.type == 'string':
            return _JSValue(left.to_string() + right.to_string(), 'string')

        # If either is an array or object, convert both to strings and concatenate
        if left.type in ('array', 'object') or right.type in ('array', 'object'):
            return _JSValue(left.to_string() + right.to_string(), 'string')

        # Otherwise numeric addition
        return _JSValue(left.to_number() + right.to_number(), 'number')


def _int_to_base(num, base):
    """Convert integer to string in given base (2-36), matching JS behavior."""
    if num == 0:
        return '0'
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    negative = num < 0
    num = abs(num)
    result = []
    while num:
        result.append(digits[num % base])
        num //= base
    if negative:
        result.append('-')
    return ''.join(reversed(result))


class _ParseError(Exception):
    pass


# ---------------------------------------------------------------------------
# High-level decoder
# ---------------------------------------------------------------------------


def jsfuck_decode(code):
    """Decode JSFuck-encoded JavaScript. Returns decoded string or None."""
    if not code or not code.strip():
        return None

    import sys
    old_limit = sys.getrecursionlimit()
    try:
        # JSFuck can be deeply nested; temporarily raise the limit
        sys.setrecursionlimit(max(old_limit, 10000))

        tokens = _tokenize(code)
        if not tokens:
            return None

        parser = _Parser(tokens)
        parser.parse()

        if parser.captured:
            return parser.captured
        return None
    except (_ParseError, RecursionError, MemoryError):
        return None
    except Exception:
        return None
    finally:
        sys.setrecursionlimit(old_limit)
