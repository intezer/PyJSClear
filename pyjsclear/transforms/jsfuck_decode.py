"""Pure Python JSFuck decoder.

JSFuck encodes JavaScript using only []()!+ characters.
It exploits JS type coercion to build strings and execute code via Function().
This decoder evaluates the JSFuck expression subset and captures the
string passed to Function().
"""

from enum import IntEnum
from enum import StrEnum


class _JSType(StrEnum):
    """JavaScript value types for coercion semantics."""

    ARRAY = 'array'
    BOOL = 'bool'
    NUMBER = 'number'
    STRING = 'string'
    UNDEFINED = 'undefined'
    OBJECT = 'object'
    FUNCTION = 'function'


class _ParseState(IntEnum):
    """State-machine states for the iterative parser."""

    EXPR = 0
    UNARY = 1
    POSTFIX = 2
    PRIMARY = 3
    RESUME = 4


class _ContinuationType(IntEnum):
    """Continuation frame types for the parser stack."""

    DONE = 0
    EXPR_LOOP = 1
    EXPR_ADD = 2
    UNARY_APPLY = 3
    POSTFIX_LOOP = 4
    POSTFIX_BRACKET = 5
    POSTFIX_ARGDONE = 6
    PAREN_CLOSE = 7
    ARRAY_ELEM = 8


_JSFUCK_OPERATORS = frozenset('[]()!+')

_ARRAY_METHODS = frozenset(
    {
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
    }
)

_STRING_METHODS = frozenset(
    {
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
    }
)


class _ParseError(Exception):
    """Raised when JSFuck parsing encounters invalid syntax."""


def is_jsfuck(code: str) -> bool:
    """Check if code is JSFuck-encoded.

    JSFuck code consists only of []()!+ characters (with optional whitespace/semicolons).
    We also require minimum length to avoid false positives.
    """
    stripped = code.strip()
    if len(stripped) < 100:
        return False
    # Only count JSFuck operator characters; whitespace/semicolons inflate the ratio
    jsfuck_count = sum(1 for character in stripped if character in _JSFUCK_OPERATORS)
    return jsfuck_count / len(stripped) > 0.95


class _JSValue:
    """A JavaScript value with type coercion semantics."""

    __slots__ = ('value', 'type')

    def __init__(self, value: object, js_type: _JSType | str) -> None:
        self.value = value
        self.type = js_type

    def to_number(self) -> int | float:
        """Coerce this value to a JS number."""
        match self.type:
            case _JSType.NUMBER:
                return self.value
            case _JSType.BOOL:
                return 1 if self.value else 0
            case _JSType.STRING:
                stripped = self.value.strip()
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
                if len(self.value) == 0:
                    return 0
                if len(self.value) == 1:
                    return _JSValue(self.value[0], _guess_type(self.value[0])).to_number()
                return float('nan')
            case _JSType.UNDEFINED:
                return float('nan')
            case _:
                return float('nan')

    def to_string(self) -> str:
        """Coerce this value to a JS string."""
        match self.type:
            case _JSType.STRING:
                return self.value
            case _JSType.NUMBER:
                if isinstance(self.value, float):
                    if self.value != self.value:  # NaN
                        return 'NaN'
                    if self.value == float('inf'):
                        return 'Infinity'
                    if self.value == float('-inf'):
                        return '-Infinity'
                    if self.value == int(self.value):
                        return str(int(self.value))
                    return str(self.value)
                return str(self.value)
            case _JSType.BOOL:
                return 'true' if self.value else 'false'
            case _JSType.ARRAY:
                parts = []
                for item in self.value:
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
                return str(self.value)

    def to_bool(self) -> bool:
        """Coerce this value to a JS boolean."""
        match self.type:
            case _JSType.BOOL:
                return self.value
            case _JSType.NUMBER:
                return self.value != 0 and self.value == self.value  # 0 and NaN are falsy
            case _JSType.STRING:
                return len(self.value) > 0
            case _JSType.ARRAY:
                return True  # arrays are always truthy in JS
            case _JSType.UNDEFINED:
                return False
            case _JSType.OBJECT:
                return True
            case _:
                return bool(self.value)

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
        return f'_JSValue({self.value!r}, {self.type!r})'


