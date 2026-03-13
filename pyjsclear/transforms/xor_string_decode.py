"""Decode XOR-obfuscated string constants.

Detects patterns like:
    function _0x291e22(_0x4385ad) {
        const prefix = _0x4385ad.slice(0, 4);
        const data = Buffer.from(_0x4385ad.slice(4));
        for (let i = 0; i < data.length; i++) {
            data[i] ^= prefix[i % N];
        }
        return data.toString(...);
    }
    var _0x457926 = _0x291e22([16, 233, 75, 213, ...]);

And replaces all references to _0x457926 with the decoded string literal.
Also resolves computed member accesses: obj[_0x457926] → obj.replace
"""

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import is_valid_identifier
from ..utils.ast_helpers import make_identifier
from ..utils.ast_helpers import make_literal
from .base import Transform


def _extract_numeric_array(node: dict | None) -> list[int] | None:
    """Extract a list of integers from an ArrayExpression node."""
    if not node or node.get('type') != 'ArrayExpression':
        return None
    elements = node.get('elements', [])
    result = []
    for element in elements:
        if not is_numeric_literal(element):
            return None
        value = element['value']
        if not isinstance(value, (int, float)) or value != int(value) or value < 0 or value > 255:
            return None
        result.append(int(value))
    return result


def _xor_decode(byte_array: list[int], prefix_len: int = 4) -> str | None:
    """Decode XOR-obfuscated byte array: prefix XOR'd against remaining data."""
    if len(byte_array) <= prefix_len:
        return None
    prefix = byte_array[:prefix_len]
    data = bytearray(byte_array[prefix_len:])
    for i in range(len(data)):
        data[i] ^= prefix[i % prefix_len]
    try:
        return data.decode('utf-8')
    except (UnicodeDecodeError, ValueError):
        return None


def _is_xor_decoder_function(node: dict | None) -> bool:
    """Heuristic: check if a function body contains XOR (^=) on array elements
    and a slice/Buffer.from pattern typical of XOR string decoders."""
    if not node:
        return False
    body = node.get('body')
    if not body:
        return False

    has_xor = [False]
    has_slice = [False]
    has_tostring = [False]

    def scan(ast_node: dict, parent: dict) -> None:
        if not isinstance(ast_node, dict):
            return
        # Look for ^= operator
        if ast_node.get('type') == 'AssignmentExpression' and ast_node.get('operator') == '^=':
            has_xor[0] = True
        # Look for .slice or .from
        if ast_node.get('type') == 'MemberExpression':
            property_node = ast_node.get('property')
            if property_node:
                name = property_node.get('name') or (property_node.get('value') if property_node.get('type') == 'Literal' else None)
                if name in ('slice', 'from'):
                    has_slice[0] = True
                if name in ('toString', 'decode'):
                    has_tostring[0] = True

    simple_traverse(node, scan)
    return has_xor[0] and has_slice[0]


class XorStringDecoder(Transform):
    """Decode XOR-obfuscated string constants and inline them."""

    def execute(self) -> bool:
        # Phase 1: Find XOR decoder functions
        decoder_funcs: set[str] = set()

        def find_decoders(node: dict, parent: dict) -> None:
            if node.get('type') not in ('FunctionDeclaration', 'FunctionExpression'):
                return
            params = node.get('params', [])
            if len(params) != 1:
                return
            if not _is_xor_decoder_function(node):
                return

            # Get function name
            if node.get('type') == 'FunctionDeclaration':
                func_id = node.get('id')
                if func_id and is_identifier(func_id):
                    decoder_funcs.add(func_id['name'])
            elif parent and parent.get('type') == 'VariableDeclarator':
                declaration_id = parent.get('id')
                if declaration_id and is_identifier(declaration_id):
                    decoder_funcs.add(declaration_id['name'])

        simple_traverse(self.ast, find_decoders)

        if not decoder_funcs:
            return False

        # Phase 2: Find calls like `var X = decoder([...bytes...])` and decode
        decoded_vars: dict[str, str] = {}  # var_name → decoded_string

        def find_calls(node: dict, parent: dict) -> None:
            if node.get('type') != 'VariableDeclarator':
                return
            declaration_id = node.get('id')
            init = node.get('init')
            if not is_identifier(declaration_id) or not init:
                return
            if init.get('type') != 'CallExpression':
                return
            callee = init.get('callee')
            if not is_identifier(callee) or callee['name'] not in decoder_funcs:
                return
            args = init.get('arguments', [])
            if len(args) != 1:
                return
            byte_array = _extract_numeric_array(args[0])
            if byte_array is None:
                return
            decoded = _xor_decode(byte_array)
            if decoded is not None:
                decoded_vars[declaration_id['name']] = decoded

        simple_traverse(self.ast, find_calls)

        if not decoded_vars:
            return False

        # Phase 3: Replace computed member accesses obj[_0xVAR] → obj.decoded
        # and standalone identifier refs with string literals
        def replace_refs(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            # Handle computed member: obj[_0xVAR] → obj.decoded or obj["decoded"]
            if node.get('type') == 'MemberExpression' and node.get('computed'):
                property_node = node.get('property')
                if is_identifier(property_node) and property_node['name'] in decoded_vars:
                    decoded = decoded_vars[property_node['name']]
                    if is_valid_identifier(decoded):
                        node['property'] = make_identifier(decoded)
                        node['computed'] = False
                    else:
                        node['property'] = make_literal(decoded)
                    self.set_changed()
                    return

            # Handle standalone identifier in other contexts (e.g., require(_0xVAR))
            if is_identifier(node) and node['name'] in decoded_vars:
                # Skip non-computed property names
                if (
                    parent
                    and parent.get('type') == 'MemberExpression'
                    and key == 'property'
                    and not parent.get('computed')
                ):
                    return
                # Skip declaration sites
                if parent and parent.get('type') == 'VariableDeclarator' and key == 'id':
                    return
                # Skip property keys
                if parent and parent.get('type') == 'Property' and key == 'key' and not parent.get('computed'):
                    return
                self.set_changed()
                return make_literal(decoded_vars[node['name']])

        traverse(self.ast, {'enter': replace_refs})

        # Phase 4: Remove dead variable declarations for decoded vars
        if self.has_changed():
            self._remove_dead_declarations(decoded_vars)

        return self.has_changed()

    def _remove_dead_declarations(self, decoded_vars: dict[str, str]) -> None:
        """Remove var X = decoder([...]) declarations that are now inlined."""
        remaining_refs = {name: 0 for name in decoded_vars}

        def count_refs(node: dict, parent: dict) -> None:
            if is_identifier(node) and node['name'] in remaining_refs:
                if parent and parent.get('type') == 'VariableDeclarator' and node is parent.get('id'):
                    return
                remaining_refs[node['name']] = remaining_refs.get(node['name'], 0) + 1

        simple_traverse(self.ast, count_refs)

        dead_vars = {name for name, ref_count in remaining_refs.items() if ref_count == 0}
        if not dead_vars:
            return

        def remove_decls(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            if node.get('type') != 'VariableDeclaration':
                return
            decls = node.get('declarations', [])
            remaining = []
            for declaration in decls:
                declaration_id = declaration.get('id')
                if is_identifier(declaration_id) and declaration_id['name'] in dead_vars:
                    continue
                remaining.append(declaration)
            if len(remaining) == len(decls):
                return
            if not remaining:
                return REMOVE
            node['declarations'] = remaining

        traverse(self.ast, {'enter': remove_decls})
