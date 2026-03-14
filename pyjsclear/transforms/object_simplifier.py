"""Inline proxy object property accesses.

Detects: const o = {x: 1, y: "hello"}; ... o.x ... o.y ...
Replaces: ... 1 ... "hello" ...
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..scope import build_scope_tree
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import replace_identifiers
from .base import Transform


if TYPE_CHECKING:
    from ..scope import Binding
    from ..scope import Scope


_FUNCTION_TYPES = ('FunctionExpression', 'ArrowFunctionExpression')


class ObjectSimplifier(Transform):
    """Replace proxy object property accesses with their literal values."""

    rebuild_scope = True

    def execute(self) -> bool:
        """Run the transform, inlining proxy object properties."""
        scope_tree = self.scope_tree if self.scope_tree is not None else build_scope_tree(self.ast)[0]
        self._process_scope(scope_tree)
        return self.has_changed()

    def _process_scope(self, scope: Scope) -> None:
        """Walk a scope tree inlining literal and function proxy properties."""
        for name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue

            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue

            initializer = node.get('init')
            if not initializer or initializer.get('type') != 'ObjectExpression':
                continue

            properties = initializer.get('properties', [])
            if not self._is_proxy_object(properties):
                continue

            property_map = self._build_property_map(properties)
            if not property_map:
                continue

            if self._has_property_assignment(binding):
                continue

            self._inline_property_references(binding, property_map)

        for child in scope.children:
            self._process_scope(child)

    def _build_property_map(self, properties: list[dict]) -> dict[str, dict]:
        """Build a mapping from property keys to their literal or function values."""
        property_map: dict[str, dict] = {}
        for property_node in properties:
            key = self._get_property_key(property_node)
            if key is None:
                continue
            value = property_node.get('value')
            if is_literal(value):
                property_map[key] = value
            elif value and value.get('type') in _FUNCTION_TYPES:
                property_map[key] = value
        return property_map

    def _inline_property_references(self, binding: Binding, property_map: dict[str, dict]) -> None:
        """Replace all member-expression references to binding with inlined values."""
        for reference_node, reference_parent, reference_key, reference_index in binding.references:
            if not reference_parent or reference_parent.get('type') != 'MemberExpression':
                continue
            if reference_key != 'object':
                continue

            member_expression = reference_parent
            property_name = self._get_member_property_name(member_expression)
            if property_name is None or property_name not in property_map:
                continue

            value = property_map[property_name]
            if is_literal(value):
                if self._replace_node(member_expression, deep_copy(value)):
                    self.set_changed()
                continue

            if value.get('type') in _FUNCTION_TYPES:
                self._try_inline_function_call(member_expression, value)

    def _has_property_assignment(self, binding: Binding) -> bool:
        """Check if any reference to the binding is a property assignment target."""
        for reference_node, reference_parent, reference_key, reference_index in binding.references:
            if not (
                reference_parent and reference_parent.get('type') == 'MemberExpression' and reference_key == 'object'
            ):
                continue
            member_expression_parent_info = self.find_parent(reference_parent)
            if not member_expression_parent_info:
                continue
            parent, key, _ = member_expression_parent_info
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return True
        return False

    def _try_inline_function_call(self, member_expression: dict, function_value: dict) -> None:
        """Try to inline a function call at a MemberExpression site."""
        member_expression_parent_info = self.find_parent(member_expression)
        if not member_expression_parent_info:
            return
        parent, key, _ = member_expression_parent_info
        if not (parent and parent.get('type') == 'CallExpression' and key == 'callee'):
            return
        replacement = self._inline_function(function_value, parent.get('arguments', []))
        if not replacement:
            return
        if self._replace_node(parent, replacement):
            self.set_changed()

    def _is_proxy_object(self, properties: list[dict]) -> bool:
        """Check if all properties are literals or simple functions."""
        for property_node in properties:
            if property_node.get('type') != 'Property':
                return False
            value = property_node.get('value')
            if not value:
                return False
            if is_literal(value):
                continue
            if value.get('type') in _FUNCTION_TYPES:
                continue
            return False
        return True

    def _get_property_key(self, property_node: dict) -> str | None:
        """Get the string key of a property node."""
        key = property_node.get('key')
        if not key:
            return None
        match key.get('type'):
            case 'Identifier':
                return key['name']
            case 'Literal' if is_string_literal(key):
                return key['value']
        return None

    def _get_member_property_name(self, member_expression: dict) -> str | None:
        """Get the resolved property name from a member expression."""
        property_node = member_expression.get('property')
        if not property_node:
            return None
        if member_expression.get('computed'):
            if is_string_literal(property_node):
                return property_node['value']
            return None
        if property_node.get('type') == 'Identifier':
            return property_node['name']
        return None

    def _replace_node(self, target: dict, replacement: dict) -> bool:
        """Replace target node in the AST. Returns True if replaced."""
        result = self.find_parent(target)
        if not result:
            return False
        parent, key, index = result
        if index is not None:
            parent[key][index] = replacement
        else:
            parent[key] = replacement
        self.invalidate_parent_map()
        return True

    def _inline_function(self, function_node: dict, arguments: list[dict]) -> dict | None:
        """Inline a simple single-return function call, substituting arguments for parameters."""
        body = function_node.get('body')
        if not body:
            return None

        expression = self._extract_return_expression(function_node, body)
        if expression is None:
            return None

        parameter_map = self._build_parameter_map(function_node.get('params', []), arguments)
        replace_identifiers(expression, parameter_map)
        return expression

    def _extract_return_expression(self, function_node: dict, body: dict) -> dict | None:
        """Extract the single return expression from a function body."""
        match function_node.get('type'):
            case 'ArrowFunctionExpression' if body.get('type') != 'BlockStatement':
                return deep_copy(body)
            case _ if body.get('type') == 'BlockStatement':
                statements = body.get('body', [])
                if len(statements) != 1 or statements[0].get('type') != 'ReturnStatement':
                    return None
                argument = statements[0].get('argument')
                if not argument:
                    return None
                return deep_copy(argument)
        return None

    def _build_parameter_map(self, params: list[dict], arguments: list[dict]) -> dict[str, dict]:
        """Map function parameter names to their corresponding call arguments."""
        parameter_map: dict[str, dict] = {}
        for index, parameter in enumerate(params):
            if parameter.get('type') != 'Identifier':
                continue
            parameter_map[parameter['name']] = (
                arguments[index] if index < len(arguments) else {'type': 'Identifier', 'name': 'undefined'}
            )
        return parameter_map
