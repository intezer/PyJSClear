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
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_null_literal
from ..utils.ast_helpers import is_undefined
from .base import Transform


def _identifiers_match(a, b):
    """Check if two nodes are the same identifier."""
    return is_identifier(a) and is_identifier(b) and a.get('name') == b.get('name')


def _nodes_match(a, b):
    """Check if two AST nodes are structurally equivalent (shallow)."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    if a.get('type') != b.get('type'):
        return False
    if a.get('type') == 'Identifier':
        return a.get('name') == b.get('name')
    if a.get('type') == 'MemberExpression':
        return (
            _nodes_match(a.get('object'), b.get('object'))
            and _nodes_match(a.get('property'), b.get('property'))
            and a.get('computed') == b.get('computed')
        )
    return False


class OptionalChaining(Transform):
    """Convert nullish check patterns to ?. operator."""

    def execute(self):
        def enter(node, parent, key, index):
            if node.get('type') != 'ConditionalExpression':
                return
            test = node.get('test')
            if not isinstance(test, dict) or test.get('type') != 'LogicalExpression' or test.get('operator') != '||':
                return
            alternate = node.get('alternate')
            consequent = node.get('consequent')

            # consequent must be undefined/void 0
            if not is_undefined(consequent):
                return

            result = self._match_optional_pattern(test.get('left'), test.get('right'), alternate)
            if result:
                self.set_changed()
                return result

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _match_optional_pattern(self, left_cmp, right_cmp, alternate):
        """Try to match X === null || X === undefined ? undefined : X.prop."""
        if not isinstance(left_cmp, dict) or not isinstance(right_cmp, dict):
            return None
        if left_cmp.get('type') != 'BinaryExpression' or left_cmp.get('operator') != '===':
            return None
        if right_cmp.get('type') != 'BinaryExpression' or right_cmp.get('operator') != '===':
            return None

        # Figure out which comparison has null and which has undefined
        checked_var = None

        # Try: left has null, right has undefined
        for null_cmp, undef_cmp in [(left_cmp, right_cmp), (right_cmp, left_cmp)]:
            null_left, null_right = null_cmp.get('left'), null_cmp.get('right')
            undef_left, undef_right = undef_cmp.get('left'), undef_cmp.get('right')

            # X === null
            if is_null_literal(null_right):
                null_checked = null_left
            elif is_null_literal(null_left):
                null_checked = null_right
            else:
                continue

            # X === undefined
            if is_undefined(undef_right):
                undef_checked = undef_left
            elif is_undefined(undef_left):
                undef_checked = undef_right
            else:
                continue

            # Case 1: Simple - both check the same identifier
            if _nodes_match(null_checked, undef_checked):
                checked_var = null_checked
                break

            # Case 2: Temp assignment - (_tmp = expr) === null || _tmp === undefined
            if (
                isinstance(null_checked, dict)
                and null_checked.get('type') == 'AssignmentExpression'
                and null_checked.get('operator') == '='
            ):
                tmp_var = null_checked.get('left')
                value_expr = null_checked.get('right')
                if _identifiers_match(tmp_var, undef_checked):
                    # The alternate should use tmp_var as the object
                    checked_var = tmp_var
                    # We'll replace tmp_var references in alternate with value_expr
                    return self._build_optional_chain(value_expr, checked_var, alternate)

        if checked_var is None:
            return None

        return self._build_optional_chain(checked_var, checked_var, alternate)

    def _build_optional_chain(self, base_expr, checked_var, alternate):
        """Build an optional chain node: base_expr?.something.

        base_expr: the actual expression to use as the object
        checked_var: the variable that was null-checked (may differ from base_expr for temp assignments)
        alternate: the expression that accesses checked_var.prop (or deeper)
        """
        if not isinstance(alternate, dict):
            return None

        # alternate should be a MemberExpression or CallExpression whose object matches checked_var
        if alternate.get('type') == 'MemberExpression':
            obj = alternate.get('object')
            if _nodes_match(obj, checked_var):
                return {
                    'type': 'MemberExpression',
                    'object': base_expr,
                    'property': alternate['property'],
                    'computed': alternate.get('computed', False),
                    'optional': True,
                }

        if alternate.get('type') == 'CallExpression':
            callee = alternate.get('callee')
            if _nodes_match(callee, checked_var):
                return {
                    'type': 'CallExpression',
                    'callee': base_expr,
                    'arguments': alternate.get('arguments', []),
                    'optional': True,
                }

        return None