def _get_string_property(string_value: '_JSValue', key_string: str) -> '_JSValue':
    """Return the result of property access on a string value."""
    try:
        index = int(key_string)
        if 0 <= index < len(string_value.value):
            return _JSValue(string_value.value[index], _JSType.STRING)
    except (ValueError, IndexError):
        pass
    if key_string == 'length':
        return _JSValue(len(string_value.value), _JSType.NUMBER)
    if key_string == 'constructor':
        return _STRING_CONSTRUCTOR
    return _get_string_method(key_string)


def _get_array_property(array_value: '_JSValue', key_string: str) -> '_JSValue':
    """Return the result of property access on an array value."""
    try:
        index = int(key_string)
        if 0 <= index < len(array_value.value):
            item = array_value.value[index]
            if isinstance(item, _JSValue):
                return item
            return _JSValue(item, _guess_type(item))
    except (ValueError, IndexError):
        pass
    if key_string == 'length':
        return _JSValue(len(array_value.value), _JSType.NUMBER)
    if key_string == 'constructor':
        return _ARRAY_CONSTRUCTOR
    if key_string in _ARRAY_METHODS:
        return _JSValue(key_string, _JSType.FUNCTION)
    return _JSValue(None, _JSType.UNDEFINED)


def _guess_type(value: object) -> _JSType:
    """Infer the _JSType for a raw Python value."""
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
    if method_name in _STRING_METHODS:
        return _JSValue(method_name, _JSType.FUNCTION)
    return _JSValue(None, _JSType.UNDEFINED)


_STRING_CONSTRUCTOR = _JSValue('String', _JSType.FUNCTION)
_NUMBER_CONSTRUCTOR = _JSValue('Number', _JSType.FUNCTION)
_BOOLEAN_CONSTRUCTOR = _JSValue('Boolean', _JSType.FUNCTION)
_ARRAY_CONSTRUCTOR = _JSValue('Array', _JSType.FUNCTION)
_OBJECT_CONSTRUCTOR = _JSValue('Object', _JSType.FUNCTION)
_FUNCTION_CONSTRUCTOR = _JSValue('Function', _JSType.FUNCTION)

_CONSTRUCTOR_MAP = {
    'String': _STRING_CONSTRUCTOR,
    'Number': _NUMBER_CONSTRUCTOR,
    'Boolean': _BOOLEAN_CONSTRUCTOR,
    'Array': _ARRAY_CONSTRUCTOR,
    'Object': _OBJECT_CONSTRUCTOR,
    'Function': _FUNCTION_CONSTRUCTOR,
}


def _tokenize(code: str) -> list[str]:
    """Extract JSFuck operator characters, discarding whitespace and semicolons."""
    return [character for character in code if character in _JSFUCK_OPERATORS]


