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


class ClassStringDecoder(Transform):
    """Resolve class-based string encoder patterns."""

    def execute(self) -> bool:
        class_props: dict = {}
        decoders: dict = {}

        self._collect_class_props(class_props)
        self._find_decoders(class_props, decoders)

        if not decoders:
            return False

        self._resolve_aliases(decoders)

        self._resolve_calls(decoders)
        return self.has_changed()

    def _collect_class_props(self, class_props: dict) -> None:
        """Collect static property assignments on class variables.

        Builds: class_props[var_name] = {prop_name: value, ...}
        Also detects array properties that reference other props.
        Handles assignments in ExpressionStatements and SequenceExpressions.
        """

        def visit(node: dict, parent: dict) -> None:
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return

            var_name, prop_name = get_member_names(node.get('left'))
            if not var_name:
                return

            right = node.get('right')
            if var_name not in class_props:
                class_props[var_name] = {}

            if is_string_literal(right):
                class_props[var_name][prop_name] = right['value']
            elif right and right.get('type') == 'ArrayExpression':
                elements = right.get('elements', [])
                class_props[var_name][prop_name] = ('array', elements)

        simple_traverse(self.ast, visit)

    def _resolve_array(self, class_props: dict, var_name: str, elements: list) -> list | None:
        """Resolve an array of MemberExpression references to string values."""
        props = class_props.get(var_name, {})
        resolved = []
        for element in elements:
            element_object, element_property = get_member_names(element)
            if not element_object or element_object != var_name:
                return None
            value = props.get(element_property)
            if not isinstance(value, str):
                return None
            resolved.append(value)
        return resolved

    def _find_decoders(self, class_props: dict, decoders: dict) -> None:
        """Find decoder methods and their associated lookup tables."""

        def visit(node: dict, parent: dict) -> None:
            if node.get('type') != 'MethodDefinition':
                return
            if not node.get('static'):
                return
            method_key = node.get('key')
            if not method_key:
                return
            match method_key.get('type'):
                case 'Literal' if isinstance(method_key.get('value'), str):
                    method_name = method_key['value']
                case 'Identifier':
                    method_name = method_key['name']
                case _:
                    return

            function_node = node.get('value')
            if not function_node or function_node.get('type') != 'FunctionExpression':
                return
            params = function_node.get('params', [])
            if len(params) != 1:
                return

            body = function_node.get('body')
            if not body or body.get('type') != 'BlockStatement':
                return
            statements = body.get('body', [])
            if len(statements) < 3:
                return

            table_info = self._extract_decoder_table(statements, class_props)
            if not table_info:
                return

            lookup_table, offset = table_info

            class_var = self._find_enclosing_class_var(node)
            if not class_var:
                return

            decoders[(class_var, method_name)] = (lookup_table, offset)

        simple_traverse(self.ast, visit)

    def _resolve_aliases(self, decoders: dict) -> None:
        """Find identifier aliases (X = Y) where Y is a decoder class, and register X too."""
        decoder_classes = {cls for cls, _ in decoders}
        new_entries = {}

        def visit(node: dict, parent: dict) -> None:
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return
            left = node.get('left')
            right = node.get('right')
            if not left or left.get('type') != 'Identifier':
                return
            if not right or right.get('type') != 'Identifier':
                return
            if right['name'] in decoder_classes:
                alias = left['name']
                for (cls, method), value in decoders.items():
                    if cls == right['name']:
                        new_entries[(alias, method)] = value

        simple_traverse(self.ast, visit)
        decoders.update(new_entries)

    def _extract_decoder_table(self, statements: list, class_props: dict) -> tuple | None:
        """Extract the lookup table and offset from decoder method body."""
        table_class_var = None
        table_prop = None

        for statement in statements:
            if statement.get('type') != 'VariableDeclaration':
                continue
            for declaration in statement.get('declarations', []):
                init = declaration.get('init')
                obj_name, prop_name = get_member_names(init)
                if not obj_name or not prop_name:
                    continue
                declaration_id = declaration.get('id')
                if declaration_id and declaration_id.get('type') == 'Identifier':
                    table_class_var = obj_name
                    table_prop = prop_name

        if not table_class_var:
            return None

        props = class_props.get(table_class_var, {})
        array_val = props.get(table_prop)
        if not isinstance(array_val, tuple) or array_val[0] != 'array':
            return None

        resolved = self._resolve_array(class_props, table_class_var, array_val[1])
        if not resolved:
            return None

        offset = self._find_offset(statements)
        return resolved, offset

    def _find_offset(self, statements: list) -> int:
        """Find the subtraction offset in the decoder loop (e.g., - 48)."""
        offset = 48

        def scan(node: dict, parent: dict) -> None:
            nonlocal offset
            if not isinstance(node, dict):
                return
            if node.get('type') == 'BinaryExpression' and node.get('operator') == '-':
                right = node.get('right')
                if right and is_numeric_literal(right):
                    val = right['value']
                    if isinstance(val, (int, float)) and val > 0:
                        offset = int(val)

        for statement in statements:
            if statement.get('type') == 'ForStatement':
                simple_traverse(statement, scan)

        return offset

    def _find_enclosing_class_var(self, method_node: dict) -> str | None:
        """Find the variable name of the class containing this method."""
        result = [None]

        def _check_class_body(class_expr: dict, var_name: str) -> bool:
            body = class_expr.get('body')
            if body and body.get('type') == 'ClassBody':
                for member in body.get('body', []):
                    if member is method_node:
                        result[0] = var_name
                        return True
            return False

        def scan(node: dict, parent: dict) -> None:
            if result[0]:
                return
            if node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                if init and init.get('type') == 'ClassExpression':
                    declaration_id = node.get('id')
                    if declaration_id and declaration_id.get('type') == 'Identifier':
                        _check_class_body(init, declaration_id['name'])
            elif node.get('type') == 'AssignmentExpression':
                right = node.get('right')
                if right and right.get('type') == 'ClassExpression':
                    left = node.get('left')
                    if left and left.get('type') == 'Identifier':
                        _check_class_body(right, left['name'])

        simple_traverse(self.ast, scan)
        return result[0]

    def _decode_call(self, lookup_table: list, offset: int, args: list) -> str | None:
        """Statically evaluate a decoder call: decode([0x4f, 0x3a, ...])."""
        if len(args) != 1:
            return None
        arg = args[0]
        if not arg or arg.get('type') != 'ArrayExpression':
            return None
        elements = arg.get('elements', [])
        result = ''
        for element in elements:
            if not is_numeric_literal(element):
                return None
            idx = int(element['value']) - offset
            if idx < 0 or idx >= len(lookup_table):
                return None
            entry = lookup_table[idx]
            if not entry:
                return None
            result += entry[0]
        return result

    def _resolve_calls(self, decoders: dict) -> None:
        """Replace all decoder calls with their decoded string literals."""
        decoded_constants: dict = {}

        def enter(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            if node.get('type') != 'CallExpression':
                return None
            callee = node.get('callee')
            obj_name, method_name = get_member_names(callee)
            if not obj_name:
                return None

            decoder_key = (obj_name, method_name)
            if decoder_key not in decoders:
                return None

            lookup_table, offset = decoders[decoder_key]
            decoded = self._decode_call(lookup_table, offset, node.get('arguments', []))
            if decoded is None:
                return None

            replacement = make_literal(decoded)

            # Track the assignment target so we can inline the constant later
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'right':
                left_object, left_property = get_member_names(parent.get('left'))
                if left_object and left_property:
                    decoded_constants[(left_object, left_property)] = decoded

            self.set_changed()
            return replacement

        traverse(self.ast, {'enter': enter})

        if decoded_constants:
            self._inline_decoded_constants(decoded_constants)

    def _inline_decoded_constants(self, decoded_constants: dict) -> None:
        """Replace references like _0x279589["propName"] with the decoded string."""

        def enter(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            if node.get('type') != 'MemberExpression':
                return None
            # Skip assignment targets
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return None

            obj_name, prop_name = get_member_names(node)
            if not obj_name:
                return None

            lookup_key = (obj_name, prop_name)
            if lookup_key not in decoded_constants:
                return None

            decoded = decoded_constants[lookup_key]
            self.set_changed()
            return make_literal(decoded)

        traverse(self.ast, {'enter': enter})
