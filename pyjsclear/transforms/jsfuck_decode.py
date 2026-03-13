"""Pure Python JSFuck decoder.

JSFuck encodes JavaScript using only []()!+ characters.
It exploits JS type coercion to build strings and execute code via Function().
This decoder evaluates the JSFuck expression subset and captures the
string passed to Function().
"""

from enum import StrEnum


class _JSType(StrEnum):
    ARRAY = 'array'
    BOOL = 'bool'
    NUMBER = 'number'
    STRING = 'string'
    UNDEFINED = 'undefined'
    OBJECT = 'object'
    FUNCTION = 'function'


def is_jsfuck(code: str) -> bool:
    """Check if code is JSFuck-encoded.

    JSFuck code consists only of []()!+ characters (with optional whitespace/semicolons).
    We also require minimum length to avoid false positives.
    """
    stripped = code.strip()
    if len(stripped) < 100:
        return False
    # Only count the six JSFuck operator characters — whitespace and
    # semicolons are not distinctive and inflate the ratio on minified JS.
    jsfuck_chars = set('[]()!+')
    jsfuck_count = sum(1 for character in stripped if character in jsfuck_chars)
    return jsfuck_count / len(stripped) > 0.95


# ---------------------------------------------------------------------------
# JSValue: models a JavaScript value with JS-like coercion semantics
# ---------------------------------------------------------------------------


class _JSValue:
    """A JavaScript value with type coercion semantics."""

    __slots__ = ('val', 'type')

    def __init__(self, val: object, js_type: _JSType | str) -> None:
        self.val = val
        self.type = js_type

    # -- coercion helpers ---------------------------------------------------

    def to_number(self) -> int | float:
        match self.type:
            case _JSType.NUMBER:
                return self.val
            case _JSType.BOOL:
                return 1 if self.val else 0
            case _JSType.STRING:
                stripped = self.val.strip()
                if stripped == '':
                    return 0
                try:
                    return int(stripped)
                except ValueError:
                    try:
                        return float(stripped)
                    except ValueError:
                        return float('nan')
            case _JSType.ARRAY:
                if len(self.val) == 0:
                    return 0
                if len(self.val) == 1:
                    return _JSValue(self.val[0], _guess_type(self.val[0])).to_number()
                return float('nan')
            case _JSType.UNDEFINED:
                return float('nan')
            case _:
                return float('nan')

    def to_string(self) -> str:
        match self.type:
            case _JSType.STRING:
                return self.val
            case _JSType.NUMBER:
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
            case _JSType.BOOL:
                return 'true' if self.val else 'false'
            case _JSType.ARRAY:
                parts = []
                for item in self.val:
                    if item is None:
                        parts.append('')
                    elif isinstance(item, _JSValue):
                        parts.append(item.to_string())
                    else:
                        parts.append(_JSValue(item, _guess_type(item)).to_string())
                return ','.join(parts)
            case _JSType.UNDEFINED:
                return 'undefined'
            case _JSType.OBJECT:
                return '[object Object]'
            case _:
                return str(self.val)

    def to_bool(self) -> bool:
        match self.type:
            case _JSType.BOOL:
                return self.val
            case _JSType.NUMBER:
                return self.val != 0 and self.val == self.val  # 0 and NaN are falsy
            case _JSType.STRING:
                return len(self.val) > 0
            case _JSType.ARRAY:
                return True  # arrays are always truthy in JS
            case _JSType.UNDEFINED:
                return False
            case _JSType.OBJECT:
                return True
            case _:
                return bool(self.val)

    def get_property(self, key: '_JSValue') -> '_JSValue':
        """Property access: self[key]."""
        key_string = key.to_string() if isinstance(key, _JSValue) else str(key)

        match self.type:
            case _JSType.STRING:
                return _get_string_property(self, key_string)
            case _JSType.ARRAY:
                return _get_array_property(self, key_string)
            case _JSType.NUMBER:
                if key_string == 'constructor':
                    return _NUMBER_CONSTRUCTOR
                if key_string == 'toString':
                    return _JSValue('toString', _JSType.FUNCTION)
                return _JSValue(None, _JSType.UNDEFINED)
            case _JSType.BOOL:
                if key_string == 'constructor':
                    return _BOOLEAN_CONSTRUCTOR
                return _JSValue(None, _JSType.UNDEFINED)
            case _JSType.FUNCTION:
                if key_string == 'constructor':
                    return _FUNCTION_CONSTRUCTOR
                return _JSValue(None, _JSType.UNDEFINED)
            case _JSType.OBJECT:
                if key_string == 'constructor':
                    return _OBJECT_CONSTRUCTOR
                return _JSValue(None, _JSType.UNDEFINED)
            case _:
                return _JSValue(None, _JSType.UNDEFINED)

    def __repr__(self) -> str:
        return f'_JSValue({self.val!r}, {self.type!r})'


