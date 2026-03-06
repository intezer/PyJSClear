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
            val = node.get('value')
            if val is None:
                return False  # null is falsy
            match val:
                case bool():
                    return val
                case int() | float():
                    return val != 0
                case str():
                    return len(val) > 0
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
            ntype = node.get('type', '')

            if ntype == 'IfStatement':
                truthy = _is_truthy_literal(node.get('test'))
                if truthy is None:
                    return
                self.set_changed()
                if truthy:
                    return node.get('consequent')
                alt = node.get('alternate')
                return alt if alt else REMOVE

            if ntype == 'ConditionalExpression':
                truthy = _is_truthy_literal(node.get('test'))
                if truthy is None:
                    return
                self.set_changed()
                return node.get('consequent' if truthy else 'alternate')

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
