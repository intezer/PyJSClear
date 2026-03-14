"""Remove unreachable statements after return/throw/break/continue."""

from __future__ import annotations

from enum import StrEnum

from ..traverser import traverse
from .base import Transform


class _TerminatorType(StrEnum):
    """AST node types that unconditionally terminate control flow."""

    RETURN = 'ReturnStatement'
    THROW = 'ThrowStatement'
    BREAK = 'BreakStatement'
    CONTINUE = 'ContinueStatement'


_TERMINATORS = frozenset(_TerminatorType)


class UnreachableCodeRemover(Transform):
    """Remove statements that follow a terminator in a block."""

    def execute(self) -> bool:
        """Traverse AST and strip unreachable statements after terminators."""
        traverse(self.ast, {'enter': self._enter})
        return self.has_changed()

    def _enter(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Visit a node and truncate dead code in statement lists."""
        node_type = node.get('type')
        match node_type:
            case 'BlockStatement' | 'Program':
                statement_list = node.get('body')
                list_key = 'body'
            case 'SwitchCase':
                statement_list = node.get('consequent')
                list_key = 'consequent'
            case _:
                return

        if statement_list and isinstance(statement_list, list):
            self._truncate_after_terminator(statement_list, node, list_key)

    def _truncate_after_terminator(
        self,
        statements: list[dict],
        node: dict,
        list_key: str,
    ) -> None:
        """Remove all statements after the first terminator in a list."""
        for statement_index, statement in enumerate(statements):
            if not isinstance(statement, dict):
                continue
            if statement.get('type') not in _TERMINATORS:
                continue
            if statement_index + 1 < len(statements):
                self.set_changed()
                node[list_key] = statements[: statement_index + 1]
            return
