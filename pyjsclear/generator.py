"""ESTree AST to JavaScript code generator."""

# Operator precedence (higher = binds tighter)
_PRECEDENCE = {
    '=': 3,
    '+=': 3,
    '-=': 3,
    '*=': 3,
    '/=': 3,
    '%=': 3,
    '<<=': 3,
    '>>=': 3,
    '>>>=': 3,
    '|=': 3,
    '^=': 3,
    '&=': 3,
    '**=': 3,
    '||': 5,
    '??': 5,
    '&&': 6,
    '|': 7,
    '^': 8,
    '&': 9,
    '==': 10,
    '!=': 10,
    '===': 10,
    '!==': 10,
    '<': 11,
    '>': 11,
    '<=': 11,
    '>=': 11,
    'instanceof': 11,
    'in': 11,
    '<<': 12,
    '>>': 12,
    '>>>': 12,
    '+': 13,
    '-': 13,
    '*': 14,
    '/': 14,
    '%': 14,
    '**': 15,
}

_UNARY_PRECEDENCE = 16

_NO_SEMI_TYPES = frozenset(
    {
        'BlockStatement',
        'IfStatement',
        'WhileStatement',
        'DoWhileStatement',
        'ForStatement',
        'ForInStatement',
        'ForOfStatement',
        'SwitchStatement',
        'TryStatement',
        'FunctionDeclaration',
        'ClassDeclaration',
        'LabeledStatement',
        'EmptyStatement',
    }
)


def generate(node, indent=0):
    """Generate JavaScript source from an ESTree AST node."""
    if node is None:
        return ''
    if not isinstance(node, dict):
        return str(node)

    node_type = node.get('type', '')
    gen = _GENERATORS.get(node_type)
    if gen:
        return gen(node, indent)
    return f'/* unknown: {node_type} */'


def _indent_str(level):
    return '  ' * level


def _is_directive(stmt):
    """Check if a statement is a string-literal directive (like 'use strict')."""
    return (
        stmt.get('type') == 'ExpressionStatement'
        and isinstance(stmt.get('expression'), dict)
        and stmt['expression'].get('type') == 'Literal'
        and isinstance(stmt['expression'].get('value'), str)
    )


def _gen_program(node, indent):
    parts = []
    body = node.get('body', [])
    for i, stmt in enumerate(body):
        if stmt is None:
            continue
        if stmt.get('type') == 'EmptyStatement':
            continue
        statement_code = _gen_stmt(stmt, indent)
        if statement_code.strip():
            parts.append(statement_code)
            if _is_directive(stmt) and i + 1 < len(body):
                parts.append('')
    return '\n'.join(parts)


def _gen_stmt(node, indent):
    """Generate a statement with indentation."""
    if node is None:
        return ''
    prefix = _indent_str(indent)
    code = generate(node, indent)
    node_type = node.get('type', '')
    if node_type in _NO_SEMI_TYPES:
        return prefix + code
    if code.endswith(';'):
        return prefix + code
    return prefix + code + ';'


def _gen_block(node, indent):
    if not node.get('body'):
        return '{}'
    lines = ['{']
    body = node.get('body', [])
    for i, stmt in enumerate(body):
        lines.append(_gen_stmt(stmt, indent + 1))
        if _is_directive(stmt) and i + 1 < len(body):
            lines.append('')
    lines.append(_indent_str(indent) + '}')
    return '\n'.join(lines)


def _gen_var_declaration(node, indent):
    kind = node.get('kind', 'var')
    declarations = []
    for declaration in node.get('declarations', []):
        name = generate(declaration['id'], indent)
        initializer = declaration.get('init')
        if initializer:
            declarations.append(f'{name} = {generate(initializer, indent)}')
        else:
            declarations.append(name)
    return f'{kind} {", ".join(declarations)}'


def _gen_function(node, indent, is_expression=False):
    """Shared generator for FunctionDeclaration and FunctionExpression."""
    name = generate(node['id'], indent) if node.get('id') else ''
    params = ', '.join(generate(p, indent) for p in node.get('params', []))
    async_prefix = 'async ' if node.get('async') else ''
    gen_prefix = '*' if node.get('generator') else ''
    body = generate(node['body'], indent)
    if name:
        return f'{async_prefix}function{gen_prefix} {name}({params}) {body}'
    # Anonymous: always put space before parens (Babel style)
    return f'{async_prefix}function{gen_prefix} ({params}) {body}'


