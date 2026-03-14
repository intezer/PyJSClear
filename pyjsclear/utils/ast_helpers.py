"""AST helper utilities for ESTree nodes."""

from __future__ import annotations

import copy
import re
from typing import Any


def deep_copy(node: dict) -> dict:
    """Deep copy an AST node."""
    return copy.deepcopy(node)


def is_literal(node: Any) -> bool:
    """Return True if node is a Literal AST node."""
    return isinstance(node, dict) and node.get('type') == 'Literal'


def is_identifier(node: Any) -> bool:
    """Return True if node is an Identifier AST node."""
    return isinstance(node, dict) and node.get('type') == 'Identifier'


def is_string_literal(node: Any) -> bool:
    """Return True if node is a string Literal."""
    return is_literal(node) and isinstance(node.get('value'), str)


def is_numeric_literal(node: Any) -> bool:
    """Return True if node is a numeric Literal."""
    return is_literal(node) and isinstance(node.get('value'), (int, float))


def is_boolean_literal(node: Any) -> bool:
    """Return True if node is a boolean Literal (true/false)."""
    return is_literal(node) and isinstance(node.get('value'), bool)


def is_null_literal(node: Any) -> bool:
    """Return True if node is a null Literal."""
    return is_literal(node) and node.get('value') is None and node.get('raw') == 'null'


def _is_void_zero(node: dict) -> bool:
    """Return True if node is a ``void 0`` expression."""
    return (
        node.get('type') == 'UnaryExpression'
        and node.get('operator') == 'void'
        and isinstance(node.get('argument'), dict)
        and node['argument'].get('type') == 'Literal'
        and node['argument'].get('value') == 0
    )


def is_undefined(node: Any) -> bool:
    """Return True if node represents ``undefined`` or ``void 0``."""
    if is_identifier(node) and node.get('name') == 'undefined':
        return True
    if isinstance(node, dict) and _is_void_zero(node):
        return True
    return False


def get_literal_value(node: Any) -> tuple[Any, bool]:
    """Extract value from a Literal node.

    Returns (value, True) on success, (None, False) otherwise.
    """
    if not is_literal(node):
        return None, False
    return node.get('value'), True


def make_literal(value: Any, raw: str | None = None) -> dict:
    """Create a Literal AST node."""
    if raw is not None:
        return {'type': 'Literal', 'value': value, 'raw': raw}

    match value:
        case str():
            escaped = value.replace('\\', '\\\\')
            escaped = escaped.replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n')
            escaped = escaped.replace('\r', '\\r')
            escaped = escaped.replace('\t', '\\t')
            escaped = escaped.replace('\0', '\\0')
            raw = f'"{escaped}"'
        case bool():
            raw = 'true' if value else 'false'
        case int() | float():
            if isinstance(value, float) and value == int(value) and not (value == 0 and str(value).startswith('-')):
                raw = str(int(value))
            else:
                raw = str(value)
        case None:
            raw = 'null'
        case _:
            raw = str(value)
    return {'type': 'Literal', 'value': value, 'raw': raw}


def make_identifier(name: str) -> dict:
    """Create an Identifier AST node."""
    return {'type': 'Identifier', 'name': name}


def make_expression_statement(expression: dict) -> dict:
    """Wrap an expression in an ExpressionStatement node."""
    return {'type': 'ExpressionStatement', 'expression': expression}


def make_block_statement(body: list[dict]) -> dict:
    """Create a BlockStatement node."""
    return {'type': 'BlockStatement', 'body': body}


def make_variable_declaration(name: str, initializer: dict | None = None, kind: str = 'var') -> dict:
    """Create a VariableDeclaration with a single declarator."""
    return {
        'type': 'VariableDeclaration',
        'declarations': [{'type': 'VariableDeclarator', 'id': make_identifier(name), 'init': initializer}],
        'kind': kind,
    }


def make_var_declaration(name: str, init: dict | None = None, kind: str = 'var') -> dict:
    """Deprecated alias for :func:`make_variable_declaration`."""
    return make_variable_declaration(name, initializer=init, kind=kind)


_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$')


