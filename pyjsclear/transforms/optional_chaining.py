"""Convert optional chaining patterns to ?. operator.

Detects patterns like:
    X === null || X === undefined ? undefined : X.prop
And simplifies to:
    X?.prop

Also handles temp assignment patterns:
    (_tmp = X.a) === null || _tmp === undefined ? undefined : _tmp.b
    → X.a?.b
"""

from ..traverser import traverse
from ..utils.ast_helpers import identifiers_match
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_null_literal
from ..utils.ast_helpers import is_undefined
from .base import Transform


def _nodes_match(node_a: object, node_b: object) -> bool:
    """Check if two AST nodes are structurally equivalent (shallow)."""
    if not isinstance(node_a, dict) or not isinstance(node_b, dict):
        return False
    if node_a.get('type') != node_b.get('type'):
        return False
    if node_a.get('type') == 'Identifier':
        return node_a.get('name') == node_b.get('name')
    if node_a.get('type') == 'MemberExpression':
        return (
            _nodes_match(node_a.get('object'), node_b.get('object'))
            and _nodes_match(node_a.get('property'), node_b.get('property'))
            and node_a.get('computed') == node_b.get('computed')
        )
    return False


class OptionalChaining(Transform):
    """Convert nullish check patterns to ?. operator."""

    def execute(self) -> bool:
        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            if node.get('type') != 'ConditionalExpression':
                return None
            test = node.get('test')
            if not isinstance(test, dict) or test.get('type') != 'LogicalExpression' or test.get('operator') != '||':
                return None
            alternate = node.get('alternate')
            consequent = node.get('consequent')

            # consequent must be undefined/void 0
            if not is_undefined(consequent):
                return None

            result = self._match_optional_pattern(test.get('left'), test.get('right'), alternate)
            if result:
                self.set_changed()
                return result
            return None

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _match_optional_pattern(self, left_comparison: object, right_comparison: object, alternate: object) -> dict | None:
        """Try to match X === null || X === undefined ? undefined : X.prop."""
        if not isinstance(left_comparison, dict) or not isinstance(right_comparison, dict):
            return None
        if left_comparison.get('type') != 'BinaryExpression' or left_comparison.get('operator') != '===':
            return None
        if right_comparison.get('type') != 'BinaryExpression' or right_comparison.get('operator') != '===':
            return None

        # Figure out which comparison has null and which has undefined
        checked_variable = None

        # Try: left has null, right has undefined
        for null_comparison, undefined_comparison in [(left_comparison, right_comparison), (right_comparison, left_comparison)]:
            null_comparison_left, null_comparison_right = null_comparison.get('left'), null_comparison.get('right')
            undefined_comparison_left, undefined_comparison_right = undefined_comparison.get('left'), undefined_comparison.get('right')

            # X === null
            if is_null_literal(null_comparison_right):
                null_checked = null_comparison_left
            elif is_null_literal(null_comparison_left):
                null_checked = null_comparison_right
            else:
                continue

            # X === undefined
            if is_undefined(undefined_comparison_right):
                undefined_checked = undefined_comparison_left
            elif is_undefined(undefined_comparison_left):
                undefined_checked = undefined_comparison_right
            else:
                continue

            # Case 1: Simple - both check the same identifier
            if _nodes_match(null_checked, undefined_checked):
                checked_variable = null_checked
                break

            # Case 2: Temp assignment - (_tmp = expr) === null || _tmp === undefined
            if (
                isinstance(null_checked, dict)
                and null_checked.get('type') == 'AssignmentExpression'
                and null_checked.get('operator') == '='
            ):
                tmp_var = null_checked.get('left')
                value_expr = null_checked.get('right')
                if identifiers_match(tmp_var, undefined_checked):
                    # The alternate should use tmp_var as the object
                    checked_variable = tmp_var
                    # We'll replace tmp_var references in alternate with value_expr
                    return self._build_optional_chain(value_expr, checked_variable, alternate)

        if checked_variable is None:
            return None

        return self._build_optional_chain(checked_variable, checked_variable, alternate)

    def _build_optional_chain(self, base_expr: object, checked_variable: object, alternate: object) -> dict | None:
        """Build an optional chain node: base_expr?.something.

        base_expr: the actual expression to use as the object
        checked_variable: the variable that was null-checked (may differ from base_expr for temp assignments)
        alternate: the expression that accesses checked_variable.prop (or deeper)
        """
        if not isinstance(alternate, dict):
            return None

        # alternate should be a MemberExpression or CallExpression whose object matches checked_variable
        if alternate.get('type') == 'MemberExpression':
            obj = alternate.get('object')
            if _nodes_match(obj, checked_variable):
                return {
                    'type': 'MemberExpression',
                    'object': base_expr,
                    'property': alternate['property'],
                    'computed': alternate.get('computed', False),
                    'optional': True,
                }

        if alternate.get('type') == 'CallExpression':
            callee = alternate.get('callee')
            if _nodes_match(callee, checked_variable):
                return {
                    'type': 'CallExpression',
                    'callee': base_expr,
                    'arguments': alternate.get('arguments', []),
                    'optional': True,
                }

        return None
