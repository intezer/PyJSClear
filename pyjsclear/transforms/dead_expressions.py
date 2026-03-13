"""Remove dead expression statements (standalone numeric literals like `0;`)."""

from ..traverser import REMOVE
from ..traverser import traverse
from .base import Transform


class DeadExpressionRemover(Transform):
    """Remove ExpressionStatements whose expression is a side-effect-free literal.

    Targets standalone `0;` left over from sequence splitting of patterns
    like `(0, fn())`, and other numeric literal statements.
    """

    def execute(self) -> bool:
        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> object:
            if node.get('type') != 'ExpressionStatement':
                return
            expression = node.get('expression')
            if not isinstance(expression, dict) or expression.get('type') != 'Literal':
                return
            value = expression.get('value')
            # Only remove numeric literals (not strings/booleans/null/regex)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                self.set_changed()
                return REMOVE

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
