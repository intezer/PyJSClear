"""Resolve TypeScript enum member accesses to their literal values.

Detects the TypeScript enum pattern:
    var E;
    (function (x) {
        x[x.FOO = 0] = "FOO";
        x[x.BAR = 1] = "BAR";
    })(E || (E = {}));

And replaces E.FOO with 0, E.BAR with 1, etc.
"""

from __future__ import annotations

from enum import StrEnum

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import make_literal
from .base import Transform


class _NodeType(StrEnum):
    """AST node type constants."""

    ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
    BLOCK_STATEMENT = 'BlockStatement'
    CALL_EXPRESSION = 'CallExpression'
    EXPRESSION_STATEMENT = 'ExpressionStatement'
    FUNCTION_EXPRESSION = 'FunctionExpression'
    LOGICAL_EXPRESSION = 'LogicalExpression'
    MEMBER_EXPRESSION = 'MemberExpression'
    UNARY_EXPRESSION = 'UnaryExpression'


class EnumResolver(Transform):
    """Replace TypeScript enum member accesses with their numeric values."""

    def execute(self) -> bool:
        """Run enum detection and replacement over the AST."""
        enum_members = self._collect_enum_members()
        if not enum_members:
            return False

        self._replace_enum_accesses(enum_members)
        return self.has_changed()

    def _collect_enum_members(self) -> dict[tuple[str, str], int | float]:
        """Scan the AST for TypeScript enum IIFEs and extract member mappings."""
        enum_members: dict[tuple[str, str], int | float] = {}

        def visitor(node: dict, parent: dict | None) -> None:
            """Visit each node looking for enum IIFE patterns."""
            if node.get('type') != _NodeType.CALL_EXPRESSION:
                return
            self._process_enum_iife(node, enum_members)

        simple_traverse(self.ast, visitor)
        return enum_members

    def _process_enum_iife(
        self,
        node: dict,
        enum_members: dict[tuple[str, str], int | float],
    ) -> None:
        """Extract enum members from a single IIFE call expression."""
        callee = node.get('callee')
        if not callee or callee.get('type') != _NodeType.FUNCTION_EXPRESSION:
            return

        parameters = callee.get('params', [])
        if len(parameters) != 1 or not is_identifier(parameters[0]):
            return
        parameter_name = parameters[0]['name']

        arguments = node.get('arguments', [])
        if len(arguments) != 1:
            return

        enum_name = self._extract_enum_name(arguments[0])
        if not enum_name:
            return

        body = callee.get('body')
        if not body or body.get('type') != _NodeType.BLOCK_STATEMENT:
            return

        for statement in body.get('body', []):
            if statement.get('type') != _NodeType.EXPRESSION_STATEMENT:
                continue
            member, value = self._extract_enum_assignment(statement.get('expression'), parameter_name)
            if member is not None:
                enum_members[(enum_name, member)] = value

    def _replace_enum_accesses(
        self,
        enum_members: dict[tuple[str, str], int | float],
    ) -> None:
        """Replace all enum member accesses with their resolved literal values."""

        def resolver(
            node: dict,
            parent: dict | None,
            key: str,
            index: int | None,
        ) -> dict | None:
            """Resolve a single enum member access to its literal value."""
            if node.get('type') != _NodeType.MEMBER_EXPRESSION:
                return None
            if node.get('computed'):
                return None

            object_node = node.get('object')
            property_node = node.get('property')
            if not object_node or not is_identifier(object_node):
                return None
            if not property_node or not is_identifier(property_node):
                return None

            # Skip assignment targets
            is_assignment_target = (
                parent and parent.get('type') == _NodeType.ASSIGNMENT_EXPRESSION and node is parent.get('left')
            )
            if is_assignment_target:
                return None

            lookup_key = (object_node['name'], property_node['name'])
            if lookup_key not in enum_members:
                return None

            self.set_changed()
            value = enum_members[lookup_key]
            if isinstance(value, (int, float)) and value < 0:
                return {
                    'type': _NodeType.UNARY_EXPRESSION,
                    'operator': '-',
                    'argument': make_literal(-value),
                    'prefix': True,
                }
            return make_literal(value)

        traverse(self.ast, {'enter': resolver})

    def _extract_enum_name(self, argument_node: dict) -> str | None:
        """Extract the enum name from the IIFE argument pattern.

        Handles:
        - E || (E = {})
        - E = X.Y || (X.Y = {})  (export-assigned variant)
        """
        # Simple case: just an identifier
        if is_identifier(argument_node):
            return argument_node['name']

        # Assignment wrapper: E = X.Y || (X.Y = {})
        if argument_node.get('type') == _NodeType.ASSIGNMENT_EXPRESSION:
            return self._extract_enum_name_from_assignment(argument_node)

        # Logical OR pattern: E || (E = {})
        if argument_node.get('type') != _NodeType.LOGICAL_EXPRESSION:
            return None
        if argument_node.get('operator') != '||':
            return None

        return self._extract_enum_name_from_logical_or(argument_node)

    @staticmethod
    def _extract_enum_name_from_assignment(node: dict) -> str | None:
        """Extract enum name from assignment wrapper pattern: E = X.Y || (X.Y = {})."""
        if node.get('operator') != '=':
            return None
        assignment_left = node.get('left')
        if not is_identifier(assignment_left):
            return None
        inner = node.get('right')
        if inner and inner.get('type') == _NodeType.LOGICAL_EXPRESSION:
            return assignment_left['name']
        return None

    @staticmethod
    def _extract_enum_name_from_logical_or(node: dict) -> str | None:
        """Extract enum name from logical OR pattern: E || (E = {})."""
        left_node = node.get('left')
        right_node = node.get('right')
        if not is_identifier(left_node):
            return None

        name = left_node['name']
        if not right_node or right_node.get('type') != _NodeType.ASSIGNMENT_EXPRESSION:
            return None

        right_left = right_node.get('left')
        if is_identifier(right_left) and right_left['name'] == name:
            return name
        return None

    def _extract_enum_assignment(
        self, expression: dict | None, parameter_name: str
    ) -> tuple[str | None, int | float | None]:
        """Extract (member_name, value) from: param[param.NAME = VALUE] = "NAME".

        Returns (member_name, numeric_value) or (None, None).
        """
        if not expression or expression.get('type') != _NodeType.ASSIGNMENT_EXPRESSION:
            return None, None

        left_node = expression.get('left')
        if not self._is_computed_member_of(left_node, parameter_name):
            return None, None

        # The computed key is the inner assignment: param.NAME = VALUE
        inner_assignment = left_node.get('property')
        if not inner_assignment or inner_assignment.get('type') != _NodeType.ASSIGNMENT_EXPRESSION:
            return None, None

        return self._extract_member_value_from_inner(inner_assignment, parameter_name)

    @staticmethod
    def _is_computed_member_of(node: dict | None, expected_object_name: str) -> bool:
        """Check if node is a computed member expression on the expected object."""
        if not node or node.get('type') != _NodeType.MEMBER_EXPRESSION:
            return False
        if not node.get('computed'):
            return False
        object_node = node.get('object')
        return is_identifier(object_node) and object_node['name'] == expected_object_name

    @staticmethod
    def _extract_member_value_from_inner(
        inner_assignment: dict, parameter_name: str
    ) -> tuple[str | None, int | float | None]:
        """Extract member name and value from the inner assignment (param.NAME = VALUE)."""
        inner_left = inner_assignment.get('left')
        inner_right = inner_assignment.get('right')
        if not inner_left or inner_left.get('type') != _NodeType.MEMBER_EXPRESSION:
            return None, None

        inner_object = inner_left.get('object')
        inner_property = inner_left.get('property')
        if not is_identifier(inner_object) or inner_object['name'] != parameter_name:
            return None, None
        if not is_identifier(inner_property):
            return None, None

        member_name = inner_property['name']
        value = _get_numeric_value(inner_right)
        if value is None:
            return None, None
        return member_name, value


def _get_numeric_value(node: dict | None) -> int | float | None:
    """Extract a numeric value from a literal or unary minus expression."""
    if not node:
        return None
    if is_numeric_literal(node):
        return node['value']
    # Handle -N (UnaryExpression with operator '-' and numeric argument)
    if (
        node.get('type') == _NodeType.UNARY_EXPRESSION
        and node.get('operator') == '-'
        and is_numeric_literal(node.get('argument'))
    ):
        return -node['argument']['value']
    return None
