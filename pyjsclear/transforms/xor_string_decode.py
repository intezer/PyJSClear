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
Also resolves computed member accesses: obj[_0x457926] -> obj.replace
"""

from __future__ import annotations

from enum import StrEnum

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import is_valid_identifier
from ..utils.ast_helpers import make_identifier
from ..utils.ast_helpers import make_literal
from .base import Transform


class _NodeType(StrEnum):
    """AST node type constants."""

    ARRAY_EXPRESSION = 'ArrayExpression'
    ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
    CALL_EXPRESSION = 'CallExpression'
    FUNCTION_DECLARATION = 'FunctionDeclaration'
    FUNCTION_EXPRESSION = 'FunctionExpression'
    LITERAL = 'Literal'
    MEMBER_EXPRESSION = 'MemberExpression'
    PROPERTY = 'Property'
    VARIABLE_DECLARATION = 'VariableDeclaration'
    VARIABLE_DECLARATOR = 'VariableDeclarator'


class _MemberName(StrEnum):
    """Known member names used in XOR decoder heuristics."""

    SLICE = 'slice'
    FROM = 'from'
    TO_STRING = 'toString'
    DECODE = 'decode'


_SLICE_OR_FROM = {_MemberName.SLICE, _MemberName.FROM}
_TOSTRING_OR_DECODE = {_MemberName.TO_STRING, _MemberName.DECODE}
_FUNCTION_TYPES = {_NodeType.FUNCTION_DECLARATION, _NodeType.FUNCTION_EXPRESSION}
_XOR_OPERATOR = '^='


def _extract_numeric_array(node: dict | None) -> list[int] | None:
    """Extract a list of integers from an ArrayExpression node."""
    if not node or node.get('type') != _NodeType.ARRAY_EXPRESSION:
        return None
    elements = node.get('elements', [])
    result: list[int] = []
    for element in elements:
        if not is_numeric_literal(element):
            return None
        value = element['value']
        if not isinstance(value, (int, float)) or value != int(value) or value < 0 or value > 255:
            return None
        result.append(int(value))
    return result


def _xor_decode(byte_array: list[int], prefix_length: int = 4) -> str | None:
    """Decode XOR-obfuscated byte array using prefix bytes as the key."""
    if len(byte_array) <= prefix_length:
        return None
    prefix = byte_array[:prefix_length]
    data = bytearray(byte_array[prefix_length:])
    for index in range(len(data)):
        data[index] ^= prefix[index % prefix_length]
    try:
        return data.decode('utf-8')
    except (UnicodeDecodeError, ValueError):
        return None


def _resolve_member_name(property_node: dict) -> str | None:
    """Extract the name from a MemberExpression property node."""
    if not property_node:
        return None
    name = property_node.get('name')
    if name:
        return name
    if property_node.get('type') == _NodeType.LITERAL:
        return property_node.get('value')
    return None


def _is_xor_decoder_function(node: dict | None) -> bool:
    """Heuristic check for XOR decoder function patterns (^= on array elements with slice/from)."""
    if not node:
        return False
    body = node.get('body')
    if not body:
        return False

    found_xor = False
    found_slice = False

    def scan(ast_node: dict, _parent: dict) -> None:
        """Scan AST nodes for XOR and slice/from patterns."""
        nonlocal found_xor, found_slice
        if not isinstance(ast_node, dict):
            return
        if ast_node.get('type') == _NodeType.ASSIGNMENT_EXPRESSION and ast_node.get('operator') == _XOR_OPERATOR:
            found_xor = True
        if ast_node.get('type') == _NodeType.MEMBER_EXPRESSION:
            member_name = _resolve_member_name(ast_node.get('property'))
            if member_name in _SLICE_OR_FROM:
                found_slice = True

    simple_traverse(node, scan)
    return found_xor and found_slice


def _extract_function_name(node: dict, parent: dict) -> str | None:
    """Extract the bound name of a function declaration or variable-assigned function expression."""
    match node.get('type'):
        case _NodeType.FUNCTION_DECLARATION:
            function_identifier = node.get('id')
            if function_identifier and is_identifier(function_identifier):
                return function_identifier['name']
        case _NodeType.FUNCTION_EXPRESSION:
            if parent and parent.get('type') == _NodeType.VARIABLE_DECLARATOR:
                declaration_identifier = parent.get('id')
                if declaration_identifier and is_identifier(declaration_identifier):
                    return declaration_identifier['name']
    return None


class XorStringDecoder(Transform):
    """Decode XOR-obfuscated string constants and inline them."""

    def execute(self) -> bool:
        """Find XOR decoder functions, decode calls, and replace references with string literals."""
        decoder_functions = self._find_decoder_functions()
        if not decoder_functions:
            return False

        decoded_variables = self._find_and_decode_calls(decoder_functions)
        if not decoded_variables:
            return False

        self._replace_references(decoded_variables)

        if self.has_changed():
            self._remove_dead_declarations(decoded_variables)

        return self.has_changed()

    def _find_decoder_functions(self) -> set[str]:
        """Scan the AST to find XOR decoder function names."""
        decoder_functions: set[str] = set()

        def find_decoders(node: dict, parent: dict) -> None:
            """Identify functions matching the XOR decoder heuristic."""
            if node.get('type') not in _FUNCTION_TYPES:
                return
            parameters = node.get('params', [])
            if len(parameters) != 1:
                return
            if not _is_xor_decoder_function(node):
                return
            function_name = _extract_function_name(node, parent)
            if function_name:
                decoder_functions.add(function_name)

        simple_traverse(self.ast, find_decoders)
        return decoder_functions

    def _find_and_decode_calls(self, decoder_functions: set[str]) -> dict[str, str]:
        """Find calls to decoder functions and decode their byte array arguments."""
        decoded_variables: dict[str, str] = {}

        def find_calls(node: dict, _parent: dict) -> None:
            """Match variable declarations that call a known decoder with a byte array."""
            if node.get('type') != _NodeType.VARIABLE_DECLARATOR:
                return
            declaration_identifier = node.get('id')
            initializer = node.get('init')
            if not is_identifier(declaration_identifier) or not initializer:
                return
            if initializer.get('type') != _NodeType.CALL_EXPRESSION:
                return
            callee = initializer.get('callee')
            if not is_identifier(callee) or callee['name'] not in decoder_functions:
                return
            arguments = initializer.get('arguments', [])
            if len(arguments) != 1:
                return
            byte_array = _extract_numeric_array(arguments[0])
            if byte_array is None:
                return
            decoded_value = _xor_decode(byte_array)
            if decoded_value is not None:
                decoded_variables[declaration_identifier['name']] = decoded_value

        simple_traverse(self.ast, find_calls)
        return decoded_variables

    def _replace_references(self, decoded_variables: dict[str, str]) -> None:
        """Replace identifier references with decoded string literals."""

        def replace_refs(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            """Substitute decoded strings for identifier references and computed members."""
            # Handle computed member: obj[_0xVAR] -> obj.decoded or obj["decoded"]
            if node.get('type') == _NodeType.MEMBER_EXPRESSION and node.get('computed'):
                property_node = node.get('property')
                if is_identifier(property_node) and property_node['name'] in decoded_variables:
                    decoded_value = decoded_variables[property_node['name']]
                    if is_valid_identifier(decoded_value):
                        node['property'] = make_identifier(decoded_value)
                        node['computed'] = False
                    else:
                        node['property'] = make_literal(decoded_value)
                    self.set_changed()
                    return None

            # Handle standalone identifier in other contexts
            if not is_identifier(node) or node['name'] not in decoded_variables:
                return None

            # Skip non-computed property names
            if (
                parent
                and parent.get('type') == _NodeType.MEMBER_EXPRESSION
                and key == 'property'
                and not parent.get('computed')
            ):
                return None
            # Skip declaration sites
            if parent and parent.get('type') == _NodeType.VARIABLE_DECLARATOR and key == 'id':
                return None
            # Skip property keys
            if parent and parent.get('type') == _NodeType.PROPERTY and key == 'key' and not parent.get('computed'):
                return None

            self.set_changed()
            return make_literal(decoded_variables[node['name']])

        traverse(self.ast, {'enter': replace_refs})

    def _remove_dead_declarations(self, decoded_variables: dict[str, str]) -> None:
        """Remove variable declarations for decoded vars that have no remaining references."""
        remaining_references: dict[str, int] = {name: 0 for name in decoded_variables}

        def count_references(node: dict, parent: dict) -> None:
            """Count non-declaration references to each decoded variable."""
            if not is_identifier(node) or node['name'] not in remaining_references:
                return
            if parent and parent.get('type') == _NodeType.VARIABLE_DECLARATOR and node is parent.get('id'):
                return
            remaining_references[node['name']] = remaining_references.get(node['name'], 0) + 1

        simple_traverse(self.ast, count_references)

        dead_variable_names = {name for name, reference_count in remaining_references.items() if reference_count == 0}
        if not dead_variable_names:
            return

        def remove_declarations(node: dict, _parent: dict, _key: str, _index: int | None) -> dict | None:
            """Remove variable declarations for dead decoded variables."""
            if node.get('type') != _NodeType.VARIABLE_DECLARATION:
                return None
            declarations = node.get('declarations', [])
            remaining = []
            for declaration in declarations:
                declaration_identifier = declaration.get('id')
                if is_identifier(declaration_identifier) and declaration_identifier['name'] in dead_variable_names:
                    continue
                remaining.append(declaration)
            if len(remaining) == len(declarations):
                return None
            if not remaining:
                return REMOVE
            node['declarations'] = remaining
            return None

        traverse(self.ast, {'enter': remove_declarations})