class _Parser:
    """Iterative state-machine parser for JSFuck expressions.

    Replaces mutual recursion (_expression → _unary → _postfix → _primary →
    _expression) with an explicit value stack and continuation stack, so
    arbitrarily deep nesting never overflows the Python call stack.
    """

    def __init__(self, tokens: list[str]) -> None:
        """Initialize parser with tokenized JSFuck input."""
        self.tokens = tokens
        self.pos: int = 0
        self.captured: str | None = None
        self._resume_state: _ParseState = _ParseState.RESUME

    def peek(self) -> str | None:
        """Return the current token without advancing, or None at end."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected: str | None = None) -> str:
        """Advance past the current token and return it, optionally asserting its value."""
        if self.pos >= len(self.tokens):
            raise _ParseError('Unexpected end of input')
        token = self.tokens[self.pos]
        if expected is not None and token != expected:
            raise _ParseError(f'Expected {expected!r}, got {token!r}')
        self.pos += 1
        return token

    def parse(self) -> _JSValue:
        """Parse and evaluate the full expression (iterative)."""
        value_stack: list[_JSValue] = []
        continuation: list[tuple] = [(_ContinuationType.DONE,)]
        state = _ParseState.EXPR

        while True:
            match state:
                case _ParseState.EXPR:
                    continuation.append((_ContinuationType.EXPR_LOOP,))
                    state = _ParseState.UNARY

                case _ParseState.UNARY:
                    operators: list[str] = []
                    while self.peek() in ('!', '+'):
                        operators.append(self.consume())
                    continuation.append((_ContinuationType.UNARY_APPLY, operators))
                    state = _ParseState.POSTFIX

                case _ParseState.POSTFIX:
                    continuation.append((_ContinuationType.POSTFIX_LOOP, None))
                    state = _ParseState.PRIMARY

                case _ParseState.PRIMARY:
                    state = self._parse_primary(value_stack, continuation)

                case _ParseState.RESUME:
                    resume_result = self._handle_resume(value_stack, continuation)
                    if resume_result is not None:
                        return resume_result
                    state = self._resume_state

    def _parse_primary(
        self,
        value_stack: list['_JSValue'],
        continuation: list[tuple],
    ) -> _ParseState:
        """Handle primary expression parsing (parenthesized or array literal)."""
        token = self.peek()
        match token:
            case '(':
                self.consume('(')
                continuation.append((_ContinuationType.PAREN_CLOSE,))
                return _ParseState.EXPR
            case '[':
                self.consume('[')
                if self.peek() == ']':
                    self.consume(']')
                    value_stack.append(_JSValue([], _JSType.ARRAY))
                    return _ParseState.RESUME
                continuation.append((_ContinuationType.ARRAY_ELEM, []))
                return _ParseState.EXPR
            case _:
                raise _ParseError(f'Unexpected token: {token!r} at pos {self.pos}')

    def _handle_resume(
        self,
        value_stack: list['_JSValue'],
        continuation: list[tuple],
    ) -> _JSValue | None:
        """Process one continuation frame. Returns a value if parsing is complete."""
        continuation_frame = continuation.pop()
        continuation_type = continuation_frame[0]

        match continuation_type:
            case _ContinuationType.DONE:
                return value_stack.pop()

            case _ContinuationType.PAREN_CLOSE:
                self.consume(')')
                self._resume_state = _ParseState.RESUME

            case _ContinuationType.ARRAY_ELEM:
                elements = continuation_frame[1]
                elements.append(value_stack.pop())
                if self.peek() not in (']', None):
                    continuation.append((_ContinuationType.ARRAY_ELEM, elements))
                    self._resume_state = _ParseState.EXPR
                else:
                    self.consume(']')
                    value_stack.append(_JSValue(elements, _JSType.ARRAY))
                    self._resume_state = _ParseState.RESUME

            case _ContinuationType.POSTFIX_LOOP:
                self._handle_postfix_loop(continuation_frame, value_stack, continuation)

            case _ContinuationType.POSTFIX_BRACKET:
                parent_value = continuation_frame[1]
                key = value_stack.pop()
                self.consume(']')
                value_stack.append(parent_value.get_property(key))
                continuation.append((_ContinuationType.POSTFIX_LOOP, parent_value))
                self._resume_state = _ParseState.RESUME

            case _ContinuationType.POSTFIX_ARGDONE:
                function_value = continuation_frame[1]
                receiver = continuation_frame[2]
                argument = value_stack.pop()
                self.consume(')')
                result = self._call(function_value, [argument], receiver)
                value_stack.append(result)
                continuation.append((_ContinuationType.POSTFIX_LOOP, None))
                self._resume_state = _ParseState.RESUME

            case _ContinuationType.UNARY_APPLY:
                prefix_operators = continuation_frame[1]
                current_value = value_stack.pop()
                for operator in reversed(prefix_operators):
                    match operator:
                        case '!':
                            current_value = _JSValue(not current_value.to_bool(), _JSType.BOOL)
                        case '+':
                            current_value = _JSValue(current_value.to_number(), _JSType.NUMBER)
                value_stack.append(current_value)
                self._resume_state = _ParseState.RESUME

            case _ContinuationType.EXPR_LOOP:
                if self.peek() == '+':
                    self.consume('+')
                    left = value_stack.pop()
                    continuation.append((_ContinuationType.EXPR_ADD, left))
                    self._resume_state = _ParseState.UNARY
                else:
                    self._resume_state = _ParseState.RESUME

            case _ContinuationType.EXPR_ADD:
                left = continuation_frame[1]
                right = value_stack.pop()
                value_stack.append(_js_add(left, right))
                continuation.append((_ContinuationType.EXPR_LOOP,))
                self._resume_state = _ParseState.RESUME

        return None

    def _handle_postfix_loop(
        self,
        continuation_frame: tuple,
        value_stack: list['_JSValue'],
        continuation: list[tuple],
    ) -> None:
        """Handle postfix operators (bracket access and function calls)."""
        receiver = continuation_frame[1]
        current_value = value_stack[-1]
        match self.peek():
            case '[':
                self.consume('[')
                value_stack.pop()
                continuation.append((_ContinuationType.POSTFIX_BRACKET, current_value))
                self._resume_state = _ParseState.EXPR
            case '(':
                self.consume('(')
                if self.peek() == ')':
                    self.consume(')')
                    value_stack.pop()
                    result = self._call(current_value, [], receiver)
                    value_stack.append(result)
                    continuation.append((_ContinuationType.POSTFIX_LOOP, None))
                    self._resume_state = _ParseState.RESUME
                else:
                    value_stack.pop()
                    continuation.append((_ContinuationType.POSTFIX_ARGDONE, current_value, receiver))
                    self._resume_state = _ParseState.EXPR
            case _:
                self._resume_state = _ParseState.RESUME

    def _call(
        self,
        function_value: _JSValue,
        arguments: list[_JSValue],
        receiver: _JSValue | None = None,
    ) -> _JSValue:
        """Handle function call semantics for JSFuck's limited call patterns."""
        if function_value.type != _JSType.FUNCTION:
            return _JSValue(None, _JSType.UNDEFINED)

        # Function constructor: Function(body) returns a new function
        if function_value.value == 'Function' and arguments:
            body = arguments[-1].to_string()
            return _JSValue(('__function_body__', body), _JSType.FUNCTION)

        # Calling a function created by Function(body)
        if isinstance(function_value.value, tuple) and function_value.value[0] == '__function_body__':
            self.captured = function_value.value[1]
            return _JSValue(None, _JSType.UNDEFINED)

        if not isinstance(function_value.value, str):
            return _JSValue(None, _JSType.UNDEFINED)

        # Constructor property access -- e.g., []["flat"]["constructor"]
        function_name = function_value.value
        if function_name in _CONSTRUCTOR_MAP:
            if arguments:
                return _JSValue(arguments[0].to_string(), _JSType.STRING)
            return _JSValue('', _JSType.STRING)

        if function_name == 'italics':
            return _JSValue('<i></i>', _JSType.STRING)
        if function_name == 'fontcolor':
            return _JSValue('<font color="undefined"></font>', _JSType.STRING)

        # toString with radix -- e.g., (10)["toString"](36) -> "a"
        if function_name == 'toString' and arguments and receiver is not None:
            radix_value = arguments[0].to_number()
            if isinstance(radix_value, (int, float)) and radix_value == int(radix_value):
                radix = int(radix_value)
                if 2 <= radix <= 36 and receiver.type == _JSType.NUMBER:
                    receiver_number = receiver.to_number()
                    if isinstance(receiver_number, (int, float)) and receiver_number == int(receiver_number):
                        return _JSValue(_int_to_base(int(receiver_number), radix), _JSType.STRING)

        return _JSValue(None, _JSType.UNDEFINED)


def _js_add(left: _JSValue, right: _JSValue) -> _JSValue:
    """JS + operator with type coercion."""
    if left.type == _JSType.STRING or right.type == _JSType.STRING:
        return _JSValue(left.to_string() + right.to_string(), _JSType.STRING)
    if left.type in (_JSType.ARRAY, _JSType.OBJECT) or right.type in (_JSType.ARRAY, _JSType.OBJECT):
        return _JSValue(left.to_string() + right.to_string(), _JSType.STRING)
    return _JSValue(left.to_number() + right.to_number(), _JSType.NUMBER)


def _int_to_base(number: int, base: int) -> str:
    """Convert integer to string in given base (2-36), matching JS behavior."""
    if number == 0:
        return '0'
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    is_negative = number < 0
    remainder = abs(number)
    result: list[str] = []
    while remainder:
        result.append(digits[remainder % base])
        remainder //= base
    if is_negative:
        result.append('-')
    return ''.join(reversed(result))


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
    except (_ParseError, MemoryError, IndexError, ValueError, TypeError, KeyError, OverflowError):
        return None
