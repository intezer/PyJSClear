"""Remove unreachable if/ternary branches based on literal tests."""

from .base import Transform
from ..traverser import traverse, REMOVE


def _is_truthy_literal(node):
    """Check if node is a literal that is truthy in JS."""
    if not isinstance(node, dict):
        return None
    ntype = node.get('type', '')
    if ntype == 'Literal':
        val = node.get('value')
        if val is None:
            return False  # null is falsy
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return len(val) > 0
        return True
    # !0 = true, !1 = false, !"" = true, ![] = false
    if ntype == 'UnaryExpression' and node.get('operator') == '!':
        arg = node.get('argument')
        inner = _is_truthy_literal(arg)
        if inner is not None:
            return not inner
    # [] is truthy
    if ntype == 'ArrayExpression' and len(node.get('elements', [])) == 0:
        return True
    # {} is truthy
    if ntype == 'ObjectExpression' and len(node.get('properties', [])) == 0:
        return True
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
                if truthy:
                    # Replace with consequent
                    cons = node.get('consequent')
                    if cons and cons.get('type') == 'BlockStatement':
                        # Return a block statement that will be inlined
                        self.set_changed()
                        return cons
                    elif cons:
                        self.set_changed()
                        return cons
                else:
                    # Replace with alternate or remove
                    alt = node.get('alternate')
                    if alt:
                        if alt.get('type') == 'BlockStatement':
                            self.set_changed()
                            return alt
                        self.set_changed()
                        return alt
                    else:
                        self.set_changed()
                        return REMOVE

            elif ntype == 'ConditionalExpression':
                truthy = _is_truthy_literal(node.get('test'))
                if truthy is None:
                    return
                if truthy:
                    self.set_changed()
                    return node.get('consequent')
                else:
                    self.set_changed()
                    return node.get('alternate')

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