def _gen_function_decl(node, indent):
    return _gen_function(node, indent)


def _gen_function_expr(node, indent):
    return _gen_function(node, indent, is_expression=True)


def _gen_arrow(node, indent):
    params = node.get('params', [])
    async_prefix = 'async ' if node.get('async') else ''
    param_str = '(' + ', '.join(generate(p, indent) for p in params) + ')'
    body = node.get('body', {})
    body_str = generate(body, indent)
    # Wrap object literal in parens to avoid ambiguity with block
    if body.get('type') == 'ObjectExpression':
        body_str = '(' + body_str + ')'
    return f'{async_prefix}{param_str} => {body_str}'


def _gen_return(node, indent):
    argument = node.get('argument')
    if argument:
        return f'return {generate(argument, indent)}'
    return 'return'


def _gen_if(node, indent):
    test = generate(node['test'], indent)
    consequent_code = generate(node['consequent'], indent)
    if node['consequent'].get('type') != 'BlockStatement':
        consequent_code = '\n' + _gen_stmt(node['consequent'], indent + 1)
    alternate = node.get('alternate')
    if alternate:
        if alternate.get('type') in ('IfStatement', 'BlockStatement'):
            alternate_code = ' else ' + generate(alternate, indent)
        else:
            alternate_code = ' else\n' + _gen_stmt(alternate, indent + 1)
        return f'if ({test}) {consequent_code}{alternate_code}'
    return f'if ({test}) {consequent_code}'


def _gen_while(node, indent):
    test = generate(node['test'], indent)
    body = generate(node['body'], indent)
    return f'while ({test}) {body}'


def _gen_do_while(node, indent):
    body = generate(node['body'], indent)
    test = generate(node['test'], indent)
    return f'do {body} while ({test})'


def _gen_for(node, indent):
    init = ''
    if node.get('init'):
        init = generate(node['init'], indent)
    test = generate(node.get('test'), indent) if node.get('test') else ''
    update = generate(node.get('update'), indent) if node.get('update') else ''
    body = generate(node['body'], indent)
    return f'for ({init}; {test}; {update}) {body}'


def _gen_for_in(node, indent):
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    body = generate(node['body'], indent)
    return f'for ({left} in {right}) {body}'


def _gen_for_of(node, indent):
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    body = generate(node['body'], indent)
    return f'for ({left} of {right}) {body}'


def _gen_switch(node, indent):
    discriminant = generate(node['discriminant'], indent)
    lines = [f'switch ({discriminant}) {{']
    for case in node.get('cases', []):
        if case.get('test'):
            lines.append(_indent_str(indent + 1) + f'case {generate(case["test"], indent + 1)}:')
        else:
            lines.append(_indent_str(indent + 1) + 'default:')
        for stmt in case.get('consequent', []):
            lines.append(_gen_stmt(stmt, indent + 2))
    lines.append(_indent_str(indent) + '}')
    return '\n'.join(lines)


def _gen_try(node, indent):
    block = generate(node['block'], indent)
    result = f'try {block}'
    handler = node.get('handler')
    if handler:
        param = generate(handler.get('param'), indent) if handler.get('param') else ''
        handler_body = generate(handler['body'], indent)
        if param:
            result += f' catch ({param}) {handler_body}'
        else:
            result += f' catch {handler_body}'
    finalizer = node.get('finalizer')
    if finalizer:
        result += f' finally {generate(finalizer, indent)}'
    return result


def _gen_throw(node, indent):
    return f'throw {generate(node["argument"], indent)}'


def _gen_break(node, indent):
    if node.get('label'):
        return f'break {generate(node["label"], indent)}'
    return 'break'


def _gen_continue(node, indent):
    if node.get('label'):
        return f'continue {generate(node["label"], indent)}'
    return 'continue'


def _gen_labeled(node, indent):
    label = generate(node['label'], indent)
    body = _gen_stmt(node['body'], indent)
    return f'{label}:\n{body}'


def _gen_expr_stmt(node, indent):
    return generate(node['expression'], indent)


