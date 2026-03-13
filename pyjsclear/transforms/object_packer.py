"""Consolidate sequential obj.x = ... assignments into object literal.

Detects: var o = {}; o.x = 1; o.y = 2;
Replaces: var o = {x: 1, y: 2};
"""

from ..utils.ast_helpers import get_child_keys
from ..utils.ast_helpers import is_identifier
from .base import Transform


class ObjectPacker(Transform):
    """Pack sequential property assignments into object initializers."""

    def execute(self) -> bool:
        self._process_bodies(self.ast)
        return self.has_changed()

    def _process_bodies(self, node: dict) -> None:
        """Recursively find body arrays and try packing."""
        if not isinstance(node, dict):
            return
        for key, child in node.items():
            if isinstance(child, list):
                if child and isinstance(child[0], dict) and 'type' in child[0]:
                    self._try_pack_body(child)
                    for item in child:
                        self._process_bodies(item)
            elif isinstance(child, dict) and 'type' in child:
                self._process_bodies(child)

    @staticmethod
    def _find_empty_object_declaration(stmt: dict) -> tuple[str, dict, dict] | None:
        """Find an empty object literal in a VariableDeclaration.

        Returns (name, declarator, object_expression) or None.
        """
        if stmt.get('type') != 'VariableDeclaration':
            return None
        for declaration in stmt.get('declarations', []):
            initializer = declaration.get('init')
            if (
                initializer
                and initializer.get('type') == 'ObjectExpression'
                and len(initializer.get('properties', [])) == 0
                and declaration.get('id', {}).get('type') == 'Identifier'
            ):
                return declaration['id']['name'], declaration, initializer
        return None

    def _try_pack_body(self, body: list) -> None:
        """Find empty object declarations followed by property assignments and pack them."""
        i = 0
        while i < len(body):
            stmt = body[i]
            if not isinstance(stmt, dict):
                i += 1
                continue

            found = self._find_empty_object_declaration(stmt)
            if not found:
                i += 1
                continue

            object_name, obj_decl, obj_expr = found

            # Collect consecutive property assignments
            assignments = []
            j = i + 1
            while j < len(body):
                statement = body[j]
                if not isinstance(statement, dict) or statement.get('type') != 'ExpressionStatement':
                    break
                expr = statement.get('expression')
                if not expr or expr.get('type') != 'AssignmentExpression' or expr.get('operator') != '=':
                    break
                left = expr.get('left')
                if not left or left.get('type') != 'MemberExpression':
                    break
                object_reference = left.get('object')
                if not is_identifier(object_reference) or object_reference.get('name') != object_name:
                    break
                property_node = left.get('property')
                right = expr.get('right')
                if property_node is None:
                    break
                property_key = property_node

                # Don't pack self-referential assignments (o.x = o.y)
                if self._references_name(right, object_name):
                    break

                computed = left.get('computed', False)
                assignments.append((property_key, right, computed))
                j += 1

            if assignments:
                # Pack into the object literal
                for property_key, value, computed in assignments:
                    new_property = {
                        'type': 'Property',
                        'key': property_key,
                        'value': value,
                        'kind': 'init',
                        'method': False,
                        'shorthand': False,
                        'computed': computed,
                    }
                    obj_expr['properties'].append(new_property)
                # Remove the assignment statements
                del body[i + 1:j]
                self.set_changed()

            i += 1

    def _references_name(self, node: dict, name: str) -> bool:
        """Check if a node references a given identifier name."""
        if not isinstance(node, dict) or 'type' not in node:
            return False
        if node.get('type') == 'Identifier' and node.get('name') == name:
            return True
        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                if any(self._references_name(item, name) for item in child):
                    return True
            elif isinstance(child, dict) and self._references_name(child, name):
                return True
        return False
