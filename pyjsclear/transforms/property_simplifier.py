"""Convert computed property access to dot notation: obj["x"] -> obj.x"""

from ..traverser import traverse
from ..utils.ast_helpers import is_string_literal, is_valid_identifier
from .base import Transform


class PropertySimplifier(Transform):
    """Simplify obj["prop"] to obj.prop when prop is a valid identifier."""

    def execute(self):
        def enter(node, parent, key, index):
            if node.get('type') != 'MemberExpression':
                return
            if not node.get('computed'):
                return
            prop = node.get('property')
            if not is_string_literal(prop):
                return
            name = prop.get('value', '')
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
                k = node.get('key')
                if is_string_literal(k) and is_valid_identifier(k.get('value', '')):
                    node['key'] = {'type': 'Identifier', 'name': k['value']}
                    self.set_changed()

        traverse(self.ast, {'enter': enter_obj})
        return self.has_changed()
