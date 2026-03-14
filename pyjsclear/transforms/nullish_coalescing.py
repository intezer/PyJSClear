"""Convert nullish coalescing patterns to ?? operator.

Detects patterns like:
    (_0x = value) !== null && _0x !== undefined ? _0x : default
And simplifies to:
    value ?? default
"""

from __future__ import annotations

from ..traverser import traverse
from ..utils.ast_helpers import identifiers_match
from ..utils.ast_helpers import is_null_literal
from ..utils.ast_helpers import is_undefined
from .base import Transform


class NullishCoalescing(Transform):
    """Convert nullish check patterns to the ?? operator."""

    def execute(self) -> bool:
        """Traverse the AST and replace nullish coalescing patterns."""
        traverse(self.ast, {'enter': self._enter})
        return self.has_changed()

    def _enter(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> dict | None:
        """Replace ternary nullish checks with ?? expressions."""
        if node.get('type') != 'ConditionalExpression':
            return None

        test = node.get('test')
        if not isinstance(test, dict):
            return None
        if test.get('type') != 'LogicalExpression' or test.get('operator') != '&&':
            return None

        left_comparison = test.get('left')
        right_comparison = test.get('right')
        if not isinstance(left_comparison, dict) or not isinstance(right_comparison, dict):
            return None

        consequent = node.get('consequent')
        alternate = node.get('alternate')

        # Try both orderings: null&&undefined and undefined&&null
        for null_side, undefined_side in [
            (left_comparison, right_comparison),
            (right_comparison, left_comparison),
        ]:
            result = self._match_nullish_pattern(null_side, undefined_side, consequent, alternate)
            if result:
                self.set_changed()
                return result

        return None

    def _match_nullish_pattern(
        self,
        null_check: dict,
        undefined_check: dict,
        consequent: dict | None,
        alternate: dict | None,
    ) -> dict | None:
        """Match a nullish guard pattern and return a ?? node if successful."""
        if null_check.get('type') != 'BinaryExpression' or null_check.get('operator') != '!==':
            return None
        if undefined_check.get('type') != 'BinaryExpression' or undefined_check.get('operator') != '!==':
            return None

        null_check_left = null_check.get('left')
        null_check_right = null_check.get('right')
        undefined_check_left = undefined_check.get('left')
        undefined_check_right = undefined_check.get('right')

        # Determine which operand is the checked value vs the literal
        if is_null_literal(null_check_right) and is_undefined(undefined_check_right):
            null_checked_value = null_check_left
            undefined_checked_value = undefined_check_left
        elif is_null_literal(null_check_left) and is_undefined(undefined_check_left):
            null_checked_value = null_check_right
            undefined_checked_value = undefined_check_right
        else:
            return None

        # (temporary = value) !== null && temporary !== undefined ? temporary : default
        if (
            isinstance(null_checked_value, dict)
            and null_checked_value.get('type') == 'AssignmentExpression'
            and null_checked_value.get('operator') == '='
        ):
            temporary_variable = null_checked_value.get('left')
            assigned_value = null_checked_value.get('right')
            if identifiers_match(temporary_variable, undefined_checked_value) and identifiers_match(
                temporary_variable, consequent
            ):
                return self._build_nullish_node(assigned_value, alternate)

        # X !== null && X !== undefined ? X : default
        if identifiers_match(null_checked_value, undefined_checked_value) and identifiers_match(
            null_checked_value, consequent
        ):
            return self._build_nullish_node(null_checked_value, alternate)

        return None

    @staticmethod
    def _build_nullish_node(left: dict | None, right: dict | None) -> dict:
        """Construct a ?? LogicalExpression AST node."""
        return {
            'type': 'LogicalExpression',
            'operator': '??',
            'left': left,
            'right': right,
        }
