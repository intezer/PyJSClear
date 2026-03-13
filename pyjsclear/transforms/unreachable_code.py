"""Remove unreachable statements after return/throw/break/continue."""

from ..traverser import traverse
from .base import Transform


# Statement types that unconditionally terminate control flow.
_TERMINATORS = frozenset({'ReturnStatement', 'ThrowStatement', 'BreakStatement', 'ContinueStatement'})


class UnreachableCodeRemover(Transform):
    """Remove statements that follow a terminator (return/throw/break/continue) in a block."""

    def execute(self) -> bool:
        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            node_type = node.get('type')
            if node_type in ('BlockStatement', 'Program'):
                body = node.get('body')
                if body and isinstance(body, list):
                    self._truncate_after_terminator(body, node, 'body')
            elif node_type == 'SwitchCase':
                consequent = node.get('consequent')
                if consequent and isinstance(consequent, list):
                    self._truncate_after_terminator(consequent, node, 'consequent')

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _truncate_after_terminator(self, statements: list, node: dict, key: str) -> None:
        for statement_index, statement in enumerate(statements):
            if not isinstance(statement, dict):
                continue
            if statement.get('type') not in _TERMINATORS:
                continue
            if statement_index + 1 < len(statements):
                self.set_changed()
                node[key] = statements[: statement_index + 1]
            return
