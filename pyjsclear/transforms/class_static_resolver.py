"""Resolve class static property accesses and inline static identity methods.

Handles two patterns common in esbuild-bundled obfuscated code:

1. Static constant propagation:
     var C = class {}; C.X = 100;
     ... C.X + 1 ...   ->   ... 100 + 1 ...

2. Static identity method inlining:
     var C = class { static id(x) { return x; } };
     ... C.id(expr) ...   ->   ... expr ...
"""

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from .base import Transform


class ClassStaticResolver(Transform):
    """Inline class static constant properties and identity methods."""

    def execute(self) -> bool:
        """Run static property propagation and identity method inlining."""
        class_variables = self._find_class_variables()
        if not class_variables:
            return False

        static_properties = self._collect_static_properties(class_variables)
        static_methods = self._collect_static_identity_methods(class_variables)

        if not static_properties and not static_methods:
            return False

        self._replace_accesses(class_variables, static_properties, static_methods)
        return self.has_changed()

    def _find_class_variables(self) -> dict[str, dict]:
        """Find variables assigned to class expressions (var X = class {})."""
        class_variables: dict[str, dict] = {}

        def visitor(node: dict, _parent: dict | None) -> None:
            if node.get('type') != 'VariableDeclarator':
                return
            initializer = node.get('init')
            if not initializer or initializer.get('type') != 'ClassExpression':
                return
            declarator_id = node.get('id')
            if declarator_id and is_identifier(declarator_id):
                class_variables[declarator_id['name']] = initializer

        simple_traverse(self.ast, visitor)
        return class_variables

    def _collect_static_properties(self, class_variables: dict[str, dict]) -> dict[tuple[str, str], dict]:
        """Collect static properties assigned after class definition (ClassName.prop = literal)."""
        static_properties: dict[tuple[str, str], dict] = {}
        reassigned_properties: set[tuple[str, str]] = set()

        def visitor(node: dict, _parent: dict | None) -> None:
            if node.get('type') != 'AssignmentExpression' or node.get('operator') != '=':
                return
            left_side = node.get('left')
            if not left_side or left_side.get('type') != 'MemberExpression':
                return
            object_node = left_side.get('object')
            if not object_node or not is_identifier(object_node):
                return
            object_name = object_node['name']
            if object_name not in class_variables:
                return

            property_name = self._extract_property_name(left_side)
            if property_name is None:
                return

            property_key = (object_name, property_name)
            value_node = node.get('right')
            if property_key in static_properties:
                reassigned_properties.add(property_key)
            elif value_node and is_literal(value_node):
                static_properties[property_key] = value_node

        simple_traverse(self.ast, visitor)

        for reassigned_key in reassigned_properties:
            static_properties.pop(reassigned_key, None)

        return static_properties

    def _collect_static_identity_methods(self, class_variables: dict[str, dict]) -> dict[tuple[str, str], dict]:
        """Collect static methods that are identity functions from class bodies."""
        static_methods: dict[tuple[str, str], dict] = {}

        for class_name, class_node in class_variables.items():
            body = class_node.get('body')
            if not body or body.get('type') != 'ClassBody':
                continue
            for member in body.get('body', []):
                if member.get('type') != 'MethodDefinition':
                    continue
                if not member.get('static'):
                    continue
                method_key = member.get('key')
                if not method_key or not is_identifier(method_key):
                    continue
                method_name = method_key['name']
                method_value = member.get('value')
                if not method_value:
                    continue
                if self._is_identity_function(method_value):
                    static_methods[(class_name, method_name)] = method_value

        return static_methods

    def _replace_accesses(
        self,
        class_variables: dict[str, dict],
        static_properties: dict[tuple[str, str], dict],
        static_methods: dict[tuple[str, str], dict],
    ) -> None:
        """Replace static property accesses and identity method calls."""
        self.get_parent_map()

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            if node.get('type') != 'MemberExpression':
                return None
            object_node = node.get('object')
            if not object_node or not is_identifier(object_node):
                return None
            object_name = object_node['name']
            if object_name not in class_variables:
                return None
            property_name = self._extract_property_name(node)
            if property_name is None:
                return None

            property_key = (object_name, property_name)

            # Skip definition sites (left-hand side of assignments)
            if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
                return None

            if property_key in static_properties:
                replacement = deep_copy(static_properties[property_key])
                self._replace_in_parent(node, replacement, parent, key, index)
                self.set_changed()
                return replacement

            if property_key in static_methods:
                self._try_inline_identity(node, parent, key, index)

            return None

        traverse(self.ast, {'enter': enter})
        self.invalidate_parent_map()

    def _extract_property_name(self, member_expression: dict) -> str | None:
        """Extract the property name from a MemberExpression node."""
        property_node = member_expression.get('property')
        if not property_node:
            return None
        if member_expression.get('computed'):
            if is_string_literal(property_node):
                return property_node['value']
            return None
        if is_identifier(property_node):
            return property_node['name']
        return None

    def _is_identity_function(self, function_node: dict) -> bool:
        """Check if a function simply returns its first argument."""
        params = function_node.get('params', [])
        if len(params) != 1:
            return False
        parameter = params[0]
        if not is_identifier(parameter):
            return False
        body = function_node.get('body')
        if not body or body.get('type') != 'BlockStatement':
            return False
        statements = body.get('body', [])
        if len(statements) != 1 or statements[0].get('type') != 'ReturnStatement':
            return False
        return_argument = statements[0].get('argument')
        if not return_argument or not is_identifier(return_argument):
            return False
        return return_argument['name'] == parameter['name']

    def _try_inline_identity(
        self,
        member_expression: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Inline Class.identity(arg) to arg."""
        if not parent or parent.get('type') != 'CallExpression' or key != 'callee':
            return
        arguments = parent.get('arguments', [])
        if len(arguments) != 1:
            return
        replacement = deep_copy(arguments[0])
        parent_map = self.get_parent_map()
        grandparent_result = parent_map.get(id(parent))
        if not grandparent_result:
            return
        grandparent, grandparent_key, grandparent_index = grandparent_result
        self._replace_in_parent(parent, replacement, grandparent, grandparent_key, grandparent_index)
        self.set_changed()

    def _replace_in_parent(
        self,
        target: dict,
        replacement: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
    ) -> None:
        """Replace target node in the AST using known parent info."""
        if parent is None or key is None:
            return
        if index is not None:
            parent[key][index] = replacement
        else:
            parent[key] = replacement
