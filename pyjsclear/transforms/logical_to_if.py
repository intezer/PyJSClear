"""Convert logical expressions in statement position to if-statements.

Converts:
  a && b()           →  if (a) { b(); }
  a || b()           →  if (!a) { b(); }
  a && (b(), c())    →  if (a) { b(); c(); }
  return a || 0, b(), c  →  if (!a) { 0; b(); } return c;
  return await x(), y  →  await x(); return y;
"""

from __future__ import annotations

from enum import StrEnum

from ..utils.ast_helpers import make_block_statement
from ..utils.ast_helpers import make_expression_statement
from .base import Transform


class _LogicalOperator(StrEnum):
    """Logical operators supported for conversion."""

    AND = '&&'
    OR = '||'


def _negate(expression: dict) -> dict:
    """Wrap an expression in a logical NOT."""
    return {
        'type': 'UnaryExpression',
        'operator': '!',
        'prefix': True,
        'argument': expression,
    }


class LogicalToIf(Transform):
    """Convert logical/comma expressions in statement position to if-statements."""

    def execute(self) -> bool:
        """Run the transform and return whether the AST was modified."""
        self._transform_bodies(self.ast)
        return self.has_changed()

    def _transform_bodies(self, node: dict | list | object) -> None:
        """Walk all statement arrays and apply transforms."""
        if not isinstance(node, dict):
            return
        for key, child in node.items():
            if isinstance(child, list):
                if child and isinstance(child[0], dict) and 'type' in child[0]:
                    self._process_statement_array(child)
                    for item in child:
                        self._transform_bodies(item)
            elif isinstance(child, dict) and 'type' in child:
                self._transform_bodies(child)

    def _process_statement_array(self, statements: list[dict]) -> None:
        """Iterate over a statement array, replacing convertible statements in-place."""
        index = 0
        while index < len(statements):
            statement = statements[index]
            if not isinstance(statement, dict):
                index += 1
                continue

            replacement = self._try_convert_stmt(statement)
            if replacement is not None:
                statements[index : index + 1] = replacement
                self.set_changed()
                index += len(replacement)
                continue

            index += 1

    def _try_convert_stmt(self, statement: dict) -> list[dict] | None:
        """Try to convert a statement. Returns replacement list or None."""
        match statement.get('type'):
            case 'ExpressionStatement':
                return self._handle_expression_stmt(statement)
            case 'ReturnStatement':
                return self._handle_return_stmt(statement)
        return None

    def _handle_expression_stmt(self, statement: dict) -> list[dict] | None:
        """Handle ExpressionStatement with logical or conditional."""
        expression = statement.get('expression')
        if not isinstance(expression, dict):
            return None
        match expression.get('type'):
            case 'LogicalExpression':
                return self._logical_to_if(expression)
            case 'ConditionalExpression':
                return self._ternary_to_if(expression)
        return None

    def _handle_return_stmt(self, statement: dict) -> list[dict] | None:
        """Handle ReturnStatement with sequence or logical expressions."""
        argument = statement.get('argument')
        if not isinstance(argument, dict):
            return None

        # return a, b, c → a; b; return c;
        if argument.get('type') == 'SequenceExpression':
            return self._split_return_sequence(argument)

        # return a || (b(), c) → if (!a) { b(); } return c;
        if argument.get('type') == 'LogicalExpression':
            return self._split_return_logical(argument)

        return None

    def _split_return_sequence(self, sequence: dict) -> list[dict] | None:
        """Split return (a, b, c) into a; b; return c."""
        expressions = sequence.get('expressions', [])
        if len(expressions) <= 1:
            return None
        new_statements = []
        for expression in expressions[:-1]:
            if isinstance(expression, dict) and expression.get('type') == 'LogicalExpression':
                converted = self._logical_to_if(expression)
                if converted:
                    new_statements.extend(converted)
                    continue
            new_statements.append(make_expression_statement(expression))
        new_statements.append({'type': 'ReturnStatement', 'argument': expressions[-1]})
        return new_statements

    def _split_return_logical(self, logical: dict) -> list[dict] | None:
        """Split return a || (b(), c) into if (!a) { b(); } return c."""
        right = logical.get('right')
        if not (isinstance(right, dict) and right.get('type') == 'SequenceExpression'):
            return None
        expressions = right.get('expressions', [])
        if len(expressions) <= 1:
            return None

        test = logical.get('left')
        if logical.get('operator') == _LogicalOperator.OR:
            test = _negate(test)

        body_statements = [make_expression_statement(expression) for expression in expressions[:-1]]
        if_statement = {
            'type': 'IfStatement',
            'test': test,
            'consequent': make_block_statement(body_statements),
            'alternate': None,
        }
        return_statement = {'type': 'ReturnStatement', 'argument': expressions[-1]}
        return [if_statement, return_statement]

    def _logical_to_if(self, expression: dict) -> list[dict] | None:
        """Convert a LogicalExpression to if-statement(s). Returns list of stmts or None."""
        left = expression.get('left')
        match expression.get('operator'):
            case _LogicalOperator.AND:
                test = left
            case _LogicalOperator.OR:
                test = _negate(left)
            case _:
                return None

        body_statements = self._expr_to_stmts(expression.get('right'))
        if_statement = {
            'type': 'IfStatement',
            'test': test,
            'consequent': make_block_statement(body_statements),
            'alternate': None,
        }
        return [if_statement]

    def _ternary_to_if(self, expression: dict) -> list[dict]:
        """Convert a ConditionalExpression to an if-else statement."""
        if_statement = {
            'type': 'IfStatement',
            'test': expression.get('test'),
            'consequent': make_block_statement(self._expr_to_stmts(expression.get('consequent'))),
            'alternate': make_block_statement(self._expr_to_stmts(expression.get('alternate'))),
        }
        return [if_statement]

    def _expr_to_stmts(self, expression: dict | None) -> list[dict]:
        """Convert an expression to a list of statements."""
        if isinstance(expression, dict) and expression.get('type') == 'SequenceExpression':
            return [make_expression_statement(item) for item in expression.get('expressions', [])]
        return [make_expression_statement(expression)]