def is_valid_identifier(name: Any) -> bool:
    """Return True if name is a valid JavaScript identifier."""
    if not isinstance(name, str) or not name:
        return False
    return bool(_IDENTIFIER_PATTERN.match(name))


# ESTree node type -> child keys that may contain AST nodes
_CHILD_KEYS: dict[str, tuple[str, ...]] = {
    'Program': ('body',),
    'ExpressionStatement': ('expression',),
    'BlockStatement': ('body',),
    'VariableDeclaration': ('declarations',),
    'VariableDeclarator': ('id', 'init'),
    'FunctionDeclaration': ('id', 'params', 'body'),
    'FunctionExpression': ('id', 'params', 'body'),
    'ArrowFunctionExpression': ('params', 'body'),
    'ReturnStatement': ('argument',),
    'IfStatement': ('test', 'consequent', 'alternate'),
    'WhileStatement': ('test', 'body'),
    'DoWhileStatement': ('test', 'body'),
    'ForStatement': ('init', 'test', 'update', 'body'),
    'ForInStatement': ('left', 'right', 'body'),
    'ForOfStatement': ('left', 'right', 'body'),
    'SwitchStatement': ('discriminant', 'cases'),
    'SwitchCase': ('test', 'consequent'),
    'BreakStatement': ('label',),
    'ContinueStatement': ('label',),
    'LabeledStatement': ('label', 'body'),
    'ThrowStatement': ('argument',),
    'TryStatement': ('block', 'handler', 'finalizer'),
    'CatchClause': ('param', 'body'),
    'BinaryExpression': ('left', 'right'),
    'LogicalExpression': ('left', 'right'),
    'UnaryExpression': ('argument',),
    'UpdateExpression': ('argument',),
    'AssignmentExpression': ('left', 'right'),
    'MemberExpression': ('object', 'property'),
    'CallExpression': ('callee', 'arguments'),
    'NewExpression': ('callee', 'arguments'),
    'ConditionalExpression': ('test', 'consequent', 'alternate'),
    'SequenceExpression': ('expressions',),
    'ArrayExpression': ('elements',),
    'ObjectExpression': ('properties',),
    'Property': ('key', 'value'),
    'SpreadElement': ('argument',),
    'TemplateLiteral': ('quasis', 'expressions'),
    'TaggedTemplateExpression': ('tag', 'quasi'),
    'TemplateElement': (),
    'AssignmentPattern': ('left', 'right'),
    'ArrayPattern': ('elements',),
    'ObjectPattern': ('properties',),
    'RestElement': ('argument',),
    'ClassDeclaration': ('id', 'superClass', 'body'),
    'ClassExpression': ('id', 'superClass', 'body'),
    'ClassBody': ('body',),
    'MethodDefinition': ('key', 'value'),
    'YieldExpression': ('argument',),
    'AwaitExpression': ('argument',),
    'EmptyStatement': (),
    'Literal': (),
    'Identifier': (),
    'ThisExpression': (),
}

# Keys that never contain child AST nodes
_SKIP_KEYS: frozenset[str] = frozenset(
    (
        'type',
        'raw',
        'value',
        'name',
        'operator',
        'kind',
        'computed',
        'method',
        'shorthand',
        'prefix',
        'async',
        'generator',
        'static',
        'sourceType',
        'start',
        'end',
        'loc',
        'range',
        'directive',
        'regex',
    )
)


def get_child_keys(node: Any) -> tuple[str, ...] | list[str]:
    """Return keys of a node that may contain child AST nodes or arrays.

    Uses the known ESTree child-key mapping when available, falling back
    to heuristic detection for unknown node types.
    """
    if not isinstance(node, dict) or 'type' not in node:
        return ()
    node_type = node['type']
    known_keys = _CHILD_KEYS.get(node_type)
    if known_keys is not None:
        return known_keys
    # Fallback: heuristic for unknown node types
    return [
        child_key
        for child_key, child_value in node.items()
        if child_key not in _SKIP_KEYS
        and not (child_key == 'expression' and node_type != 'ExpressionStatement')
        and isinstance(child_value, (dict, list))
    ]


