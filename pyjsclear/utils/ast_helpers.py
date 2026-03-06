"""AST helper utilities for ESTree nodes."""

import copy
import keyword
import re


def deep_copy(node):
    """Deep copy an AST node."""
    return copy.deepcopy(node)


def is_literal(node):
    """Check if node is a Literal."""
    return isinstance(node, dict) and node.get('type') == 'Literal'


def is_identifier(node):
    """Check if node is an Identifier."""
    return isinstance(node, dict) and node.get('type') == 'Identifier'


def is_string_literal(node):
    """Check if node is a string Literal."""
    return is_literal(node) and isinstance(node.get('value'), str)


def is_numeric_literal(node):
    """Check if node is a numeric Literal."""
    return is_literal(node) and isinstance(node.get('value'), (int, float))


def is_boolean_literal(node):
    """Check if node is a boolean-ish literal (true/false or !0/!1)."""
    if is_literal(node):
        return isinstance(node.get('value'), bool)
    return False


def is_null_literal(node):
    """Check if node is null literal."""
    return is_literal(node) and node.get('value') is None and node.get('raw') == 'null'


def is_undefined(node):
    """Check if node represents undefined."""
    return is_identifier(node) and node.get('name') == 'undefined'


def get_literal_value(node):
    """Extract the value from a literal node. Returns (value, True) or (None, False)."""
    if not is_literal(node):
        return None, False
    return node.get('value'), True


def make_literal(value, raw=None):
    """Create a Literal AST node."""
    if raw is None:
        if isinstance(value, str):
            raw = repr(value).replace("'", '"')
            # Ensure double-quote wrapping
            if not raw.startswith('"'):
                raw = '"' + raw[1:-1].replace('"', '\\"') + '"'
        elif isinstance(value, bool):
            raw = 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            if isinstance(value, float) and value == int(value) and not (value == 0 and str(value).startswith('-')):
                raw = str(int(value))
            else:
                raw = str(value)
        elif value is None:
            raw = 'null'
        else:
            raw = str(value)
    return {'type': 'Literal', 'value': value, 'raw': raw}


def make_identifier(name):
    """Create an Identifier AST node."""
    return {'type': 'Identifier', 'name': name}


def make_expression_statement(expr):
    """Wrap an expression in an ExpressionStatement."""
    return {'type': 'ExpressionStatement', 'expression': expr}


def make_block_statement(body):
    """Create a BlockStatement."""
    return {'type': 'BlockStatement', 'body': body}


def make_var_declaration(name, init=None, kind='var'):
    """Create a VariableDeclaration with a single declarator."""
    return {
        'type': 'VariableDeclaration',
        'declarations': [{
            'type': 'VariableDeclarator',
            'id': make_identifier(name),
            'init': init
        }],
        'kind': kind
    }


def is_valid_identifier(name):
    """Check if a string is a valid JS identifier (for obj.prop access)."""
    if not isinstance(name, str) or not name:
        return False
    # JS reserved words are fine as property names in member access
    # But we check basic identifier syntax
    return bool(re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', name))


def get_child_keys(node):
    """Get keys of a node that may contain child nodes/arrays."""
    if not isinstance(node, dict) or 'type' not in node:
        return []
    # ESTree child node fields by type
    _CHILD_KEYS = {
        'Program': ['body'],
        'ExpressionStatement': ['expression'],
        'BlockStatement': ['body'],
        'VariableDeclaration': ['declarations'],
        'VariableDeclarator': ['id', 'init'],
        'FunctionDeclaration': ['id', 'params', 'body'],
        'FunctionExpression': ['id', 'params', 'body'],
        'ArrowFunctionExpression': ['params', 'body'],
        'ReturnStatement': ['argument'],
        'IfStatement': ['test', 'consequent', 'alternate'],
        'WhileStatement': ['test', 'body'],
        'DoWhileStatement': ['test', 'body'],
        'ForStatement': ['init', 'test', 'update', 'body'],
        'ForInStatement': ['left', 'right', 'body'],
        'ForOfStatement': ['left', 'right', 'body'],
        'SwitchStatement': ['discriminant', 'cases'],
        'SwitchCase': ['test', 'consequent'],
        'BreakStatement': ['label'],
        'ContinueStatement': ['label'],
        'LabeledStatement': ['label', 'body'],
        'ThrowStatement': ['argument'],
        'TryStatement': ['block', 'handler', 'finalizer'],
        'CatchClause': ['param', 'body'],
        'BinaryExpression': ['left', 'right'],
        'LogicalExpression': ['left', 'right'],
        'UnaryExpression': ['argument'],
        'UpdateExpression': ['argument'],
        'AssignmentExpression': ['left', 'right'],
        'MemberExpression': ['object', 'property'],
        'CallExpression': ['callee', 'arguments'],
        'NewExpression': ['callee', 'arguments'],
        'ConditionalExpression': ['test', 'consequent', 'alternate'],
        'SequenceExpression': ['expressions'],
        'ArrayExpression': ['elements'],
        'ObjectExpression': ['properties'],
        'Property': ['key', 'value'],
        'SpreadElement': ['argument'],
        'TemplateLiteral': ['quasis', 'expressions'],
        'TaggedTemplateExpression': ['tag', 'quasi'],
        'TemplateElement': [],
        'AssignmentPattern': ['left', 'right'],
        'ArrayPattern': ['elements'],
        'ObjectPattern': ['properties'],
        'RestElement': ['argument'],
        'ClassDeclaration': ['id', 'superClass', 'body'],
        'ClassExpression': ['id', 'superClass', 'body'],
        'ClassBody': ['body'],
        'MethodDefinition': ['key', 'value'],
        'YieldExpression': ['argument'],
        'AwaitExpression': ['argument'],
        'EmptyStatement': [],
        'Literal': [],
        'Identifier': [],
        'ThisExpression': [],
    }
    ntype = node.get('type', '')
    if ntype in _CHILD_KEYS:
        return _CHILD_KEYS[ntype]
    # Fallback: return all keys that look like they might contain nodes
    keys = []
    for k, v in node.items():
        if k in ('type', 'raw', 'value', 'name', 'operator', 'kind',
                  'computed', 'method', 'shorthand', 'prefix', 'async',
                  'generator', 'expression', 'static', 'sourceType',
                  'start', 'end', 'loc', 'range', 'directive', 'regex'):
            # 'expression' is a bool on ArrowFunctionExpression but a node on ExpressionStatement
            if k == 'expression' and ntype != 'ExpressionStatement':
                continue
            continue
        if isinstance(v, (dict, list)):
            keys.append(k)
    return keys


def nodes_equal(a, b):
    """Check if two AST nodes are structurally equal (ignoring position info)."""
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        keys_a = {k for k in a if k not in ('start', 'end', 'loc', 'range')}
        keys_b = {k for k in b if k not in ('start', 'end', 'loc', 'range')}
        if keys_a != keys_b:
            return False
        return all(nodes_equal(a[k], b[k]) for k in keys_a)
    if isinstance(a, list):
        return len(a) == len(b) and all(nodes_equal(x, y) for x, y in zip(a, b))
    return a == b
