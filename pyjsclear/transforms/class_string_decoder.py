"""Decode class-based string encoding patterns.

Detects patterns like:
    var _0x3bb8cb = class {};
    _0x3bb8cb["prop1"] = "abc";
    ...
    _0x3bb8cb["arrayProp"] = [_0x3bb8cb["prop1"], ...];

    var _0x279589 = class {
        static ["decoderMethod"](arr) {
            let s = '';
            const table = _0x3bb8cb.arrayProp;
            for (...) { s += table[arr[i] - 48][0]; }
            return s;
        }
    };

    _0x279589.X = _0x2db60b.decoderMethod([0x4f, 0x3a, 0x5a]);

And replaces decoder calls with the decoded string literal, then inlines the
resolved constants at their usage sites.
"""

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import get_member_names
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import make_literal
from .base import Transform


# Type aliases for clarity
ClassProperties = dict[str, dict[str, str | tuple[str, list[dict]]]]
DecoderMap = dict[tuple[str, str], tuple[list[str], int]]
DecodedConstants = dict[tuple[str, str], str]


class ClassStringDecoder(Transform):
    """Resolve class-based string encoder patterns.

    Finds class variables with static string properties and decoder methods,
    then replaces decoder calls with their decoded string literals.
    """

    def execute(self) -> bool:
        """Run the decoder transform and return whether the AST changed."""
        class_properties: ClassProperties = {}
        decoder_map: DecoderMap = {}

        self._collect_class_properties(class_properties)
        self._find_decoders(class_properties, decoder_map)

        if not decoder_map:
            return False

        self._resolve_aliases(decoder_map)
        self._resolve_calls(decoder_map)
        return self.has_changed()

    def _collect_class_properties(self, class_properties: ClassProperties) -> None:
        """Collect static property assignments on class variables.

        Builds: class_properties[variable_name] = {property_name: value, ...}
        Also detects array properties that reference other properties.
        """

        def visit(node: dict, parent: dict) -> None:
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return

            variable_name, property_name = get_member_names(node.get('left'))
            if not variable_name:
                return

            right_side = node.get('right')
            if variable_name not in class_properties:
                class_properties[variable_name] = {}

            if is_string_literal(right_side):
                class_properties[variable_name][property_name] = right_side['value']
            elif right_side and right_side.get('type') == 'ArrayExpression':
                elements = right_side.get('elements', [])
                class_properties[variable_name][property_name] = ('array', elements)

        simple_traverse(self.ast, visit)

    def _resolve_array(
        self,
        class_properties: ClassProperties,
        variable_name: str,
        elements: list[dict],
    ) -> list[str] | None:
        """Resolve an array of MemberExpression references to string values."""
        properties = class_properties.get(variable_name, {})
        resolved = []
        for element in elements:
            element_object, element_property = get_member_names(element)
            if not element_object or element_object != variable_name:
                return None
            value = properties.get(element_property)
            if not isinstance(value, str):
                return None
            resolved.append(value)
        return resolved

    def _find_decoders(
        self,
        class_properties: ClassProperties,
        decoder_map: DecoderMap,
    ) -> None:
        """Find decoder methods and their associated lookup tables."""

        def visit(node: dict, parent: dict) -> None:
            if node.get('type') != 'MethodDefinition':
                return
            if not node.get('static'):
                return

            method_name = self._extract_method_name(node)
            if not method_name:
                return

            function_node = node.get('value')
            if not function_node or function_node.get('type') != 'FunctionExpression':
                return
            if len(function_node.get('params', [])) != 1:
                return

            body = function_node.get('body')
            if not body or body.get('type') != 'BlockStatement':
                return
            statements = body.get('body', [])
            if len(statements) < 3:
                return

            table_info = self._extract_decoder_table(statements, class_properties)
            if not table_info:
                return

            lookup_table, offset = table_info

            class_variable = self._find_enclosing_class_variable(node)
            if not class_variable:
                return

            decoder_map[(class_variable, method_name)] = (lookup_table, offset)

        simple_traverse(self.ast, visit)

    @staticmethod
    def _extract_method_name(method_node: dict) -> str | None:
        """Extract the method name from a MethodDefinition node."""
        method_key = method_node.get('key')
        if not method_key:
            return None
        match method_key.get('type'):
            case 'Literal' if isinstance(method_key.get('value'), str):
                return method_key['value']
            case 'Identifier':
                return method_key['name']
            case _:
                return None

    def _resolve_aliases(self, decoder_map: DecoderMap) -> None:
        """Register identifier aliases (X = Y) where Y is a decoder class."""
        decoder_classes = {class_name for class_name, _ in decoder_map}
        new_entries: DecoderMap = {}

        def visit(node: dict, parent: dict) -> None:
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return
            left_side = node.get('left')
            right_side = node.get('right')
            if not left_side or left_side.get('type') != 'Identifier':
                return
            if not right_side or right_side.get('type') != 'Identifier':
                return
            if right_side['name'] not in decoder_classes:
                return
            alias_name = left_side['name']
            for (class_name, method), value in decoder_map.items():
                if class_name == right_side['name']:
                    new_entries[(alias_name, method)] = value

        simple_traverse(self.ast, visit)
        decoder_map.update(new_entries)

    def _extract_decoder_table(
        self,
        statements: list[dict],
        class_properties: ClassProperties,
    ) -> tuple[list[str], int] | None:
        """Extract the lookup table and offset from decoder method body."""
        table_class_variable = None
        table_property = None

        for statement in statements:
            if statement.get('type') != 'VariableDeclaration':
                continue
            for declaration in statement.get('declarations', []):
                initializer = declaration.get('init')
                object_name, property_name = get_member_names(initializer)
                if not object_name or not property_name:
                    continue
                declaration_identifier = declaration.get('id')
                if declaration_identifier and declaration_identifier.get('type') == 'Identifier':
                    table_class_variable = object_name
                    table_property = property_name

        if not table_class_variable:
            return None

        properties = class_properties.get(table_class_variable, {})
        array_value = properties.get(table_property)
        if not isinstance(array_value, tuple) or array_value[0] != 'array':
            return None

        resolved = self._resolve_array(class_properties, table_class_variable, array_value[1])
        if not resolved:
            return None

        offset = self._find_offset(statements)
        return resolved, offset

    def _find_offset(self, statements: list[dict]) -> int:
        """Find the subtraction offset in the decoder loop (e.g., - 48)."""
        offset = 48

        def scan(node: dict, parent: dict) -> None:
            nonlocal offset
            if not isinstance(node, dict):
                return
            if node.get('type') != 'BinaryExpression':
                return
            if node.get('operator') != '-':
                return
            right_side = node.get('right')
            if not right_side or not is_numeric_literal(right_side):
                return
            numeric_value = right_side['value']
            if isinstance(numeric_value, (int, float)) and numeric_value > 0:
                offset = int(numeric_value)

        for statement in statements:
            if statement.get('type') == 'ForStatement':
                simple_traverse(statement, scan)

        return offset

    def _find_enclosing_class_variable(self, method_node: dict) -> str | None:
        """Find the variable name of the class containing this method."""
        enclosing_name: str | None = None

        def check_class_body(class_expression: dict, variable_name: str) -> bool:
            nonlocal enclosing_name
            body = class_expression.get('body')
            if not body or body.get('type') != 'ClassBody':
                return False
            for member in body.get('body', []):
                if member is method_node:
                    enclosing_name = variable_name
                    return True
            return False

        def scan(node: dict, parent: dict) -> None:
            if enclosing_name:
                return
            match node.get('type'):
                case 'VariableDeclarator':
                    initializer = node.get('init')
                    if not initializer or initializer.get('type') != 'ClassExpression':
                        return
                    declaration_identifier = node.get('id')
                    if declaration_identifier and declaration_identifier.get('type') == 'Identifier':
                        check_class_body(initializer, declaration_identifier['name'])
                case 'AssignmentExpression':
                    right_side = node.get('right')
                    if not right_side or right_side.get('type') != 'ClassExpression':
                        return
                    left_side = node.get('left')
                    if left_side and left_side.get('type') == 'Identifier':
                        check_class_body(right_side, left_side['name'])

        simple_traverse(self.ast, scan)
        return enclosing_name

    def _decode_call(
        self,
        lookup_table: list[str],
        offset: int,
        arguments: list[dict],
    ) -> str | None:
        """Statically evaluate a decoder call: decode([0x4f, 0x3a, ...])."""
        if len(arguments) != 1:
            return None
        argument = arguments[0]
        if not argument or argument.get('type') != 'ArrayExpression':
            return None
        elements = argument.get('elements', [])
        result = ''
        for element in elements:
            if not is_numeric_literal(element):
                return None
            index = int(element['value']) - offset
            if index < 0 or index >= len(lookup_table):
                return None
            entry = lookup_table[index]
            if not entry:
                return None
            result += entry[0]
        return result

    def _resolve_calls(self, decoder_map: DecoderMap) -> None:
        """Replace all decoder calls with their decoded string literals."""
        decoded_constants: DecodedConstants = {}

        def enter(
            node: dict,
            parent: dict,
            key: str,
            index: int | None,
        ) -> dict | None:
            if node.get('type') != 'CallExpression':
                return None
            callee = node.get('callee')
            object_name, method_name = get_member_names(callee)
            if not object_name:
                return None

            decoder_key = (object_name, method_name)
            if decoder_key not in decoder_map:
                return None

            lookup_table, offset = decoder_map[decoder_key]
            decoded = self._decode_call(lookup_table, offset, node.get('arguments', []))
            if decoded is None:
                return None

            replacement = make_literal(decoded)

            # Track assignment target for later constant inlining
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'right':
                left_object, left_property = get_member_names(parent.get('left'))
                if left_object and left_property:
                    decoded_constants[(left_object, left_property)] = decoded

            self.set_changed()
            return replacement

        traverse(self.ast, {'enter': enter})

        if decoded_constants:
            self._inline_decoded_constants(decoded_constants)

    def _inline_decoded_constants(self, decoded_constants: DecodedConstants) -> None:
        """Replace references like _0x279589['propName'] with the decoded string."""

        def enter(
            node: dict,
            parent: dict,
            key: str,
            index: int | None,
        ) -> dict | None:
            if node.get('type') != 'MemberExpression':
                return None
            # Skip assignment targets
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return None

            object_name, property_name = get_member_names(node)
            if not object_name:
                return None

            lookup_key = (object_name, property_name)
            if lookup_key not in decoded_constants:
                return None

            decoded = decoded_constants[lookup_key]
            self.set_changed()
            return make_literal(decoded)

        traverse(self.ast, {'enter': enter})
