"""Remove unreachable if/ternary branches based on literal tests."""

from ..traverser import REMOVE
from ..traverser import traverse
from .base import Transform


def _is_truthy_literal(node):
    """Check if node is a literal that is truthy in JS. Returns None if unknown."""
    if not isinstance(node, dict):
        return None
    match node.get('type', ''):
        case 'Literal':
            value = node.get('value')
            if value is None:
                return False  # null is falsy
            match value:
                case bool():
                    return value
                case int() | float():
                    return value != 0
                case str():
                    return len(value) > 0
                case _:
                    return True
        case 'UnaryExpression' if node.get('operator') == '!':
            inner = _is_truthy_literal(node.get('argument'))
            if inner is not None:
                return not inner
        case 'ArrayExpression' if len(node.get('elements', [])) == 0:
            return True  # [] is truthy
        case 'ObjectExpression' if len(node.get('properties', [])) == 0:
            return True  # {} is truthy
        case 'LogicalExpression':
            left = _is_truthy_literal(node.get('left'))
            right = _is_truthy_literal(node.get('right'))
            op = node.get('operator')
            if op == '&&':
                # falsy && anything → falsy
                if left is False:
                    return False
                # truthy && right → right (if right is known)
                if left is True and right is not None:
                    return right
            elif op == '||':
                # truthy || anything → truthy
                if left is True:
                    return True
                # falsy || right → right (if right is known)
                if left is False and right is not None:
                    return right
    return None


def _unwrap_block(node):
    """Unwrap a single-statement block to its contents."""
    if isinstance(node, dict) and node.get('type') == 'BlockStatement':
        body = node.get('body', [])
        if len(body) == 1:
            return body[0]
    return node


class DeadBranchRemover(Transform):
    """Remove dead branches from if statements and ternary expressions."""

    def execute(self):
        def enter(node, parent, key, index):
            node_type = node.get('type', '')

            if node_type == 'IfStatement':
                truthy = _is_truthy_literal(node.get('test'))
                if truthy is None:
                    return
                self.set_changed()
                if truthy:
                    return node.get('consequent')
                alt = node.get('alternate')
                return alt if alt else REMOVE

            if node_type == 'ConditionalExpression':
                truthy = _is_truthy_literal(node.get('test'))
                if truthy is None:
                    return
                self.set_changed()
                return node.get('consequent' if truthy else 'alternate')

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
