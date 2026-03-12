"""Remove dead expression statements (standalone numeric literals like `0;`)."""

from ..traverser import REMOVE
from ..traverser import traverse
from .base import Transform


class DeadExpressionRemover(Transform):
    """Remove ExpressionStatements whose expression is a side-effect-free literal.

    Targets standalone `0;` left over from sequence splitting of patterns
    like `(0, fn())`, and other numeric literal statements.
    """

    def execute(self):
        def enter(node, parent, key, index):
            if node.get('type') != 'ExpressionStatement':
                return
            expr = node.get('expression')
            if not isinstance(expr, dict) or expr.get('type') != 'Literal':
                return
            value = expr.get('value')
            # Only remove numeric literals (not strings/booleans/null/regex)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                self.set_changed()
                return REMOVE

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
