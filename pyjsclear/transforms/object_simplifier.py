"""Inline proxy object property accesses.

Detects: const o = {x: 1, y: "hello"}; ... o.x ... o.y ...
Replaces: ... 1 ... "hello" ...
"""

from ..scope import build_scope_tree
from ..traverser import find_parent
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import replace_identifiers
from .base import Transform


class ObjectSimplifier(Transform):
    """Replace proxy object property accesses with their literal values."""

    rebuild_scope = True

    def execute(self) -> bool:
        scope_tree, _ = build_scope_tree(self.ast)
        self._process_scope(scope_tree)
        return self.has_changed()

    def _process_scope(self, scope) -> None:
        for name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            initializer = node.get('init')
            if not initializer or initializer.get('type') != 'ObjectExpression':
                continue

            # Build property map (only literals and simple function expressions)
            properties = initializer.get('properties', [])
            if not self._is_proxy_object(properties):
                continue

            property_map = {}
            for property_node in properties:
                key = self._get_property_key(property_node)
                if key is None:
                    continue
                value = property_node.get('value')
                if is_literal(value):
                    property_map[key] = value
                elif value and value.get('type') in (
                    'FunctionExpression',
                    'ArrowFunctionExpression',
                ):
                    property_map[key] = value

            if not property_map:
                continue

            if self._has_property_assignment(binding):
                continue

            # Replace property accesses
            for reference_node, ref_parent, ref_key, ref_index in binding.references:
                if not ref_parent or ref_parent.get('type') != 'MemberExpression':
                    continue
                if ref_key != 'object':
                    continue

                member_expression = ref_parent
                property_name = self._get_member_prop_name(member_expression)
                if property_name is None or property_name not in property_map:
                    continue

                value = property_map[property_name]
                if is_literal(value):
                    if self._replace_node(member_expression, deep_copy(value)):
                        self.set_changed()
                    continue

                if value.get('type') not in (
                    'FunctionExpression',
                    'ArrowFunctionExpression',
                ):
                    continue
                self._try_inline_function_call(member_expression, value)

        for child in scope.children:
            self._process_scope(child)

    def _has_property_assignment(self, binding) -> bool:
        """Check if any reference to the binding is a property assignment target."""
        for reference_node, reference_parent, ref_key, ref_index in binding.references:
            if not (reference_parent and reference_parent.get('type') == 'MemberExpression' and ref_key == 'object'):
                continue
            member_expression_parent_info = find_parent(self.ast, reference_parent)
            if not member_expression_parent_info:
                continue
            parent, key, _ = member_expression_parent_info
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return True
        return False

    def _try_inline_function_call(self, member_expression, function_value) -> None:
        """Try to inline a function call at a MemberExpression site."""
        member_expression_parent_info = find_parent(self.ast, member_expression)
        if not member_expression_parent_info:
            return
        parent, key, _ = member_expression_parent_info
        if not (parent and parent.get('type') == 'CallExpression' and key == 'callee'):
            return
        replacement = self._inline_func(function_value, parent.get('arguments', []))
        if not replacement:
            return
        if self._replace_node(parent, replacement):
            self.set_changed()

    def _is_proxy_object(self, properties: list) -> bool:
        """Check if all properties are literals or simple functions."""
        for property_node in properties:
            if property_node.get('type') != 'Property':
                return False
            value = property_node.get('value')
            if not value:
                return False
            if is_literal(value):
                continue
            if value.get('type') in ('FunctionExpression', 'ArrowFunctionExpression'):
                continue
            return False
        return True

    def _get_property_key(self, property_node) -> str | None:
        """Get the string key of a property."""
        key = property_node.get('key')
        if not key:
            return None
        match key.get('type'):
            case 'Identifier':
                return key['name']
            case 'Literal' if is_string_literal(key):
                return key['value']
        return None

    def _get_member_prop_name(self, member_expression) -> str | None:
        """Get property name from a member expression."""
        prop = member_expression.get('property')
        if not prop:
            return None
        if member_expression.get('computed'):
            if is_string_literal(prop):
                return prop['value']
            return None
        if prop.get('type') == 'Identifier':
            return prop['name']
        return None

    def _replace_node(self, target, replacement) -> bool:
        """Replace target node in the AST. Returns True if replaced."""
        result = find_parent(self.ast, target)
        if result:
            parent, key, index = result
            if index is not None:
                parent[key][index] = replacement
            else:
                parent[key] = replacement
            return True
        return False

    def _inline_func(self, function_node, arguments: list):
        """Inline a simple function call."""
        body = function_node.get('body')
        if not body:
            return None
        if function_node.get('type') == 'ArrowFunctionExpression' and body.get('type') != 'BlockStatement':
            expr = deep_copy(body)
        elif body.get('type') == 'BlockStatement':
            statements = body.get('body', [])
            if len(statements) != 1 or statements[0].get('type') != 'ReturnStatement':
                return None
            argument = statements[0].get('argument')
            if not argument:
                return None
            expr = deep_copy(argument)
        else:
            return None

        params = function_node.get('params', [])
        param_map = {}
        for index, parameter in enumerate(params):
            if parameter.get('type') == 'Identifier':
                param_map[parameter['name']] = arguments[index] if index < len(arguments) else {'type': 'Identifier', 'name': 'undefined'}

        replace_identifiers(expr, param_map)
        return expr
