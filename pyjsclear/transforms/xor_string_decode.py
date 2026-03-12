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


def _extract_numeric_array(node):
    """Extract a list of integers from an ArrayExpression node."""
    if not node or node.get('type') != 'ArrayExpression':
        return None
    elements = node.get('elements', [])
    result = []
    for el in elements:
        if not is_numeric_literal(el):
            return None
        val = el['value']
        if not isinstance(val, (int, float)) or val != int(val) or val < 0 or val > 255:
            return None
        result.append(int(val))
    return result


def _xor_decode(byte_array, prefix_len=4):
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


def _is_xor_decoder_function(node):
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

    def scan(n, parent):
        if not isinstance(n, dict):
            return
        # Look for ^= operator
        if n.get('type') == 'AssignmentExpression' and n.get('operator') == '^=':
            has_xor[0] = True
        # Look for .slice or .from
        if n.get('type') == 'MemberExpression':
            prop = n.get('property')
            if prop:
                name = prop.get('name') or (prop.get('value') if prop.get('type') == 'Literal' else None)
                if name in ('slice', 'from'):
                    has_slice[0] = True
                if name in ('toString', 'decode'):
                    has_tostring[0] = True

    simple_traverse(node, scan)
    return has_xor[0] and has_slice[0]


class XorStringDecoder(Transform):
    """Decode XOR-obfuscated string constants and inline them."""

    def execute(self):
        # Phase 1: Find XOR decoder functions
        decoder_funcs = set()

        def find_decoders(node, parent):
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
                decl_id = parent.get('id')
                if decl_id and is_identifier(decl_id):
                    decoder_funcs.add(decl_id['name'])

        simple_traverse(self.ast, find_decoders)

        if not decoder_funcs:
            return False

        # Phase 2: Find calls like `var X = decoder([...bytes...])` and decode
        decoded_vars = {}  # var_name → decoded_string

        def find_calls(node, parent):
            if node.get('type') != 'VariableDeclarator':
                return
            decl_id = node.get('id')
            init = node.get('init')
            if not is_identifier(decl_id) or not init:
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
                decoded_vars[decl_id['name']] = decoded

        simple_traverse(self.ast, find_calls)

        if not decoded_vars:
            return False

        # Phase 3: Replace computed member accesses obj[_0xVAR] → obj.decoded
        # and standalone identifier refs with string literals
        def replace_refs(node, parent, key, index):
            # Handle computed member: obj[_0xVAR] → obj.decoded or obj["decoded"]
            if node.get('type') == 'MemberExpression' and node.get('computed'):
                prop = node.get('property')
                if is_identifier(prop) and prop['name'] in decoded_vars:
                    decoded = decoded_vars[prop['name']]
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

    def _remove_dead_declarations(self, decoded_vars):
        """Remove var X = decoder([...]) declarations that are now inlined."""
        remaining_refs = {name: 0 for name in decoded_vars}

        def count(node, parent):
            if is_identifier(node) and node['name'] in remaining_refs:
                if parent and parent.get('type') == 'VariableDeclarator' and node is parent.get('id'):
                    return
                remaining_refs[node['name']] = remaining_refs.get(node['name'], 0) + 1

        simple_traverse(self.ast, count)

        dead_vars = {name for name, count in remaining_refs.items() if count == 0}
        if not dead_vars:
            return

        def remove_decls(node, parent, key, index):
            if node.get('type') != 'VariableDeclaration':
                return
            decls = node.get('declarations', [])
            remaining = []
            for d in decls:
                did = d.get('id')
                if is_identifier(did) and did['name'] in dead_vars:
                    continue
                remaining.append(d)
            if len(remaining) == len(decls):
                return
            if not remaining:
                return REMOVE
            node['declarations'] = remaining

        traverse(self.ast, {'enter': remove_decls})