def _gen_binary(node, indent):
    operator = node.get('operator', '')
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    my_prec = _PRECEDENCE.get(operator, 1)
    left_prec = _expr_precedence(node['left'])
    right_prec = _expr_precedence(node['right'])
    if left_prec < my_prec:
        left = f'({left})'
    if right_prec < my_prec or (right_prec == my_prec and operator not in ('+', '*', '|', '&', '^')):
        right = f'({right})'
    return f'{left} {operator} {right}'


def _gen_logical(node, indent):
    return _gen_binary(node, indent)


def _gen_unary(node, indent):
    operator = node.get('operator', '')
    operand = generate(node['argument'], indent)
    operand_prec = _expr_precedence(node['argument'])
    if operand_prec < _UNARY_PRECEDENCE:
        operand = f'({operand})'
    if operator in ('typeof', 'void', 'delete'):
        return f'{operator} {operand}'
    if node.get('prefix', True):
        return f'{operator}{operand}'
    return f'{operand}{operator}'


def _gen_update(node, indent):
    argument = generate(node['argument'], indent)
    operator = node.get('operator', '++')
    if node.get('prefix'):
        return f'{operator}{argument}'
    return f'{argument}{operator}'


def _gen_assignment(node, indent):
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    operator = node.get('operator', '=')
    return f'{left} {operator} {right}'


def _gen_member(node, indent):
    object_code = generate(node['object'], indent)
    obj_type = node['object'].get('type', '')
    computed = node.get('computed')

    needs_parens = False
    if obj_type == 'Literal' and isinstance(node['object'].get('value'), (int, float)):
        needs_parens = not computed
    elif obj_type in (
        'BinaryExpression',
        'UnaryExpression',
        'ConditionalExpression',
        'AssignmentExpression',
        'SequenceExpression',
        'ArrowFunctionExpression',
    ):
        needs_parens = _expr_precedence(node['object']) < 19

    if needs_parens:
        object_code = f'({object_code})'

    property_code = generate(node['property'], indent)
    if computed:
        return f'{object_code}[{property_code}]'
    return f'{object_code}.{property_code}'


def _gen_call(node, indent):
    callee = generate(node['callee'], indent)
    callee_type = node['callee'].get('type', '')
    if callee_type in ('FunctionExpression', 'ArrowFunctionExpression', 'SequenceExpression'):
        callee = f'({callee})'
    args = ', '.join(generate(a, indent) for a in node.get('arguments', []))
    return f'{callee}({args})'


def _gen_new(node, indent):
    callee = generate(node['callee'], indent)
    args = node.get('arguments', [])
    if args:
        arg_str = ', '.join(generate(a, indent) for a in args)
        return f'new {callee}({arg_str})'
    return f'new {callee}()'


def _wrap_if_sequence(node, code):
    """Wrap code in parens if node is a SequenceExpression."""
    if isinstance(node, dict) and node.get('type') == 'SequenceExpression':
        return f'({code})'
    return code


def _gen_conditional(node, indent):
    test = generate(node['test'], indent)
    consequent_code = _wrap_if_sequence(node.get('consequent'), generate(node['consequent'], indent))
    alternate_code = _wrap_if_sequence(node.get('alternate'), generate(node['alternate'], indent))
    return f'{test} ? {consequent_code} : {alternate_code}'


def _gen_sequence(node, indent):
    exprs = ', '.join(generate(e, indent) for e in node.get('expressions', []))
    return exprs


def _gen_bracket_list(elements, indent):
    """Generate a bracketed list of elements, replacing None with empty slots."""
    elems = [generate(e, indent) if e is not None else '' for e in elements]
    return '[' + ', '.join(elems) + ']'


def _gen_array(node, indent):
    return _gen_bracket_list(node.get('elements', []), indent)


def _gen_object_property(property_node, indent):
    """Generate a single object property string."""
    if property_node.get('type') == 'SpreadElement':
        return '...' + generate(property_node['argument'], indent)

    key = generate(property_node['key'], indent)
    if property_node.get('computed'):
        key = f'[{key}]'

    kind = property_node.get('kind', 'init')
    if kind in ('get', 'set') or property_node.get('method'):
        prefix = f'{kind} ' if kind in ('get', 'set') else ''
        params = ', '.join(generate(pp, indent) for pp in property_node['value'].get('params', []))
        body = generate(property_node['value'].get('body'), indent)
        return f'{prefix}{key}({params}) {body}'

    if property_node.get('shorthand'):
        return key

    value = generate(property_node['value'], indent)
    # Quote non-computed identifier keys (Babel style)
    if property_node['key'].get('type') == 'Identifier' and not property_node.get('computed'):
        key = f"'{property_node['key']['name']}'"
    return f'{key}: {value}'


