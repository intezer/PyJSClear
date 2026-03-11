"""Evaluate static unary/binary expressions to literals."""

import math

from ..traverser import traverse
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import make_literal
from .base import Transform


# Sentinel to distinguish JS null (Literal value=None) from JS undefined
# (Identifier name='undefined'). Python None represents undefined.
_JS_NULL = object()

_RESOLVABLE_UNARY = {'-', '+', '!', '~', 'typeof', 'void'}
_RESOLVABLE_BINARY = {
    '==',
    '!=',
    '===',
    '!==',
    '<',
    '<=',
    '>',
    '>=',
    '<<',
    '>>',
    '>>>',
    '+',
    '-',
    '*',
    '/',
    '%',
    '**',
    '|',
    '^',
    '&',
}


class ExpressionSimplifier(Transform):
    """Simplify constant unary/binary expressions to literals."""

    def execute(self):
        self._simplify_unary_binary()
        self._simplify_conditionals()
        self._simplify_awaits()
        self._simplify_method_calls()
        return self.has_changed()

    def _simplify_unary_binary(self):
        """Fold constant unary and binary expressions."""

        def enter(node, parent, key, index):
            match node.get('type', ''):
                case 'UnaryExpression':
                    result = self._simplify_unary(node)
                case 'BinaryExpression':
                    result = self._simplify_binary(node)
                case _:
                    return
            if result is not None:
                self.set_changed()
                return result

        traverse(self.ast, {'enter': enter})

    def _simplify_conditionals(self):
        """Convert test ? false : true → !test."""

        def enter(node, parent, key, index):
            if node.get('type') != 'ConditionalExpression':
                return
            cons = node.get('consequent')
            alt = node.get('alternate')
            if is_literal(cons) and cons.get('value') is False and is_literal(alt) and alt.get('value') is True:
                self.set_changed()
                return {
                    'type': 'UnaryExpression',
                    'operator': '!',
                    'prefix': True,
                    'argument': node['test'],
                }

        traverse(self.ast, {'enter': enter})

    def _simplify_awaits(self):
        """Simplify await (0x0, expr) → await expr."""

        def enter(node, parent, key, index):
            if node.get('type') != 'AwaitExpression':
                return
            arg = node.get('argument')
            if not isinstance(arg, dict) or arg.get('type') != 'SequenceExpression':
                return
            exprs = arg.get('expressions', [])
            if len(exprs) <= 1:
                return
            node['argument'] = exprs[-1]
            self.set_changed()

        traverse(self.ast, {'enter': enter})

    def _simplify_unary(self, node):
        operator = node.get('operator', '')
        if operator not in _RESOLVABLE_UNARY:
            return None
        # Skip negative numeric literals (already in normal form)
        if (
            operator == '-'
            and is_literal(node.get('argument'))
            and isinstance(node['argument'].get('value'), (int, float))
        ):
            return None

        argument = node.get('argument')
        argument = self._simplify_expr(argument)
        value, ok = self._get_resolvable_value(argument)
        if not ok:
            return None

        try:
            result = self._apply_unary(operator, value)
        except Exception:
            return None
        return self._value_to_node(result)

    def _simplify_binary(self, node):
        operator = node.get('operator', '')
        if operator not in _RESOLVABLE_BINARY:
            return None

        left = self._simplify_expr(node.get('left'))
        right = self._simplify_expr(node.get('right'))

        left_value, left_resolved = self._get_resolvable_value(left)
        right_value, right_resolved = self._get_resolvable_value(right)

        if not (left_resolved and right_resolved):
            # Convert x - (-y) to x + y
            if operator == '-' and self._is_negative_numeric(right):
                node['right'] = right['argument']
                node['operator'] = '+'
                return node
            return None

        try:
            result = self._apply_binary(operator, left_value, right_value)
        except Exception:
            return None
        return self._value_to_node(result)

    def _simplify_expr(self, node):
        if not isinstance(node, dict):
            return node
        match node.get('type', ''):
            case 'UnaryExpression':
                result = self._simplify_unary(node)
                return result if result is not None else node
            case 'BinaryExpression':
                result = self._simplify_binary(node)
                return result if result is not None else node
        return node

    def _is_negative_numeric(self, node):
        return (
            isinstance(node, dict)
            and node.get('type') == 'UnaryExpression'
            and node.get('operator') == '-'
            and is_literal(node.get('argument'))
            and isinstance(node['argument'].get('value'), (int, float))
        )

    def _get_resolvable_value(self, node):
        if not isinstance(node, dict):
            return None, False
        match node.get('type', ''):
            case 'Literal':
                if node.get('regex'):
                    return None, False
                value = node.get('value')
                # Literal with value None is JS null, not undefined
                return (_JS_NULL if value is None else value), True
            case 'UnaryExpression' if node.get('operator') == '-':
                arg = node.get('argument')
                if is_literal(arg) and isinstance(arg.get('value'), (int, float)):
                    return -arg['value'], True
            case 'Identifier' if node.get('name') == 'undefined':
                return None, True
            case 'ArrayExpression' if len(node.get('elements', [])) == 0:
                return [], True
            case 'ObjectExpression' if len(node.get('properties', [])) == 0:
                return {}, True
        return None, False

    def _apply_unary(self, operator, value):
        match operator:
            case '-':
                return -self._js_to_number(value)
            case '+':
                return self._js_to_number(value)
            case '!':
                return not self._js_truthy(value)
            case '~':
                n = self._js_to_number(value)
                if isinstance(n, float) and math.isnan(n):
                    return -1  # ~NaN → -1
                return ~int(n)
            case 'typeof':
                return self._js_typeof(value)
            case 'void':
                return None  # JS undefined

    def _apply_binary(self, operator, left, right):
        match operator:
            case '+':
                if isinstance(left, str) or isinstance(right, str):
                    return self._js_to_string(left) + self._js_to_string(right)
                return self._js_to_number(left) + self._js_to_number(right)
            case '-':
                return self._js_to_number(left) - self._js_to_number(right)
            case '*':
                return self._js_to_number(left) * self._js_to_number(right)
            case '/':
                result = self._js_to_number(right)
                if result == 0:
                    raise ValueError('division by zero')
                return self._js_to_number(left) / result
            case '%':
                result = self._js_to_number(right)
                if result == 0:
                    raise ValueError('mod by zero')
                return self._js_to_number(left) % result
            case '**':
                return self._js_to_number(left) ** self._js_to_number(right)
            case '|':
                return self._js_to_int32(left) | self._js_to_int32(right)
            case '&':
                return self._js_to_int32(left) & self._js_to_int32(right)
            case '^':
                return self._js_to_int32(left) ^ self._js_to_int32(right)
            case '<<':
                return self._js_to_int32(left) << (self._js_to_int32(right) & 31)
            case '>>':
                return self._js_to_int32(left) >> (self._js_to_int32(right) & 31)
            case '>>>':
                left_operand = self._js_to_int32(left) & 0xFFFFFFFF
                result = self._js_to_int32(right) & 31
                return left_operand >> result
            case '==' | '!=':
                eq = self._js_abstract_eq(left, right)
                return eq if operator == '==' else not eq
            case '===' | '!==':
                eq = self._js_strict_eq(left, right)
                return eq if operator == '===' else not eq
            case '<':
                return self._js_compare(left, right) < 0
            case '<=':
                return self._js_compare(left, right) <= 0
            case '>':
                return self._js_compare(left, right) > 0
            case '>=':
                return self._js_compare(left, right) >= 0
            case _:
                raise ValueError(f'Unknown operator: {operator}')

    def _js_abstract_eq(self, left, right):
        """JS == (null and undefined are equal to each other only)."""
        if (left is None or left is _JS_NULL) and (right is None or right is _JS_NULL):
            return True
        if left is _JS_NULL or right is _JS_NULL:
            return False
        return left == right

    def _js_strict_eq(self, left, right):
        """JS === (null !== undefined)."""
        if left is _JS_NULL:
            return right is _JS_NULL
        if right is _JS_NULL:
            return False
        return left == right and type(left) == type(right)

    def _js_truthy(self, value):
        if value is None or value is _JS_NULL:
            return False
        match value:
            case bool():
                return value
            case int() | float():
                return value != 0 and not (isinstance(value, float) and math.isnan(value))
            case str():
                return len(value) > 0
            case list() | dict():
                return True
            case _:
                return bool(value)

    def _js_typeof(self, value):
        if value is _JS_NULL:
            return 'object'  # typeof null === 'object' in JS
        if value is None:
            return 'undefined'
        match value:
            case bool():
                return 'boolean'
            case int() | float():
                return 'number'
            case str():
                return 'string'
            case list() | dict():
                return 'object'
            case _:
                return 'undefined'

    def _js_to_int32(self, value):
        """Coerce to 32-bit integer (for bitwise ops)."""
        return int(self._js_to_number(value))

    def _js_to_number(self, value):
        if value is _JS_NULL:
            return 0  # Number(null) → 0
        if value is None:
            return float('nan')  # Number(undefined) → NaN
        match value:
            case bool():
                return 1 if value else 0
            case int() | float():
                return value
            case str():
                try:
                    return (
                        int(value)
                        if value.isdigit() or (value.startswith('-') and value[1:].isdigit())
                        else float(value)
                    )
                except (ValueError, IndexError):
                    return 0
            case list():
                return 0
            case _:
                return 0

    def _js_to_string(self, value):
        if value is _JS_NULL:
            return 'null'
        if value is None:
            return 'undefined'
        match value:
            case bool():
                return 'true' if value else 'false'
            case int() | float():
                return str(int(value)) if isinstance(value, float) and value == int(value) else str(value)
            case str():
                return value
            case list():
                return ''
            case dict():
                return '[object Object]'
            case _:
                return str(value)

    def _js_compare(self, left, right):
        # JS compares strings lexicographically, not numerically
        if isinstance(left, str) and isinstance(right, str):
            if left < right:
                return -1
            if left > right:
                return 1
            return 0
        left_num = self._js_to_number(left)
        right_num = self._js_to_number(right)
        # NaN comparisons always return false in JS; returning NaN
        # ensures < <= > >= all evaluate to False in the caller.
        if isinstance(left_num, float) and math.isnan(left_num):
            return float('nan')
        if isinstance(right_num, float) and math.isnan(right_num):
            return float('nan')
        if left_num < right_num:
            return -1
        if left_num > right_num:
            return 1
        return 0

    def _value_to_node(self, value):
        if value is _JS_NULL:
            return make_literal(None)  # null literal
        if value is None:
            return {'type': 'Identifier', 'name': 'undefined'}
        match value:
            case bool():
                return make_literal(value)
            case int() | float():
                if isinstance(value, float) and (value != value or math.isinf(value)):
                    return None
                if value < 0:
                    return {
                        'type': 'UnaryExpression',
                        'operator': '-',
                        'prefix': True,
                        'argument': make_literal(abs(value)),
                    }
                return make_literal(value)
            case str():
                return make_literal(value)
        return None

    def _simplify_method_calls(self):
        """Statically evaluate simple method calls on literals.

        Handles:
          Buffer.from([...nums...]).toString("utf8") → string literal
          (N).toString() → "N"
        """

        def enter(node, parent, key, index):
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not isinstance(callee, dict) or callee.get('type') != 'MemberExpression':
                return
            prop = callee.get('property')
            if not prop:
                return
            method_name = prop.get('name') if prop.get('type') == 'Identifier' else None
            if not method_name:
                return

            # (N).toString() → "N"
            if method_name == 'toString' and len(node.get('arguments', [])) == 0:
                obj = callee.get('object')
                if is_numeric_literal(obj):
                    val = obj['value']
                    s = str(int(val)) if isinstance(val, float) and val == int(val) else str(val)
                    self.set_changed()
                    return make_literal(s)

            # Buffer.from([...nums...]).toString(encoding) → string literal
            if method_name == 'toString' and len(node.get('arguments', [])) <= 1:
                result = self._try_eval_buffer_from_tostring(callee.get('object'), node.get('arguments', []))
                if result is not None:
                    self.set_changed()
                    return make_literal(result)

        traverse(self.ast, {'enter': enter})

    def _try_eval_buffer_from_tostring(self, obj, args):
        """Try to evaluate Buffer.from([...nums...]).toString(encoding)."""
        if not isinstance(obj, dict) or obj.get('type') != 'CallExpression':
            return None
        callee = obj.get('callee')
        if not isinstance(callee, dict) or callee.get('type') != 'MemberExpression':
            return None
        # Check for Buffer.from
        buf_obj = callee.get('object')
        buf_prop = callee.get('property')
        if not (buf_obj and buf_obj.get('type') == 'Identifier' and buf_obj.get('name') == 'Buffer'):
            return None
        if not (buf_prop and buf_prop.get('type') == 'Identifier' and buf_prop.get('name') == 'from'):
            return None
        # First arg must be an array of numbers
        call_args = obj.get('arguments', [])
        if not call_args or call_args[0].get('type') != 'ArrayExpression':
            return None
        elements = call_args[0].get('elements', [])
        byte_values = []
        for el in elements:
            if not is_numeric_literal(el):
                return None
            val = el['value']
            if not isinstance(val, (int, float)) or val != int(val) or val < 0 or val > 255:
                return None
            byte_values.append(int(val))
        # Determine encoding for toString
        encoding = 'utf8'
        if args and is_literal(args[0]) and isinstance(args[0].get('value'), str):
            encoding = args[0]['value']
        try:
            data = bytes(byte_values)
            if encoding in ('utf8', 'utf-8'):
                return data.decode('utf-8')
            if encoding == 'hex':
                return data.hex()
            if encoding in ('ascii', 'latin1', 'binary'):
                return data.decode(encoding)
        except (UnicodeDecodeError, ValueError):
            pass
        return None
