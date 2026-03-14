"""Consolidate sequential obj.x = ... assignments into object literal.

Detects: var o = {}; o.x = 1; o.y = 2;
Replaces: var o = {x: 1, y: 2};
"""

from __future__ import annotations

from ..utils.ast_helpers import get_child_keys
from ..utils.ast_helpers import is_identifier
from .base import Transform


class ObjectPacker(Transform):
    """Pack sequential property assignments into object initializers."""

    def execute(self) -> bool:
        """Run the transform and return whether any changes were made."""
        self._process_bodies(self.ast)
        return self.has_changed()

    def _process_bodies(self, node: dict) -> None:
        """Iteratively find body arrays and try packing."""
        stack: list[dict] = [node] if isinstance(node, dict) else []
        while stack:
            current = stack.pop()
            for child in current.values():
                if isinstance(child, list):
                    if child and isinstance(child[0], dict) and 'type' in child[0]:
                        self._try_pack_body(child)
                        stack.extend(item for item in child if isinstance(item, dict))
                elif isinstance(child, dict) and 'type' in child:
                    stack.append(child)

    @staticmethod
    def _find_empty_object_declaration(statement: dict) -> tuple[str, dict, dict] | None:
        """Return (name, declarator, object_expression) for an empty object literal, or None."""
        if statement.get('type') != 'VariableDeclaration':
            return None
        for declaration in statement.get('declarations', []):
            initializer = declaration.get('init')
            if (
                initializer
                and initializer.get('type') == 'ObjectExpression'
                and len(initializer.get('properties', [])) == 0
                and declaration.get('id', {}).get('type') == 'Identifier'
            ):
                return declaration['id']['name'], declaration, initializer
        return None

    def _try_pack_body(self, body: list[dict]) -> None:
        """Find empty object declarations followed by property assignments and pack them."""
        statement_index = 0
        while statement_index < len(body):
            statement = body[statement_index]
            if not isinstance(statement, dict):
                statement_index += 1
                continue

            found = self._find_empty_object_declaration(statement)
            if not found:
                statement_index += 1
                continue

            object_name, _declarator, object_expression = found
            assignments = self._collect_assignments(body, statement_index + 1, object_name)

            if assignments:
                self._pack_assignments(object_expression, assignments)
                end_index = statement_index + 1 + len(assignments)
                del body[statement_index + 1 : end_index]
                self.set_changed()

            statement_index += 1

    def _collect_assignments(
        self,
        body: list[dict],
        start_index: int,
        object_name: str,
    ) -> list[tuple[dict, dict, bool]]:
        """Collect consecutive property assignments targeting the named object."""
        assignments: list[tuple[dict, dict, bool]] = []
        scan_index = start_index
        while scan_index < len(body):
            candidate = body[scan_index]
            if not isinstance(candidate, dict) or candidate.get('type') != 'ExpressionStatement':
                break

            expression = candidate.get('expression')
            if not self._is_simple_member_assignment(expression, object_name):
                break

            left_side = expression.get('left')
            property_key = left_side.get('property')
            right_side = expression.get('right')
            if property_key is None:
                break

            # Don't pack self-referential assignments (o.x = o.y)
            if self._references_name(right_side, object_name):
                break

            computed = left_side.get('computed', False)
            assignments.append((property_key, right_side, computed))
            scan_index += 1

        return assignments

    @staticmethod
    def _is_simple_member_assignment(expression: dict | None, object_name: str) -> bool:
        """Check whether expression is `object_name.prop = value`."""
        if not expression:
            return False
        if expression.get('type') != 'AssignmentExpression' or expression.get('operator') != '=':
            return False
        left_side = expression.get('left')
        if not left_side or left_side.get('type') != 'MemberExpression':
            return False
        object_reference = left_side.get('object')
        return bool(is_identifier(object_reference) and object_reference.get('name') == object_name)

    @staticmethod
    def _pack_assignments(
        object_expression: dict,
        assignments: list[tuple[dict, dict, bool]],
    ) -> None:
        """Append collected property assignments into the object literal."""
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
            object_expression['properties'].append(new_property)

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