def _gen_object(node, indent):
    properties = node.get('properties', [])
    if not properties:
        return '{}'
    parts = [_gen_object_property(property_node, indent + 1) for property_node in properties]
    inner_indent = _indent_str(indent + 1)
    outer_indent = _indent_str(indent)
    lines = ',\n'.join(inner_indent + part for part in parts)
    return '{\n' + lines + '\n' + outer_indent + '}'


def _gen_property(node, indent):
    key = generate(node['key'], indent)
    value = generate(node['value'], indent)
    return f'{key}: {value}'


def _gen_spread(node, indent):
    return '...' + generate(node['argument'], indent)


def _escape_string(val, raw):
    """Escape a string value and wrap in the appropriate quotes."""
    if raw and len(raw) >= 2 and raw[0] in ('"', "'"):
        quote = raw[0]
    else:
        quote = '"'
    escaped = val.replace('\\', '\\\\')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\r', '\\r')
    escaped = escaped.replace('\t', '\\t')
    escaped = escaped.replace(quote, '\\' + quote)
    return f'{quote}{escaped}{quote}'


def _gen_literal(node, indent):
    raw = node.get('raw')
    value = node.get('value')
    if isinstance(value, str):
        return _escape_string(value, raw)
    if raw is not None:
        return str(raw)
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value == int(value) and value >= 0:
            return str(int(value))
        return str(value)
    return str(value)


def _gen_identifier(node, indent):
    return node.get('name', '')


def _gen_this(node, indent):
    return 'this'


def _gen_empty(node, indent):
    return ';'


def _gen_template_literal(node, indent):
    quasis = node.get('quasis', [])
    exprs = node.get('expressions', [])
    parts = []
    for i, quasi in enumerate(quasis):
        raw = quasi.get('value', {}).get('raw', '')
        parts.append(raw)
        if i < len(exprs):
            parts.append('${' + generate(exprs[i], indent) + '}')
    return '`' + ''.join(parts) + '`'


def _gen_tagged_template(node, indent):
    tag = generate(node['tag'], indent)
    quasi = generate(node['quasi'], indent)
    return f'{tag}{quasi}'


def _gen_class_decl(node, indent):
    name = generate(node['id'], indent) if node.get('id') else ''
    superclass_clause = ''
    if node.get('superClass'):
        superclass_clause = f' extends {generate(node["superClass"], indent)}'
    body = generate(node['body'], indent)
    if name:
        return f'class {name}{superclass_clause} {body}'
    return f'class{superclass_clause} {body}'


def _gen_class_body(node, indent):
    if not node.get('body'):
        return '{}'
    lines = ['{']
    for method in node.get('body', []):
        lines.append(_indent_str(indent + 1) + generate(method, indent + 1))
    lines.append(_indent_str(indent) + '}')
    return '\n'.join(lines)


def _gen_method_def(node, indent):
    key = generate(node['key'], indent)
    if node.get('computed') or node['key'].get('type') == 'Literal':
        key = f'[{key}]'
    static = 'static ' if node.get('static') else ''
    kind = node.get('kind', 'method')
    value = node.get('value', {})
    params = ', '.join(generate(p, indent) for p in value.get('params', []))
    body = generate(value.get('body'), indent)
    match kind:
        case 'constructor':
            return f'{static}constructor({params}) {body}'
        case 'get':
            return f'{static}get {key}({params}) {body}'
        case 'set':
            return f'{static}set {key}({params}) {body}'
        case _:
            async_prefix = 'async ' if value.get('async') else ''
            gen_prefix = '*' if value.get('generator') else ''
            return f'{static}{async_prefix}{gen_prefix}{key}({params}) {body}'


def _gen_yield(node, indent):
    argument = generate(node.get('argument'), indent) if node.get('argument') else ''
    delegate = '*' if node.get('delegate') else ''
    if argument:
        return f'yield{delegate} {argument}'
    return f'yield{delegate}'


def _gen_await(node, indent):
    return f'await {generate(node["argument"], indent)}'


def _gen_assignment_pattern(node, indent):
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    return f'{left} = {right}'