def replace_identifiers(node: dict, parameter_map: dict[str, dict]) -> None:
    """Replace Identifier nodes whose names appear in parameter_map with deep copies.

    Skips non-computed property names in MemberExpressions.
    """
    if not isinstance(node, dict) or 'type' not in node:
        return
    for child_key in get_child_keys(node):
        child = node.get(child_key)
        if child is None:
            continue
        is_non_computed_property = (
            child_key == 'property' and node.get('type') == 'MemberExpression' and not node.get('computed')
        )
        if isinstance(child, list):
            for index, item in enumerate(child):
                if isinstance(item, dict) and item.get('type') == 'Identifier':
                    if not is_non_computed_property and item.get('name', '') in parameter_map:
                        child[index] = copy.deepcopy(parameter_map[item['name']])
                elif isinstance(item, dict) and 'type' in item:
                    replace_identifiers(item, parameter_map)
        elif isinstance(child, dict):
            if child.get('type') == 'Identifier':
                if not is_non_computed_property and child.get('name', '') in parameter_map:
                    node[child_key] = copy.deepcopy(parameter_map[child['name']])
            elif 'type' in child:
                replace_identifiers(child, parameter_map)


def identifiers_match(first_node: Any, second_node: Any) -> bool:
    """Return True if both nodes are Identifiers with the same name."""
    return (
        is_identifier(first_node) and is_identifier(second_node) and first_node.get('name') == second_node.get('name')
    )


def is_side_effect_free(node: Any) -> bool:
    """Return True if an expression node is side-effect-free (safe to discard)."""
    if not isinstance(node, dict):
        return False
    match node.get('type'):
        case 'Literal' | 'Identifier':
            return True
        case 'MemberExpression':
            return is_side_effect_free(node.get('object')) and (
                not node.get('computed') or is_side_effect_free(node.get('property'))
            )
        case 'UnaryExpression':
            if node.get('operator') in ('-', '+', '!', '~', 'typeof', 'void'):
                return is_side_effect_free(node.get('argument'))
        case 'BinaryExpression' | 'LogicalExpression':
            return is_side_effect_free(node.get('left')) and is_side_effect_free(node.get('right'))
        case 'ConditionalExpression':
            return (
                is_side_effect_free(node.get('test'))
                and is_side_effect_free(node.get('consequent'))
                and is_side_effect_free(node.get('alternate'))
            )
        case 'ArrayExpression':
            return all(is_side_effect_free(element) for element in (node.get('elements') or []) if element)
        case 'ObjectExpression':
            return all(
                is_side_effect_free(property_node.get('value')) for property_node in (node.get('properties') or [])
            )
        case 'TemplateLiteral':
            return all(is_side_effect_free(expression) for expression in (node.get('expressions') or []))
    return False


def get_member_names(node: Any) -> tuple[str, str] | tuple[None, None]:
    """Extract (object_name, property_name) from a MemberExpression.

    Handles both computed (obj["prop"]) and non-computed (obj.prop) forms.
    Returns (None, None) if extraction is not possible.
    """
    if not node or node.get('type') != 'MemberExpression':
        return None, None
    object_node = node.get('object')
    property_node = node.get('property')
    if not object_node or not is_identifier(object_node):
        return None, None
    if not property_node:
        return None, None
    if node.get('computed'):
        if is_string_literal(property_node):
            return object_node['name'], property_node['value']
        return None, None
    if is_identifier(property_node):
        return object_node['name'], property_node['name']
    return None, None


_POSITION_KEYS: frozenset[str] = frozenset(('start', 'end', 'loc', 'range'))


def nodes_equal(first_node: Any, second_node: Any) -> bool:
    """Return True if two AST nodes are structurally equal (ignoring position info)."""
    if type(first_node) != type(second_node):
        return False
    match first_node:
        case dict():
            first_keys = {key for key in first_node if key not in _POSITION_KEYS}
            second_keys = {key for key in second_node if key not in _POSITION_KEYS}
            if first_keys != second_keys:
                return False
            return all(nodes_equal(first_node[key], second_node[key]) for key in first_keys)
        case list():
            return len(first_node) == len(second_node) and all(
                nodes_equal(first_item, second_item) for first_item, second_item in zip(first_node, second_node)
            )
    return first_node == second_node
