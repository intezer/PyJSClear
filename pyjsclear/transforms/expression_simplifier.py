"""Evaluate static unary/binary expressions to literals."""

from __future__ import annotations

import math
from typing import Any

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

    def execute(self) -> bool:
        """Run all expression simplification passes and return whether AST changed."""
        self._simplify_unary_binary()
        self._simplify_conditionals()
        self._simplify_awaits()
        self._simplify_comma_calls()
        self._simplify_method_calls()
        return self.has_changed()

    def _simplify_unary_binary(self) -> None:
        """Fold constant unary and binary expressions."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            match node.get('type', ''):
                case 'UnaryExpression':
                    result = self._simplify_unary(node)
                case 'BinaryExpression':
                    result = self._simplify_binary(node)
                case _:
                    return None
            if result is not None:
                self.set_changed()
                return result
            return None

        traverse(self.ast, {'enter': enter})

    def _simplify_conditionals(self) -> None:
        """Convert test ? false : true → !test."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            if node.get('type') != 'ConditionalExpression':
                return None
            consequent = node.get('consequent')
            alternate = node.get('alternate')
            if (
                is_literal(consequent)
                and consequent.get('value') is False
                and is_literal(alternate)
                and alternate.get('value') is True
            ):
                self.set_changed()
                return {
                    'type': 'UnaryExpression',
                    'operator': '!',
                    'prefix': True,
                    'argument': node['test'],
                }
            return None

        traverse(self.ast, {'enter': enter})

    def _simplify_awaits(self) -> None:
        """Simplify await (0x0, expr) → await expr."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            if node.get('type') != 'AwaitExpression':
                return
            argument = node.get('argument')
            if not isinstance(argument, dict) or argument.get('type') != 'SequenceExpression':
                return
            expressions = argument.get('expressions', [])
            if len(expressions) <= 1:
                return
            node['argument'] = expressions[-1]
            self.set_changed()

        traverse(self.ast, {'enter': enter})

    def _simplify_comma_calls(self) -> None:
        """Simplify (0, expr)(args) → expr(args)."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not isinstance(callee, dict) or callee.get('type') != 'SequenceExpression':
                return
            expressions = callee.get('expressions', [])
            if len(expressions) < 2:
                return
            # Only simplify when the leading expressions are side-effect-free literals
            for expression in expressions[:-1]:
                if not isinstance(expression, dict) or expression.get('type') != 'Literal':
                    return
            node['callee'] = expressions[-1]
            self.set_changed()

        traverse(self.ast, {'enter': enter})

    def _simplify_unary(self, node: dict) -> dict | None:
        """Fold a constant unary expression into a single literal node."""
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
        value, resolved = self._get_resolvable_value(argument)
        if not resolved:
            return None

        try:
            result = self._apply_unary(operator, value)
        except Exception:
            return None
        return self._value_to_node(result)

    def _simplify_binary(self, node: dict) -> dict | None:
        """Fold a constant binary expression into a single literal node."""
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

    def _simplify_expr(self, node: Any) -> Any:
        """Recursively simplify a sub-expression if it is unary or binary."""
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

    def _is_negative_numeric(self, node: Any) -> bool:
        """Check whether node is a unary-minus wrapping a numeric literal."""
        return (
            isinstance(node, dict)
            and node.get('type') == 'UnaryExpression'
            and node.get('operator') == '-'
            and is_literal(node.get('argument'))
            and isinstance(node['argument'].get('value'), (int, float))
        )

    def _get_resolvable_value(self, node: Any) -> tuple[Any, bool]:
        """Extract a Python value from a constant AST node, returning (value, resolved)."""
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
                argument = node.get('argument')
                if is_literal(argument) and isinstance(argument.get('value'), (int, float)):
                    return -argument['value'], True
            case 'Identifier' if node.get('name') == 'undefined':
                return None, True
            case 'ArrayExpression' if len(node.get('elements', [])) == 0:
                return [], True
            case 'ObjectExpression' if len(node.get('properties', [])) == 0:
                return {}, True
        return None, False

    def _apply_unary(self, operator: str, value: Any) -> Any:
        """Evaluate a JS unary operator on a resolved Python value."""
        match operator:
            case '-':
                return -self._js_to_number(value)
            case '+':
                return self._js_to_number(value)
            case '!':
                return not self._js_truthy(value)
            case '~':
                number = self._js_to_number(value)
                if isinstance(number, float) and math.isnan(number):
                    return -1  # ~NaN → -1
                return ~int(number)
            case 'typeof':
                return self._js_typeof(value)
            case 'void':
                return None  # JS undefined

    def _apply_binary(self, operator: str, left: Any, right: Any) -> Any:
        """Evaluate a JS binary operator on two resolved Python values."""
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
                divisor = self._js_to_number(right)
                if divisor == 0:
                    raise ValueError('division by zero')
                return self._js_to_number(left) / divisor
            case '%':
                modulus = self._js_to_number(right)
                if modulus == 0:
                    raise ValueError('mod by zero')
                return self._js_to_number(left) % modulus
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
                shift = self._js_to_int32(right) & 31
                return left_operand >> shift
            case '==' | '!=':
                equal = self._js_abstract_eq(left, right)
                return equal if operator == '==' else not equal
            case '===' | '!==':
                equal = self._js_strict_eq(left, right)
                return equal if operator == '===' else not equal
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

    def _js_abstract_eq(self, left: Any, right: Any) -> bool:
        """JS == (null and undefined are equal to each other only)."""
        if (left is None or left is _JS_NULL) and (right is None or right is _JS_NULL):
            return True
        if left is _JS_NULL or right is _JS_NULL:
            return False
        return left == right

    def _js_strict_eq(self, left: Any, right: Any) -> bool:
        """JS === (null !== undefined)."""
        if left is _JS_NULL:
            return right is _JS_NULL
        if right is _JS_NULL:
            return False
        return left == right and type(left) == type(right)

    def _js_truthy(self, value: Any) -> bool:
        """Return whether a JS value is truthy per JS coercion rules."""
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

    def _js_typeof(self, value: Any) -> str:
        """Return the JS typeof string for a resolved Python value."""
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

    def _js_to_int32(self, value: Any) -> int:
        """Coerce to 32-bit integer (for bitwise ops)."""
        return int(self._js_to_number(value))

    def _js_to_number(self, value: Any) -> int | float:
        """Coerce a Python value to a number following JS Number() semantics."""
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

    def _js_to_string(self, value: Any) -> str:
        """Coerce a Python value to a string following JS String() semantics."""
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

    def _js_compare(self, left: Any, right: Any) -> int | float:
        """Compare two JS values, returning -1/0/1 or NaN for uncomparable."""
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

    def _value_to_node(self, value: Any) -> dict | None:
        """Convert a resolved Python value back into an AST literal node."""
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

    def _simplify_method_calls(self) -> None:
        """Statically evaluate simple method calls on literals.

        Handles:
          Buffer.from([...nums...]).toString("utf8") → string literal
          (N).toString() → "N"
        """

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            if node.get('type') != 'CallExpression':
                return None
            callee = node.get('callee')
            if not isinstance(callee, dict) or callee.get('type') != 'MemberExpression':
                return None
            property_node = callee.get('property')
            if not property_node:
                return None
            method_name = property_node.get('name') if property_node.get('type') == 'Identifier' else None
            if not method_name:
                return None

            # (N).toString() → "N"
            if method_name == 'toString' and len(node.get('arguments', [])) == 0:
                object_node = callee.get('object')
                if is_numeric_literal(object_node):
                    numeric_value = object_node['value']
                    string_value = (
                        str(int(numeric_value))
                        if isinstance(numeric_value, float) and numeric_value == int(numeric_value)
                        else str(numeric_value)
                    )
                    self.set_changed()
                    return make_literal(string_value)

            # Buffer.from([...nums...]).toString(encoding) → string literal
            if method_name == 'toString' and len(node.get('arguments', [])) <= 1:
                result = self._try_eval_buffer_from_tostring(callee.get('object'), node.get('arguments', []))
                if result is not None:
                    self.set_changed()
                    return make_literal(result)

            return None

        traverse(self.ast, {'enter': enter})

    def _try_eval_buffer_from_tostring(self, object_node: Any, arguments: list) -> str | None:
        """Try to evaluate Buffer.from([...nums...]).toString(encoding)."""
        if not isinstance(object_node, dict) or object_node.get('type') != 'CallExpression':
            return None
        callee = object_node.get('callee')
        if not isinstance(callee, dict) or callee.get('type') != 'MemberExpression':
            return None
        # Check for Buffer.from
        buffer_object = callee.get('object')
        buffer_property = callee.get('property')
        if not (buffer_object and buffer_object.get('type') == 'Identifier' and buffer_object.get('name') == 'Buffer'):
            return None
        if not (
            buffer_property and buffer_property.get('type') == 'Identifier' and buffer_property.get('name') == 'from'
        ):
            return None
        # First arg must be an array of numbers
        call_args = object_node.get('arguments', [])
        if not call_args or call_args[0].get('type') != 'ArrayExpression':
            return None
        elements = call_args[0].get('elements', [])
        byte_values = []
        for element in elements:
            if not is_numeric_literal(element):
                return None
            element_value = element['value']
            if (
                not isinstance(element_value, (int, float))
                or element_value != int(element_value)
                or element_value < 0
                or element_value > 255
            ):
                return None
            byte_values.append(int(element_value))
        # Determine encoding for toString
        encoding = 'utf8'
        if arguments and is_literal(arguments[0]) and isinstance(arguments[0].get('value'), str):
            encoding = arguments[0]['value']
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
