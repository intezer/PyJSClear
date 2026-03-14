"""Remove dead expression statements (standalone numeric literals like `0;`)."""

from __future__ import annotations

from ..traverser import REMOVE
from ..traverser import traverse
from .base import Transform


class DeadExpressionRemover(Transform):
    """Remove ExpressionStatements whose expression is a side-effect-free literal.

    Targets standalone `0;` left over from sequence splitting of patterns
    like `(0, fn())`, and other numeric literal statements.
    """

    def execute(self) -> bool:
        """Traverse the AST and remove dead numeric literal statements."""
        traverse(self.ast, {'enter': self._enter_visitor})
        return self.has_changed()

    def _enter_visitor(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> object | None:
        """Remove numeric literal expression statements, return REMOVE or None."""
        if node.get('type') != 'ExpressionStatement':
            return None

        expression = node.get('expression')
        if not isinstance(expression, dict) or expression.get('type') != 'Literal':
            return None

        value = expression.get('value')
        # only remove numeric literals (not strings/booleans/null/regex)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            self.set_changed()
            return REMOVE

        return None
