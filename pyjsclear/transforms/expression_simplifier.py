"""Evaluate static unary/binary expressions to literals."""

import math

from ..traverser import traverse
from ..utils.ast_helpers import is_literal, make_literal
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
            if (
                is_literal(cons)
                and cons.get('value') is False
                and is_literal(alt)
                and alt.get('value') is True
            ):
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
        op = node.get('operator', '')
        if op not in _RESOLVABLE_UNARY:
            return None
        # Skip negative numeric literals (already in normal form)
        if (
            op == '-'
            and is_literal(node.get('argument'))
            and isinstance(node['argument'].get('value'), (int, float))
        ):
            return None

        arg = node.get('argument')
        arg = self._simplify_expr(arg)
        val, ok = self._get_resolvable_value(arg)
        if not ok:
            return None

        try:
            result = self._apply_unary(op, val)
        except Exception:
            return None
        return self._value_to_node(result)

    def _simplify_binary(self, node):
        op = node.get('operator', '')
        if op not in _RESOLVABLE_BINARY:
            return None

        left = self._simplify_expr(node.get('left'))
        right = self._simplify_expr(node.get('right'))

        lval, lok = self._get_resolvable_value(left)
        rval, rok = self._get_resolvable_value(right)

        if not (lok and rok):
            # Convert x - (-y) to x + y
            if op == '-' and self._is_negative_numeric(right):
                node['right'] = right['argument']
                node['operator'] = '+'
                return node
            return None

        try:
            result = self._apply_binary(op, lval, rval)
        except Exception:
            return None
        return self._value_to_node(result)

    def _simplify_expr(self, node):
        if not isinstance(node, dict):
            return node
        match node.get('type', ''):
            case 'UnaryExpression':
                r = self._simplify_unary(node)
                return r if r is not None else node
            case 'BinaryExpression':
                r = self._simplify_binary(node)
                return r if r is not None else node
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
                val = node.get('value')
                # Literal with value None is JS null, not undefined
                return (_JS_NULL if val is None else val), True
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

    def _apply_unary(self, op, val):
        match op:
            case '-':
                return -self._js_to_number(val)
            case '+':
                return self._js_to_number(val)
            case '!':
                return not self._js_truthy(val)
            case '~':
                n = self._js_to_number(val)
                if isinstance(n, float) and math.isnan(n):
                    return -1  # ~NaN → -1
                return ~int(n)
            case 'typeof':
                return self._js_typeof(val)
            case 'void':
                return None  # JS undefined

    def _apply_binary(self, op, left, right):
        match op:
            case '+':
                if isinstance(left, str) or isinstance(right, str):
                    return self._js_to_string(left) + self._js_to_string(right)
                return self._js_to_number(left) + self._js_to_number(right)
            case '-':
                return self._js_to_number(left) - self._js_to_number(right)
            case '*':
                return self._js_to_number(left) * self._js_to_number(right)
            case '/':
                r = self._js_to_number(right)
                if r == 0:
                    raise ValueError('division by zero')
                return self._js_to_number(left) / r
            case '%':
                r = self._js_to_number(right)
                if r == 0:
                    raise ValueError('mod by zero')
                return self._js_to_number(left) % r
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
                l = self._js_to_int32(left) & 0xFFFFFFFF
                r = self._js_to_int32(right) & 31
                return l >> r
            case '==' | '!=':
                eq = self._js_abstract_eq(left, right)
                return eq if op == '==' else not eq
            case '===' | '!==':
                eq = self._js_strict_eq(left, right)
                return eq if op == '===' else not eq
            case '<':
                return self._js_compare(left, right) < 0
            case '<=':
                return self._js_compare(left, right) <= 0
            case '>':
                return self._js_compare(left, right) > 0
            case '>=':
                return self._js_compare(left, right) >= 0
            case _:
                raise ValueError(f'Unknown operator: {op}')

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

    def _js_truthy(self, val):
        if val is None or val is _JS_NULL:
            return False
        match val:
            case bool():
                return val
            case int() | float():
                return val != 0 and not (isinstance(val, float) and math.isnan(val))
            case str():
                return len(val) > 0
            case list() | dict():
                return True
            case _:
                return bool(val)

    def _js_typeof(self, val):
        if val is _JS_NULL:
            return 'object'  # typeof null === 'object' in JS
        if val is None:
            return 'undefined'
        match val:
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

    def _js_to_int32(self, val):
        """Coerce to 32-bit integer (for bitwise ops)."""
        return int(self._js_to_number(val))

    def _js_to_number(self, val):
        if val is _JS_NULL:
            return 0  # Number(null) → 0
        if val is None:
            return float('nan')  # Number(undefined) → NaN
        match val:
            case bool():
                return 1 if val else 0
            case int() | float():
                return val
            case str():
                try:
                    return (
                        int(val)
                        if val.isdigit() or (val.startswith('-') and val[1:].isdigit())
                        else float(val)
                    )
                except (ValueError, IndexError):
                    return 0
            case list():
                return 0
            case _:
                return 0

    def _js_to_string(self, val):
        if val is _JS_NULL:
            return 'null'
        if val is None:
            return 'undefined'
        match val:
            case bool():
                return 'true' if val else 'false'
            case int() | float():
                if isinstance(val, float) and val == int(val):
                    return str(int(val))
                return str(val)
            case str():
                return val
            case list():
                return ''
            case dict():
                return '[object Object]'
            case _:
                return str(val)

    def _js_compare(self, left, right):
        # JS compares strings lexicographically, not numerically
        if isinstance(left, str) and isinstance(right, str):
            if left < right:
                return -1
            if left > right:
                return 1
            return 0
        l = self._js_to_number(left)
        r = self._js_to_number(right)
        # NaN comparisons always return false in JS; returning NaN
        # ensures < <= > >= all evaluate to False in the caller.
        if isinstance(l, float) and math.isnan(l):
            return float('nan')
        if isinstance(r, float) and math.isnan(r):
            return float('nan')
        if l < r:
            return -1
        if l > r:
            return 1
        return 0

    def _value_to_node(self, val):
        if val is _JS_NULL:
            return make_literal(None)  # null literal
        if val is None:
            return {'type': 'Identifier', 'name': 'undefined'}
        if isinstance(val, bool):
            return make_literal(val)
        if isinstance(val, (int, float)):
            if isinstance(val, float) and (val != val or math.isinf(val)):
                return None
            if val < 0:
                return {
                    'type': 'UnaryExpression',
                    'operator': '-',
                    'prefix': True,
                    'argument': make_literal(abs(val)),
                }
            return make_literal(val)
        if isinstance(val, str):
            return make_literal(val)
        return None
