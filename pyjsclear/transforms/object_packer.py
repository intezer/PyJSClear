"""Consolidate sequential obj.x = ... assignments into object literal.

Detects: var o = {}; o.x = 1; o.y = 2;
Replaces: var o = {x: 1, y: 2};
"""

from .base import Transform
from ..utils.ast_helpers import is_identifier


class ObjectPacker(Transform):
    """Pack sequential property assignments into object initializers."""

    def execute(self):
        self._process_bodies(self.ast)
        return self.has_changed()

    def _process_bodies(self, node):
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

    def _try_pack_body(self, body):
        """Find empty object declarations followed by property assignments and pack them."""
        i = 0
        while i < len(body):
            stmt = body[i]
            if not isinstance(stmt, dict):
                i += 1
                continue

            # Find: var obj = {} or let obj = {} or const obj = {}
            obj_name = None
            obj_decl = None
            obj_expr = None

            if stmt.get('type') == 'VariableDeclaration':
                for d in stmt.get('declarations', []):
                    init = d.get('init')
                    if (
                        init
                        and init.get('type') == 'ObjectExpression'
                        and len(init.get('properties', [])) == 0
                        and d.get('id', {}).get('type') == 'Identifier'
                    ):
                        obj_name = d['id']['name']
                        obj_decl = d
                        obj_expr = init
                        break

            if obj_name is None:
                i += 1
                continue

            # Collect consecutive property assignments
            assignments = []
            j = i + 1
            while j < len(body):
                s = body[j]
                if not isinstance(s, dict) or s.get('type') != 'ExpressionStatement':
                    break
                expr = s.get('expression')
                if (
                    not expr
                    or expr.get('type') != 'AssignmentExpression'
                    or expr.get('operator') != '='
                ):
                    break
                left = expr.get('left')
                if not left or left.get('type') != 'MemberExpression':
                    break
                obj = left.get('object')
                if not is_identifier(obj) or obj.get('name') != obj_name:
                    break
                prop = left.get('property')
                right = expr.get('right')
                # Get property key
                if prop is None:
                    break
                # Support both computed and non-computed property keys
                prop_key = prop

                # Don't pack self-referential assignments (o.x = o.y)
                if self._references_name(right, obj_name):
                    break

                computed = left.get('computed', False)
                assignments.append((prop_key, right, computed))
                j += 1

            if assignments:
                # Pack into the object literal
                for prop_key, value, computed in assignments:
                    prop = {
                        'type': 'Property',
                        'key': prop_key,
                        'value': value,
                        'kind': 'init',
                        'method': False,
                        'shorthand': False,
                        'computed': computed,
                    }
                    obj_expr['properties'].append(prop)
                # Remove the assignment statements
                del body[i + 1 : j]
                self.set_changed()

            i += 1

    def _references_name(self, node, name):
        """Check if a node references a given identifier name."""
        if not isinstance(node, dict) or 'type' not in node:
            return False
        if node.get('type') == 'Identifier' and node.get('name') == name:
            return True
        from ..utils.ast_helpers import get_child_keys

        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if self._references_name(item, name):
                        return True
            elif isinstance(child, dict):
                if self._references_name(child, name):
                    return True
        return False
