"""Resolve TypeScript enum member accesses to their literal values.

Detects the TypeScript enum pattern:
    var E;
    (function (x) {
        x[x.FOO = 0] = "FOO";
        x[x.BAR = 1] = "BAR";
    })(E || (E = {}));

And replaces E.FOO with 0, E.BAR with 1, etc.
"""

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import make_literal
from .base import Transform


class EnumResolver(Transform):
    """Replace TypeScript enum member accesses with their numeric values."""

    def execute(self):
        # Phase 1: Detect enum IIFEs and extract member values.
        # Pattern: (function(param) { param[param.NAME = VALUE] = "NAME"; ... })(E || (E = {}))
        enum_members = {}  # (enum_name, member_name) -> numeric value

        def find_enums(node, parent):
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not callee or callee.get('type') != 'FunctionExpression':
                return
            params = callee.get('params', [])
            if len(params) != 1 or not is_identifier(params[0]):
                return
            param_name = params[0]['name']

            # Check the argument pattern: E || (E = {})
            args = node.get('arguments', [])
            if len(args) != 1:
                return
            arg = args[0]
            enum_name = self._extract_enum_name(arg)
            if not enum_name:
                return

            # Extract member assignments from the function body
            body = callee.get('body')
            if not body or body.get('type') != 'BlockStatement':
                return
            for stmt in body.get('body', []):
                if stmt.get('type') != 'ExpressionStatement':
                    continue
                member, value = self._extract_enum_assignment(stmt.get('expression'), param_name)
                if member is not None:
                    enum_members[(enum_name, member)] = value

        simple_traverse(self.ast, find_enums)

        if not enum_members:
            return False

        # Phase 2: Replace enum member accesses with their values
        def resolve(node, parent, key, index):
            if node.get('type') != 'MemberExpression':
                return
            if node.get('computed'):
                return
            obj = node.get('object')
            prop = node.get('property')
            if not obj or not is_identifier(obj) or not prop or not is_identifier(prop):
                return
            # Skip assignment targets
            if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
                return
            pair = (obj['name'], prop['name'])
            if pair in enum_members:
                self.set_changed()
                value = enum_members[pair]
                if isinstance(value, (int, float)) and value < 0:
                    return {
                        'type': 'UnaryExpression',
                        'operator': '-',
                        'argument': make_literal(-value),
                        'prefix': True,
                    }
                return make_literal(value)

        traverse(self.ast, {'enter': resolve})
        return self.has_changed()

    def _extract_enum_name(self, arg):
        """Extract the enum name from the IIFE argument pattern.

        Handles:
        - E || (E = {})
        - E = X.Y || (X.Y = {})  (export-assigned variant)
        """
        # Simple case: just an identifier
        if is_identifier(arg):
            return arg['name']
        # Assignment wrapper: E = X.Y || (X.Y = {})
        if arg.get('type') == 'AssignmentExpression' and arg.get('operator') == '=':
            assign_left = arg.get('left')
            if is_identifier(assign_left):
                inner = arg.get('right')
                if inner and inner.get('type') == 'LogicalExpression':
                    return assign_left['name']
            return None
        # Logical OR pattern: E || (E = {})
        if arg.get('type') != 'LogicalExpression' or arg.get('operator') != '||':
            return None
        left = arg.get('left')
        right = arg.get('right')
        if not is_identifier(left):
            return None
        name = left['name']
        # Right side should be (E = {})
        if right and right.get('type') == 'AssignmentExpression':
            right_left = right.get('left')
            if is_identifier(right_left) and right_left['name'] == name:
                return name
        return None

    def _extract_enum_assignment(self, expr, param_name):
        """Extract (member_name, value) from: param[param.NAME = VALUE] = "NAME".

        Returns (member_name, numeric_value) or (None, None).
        """
        if not expr or expr.get('type') != 'AssignmentExpression':
            return None, None
        # The outer assignment: param[...] = "NAME"
        left = expr.get('left')
        if not left or left.get('type') != 'MemberExpression' or not left.get('computed'):
            return None, None
        obj = left.get('object')
        if not is_identifier(obj) or obj['name'] != param_name:
            return None, None
        # The computed key is the inner assignment: param.NAME = VALUE
        inner = left.get('property')
        if not inner or inner.get('type') != 'AssignmentExpression':
            return None, None
        inner_left = inner.get('left')
        inner_right = inner.get('right')
        if not inner_left or inner_left.get('type') != 'MemberExpression':
            return None, None
        inner_obj = inner_left.get('object')
        inner_prop = inner_left.get('property')
        if not is_identifier(inner_obj) or inner_obj['name'] != param_name:
            return None, None
        if not is_identifier(inner_prop):
            return None, None
        member_name = inner_prop['name']
        value = self._get_numeric_value(inner_right)
        if value is None:
            return None, None
        return member_name, value

    @staticmethod
    def _get_numeric_value(node):
        """Extract a numeric value from a literal or unary minus expression."""
        if not node:
            return None
        if is_numeric_literal(node):
            return node['value']
        # Handle -N (UnaryExpression with operator '-' and numeric argument)
        if (
            node.get('type') == 'UnaryExpression'
            and node.get('operator') == '-'
            and is_numeric_literal(node.get('argument'))
        ):
            return -node['argument']['value']
        return None