def _get_string_property(string_value: '_JSValue', key_string: str) -> '_JSValue':
    """Return the result of property access on a string value."""
    try:
        index = int(key_string)
        if 0 <= index < len(string_value.val):
            return _JSValue(string_value.val[index], _JSType.STRING)
    except (ValueError, IndexError):
        pass
    if key_string == 'length':
        return _JSValue(len(string_value.val), _JSType.NUMBER)
    if key_string == 'constructor':
        return _STRING_CONSTRUCTOR
    return _get_string_method(key_string)


def _get_array_property(array_value: '_JSValue', key_string: str) -> '_JSValue':
    """Return the result of property access on an array value."""
    try:
        index = int(key_string)
        if 0 <= index < len(array_value.val):
            item = array_value.val[index]
            if isinstance(item, _JSValue):
                return item
            return _JSValue(item, _guess_type(item))
    except (ValueError, IndexError):
        pass
    if key_string == 'length':
        return _JSValue(len(array_value.val), _JSType.NUMBER)
    if key_string == 'constructor':
        return _ARRAY_CONSTRUCTOR
    # Array methods that JSFuck commonly accesses
    if key_string in (
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
        return _JSValue(key_string, _JSType.FUNCTION)
    return _JSValue(None, _JSType.UNDEFINED)


def _guess_type(value: object) -> _JSType:
    if isinstance(value, bool):
        return _JSType.BOOL
    if isinstance(value, (int, float)):
        return _JSType.NUMBER
    if isinstance(value, str):
        return _JSType.STRING
    if isinstance(value, list):
        return _JSType.ARRAY
    if value is None:
        return _JSType.UNDEFINED
    return _JSType.OBJECT


def _get_string_method(method_name: str) -> '_JSValue':
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
        return _JSValue(method_name, _JSType.FUNCTION)
    return _JSValue(None, _JSType.UNDEFINED)


# Sentinel constructors for property chain resolution
_STRING_CONSTRUCTOR = _JSValue('String', _JSType.FUNCTION)
_NUMBER_CONSTRUCTOR = _JSValue('Number', _JSType.FUNCTION)
_BOOLEAN_CONSTRUCTOR = _JSValue('Boolean', _JSType.FUNCTION)
_ARRAY_CONSTRUCTOR = _JSValue('Array', _JSType.FUNCTION)
_OBJECT_CONSTRUCTOR = _JSValue('Object', _JSType.FUNCTION)
_FUNCTION_CONSTRUCTOR = _JSValue('Function', _JSType.FUNCTION)

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


def _tokenize(code: str) -> list[str]:
    """Tokenize JSFuck code into a list of characters/tokens."""
    tokens = []
    for character in code:
        if character in '[]()!+':
            tokens.append(character)
        # Skip whitespace, semicolons
    return tokens


# ---------------------------------------------------------------------------
# Iterative parser/evaluator (state-machine with explicit continuation stack)
# ---------------------------------------------------------------------------

# Parse states
_S_EXPR = 0
_S_UNARY = 1
_S_POSTFIX = 2
_S_PRIMARY = 3
_S_RESUME = 4

# Continuation types
_K_DONE = 0
_K_EXPR_LOOP = 1
_K_EXPR_ADD = 2
_K_UNARY_APPLY = 3
_K_POSTFIX_LOOP = 4
_K_POSTFIX_BRACKET = 5
_K_POSTFIX_ARGDONE = 6
_K_PAREN_CLOSE = 7
_K_ARRAY_ELEM = 8


class _Parser:
    """Iterative state-machine parser for JSFuck expressions.

    Replaces mutual recursion (_expression → _unary → _postfix → _primary →
    _expression) with an explicit value stack and continuation stack, so
    arbitrarily deep nesting never overflows the Python call stack.
    """

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.captured: str | None = None  # Result from Function(body)()

    def peek(self) -> str | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected: str | None = None) -> str:
        if self.pos >= len(self.tokens):
            raise _ParseError('Unexpected end of input')
        token = self.tokens[self.pos]
        if expected is not None and token != expected:
            raise _ParseError(f'Expected {expected!r}, got {token!r}')
        self.pos += 1
        return token

    # ------------------------------------------------------------------

    def parse(self) -> _JSValue:
        """Parse and evaluate the full expression (iterative)."""
        value_stack: list[_JSValue] = []
        continuation: list[tuple] = [(_K_DONE,)]
        state = _S_EXPR

        while True:
            if state == _S_EXPR:
                # expression = unary ('+' unary)*
                continuation.append((_K_EXPR_LOOP,))
                state = _S_UNARY

            elif state == _S_UNARY:
                # Collect prefix operators, then parse postfix
                operators = []
                while self.peek() in ('!', '+'):
                    operators.append(self.consume())
                continuation.append((_K_UNARY_APPLY, operators))
                state = _S_POSTFIX

            elif state == _S_POSTFIX:
                # Parse primary, then handle postfix [ ] and ( )
                continuation.append((_K_POSTFIX_LOOP, None))  # receiver=None
                state = _S_PRIMARY

            elif state == _S_PRIMARY:
                token = self.peek()
                if token == '(':
                    self.consume('(')
                    continuation.append((_K_PAREN_CLOSE,))
                    state = _S_EXPR
                elif token == '[':
                    self.consume('[')
                    if self.peek() == ']':
                        self.consume(']')
                        value_stack.append(_JSValue([], _JSType.ARRAY))
                        state = _S_RESUME
                    else:
                        continuation.append((_K_ARRAY_ELEM, []))
                        state = _S_EXPR
                else:
                    raise _ParseError(
                        f'Unexpected token: {token!r} at pos {self.pos}')

            elif state == _S_RESUME:
                continuation_frame = continuation.pop()
                continuation_type = continuation_frame[0]

                if continuation_type == _K_DONE:
                    return value_stack.pop()

                elif continuation_type == _K_PAREN_CLOSE:
                    self.consume(')')
                    state = _S_RESUME

                elif continuation_type == _K_ARRAY_ELEM:
                    elements = continuation_frame[1]
                    elements.append(value_stack.pop())
                    if self.peek() not in (']', None):
                        continuation.append((_K_ARRAY_ELEM, elements))
                        state = _S_EXPR
                    else:
                        self.consume(']')
                        value_stack.append(_JSValue(elements, _JSType.ARRAY))
                        state = _S_RESUME

                elif continuation_type == _K_POSTFIX_LOOP:
                    receiver = continuation_frame[1]
                    current_value = value_stack[-1]
                    if self.peek() == '[':
                        self.consume('[')
                        value_stack.pop()
                        continuation.append((_K_POSTFIX_BRACKET, current_value))
                        state = _S_EXPR
                    elif self.peek() == '(':
                        self.consume('(')
                        if self.peek() == ')':
                            self.consume(')')
                            value_stack.pop()
                            result = self._call(current_value, [], receiver)
                            value_stack.append(result)
                            continuation.append((_K_POSTFIX_LOOP, None))
                            state = _S_RESUME
                        else:
                            value_stack.pop()
                            continuation.append((_K_POSTFIX_ARGDONE, current_value, receiver))
                            state = _S_EXPR
                    else:
                        # No more postfix ops
                        state = _S_RESUME

                elif continuation_type == _K_POSTFIX_BRACKET:
                    parent_value = continuation_frame[1]
                    key = value_stack.pop()
                    self.consume(']')
                    value_stack.append(parent_value.get_property(key))
                    continuation.append((_K_POSTFIX_LOOP, parent_value))
                    state = _S_RESUME

                elif continuation_type == _K_POSTFIX_ARGDONE:
                    func = continuation_frame[1]
                    receiver = continuation_frame[2]
                    argument = value_stack.pop()
                    self.consume(')')
                    result = self._call(func, [argument], receiver)
                    value_stack.append(result)
                    continuation.append((_K_POSTFIX_LOOP, None))
                    state = _S_RESUME

                elif continuation_type == _K_UNARY_APPLY:
                    operators = continuation_frame[1]
                    current_value = value_stack.pop()
                    for operator in reversed(operators):
                        if operator == '!':
                            current_value = _JSValue(not current_value.to_bool(), _JSType.BOOL)
                        elif operator == '+':
                            current_value = _JSValue(current_value.to_number(), _JSType.NUMBER)
                    value_stack.append(current_value)
                    state = _S_RESUME

                elif continuation_type == _K_EXPR_LOOP:
                    if self.peek() == '+':
                        self.consume('+')
                        left = value_stack.pop()
                        continuation.append((_K_EXPR_ADD, left))
                        state = _S_UNARY
                    else:
                        state = _S_RESUME

                elif continuation_type == _K_EXPR_ADD:
                    left = continuation_frame[1]
                    right = value_stack.pop()
                    value_stack.append(_js_add(left, right))
                    continuation.append((_K_EXPR_LOOP,))
                    state = _S_RESUME

    # ------------------------------------------------------------------

    def _call(self, func: _JSValue, args: list[_JSValue], receiver: _JSValue | None = None) -> _JSValue:
        """Handle function call semantics.

        Only single-argument calls are supported (e.g. Function(body),
        toString(radix)).  This is sufficient for JSFuck which never
        emits multi-argument calls.
        """
        # Function constructor: Function(body) returns a new function
        if func.type == _JSType.FUNCTION and func.val == 'Function':
            if args:
                body = args[-1].to_string()
                return _JSValue(('__function_body__', body), _JSType.FUNCTION)

        # Calling a function created by Function(body)
        if func.type == _JSType.FUNCTION and isinstance(func.val, tuple):
            if func.val[0] == '__function_body__':
                self.captured = func.val[1]
                return _JSValue(None, _JSType.UNDEFINED)

        # Constructor property access — e.g., []["flat"]["constructor"]
        if func.type == _JSType.FUNCTION and isinstance(func.val, str):
            name = func.val
            if name in _CONSTRUCTOR_MAP:
                if args:
                    return _JSValue(args[0].to_string(), _JSType.STRING)
                return _JSValue('', _JSType.STRING)

            if name == 'italics':
                return _JSValue('<i></i>', _JSType.STRING)
            if name == 'fontcolor':
                return _JSValue('<font color="undefined"></font>', _JSType.STRING)

            # toString with radix — e.g., (10)["toString"](36) → "a"
            if name == 'toString' and args and receiver is not None:
                radix = args[0].to_number()
                if isinstance(radix, (int, float)) and radix == int(radix):
                    radix = int(radix)
                    if 2 <= radix <= 36 and receiver.type == _JSType.NUMBER:
                        num = receiver.to_number()
                        if isinstance(num, (int, float)) and num == int(num):
                            return _JSValue(_int_to_base(int(num), radix), _JSType.STRING)

        return _JSValue(None, _JSType.UNDEFINED)


def _js_add(left: _JSValue, right: _JSValue) -> _JSValue:
    """JS + operator with type coercion."""
    if left.type == _JSType.STRING or right.type == _JSType.STRING:
        return _JSValue(left.to_string() + right.to_string(), _JSType.STRING)
    if left.type in (_JSType.ARRAY, _JSType.OBJECT) or right.type in (_JSType.ARRAY, _JSType.OBJECT):
        return _JSValue(left.to_string() + right.to_string(), _JSType.STRING)
    return _JSValue(left.to_number() + right.to_number(), _JSType.NUMBER)


def _int_to_base(num: int, base: int) -> str:
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


def jsfuck_decode(code: str) -> str | None:
    """Decode JSFuck-encoded JavaScript. Returns decoded string or None."""
    if not code or not code.strip():
        return None

    try:
        tokens = _tokenize(code)
        if not tokens:
            return None

        parser = _Parser(tokens)
        parser.parse()

        if parser.captured:
            return parser.captured
        return None
    except (_ParseError, MemoryError, IndexError, ValueError, TypeError,
            KeyError, OverflowError):
        return None
