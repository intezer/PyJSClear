"""Convert computed property access to dot notation: obj["x"] -> obj.x"""

from ..traverser import traverse
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import is_valid_identifier
from .base import Transform


class PropertySimplifier(Transform):
    """Simplify obj["prop"] to obj.prop when prop is a valid identifier."""

    def execute(self):
        def enter(node, parent, key, index):
            if node.get('type') != 'MemberExpression':
                return
            if not node.get('computed'):
                return
            property_node = node.get('property')
            if not is_string_literal(property_node):
                return
            name = property_node.get('value', '')
            if not is_valid_identifier(name):
                return
            # Convert to dot notation
            node['computed'] = False
            node['property'] = {'type': 'Identifier', 'name': name}
            self.set_changed()

        traverse(self.ast, {'enter': enter})

        # Also simplify computed property keys in object literals
        def enter_obj(node, parent, key, index):
            if node.get('type') != 'Property':
                return
            if not node.get('computed'):
                # Check string literal keys
                key_node = node.get('key')
                if is_string_literal(key_node) and is_valid_identifier(key_node.get('value', '')):
                    node['key'] = {'type': 'Identifier', 'name': key_node['value']}
                    self.set_changed()

        traverse(self.ast, {'enter': enter_obj})

        # Simplify method definitions with string literal keys:
        # static ["name"]() → static name()
        # Also handles cases where parser sets computed=False but key is still a Literal
        def enter_method(node, parent, key, index):
            if node.get('type') != 'MethodDefinition':
                return
            key_node = node.get('key')
            if not is_string_literal(key_node):
                return
            name = key_node.get('value', '')
            if not is_valid_identifier(name):
                return
            node['computed'] = False
            node['key'] = {'type': 'Identifier', 'name': name}
            self.set_changed()

        traverse(self.ast, {'enter': enter_method})
        return self.has_changed()
