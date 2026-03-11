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
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import make_literal
from .base import Transform


def _get_member_names(node):
    """Extract (object_name, property_name) from a MemberExpression.

    Handles both computed (obj["prop"]) and non-computed (obj.prop) forms.
    Returns (str, str) or (None, None).
    """
    if not node or node.get('type') != 'MemberExpression':
        return None, None
    obj = node.get('object')
    prop = node.get('property')
    if not obj or obj.get('type') != 'Identifier':
        return None, None
    if not prop:
        return None, None
    if node.get('computed'):
        if is_string_literal(prop):
            return obj['name'], prop['value']
        return None, None
    if prop.get('type') == 'Identifier':
        return obj['name'], prop['name']
    return None, None


class ClassStringDecoder(Transform):
    """Resolve class-based string encoder patterns."""

    def execute(self):
        class_props = {}
        decoders = {}

        self._collect_class_props(class_props)
        self._find_decoders(class_props, decoders)

        if not decoders:
            return False

        self._resolve_aliases(decoders)

        self._resolve_calls(decoders)
        return self.has_changed()

    def _collect_class_props(self, class_props):
        """Collect static property assignments on class variables.

        Builds: class_props[var_name] = {prop_name: value, ...}
        Also detects array properties that reference other props.
        Handles assignments in ExpressionStatements and SequenceExpressions.
        """

        def visit(node, parent):
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return

            var_name, prop_name = _get_member_names(node.get('left'))
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

    def _resolve_array(self, class_props, var_name, elements):
        """Resolve an array of MemberExpression references to string values."""
        props = class_props.get(var_name, {})
        resolved = []
        for el in elements:
            el_obj, el_prop = _get_member_names(el)
            if not el_obj or el_obj != var_name:
                return None
            value = props.get(el_prop)
            if not isinstance(value, str):
                return None
            resolved.append(value)
        return resolved

    def _find_decoders(self, class_props, decoders):
        """Find decoder methods and their associated lookup tables."""

        def visit(node, parent):
            if node.get('type') != 'MethodDefinition':
                return
            if not node.get('static'):
                return
            method_key = node.get('key')
            if not method_key:
                return
            if method_key.get('type') == 'Literal' and isinstance(method_key.get('value'), str):
                method_name = method_key['value']
            elif method_key.get('type') == 'Identifier':
                method_name = method_key['name']
            else:
                return

            func = node.get('value')
            if not func or func.get('type') != 'FunctionExpression':
                return
            params = func.get('params', [])
            if len(params) != 1:
                return

            body = func.get('body')
            if not body or body.get('type') != 'BlockStatement':
                return
            stmts = body.get('body', [])
            if len(stmts) < 3:
                return

            table_info = self._extract_decoder_table(stmts, class_props)
            if not table_info:
                return

            lookup_table, offset = table_info

            class_var = self._find_enclosing_class_var(node)
            if not class_var:
                return

            decoders[(class_var, method_name)] = (lookup_table, offset)

        simple_traverse(self.ast, visit)

    def _resolve_aliases(self, decoders):
        """Find identifier aliases (X = Y) where Y is a decoder class, and register X too."""
        decoder_classes = {cls for cls, _ in decoders}
        new_entries = {}

        def visit(node, parent):
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

    def _extract_decoder_table(self, stmts, class_props):
        """Extract the lookup table and offset from decoder method body."""
        table_class_var = None
        table_prop = None

        for stmt in stmts:
            if stmt.get('type') != 'VariableDeclaration':
                continue
            for decl in stmt.get('declarations', []):
                init = decl.get('init')
                obj_name, prop_name = _get_member_names(init)
                if obj_name and prop_name:
                    decl_id = decl.get('id')
                    if decl_id and decl_id.get('type') == 'Identifier':
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

        offset = self._find_offset(stmts)
        return resolved, offset

    def _find_offset(self, stmts):
        """Find the subtraction offset in the decoder loop (e.g., - 48)."""
        offset = 48

        def scan(node, parent):
            nonlocal offset
            if not isinstance(node, dict):
                return
            if node.get('type') == 'BinaryExpression' and node.get('operator') == '-':
                right = node.get('right')
                if right and is_numeric_literal(right):
                    val = right['value']
                    if isinstance(val, (int, float)) and val > 0:
                        offset = int(val)

        for stmt in stmts:
            if stmt.get('type') == 'ForStatement':
                simple_traverse(stmt, scan)

        return offset

    def _find_enclosing_class_var(self, method_node):
        """Find the variable name of the class containing this method."""
        result = [None]

        def _check_class_body(class_expr, var_name):
            body = class_expr.get('body')
            if body and body.get('type') == 'ClassBody':
                for member in body.get('body', []):
                    if member is method_node:
                        result[0] = var_name
                        return True
            return False

        def scan(node, parent):
            if result[0]:
                return
            if node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                if init and init.get('type') == 'ClassExpression':
                    decl_id = node.get('id')
                    if decl_id and decl_id.get('type') == 'Identifier':
                        _check_class_body(init, decl_id['name'])
            elif node.get('type') == 'AssignmentExpression':
                right = node.get('right')
                if right and right.get('type') == 'ClassExpression':
                    left = node.get('left')
                    if left and left.get('type') == 'Identifier':
                        _check_class_body(right, left['name'])

        simple_traverse(self.ast, scan)
        return result[0]

    def _decode_call(self, lookup_table, offset, args):
        """Statically evaluate a decoder call: decode([0x4f, 0x3a, ...])."""
        if len(args) != 1:
            return None
        arg = args[0]
        if not arg or arg.get('type') != 'ArrayExpression':
            return None
        elements = arg.get('elements', [])
        result = ''
        for el in elements:
            if not is_numeric_literal(el):
                return None
            idx = int(el['value']) - offset
            if idx < 0 or idx >= len(lookup_table):
                return None
            entry = lookup_table[idx]
            if not entry:
                return None
            result += entry[0]
        return result

    def _resolve_calls(self, decoders):
        """Replace all decoder calls with their decoded string literals."""
        decoded_constants = {}

        def enter(node, parent, key, index):
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            obj_name, method_name = _get_member_names(callee)
            if not obj_name:
                return

            decoder_key = (obj_name, method_name)
            if decoder_key not in decoders:
                return

            lookup_table, offset = decoders[decoder_key]
            decoded = self._decode_call(lookup_table, offset, node.get('arguments', []))
            if decoded is None:
                return

            replacement = make_literal(decoded)

            # Track the assignment target so we can inline the constant later
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'right':
                lobj, lprop = _get_member_names(parent.get('left'))
                if lobj and lprop:
                    decoded_constants[(lobj, lprop)] = decoded

            self.set_changed()
            return replacement

        traverse(self.ast, {'enter': enter})

        if decoded_constants:
            self._inline_decoded_constants(decoded_constants)

    def _inline_decoded_constants(self, decoded_constants):
        """Replace references like _0x279589["propName"] with the decoded string."""

        def enter(node, parent, key, index):
            if node.get('type') != 'MemberExpression':
                return
            # Skip assignment targets
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return

            obj_name, prop_name = _get_member_names(node)
            if not obj_name:
                return

            lookup_key = (obj_name, prop_name)
            if lookup_key not in decoded_constants:
                return

            decoded = decoded_constants[lookup_key]
            self.set_changed()
            return make_literal(decoded)

        traverse(self.ast, {'enter': enter})
