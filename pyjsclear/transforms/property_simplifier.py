"""Convert computed property access to dot notation: obj["x"] -> obj.x"""

from __future__ import annotations

from enum import StrEnum

from ..traverser import traverse
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import is_valid_identifier
from .base import Transform


class _NodeType(StrEnum):
    """AST node types handled by PropertySimplifier."""

    MEMBER_EXPRESSION = 'MemberExpression'
    PROPERTY = 'Property'
    METHOD_DEFINITION = 'MethodDefinition'
    IDENTIFIER = 'Identifier'


class PropertySimplifier(Transform):
    """Simplify obj["prop"] to obj.prop when prop is a valid identifier."""

    def execute(self) -> bool:
        """Run all property simplification passes over the AST."""
        traverse(self.ast, {'enter': self._simplify_member_expression})
        traverse(self.ast, {'enter': self._simplify_object_key})
        traverse(self.ast, {'enter': self._simplify_method_key})
        return self.has_changed()

    def _replace_with_identifier(self, node: dict, property_name: str) -> None:
        """Replace a computed/literal key with an Identifier node and mark changed."""
        node['computed'] = False
        node['key' if 'key' in node else 'property'] = {
            'type': _NodeType.IDENTIFIER,
            'name': property_name,
        }
        self.set_changed()

    def _simplify_member_expression(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Convert obj["prop"] to obj.prop for valid identifiers."""
        if node.get('type') != _NodeType.MEMBER_EXPRESSION:
            return
        if not node.get('computed'):
            return
        property_node = node.get('property')
        if not is_string_literal(property_node):
            return
        property_name = property_node.get('value', '')
        if not is_valid_identifier(property_name):
            return

        node['computed'] = False
        node['property'] = {'type': _NodeType.IDENTIFIER, 'name': property_name}
        self.set_changed()

    def _simplify_object_key(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Simplify computed and non-computed string literal keys in object literals."""
        if node.get('type') != _NodeType.PROPERTY:
            return

        key_node = node.get('key')
        if not is_string_literal(key_node):
            return

        property_name = key_node.get('value', '')
        is_computed = node.get('computed', False)

        match (is_computed, is_valid_identifier(property_name)):
            case (True, True):
                # ["validName"] -> validName
                self._replace_with_identifier(node, property_name)
            case (True, False):
                # ["invalid-name"] -> just remove computed flag
                node['computed'] = False
                self.set_changed()
            case (False, True):
                # "validName" -> validName
                self._replace_with_identifier(node, property_name)

    def _simplify_method_key(
        self,
        node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Simplify string literal method keys: static ["name"]() -> static name()."""
        if node.get('type') != _NodeType.METHOD_DEFINITION:
            return
        key_node = node.get('key')
        if not is_string_literal(key_node):
            return
        property_name = key_node.get('value', '')
        if not is_valid_identifier(property_name):
            return

        self._replace_with_identifier(node, property_name)
