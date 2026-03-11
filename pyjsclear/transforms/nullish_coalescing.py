"""Convert nullish coalescing patterns to ?? operator.

Detects patterns like:
    (_0x = value) !== null && _0x !== undefined ? _0x : default
And simplifies to:
    value ?? default
"""

from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_literal
from .base import Transform


def _is_null_literal(node):
    """Check if node is `null`."""
    return isinstance(node, dict) and node.get('type') == 'Literal' and node.get('value') is None


def _is_undefined_identifier(node):
    """Check if node is `undefined`."""
    return is_identifier(node) and node.get('name') == 'undefined'


def _identifiers_match(a, b):
    """Check if two nodes are the same identifier."""
    return is_identifier(a) and is_identifier(b) and a.get('name') == b.get('name')


class NullishCoalescing(Transform):
    """Convert nullish check patterns to ?? operator."""

    def execute(self):
        def enter(node, parent, key, index):
            if node.get('type') != 'ConditionalExpression':
                return
            test = node.get('test')
            if not isinstance(test, dict) or test.get('type') != 'LogicalExpression' or test.get('operator') != '&&':
                return

            left_cmp = test.get('left')
            right_cmp = test.get('right')
            if not isinstance(left_cmp, dict) or not isinstance(right_cmp, dict):
                return

            # Pattern: X !== null && X !== undefined ? X : default
            # Where X might be (_0x = value) or just an identifier
            result = self._match_nullish_pattern(left_cmp, right_cmp, node.get('consequent'), node.get('alternate'))
            if result:
                self.set_changed()
                return result

            # Also handle reversed order: X !== undefined && X !== null ? X : default
            result = self._match_nullish_pattern(right_cmp, left_cmp, node.get('consequent'), node.get('alternate'))
            if result:
                self.set_changed()
                return result

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _match_nullish_pattern(self, null_check, undef_check, consequent, alternate):
        """Try to match the pattern and return a ?? node if successful."""
        # null_check: X !== null (or (tmp = value) !== null)
        if null_check.get('type') != 'BinaryExpression' or null_check.get('operator') != '!==':
            return None
        # undef_check: X !== undefined
        if undef_check.get('type') != 'BinaryExpression' or undef_check.get('operator') != '!==':
            return None

        null_left = null_check.get('left')
        null_right = null_check.get('right')
        undef_left = undef_check.get('left')
        undef_right = undef_check.get('right')

        # Determine which side has null and which has undefined
        if _is_null_literal(null_right) and _is_undefined_identifier(undef_right):
            checked_in_null = null_left
            checked_in_undef = undef_left
        elif _is_null_literal(null_left) and _is_undefined_identifier(undef_left):
            checked_in_null = null_right
            checked_in_undef = undef_right
        else:
            return None

        # Case 1: (tmp = value) !== null && tmp !== undefined ? tmp : default
        if (
            isinstance(checked_in_null, dict)
            and checked_in_null.get('type') == 'AssignmentExpression'
            and checked_in_null.get('operator') == '='
        ):
            tmp_var = checked_in_null.get('left')
            value_expr = checked_in_null.get('right')
            if (
                _identifiers_match(tmp_var, checked_in_undef)
                and _identifiers_match(tmp_var, consequent)
            ):
                return {
                    'type': 'LogicalExpression',
                    'operator': '??',
                    'left': value_expr,
                    'right': alternate,
                }

        # Case 2: X !== null && X !== undefined ? X : default (no temp assignment)
        if (
            _identifiers_match(checked_in_null, checked_in_undef)
            and _identifiers_match(checked_in_null, consequent)
        ):
            return {
                'type': 'LogicalExpression',
                'operator': '??',
                'left': checked_in_null,
                'right': alternate,
            }

        return None
