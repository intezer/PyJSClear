"""Remove unreachable statements after return/throw/break/continue."""

from ..traverser import traverse
from .base import Transform


# Statement types that unconditionally terminate control flow.
_TERMINATORS = frozenset({'ReturnStatement', 'ThrowStatement', 'BreakStatement', 'ContinueStatement'})


class UnreachableCodeRemover(Transform):
    """Remove statements that follow a terminator (return/throw/break/continue) in a block."""

    def execute(self):
        def enter(node, parent, key, index):
            t = node.get('type')
            if t in ('BlockStatement', 'Program'):
                body = node.get('body')
                if body and isinstance(body, list):
                    self._truncate_after_terminator(body, node, 'body')
            elif t == 'SwitchCase':
                consequent = node.get('consequent')
                if consequent and isinstance(consequent, list):
                    self._truncate_after_terminator(consequent, node, 'consequent')

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _truncate_after_terminator(self, stmts, node, key):
        for i, stmt in enumerate(stmts):
            if not isinstance(stmt, dict):
                continue
            if stmt.get('type') in _TERMINATORS:
                if i + 1 < len(stmts):
                    self.set_changed()
                    node[key] = stmts[: i + 1]
                return