def _gen_array_pattern(node, indent):
    return _gen_bracket_list(node.get('elements', []), indent)


def _gen_object_pattern_part(property_node, indent):
    """Generate a single destructuring pattern property."""
    if property_node.get('type') == 'RestElement':
        return '...' + generate(property_node['argument'], indent)
    key = generate(property_node['key'], indent)
    if property_node.get('shorthand'):
        return key
    value = generate(property_node['value'], indent)
    return f'{key}: {value}'


def _gen_object_pattern(node, indent):
    properties = [_gen_object_pattern_part(property_node, indent + 1) for property_node in node.get('properties', [])]
    if not properties:
        return '{}'
    inner_indent = _indent_str(indent + 1)
    outer_indent = _indent_str(indent)
    lines = ',\n'.join(inner_indent + part for part in properties)
    return '{\n' + lines + '\n' + outer_indent + '}'


def _gen_rest_element(node, indent):
    return '...' + generate(node['argument'], indent)


def _expr_precedence(node):
    """Get the precedence level of an expression node."""
    if not isinstance(node, dict):
        return 20
    match node.get('type', ''):
        case (
            'Literal'
            | 'Identifier'
            | 'ThisExpression'
            | 'ArrayExpression'
            | 'ObjectExpression'
            | 'FunctionExpression'
            | 'ClassExpression'
            | 'TemplateLiteral'
        ):
            return 20
        case 'MemberExpression' | 'CallExpression' | 'NewExpression' | 'TaggedTemplateExpression':
            return 19
        case 'UpdateExpression':
            return 17 if node.get('prefix') else 18
        case 'UnaryExpression':
            return _UNARY_PRECEDENCE
        case 'BinaryExpression' | 'LogicalExpression':
            return _PRECEDENCE.get(node.get('operator', ''), 1)
        case 'ConditionalExpression':
            return 4
        case 'AssignmentExpression' | 'ArrowFunctionExpression':
            return 3
        case 'YieldExpression':
            return 2
        case 'SequenceExpression':
            return 1
        case _:
            return 0


# Generator dispatch table
_GENERATORS = {
    'Program': _gen_program,
    'BlockStatement': _gen_block,
    'VariableDeclaration': _gen_var_declaration,
    'FunctionDeclaration': _gen_function_decl,
    'FunctionExpression': _gen_function_expr,
    'ArrowFunctionExpression': _gen_arrow,
    'ReturnStatement': _gen_return,
    'IfStatement': _gen_if,
    'WhileStatement': _gen_while,
    'DoWhileStatement': _gen_do_while,
    'ForStatement': _gen_for,
    'ForInStatement': _gen_for_in,
    'ForOfStatement': _gen_for_of,
    'SwitchStatement': _gen_switch,
    'TryStatement': _gen_try,
    'ThrowStatement': _gen_throw,
    'BreakStatement': _gen_break,
    'ContinueStatement': _gen_continue,
    'LabeledStatement': _gen_labeled,
    'ExpressionStatement': _gen_expr_stmt,
    'BinaryExpression': _gen_binary,
    'LogicalExpression': _gen_logical,
    'UnaryExpression': _gen_unary,
    'UpdateExpression': _gen_update,
    'AssignmentExpression': _gen_assignment,
    'MemberExpression': _gen_member,
    'CallExpression': _gen_call,
    'NewExpression': _gen_new,
    'ConditionalExpression': _gen_conditional,
    'SequenceExpression': _gen_sequence,
    'ArrayExpression': _gen_array,
    'ObjectExpression': _gen_object,
    'Property': _gen_property,
    'SpreadElement': _gen_spread,
    'Literal': _gen_literal,
    'Identifier': _gen_identifier,
    'ThisExpression': _gen_this,
    'EmptyStatement': _gen_empty,
    'TemplateLiteral': _gen_template_literal,
    'TaggedTemplateExpression': _gen_tagged_template,
    'ClassDeclaration': _gen_class_decl,
    'ClassExpression': _gen_class_decl,
    'ClassBody': _gen_class_body,
    'MethodDefinition': _gen_method_def,
    'YieldExpression': _gen_yield,
    'AwaitExpression': _gen_await,
    'AssignmentPattern': _gen_assignment_pattern,
    'ArrayPattern': _gen_array_pattern,
    'ObjectPattern': _gen_object_pattern,
    'RestElement': _gen_rest_element,
}
