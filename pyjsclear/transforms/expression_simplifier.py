"""Evaluate static unary/binary expressions to literals."""

import math
from .base import Transform
from ..traverser import traverse
from ..utils.ast_helpers import is_literal, is_identifier, make_literal


_RESOLVABLE_UNARY = {'-', '+', '!', '~', 'typeof', 'void'}
_RESOLVABLE_BINARY = {
    '==', '!=', '===', '!==', '<', '<=', '>', '>=',
    '<<', '>>', '>>>', '+', '-', '*', '/', '%', '**',
    '|', '^', '&'
}


class ExpressionSimplifier(Transform):
    """Simplify constant unary/binary expressions to literals."""

    def execute(self):
        def enter(node, parent, key, index):
            ntype = node.get('type', '')
            if ntype == 'UnaryExpression':
                result = self._simplify_unary(node)
                if result is not None:
                    self.set_changed()
                    return result
            elif ntype == 'BinaryExpression':
                result = self._simplify_binary(node)
                if result is not None:
                    self.set_changed()
                    return result

        traverse(self.ast, {'enter': enter})

        # Simplify ConditionalExpression patterns:
        # test ? false : true → !test
        # test ? true : false → !!test (or just test if already boolean)
        def simplify_conditional(node, parent, key, index):
            if node.get('type') != 'ConditionalExpression':
                return
            cons = node.get('consequent')
            alt = node.get('alternate')
            if (is_literal(cons) and cons.get('value') is False and
                    is_literal(alt) and alt.get('value') is True):
                self.set_changed()
                return {
                    'type': 'UnaryExpression',
                    'operator': '!',
                    'prefix': True,
                    'argument': node['test']
                }
        traverse(self.ast, {'enter': simplify_conditional})

        # Simplify AwaitExpression with SequenceExpression argument:
        # await (0x0, expr) → await expr
        def simplify_await(node, parent, key, index):
            if (node.get('type') == 'AwaitExpression' and
                    isinstance(node.get('argument'), dict) and
                    node['argument'].get('type') == 'SequenceExpression'):
                exprs = node['argument'].get('expressions', [])
                if len(exprs) > 1:
                    node['argument'] = exprs[-1]
                    self.set_changed()
        traverse(self.ast, {'enter': simplify_await})

        return self.has_changed()

    def _simplify_unary(self, node):
        op = node.get('operator', '')
        if op not in _RESOLVABLE_UNARY:
            return None
        # Skip negative numeric literals (already in normal form)
        if op == '-' and is_literal(node.get('argument')) and isinstance(node['argument'].get('value'), (int, float)):
            return None

        arg = node.get('argument')
        # Try to simplify the argument first
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

        if lok and rok:
            try:
                result = self._apply_binary(op, lval, rval)
            except Exception:
                return None
            return self._value_to_node(result)

        # Convert x - (-y) to x + y
        if op == '-' and self._is_negative_numeric(right):
            node['right'] = right['argument']
            node['operator'] = '+'
            return node

        return None

    def _simplify_expr(self, node):
        if not isinstance(node, dict):
            return node
        ntype = node.get('type', '')
        if ntype == 'UnaryExpression':
            r = self._simplify_unary(node)
            return r if r is not None else node
        elif ntype == 'BinaryExpression':
            r = self._simplify_binary(node)
            return r if r is not None else node
        return node

    def _is_negative_numeric(self, node):
        return (isinstance(node, dict) and
                node.get('type') == 'UnaryExpression' and
                node.get('operator') == '-' and
                is_literal(node.get('argument')) and
                isinstance(node['argument'].get('value'), (int, float)))

    def _get_resolvable_value(self, node):
        if not isinstance(node, dict):
            return None, False
        ntype = node.get('type', '')
        if ntype == 'Literal':
            val = node.get('value')
            # Exclude regex literals
            if node.get('regex'):
                return None, False
            return val, True
        if ntype == 'UnaryExpression' and node.get('operator') == '-':
            arg = node.get('argument')
            if is_literal(arg) and isinstance(arg.get('value'), (int, float)):
                return -arg['value'], True
        if ntype == 'Identifier' and node.get('name') == 'undefined':
            return None, True  # JS undefined
        if ntype == 'ArrayExpression' and len(node.get('elements', [])) == 0:
            return [], True
        if ntype == 'ObjectExpression' and len(node.get('properties', [])) == 0:
            return {}, True
        return None, False

    def _apply_unary(self, op, val):
        if op == '-':
            return -val
        if op == '+':
            if isinstance(val, (int, float)):
                return +val
            if isinstance(val, str):
                try:
                    return float(val)
                except ValueError:
                    return None  # NaN - can't simplify
            if isinstance(val, list):
                return 0
            if val is None:
                return None  # NaN
            return 0
        if op == '!':
            # JS truthiness
            return not self._js_truthy(val)
        if op == '~':
            return ~int(val) if isinstance(val, (int, float)) else ~0
        if op == 'typeof':
            return self._js_typeof(val)
        if op == 'void':
            return None  # undefined

    def _apply_binary(self, op, left, right):
        # Coerce types similar to JS
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return self._js_to_string(left) + self._js_to_string(right)
            return self._js_to_number(left) + self._js_to_number(right)
        if op == '-':
            return self._js_to_number(left) - self._js_to_number(right)
        if op == '*':
            return self._js_to_number(left) * self._js_to_number(right)
        if op == '/':
            r = self._js_to_number(right)
            if r == 0:
                raise ValueError('division by zero')
            return self._js_to_number(left) / r
        if op == '%':
            r = self._js_to_number(right)
            if r == 0:
                raise ValueError('mod by zero')
            return self._js_to_number(left) % r
        if op == '**':
            return self._js_to_number(left) ** self._js_to_number(right)
        if op == '|':
            return int(self._js_to_number(left)) | int(self._js_to_number(right))
        if op == '&':
            return int(self._js_to_number(left)) & int(self._js_to_number(right))
        if op == '^':
            return int(self._js_to_number(left)) ^ int(self._js_to_number(right))
        if op == '<<':
            return int(self._js_to_number(left)) << (int(self._js_to_number(right)) & 31)
        if op == '>>':
            return int(self._js_to_number(left)) >> (int(self._js_to_number(right)) & 31)
        if op == '>>>':
            l = int(self._js_to_number(left)) & 0xFFFFFFFF
            r = int(self._js_to_number(right)) & 31
            return l >> r
        if op == '==':
            return left == right
        if op == '!=':
            return left != right
        if op == '===':
            return left == right and type(left) == type(right)
        if op == '!==':
            return not (left == right and type(left) == type(right))
        if op == '<':
            return self._js_compare(left, right) < 0
        if op == '<=':
            return self._js_compare(left, right) <= 0
        if op == '>':
            return self._js_compare(left, right) > 0
        if op == '>=':
            return self._js_compare(left, right) >= 0
        raise ValueError(f'Unknown operator: {op}')

    def _js_truthy(self, val):
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0 and not math.isnan(val) if isinstance(val, float) else val != 0
        if isinstance(val, str):
            return len(val) > 0
        if isinstance(val, (list, dict)):
            return True
        return bool(val)

    def _js_typeof(self, val):
        if val is None:
            return 'undefined'
        if isinstance(val, bool):
            return 'boolean'
        if isinstance(val, (int, float)):
            return 'number'
        if isinstance(val, str):
            return 'string'
        if isinstance(val, (list, dict)):
            return 'object'
        return 'undefined'

    def _js_to_number(self, val):
        if val is None:
            return 0
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            try:
                return int(val) if val.isdigit() or (val.startswith('-') and val[1:].isdigit()) else float(val)
            except (ValueError, IndexError):
                return 0
        if isinstance(val, list):
            return 0
        return 0

    def _js_to_string(self, val):
        if val is None:
            return 'undefined'
        if isinstance(val, bool):
            return 'true' if val else 'false'
        if isinstance(val, (int, float)):
            if isinstance(val, float) and val == int(val):
                return str(int(val))
            return str(val)
        if isinstance(val, str):
            return val
        if isinstance(val, list):
            return ''
        if isinstance(val, dict):
            return '[object Object]'
        return str(val)

    def _js_compare(self, left, right):
        l = self._js_to_number(left)
        r = self._js_to_number(right)
        if l < r:
            return -1
        if l > r:
            return 1
        return 0

    def _value_to_node(self, val):
        if val is None:
            return {'type': 'Identifier', 'name': 'undefined'}
        if isinstance(val, bool):
            return make_literal(val)
        if isinstance(val, (int, float)):
            if isinstance(val, float) and val != val:  # NaN
                return None
            if isinstance(val, float) and math.isinf(val):
                return None
            if val < 0:
                return {
                    'type': 'UnaryExpression',
                    'operator': '-',
                    'prefix': True,
                    'argument': make_literal(abs(val))
                }
            return make_literal(val)
        if isinstance(val, str):
            return make_literal(val)
        return None
