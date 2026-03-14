"""Convert optional chaining patterns to ?. operator.

Detects patterns like:
    X === null || X === undefined ? undefined : X.prop
And simplifies to:
    X?.prop

Also handles temp assignment patterns:
    (_tmp = X.a) === null || _tmp === undefined ? undefined : _tmp.b
    -> X.a?.b
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from ..traverser import traverse
from ..utils.ast_helpers import identifiers_match
from ..utils.ast_helpers import is_null_literal
from ..utils.ast_helpers import is_undefined
from .base import Transform


class _NodeType(StrEnum):
    """AST node types used in optional chaining detection."""

    ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
    BINARY_EXPRESSION = 'BinaryExpression'
    CALL_EXPRESSION = 'CallExpression'
    CONDITIONAL_EXPRESSION = 'ConditionalExpression'
    IDENTIFIER = 'Identifier'
    LOGICAL_EXPRESSION = 'LogicalExpression'
    MEMBER_EXPRESSION = 'MemberExpression'


class _Operator(StrEnum):
    """Operators used in optional chaining pattern matching."""

    ASSIGN = '='
    LOGICAL_OR = '||'
    STRICT_EQUAL = '==='


def _nodes_match(node_a: Any, node_b: Any) -> bool:
    """Check if two AST nodes are structurally equivalent (shallow)."""
    if not isinstance(node_a, dict) or not isinstance(node_b, dict):
        return False
    if node_a.get('type') != node_b.get('type'):
        return False
    match node_a.get('type'):
        case _NodeType.IDENTIFIER:
            return node_a.get('name') == node_b.get('name')
        case _NodeType.MEMBER_EXPRESSION:
            return (
                _nodes_match(node_a.get('object'), node_b.get('object'))
                and _nodes_match(node_a.get('property'), node_b.get('property'))
                and node_a.get('computed') == node_b.get('computed')
            )
        case _:
            return False


def _extract_null_checked_variable(comparison: dict) -> dict | None:
    """Extract the variable being compared to null in a === null check."""
    left = comparison.get('left')
    right = comparison.get('right')
    if is_null_literal(right):
        return left
    if is_null_literal(left):
        return right
    return None


def _extract_undefined_checked_variable(comparison: dict) -> dict | None:
    """Extract the variable being compared to undefined in a === undefined check."""
    left = comparison.get('left')
    right = comparison.get('right')
    if is_undefined(right):
        return left
    if is_undefined(left):
        return right
    return None


class OptionalChaining(Transform):
    """Convert nullish check patterns to ?. operator."""

    def execute(self) -> bool:
        """Traverse the AST and replace nullish check ternaries with optional chaining."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            if node.get('type') != _NodeType.CONDITIONAL_EXPRESSION:
                return None

            test = node.get('test')
            if not isinstance(test, dict):
                return None
            if test.get('type') != _NodeType.LOGICAL_EXPRESSION:
                return None
            if test.get('operator') != _Operator.LOGICAL_OR:
                return None

            consequent = node.get('consequent')
            if not is_undefined(consequent):
                return None

            alternate = node.get('alternate')
            result = self._match_optional_pattern(test.get('left'), test.get('right'), alternate)
            if not result:
                return None

            self.set_changed()
            return result

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _match_optional_pattern(self, left_comparison: Any, right_comparison: Any, alternate: Any) -> dict | None:
        """Match X === null || X === undefined ? undefined : X.prop and return optional chain node."""
        if not isinstance(left_comparison, dict) or not isinstance(right_comparison, dict):
            return None
        if left_comparison.get('type') != _NodeType.BINARY_EXPRESSION:
            return None
        if left_comparison.get('operator') != _Operator.STRICT_EQUAL:
            return None
        if right_comparison.get('type') != _NodeType.BINARY_EXPRESSION:
            return None
        if right_comparison.get('operator') != _Operator.STRICT_EQUAL:
            return None

        # Try both orderings: left has null + right has undefined, and vice versa
        for null_comparison, undefined_comparison in [
            (left_comparison, right_comparison),
            (right_comparison, left_comparison),
        ]:
            null_checked = _extract_null_checked_variable(null_comparison)
            if null_checked is None:
                continue

            undefined_checked = _extract_undefined_checked_variable(undefined_comparison)
            if undefined_checked is None:
                continue

            # Simple case: both check the same identifier
            if _nodes_match(null_checked, undefined_checked):
                return self._build_optional_chain(null_checked, null_checked, alternate)

            # Temp assignment: (_tmp = expr) === null || _tmp === undefined
            result = self._try_temp_assignment_pattern(null_checked, undefined_checked, alternate)
            if result is not None:
                return result

        return None

    def _try_temp_assignment_pattern(
        self,
        null_checked: Any,
        undefined_checked: Any,
        alternate: Any,
    ) -> dict | None:
        """Match temp assignment pattern like (_tmp = expr) === null || _tmp === undefined."""
        if not isinstance(null_checked, dict):
            return None
        if null_checked.get('type') != _NodeType.ASSIGNMENT_EXPRESSION:
            return None
        if null_checked.get('operator') != _Operator.ASSIGN:
            return None

        temporary_variable = null_checked.get('left')
        value_expression = null_checked.get('right')
        if not identifiers_match(temporary_variable, undefined_checked):
            return None

        return self._build_optional_chain(value_expression, temporary_variable, alternate)

    def _build_optional_chain(
        self,
        base_expression: Any,
        checked_variable: Any,
        alternate: Any,
    ) -> dict | None:
        """Build an optional chain node from matched pattern components.

        base_expression: the actual expression to use as the object
        checked_variable: the variable that was null-checked (may differ for temp assignments)
        alternate: the expression that accesses checked_variable.prop (or deeper)
        """
        if not isinstance(alternate, dict):
            return None

        match alternate.get('type'):
            case _NodeType.MEMBER_EXPRESSION:
                alternate_object = alternate.get('object')
                if not _nodes_match(alternate_object, checked_variable):
                    return None
                return {
                    'type': _NodeType.MEMBER_EXPRESSION,
                    'object': base_expression,
                    'property': alternate['property'],
                    'computed': alternate.get('computed', False),
                    'optional': True,
                }

            case _NodeType.CALL_EXPRESSION:
                callee = alternate.get('callee')
                if not _nodes_match(callee, checked_variable):
                    return None
                return {
                    'type': _NodeType.CALL_EXPRESSION,
                    'callee': base_expression,
                    'arguments': alternate.get('arguments', []),
                    'optional': True,
                }

            case _:
                return None
