"""Remove unreachable if/ternary branches based on literal tests."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum

from ..traverser import REMOVE
from ..traverser import traverse
from .base import Transform


class _LogicalOperator(StrEnum):
    """Logical operators recognized in truthiness evaluation."""

    AND = '&&'
    OR = '||'


def _evaluate_logical_expression(
    left_truthiness: bool | None,
    right_truthiness: bool | None,
    operator: str,
) -> bool | None:
    """Evaluate a logical expression given known truthiness of operands.

    Returns the resulting truthiness, or None if indeterminate.
    """
    match operator:
        case _LogicalOperator.AND:
            if left_truthiness is False:
                return False
            if left_truthiness is True and right_truthiness is not None:
                return right_truthiness
        case _LogicalOperator.OR:
            if left_truthiness is True:
                return True
            if left_truthiness is False and right_truthiness is not None:
                return right_truthiness
    return None


def _is_truthy_literal(node: dict) -> bool | None:
    """Determine whether an AST node is a JS truthy literal.

    Returns True/False for known literals, None if indeterminate.
    """
    if not isinstance(node, dict):
        return None
    match node.get('type', ''):
        case 'Literal':
            return _evaluate_literal_value(node.get('value'))
        case 'UnaryExpression' if node.get('operator') == '!':
            argument_truthiness = _is_truthy_literal(node.get('argument'))
            if argument_truthiness is not None:
                return not argument_truthiness
        case 'ArrayExpression' if len(node.get('elements', [])) == 0:
            return True  # [] is truthy in JS
        case 'ObjectExpression' if len(node.get('properties', [])) == 0:
            return True  # {} is truthy in JS
        case 'LogicalExpression':
            left_truthiness = _is_truthy_literal(node.get('left'))
            right_truthiness = _is_truthy_literal(node.get('right'))
            return _evaluate_logical_expression(
                left_truthiness,
                right_truthiness,
                node.get('operator'),
            )
    return None


def _evaluate_literal_value(value: object) -> bool | None:
    """Evaluate the JS truthiness of a parsed literal value.

    Returns True/False for known types, None if indeterminate.
    """
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


def _unwrap_block(node: dict) -> dict:
    """Unwrap a single-statement BlockStatement to its sole child."""
    if isinstance(node, dict) and node.get('type') == 'BlockStatement':
        body = node.get('body', [])
        if len(body) == 1:
            return body[0]
    return node


def _handle_if_statement(node: dict, set_changed: Callable[[], None]) -> dict | object | None:
    """Handle dead-branch removal for an IfStatement node.

    Returns the replacement node, REMOVE sentinel, or None to skip.
    """
    truthiness = _is_truthy_literal(node.get('test'))
    if truthiness is None:
        return None
    set_changed()
    if truthiness:
        return node.get('consequent')
    alternate_branch = node.get('alternate')
    return alternate_branch if alternate_branch else REMOVE


def _handle_conditional_expression(node: dict, set_changed: Callable[[], None]) -> dict | None:
    """Handle dead-branch removal for a ConditionalExpression node.

    Returns the replacement node, or None to skip.
    """
    truthiness = _is_truthy_literal(node.get('test'))
    if truthiness is None:
        return None
    set_changed()
    return node.get('consequent' if truthiness else 'alternate')


class DeadBranchRemover(Transform):
    """Remove dead branches from if statements and ternary expressions.

    Evaluates literal test conditions and replaces dead if/ternary
    branches with their live counterparts.
    """

    def execute(self) -> bool:
        """Run the transform, returning True if the AST was modified."""

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> dict | object | None:
            """Visitor callback that replaces dead branches."""
            match node.get('type', ''):
                case 'IfStatement':
                    return _handle_if_statement(node, self.set_changed)
                case 'ConditionalExpression':
                    return _handle_conditional_expression(node, self.set_changed)

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
