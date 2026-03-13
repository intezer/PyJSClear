"""ESTree AST to JavaScript code generator."""
from __future__ import annotations

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


def generate(node: dict | None, indent: int = 0) -> str:
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


def _indent_str(level: int) -> str:
    return '  ' * level


def _is_directive(stmt: dict) -> bool:
    """Check if a statement is a string-literal directive (like 'use strict')."""
    return (
        stmt.get('type') == 'ExpressionStatement'
        and isinstance(stmt.get('expression'), dict)
        and stmt['expression'].get('type') == 'Literal'
        and isinstance(stmt['expression'].get('value'), str)
    )


def _gen_program(node: dict, indent: int) -> str:
    parts = []
    body = node.get('body', [])
    for index, stmt in enumerate(body):
        if stmt is None:
            continue
        if stmt.get('type') == 'EmptyStatement':
            continue
        statement_code = _gen_stmt(stmt, indent)
        if statement_code.strip():
            parts.append(statement_code)
            if _is_directive(stmt) and index + 1 < len(body):
                parts.append('')
    return '\n'.join(parts)


def _gen_stmt(node: dict | None, indent: int) -> str:
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


def _gen_block(node: dict, indent: int) -> str:
    if not node.get('body'):
        return '{}'
    lines = ['{']
    body = node.get('body', [])
    for index, stmt in enumerate(body):
        lines.append(_gen_stmt(stmt, indent + 1))
        if _is_directive(stmt) and index + 1 < len(body):
            lines.append('')
    lines.append(_indent_str(indent) + '}')
    return '\n'.join(lines)


def _gen_var_declaration(node: dict, indent: int) -> str:
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


def _gen_function(node: dict, indent: int, is_expression: bool = False) -> str:
    """Shared generator for FunctionDeclaration and FunctionExpression."""
    name = generate(node['id'], indent) if node.get('id') else ''
    params = ', '.join(generate(param, indent) for param in node.get('params', []))
    async_prefix = 'async ' if node.get('async') else ''
    gen_prefix = '*' if node.get('generator') else ''
    body = generate(node['body'], indent)
    if name:
        return f'{async_prefix}function{gen_prefix} {name}({params}) {body}'
    # Anonymous: always put space before parens (Babel style)
    return f'{async_prefix}function{gen_prefix} ({params}) {body}'


def _gen_function_decl(node: dict, indent: int) -> str:
    return _gen_function(node, indent)


def _gen_function_expr(node: dict, indent: int) -> str:
    return _gen_function(node, indent, is_expression=True)


def _gen_arrow(node: dict, indent: int) -> str:
    params = node.get('params', [])
    async_prefix = 'async ' if node.get('async') else ''
    param_str = '(' + ', '.join(generate(param, indent) for param in params) + ')'
    body = node.get('body', {})
    body_str = generate(body, indent)
    # Wrap object literal in parens to avoid ambiguity with block
    if body.get('type') == 'ObjectExpression':
        body_str = '(' + body_str + ')'
    return f'{async_prefix}{param_str} => {body_str}'


def _gen_return(node: dict, indent: int) -> str:
    argument = node.get('argument')
    if argument:
        return f'return {generate(argument, indent)}'
    return 'return'


def _gen_if(node: dict, indent: int) -> str:
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


def _gen_while(node: dict, indent: int) -> str:
    test = generate(node['test'], indent)
    body = generate(node['body'], indent)
    return f'while ({test}) {body}'


def _gen_do_while(node: dict, indent: int) -> str:
    body = generate(node['body'], indent)
    test = generate(node['test'], indent)
    return f'do {body} while ({test})'


def _gen_for(node: dict, indent: int) -> str:
    init = ''
    if node.get('init'):
        init = generate(node['init'], indent)
    test = generate(node.get('test'), indent) if node.get('test') else ''
    update = generate(node.get('update'), indent) if node.get('update') else ''
    body = generate(node['body'], indent)
    return f'for ({init}; {test}; {update}) {body}'


def _gen_for_in(node: dict, indent: int) -> str:
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    body = generate(node['body'], indent)
    return f'for ({left} in {right}) {body}'


def _gen_for_of(node: dict, indent: int) -> str:
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    body = generate(node['body'], indent)
    return f'for ({left} of {right}) {body}'


def _gen_switch(node: dict, indent: int) -> str:
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


def _gen_try(node: dict, indent: int) -> str:
    block = generate(node['block'], indent)
    result = f'try {block}'
    handler = node.get('handler')
    if handler:
        catch_param = generate(handler.get('param'), indent) if handler.get('param') else ''
        handler_body = generate(handler['body'], indent)
        if catch_param:
            result += f' catch ({catch_param}) {handler_body}'
        else:
            result += f' catch {handler_body}'
    finalizer = node.get('finalizer')
    if finalizer:
        result += f' finally {generate(finalizer, indent)}'
    return result


def _gen_throw(node: dict, indent: int) -> str:
    return f'throw {generate(node["argument"], indent)}'


def _gen_break(node: dict, indent: int) -> str:
    if node.get('label'):
        return f'break {generate(node["label"], indent)}'
    return 'break'


def _gen_continue(node: dict, indent: int) -> str:
    if node.get('label'):
        return f'continue {generate(node["label"], indent)}'
    return 'continue'


def _gen_labeled(node: dict, indent: int) -> str:
    label = generate(node['label'], indent)
    body = _gen_stmt(node['body'], indent)
    return f'{label}:\n{body}'


def _gen_expr_stmt(node: dict, indent: int) -> str:
    return generate(node['expression'], indent)


def _gen_binary(node: dict, indent: int) -> str:
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


def _gen_logical(node: dict, indent: int) -> str:
    return _gen_binary(node, indent)


def _gen_unary(node: dict, indent: int) -> str:
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


def _gen_update(node: dict, indent: int) -> str:
    argument = generate(node['argument'], indent)
    operator = node.get('operator', '++')
    if node.get('prefix'):
        return f'{operator}{argument}'
    return f'{argument}{operator}'


def _gen_assignment(node: dict, indent: int) -> str:
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    operator = node.get('operator', '=')
    return f'{left} {operator} {right}'


def _gen_member(node: dict, indent: int) -> str:
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
    dot = '?.' if node.get('optional') else '.'
    if computed:
        if node.get('optional'):
            return f'{object_code}?.[{property_code}]'
        return f'{object_code}[{property_code}]'
    return f'{object_code}{dot}{property_code}'


def _gen_call(node: dict, indent: int) -> str:
    callee = generate(node['callee'], indent)
    callee_type = node['callee'].get('type', '')
    if callee_type in ('FunctionExpression', 'ArrowFunctionExpression', 'SequenceExpression'):
        callee = f'({callee})'
    args = ', '.join(generate(argument, indent) for argument in node.get('arguments', []))
    if node.get('optional'):
        return f'{callee}?.({args})'
    return f'{callee}({args})'


def _gen_new(node: dict, indent: int) -> str:
    callee = generate(node['callee'], indent)
    args = node.get('arguments', [])
    if args:
        arg_str = ', '.join(generate(argument, indent) for argument in args)
        return f'new {callee}({arg_str})'
    return f'new {callee}()'


def _wrap_if_sequence(node: dict | None, code: str) -> str:
    """Wrap code in parens if node is a SequenceExpression."""
    if isinstance(node, dict) and node.get('type') == 'SequenceExpression':
        return f'({code})'
    return code


def _gen_conditional(node: dict, indent: int) -> str:
    test = generate(node['test'], indent)
    consequent_code = _wrap_if_sequence(node.get('consequent'), generate(node['consequent'], indent))
    alternate_code = _wrap_if_sequence(node.get('alternate'), generate(node['alternate'], indent))
    return f'{test} ? {consequent_code} : {alternate_code}'


def _gen_sequence(node: dict, indent: int) -> str:
    exprs = ', '.join(generate(expression, indent) for expression in node.get('expressions', []))
    return exprs


def _gen_bracket_list(elements: list, indent: int) -> str:
    """Generate a bracketed list of elements, replacing None with empty slots."""
    elems = [generate(element, indent) if element is not None else '' for element in elements]
    return '[' + ', '.join(elems) + ']'


def _gen_array(node: dict, indent: int) -> str:
    return _gen_bracket_list(node.get('elements', []), indent)


def _gen_object_property(property_node: dict, indent: int) -> str:
    """Generate a single object property string."""
    if property_node.get('type') == 'SpreadElement':
        return '...' + generate(property_node['argument'], indent)

    key = generate(property_node['key'], indent)
    if property_node.get('computed'):
        key = f'[{key}]'

    kind = property_node.get('kind', 'init')
    if kind in ('get', 'set') or property_node.get('method'):
        prefix = f'{kind} ' if kind in ('get', 'set') else ''
        params = ', '.join(generate(param, indent) for param in property_node['value'].get('params', []))
        body = generate(property_node['value'].get('body'), indent)
        return f'{prefix}{key}({params}) {body}'

    if property_node.get('shorthand'):
        return key

    value = generate(property_node['value'], indent)
    return f'{key}: {value}'


def _gen_object(node: dict, indent: int) -> str:
    properties = node.get('properties', [])
    if not properties:
        return '{}'
    parts = [_gen_object_property(property_node, indent + 1) for property_node in properties]
    inner_indent = _indent_str(indent + 1)
    outer_indent = _indent_str(indent)
    lines = ',\n'.join(inner_indent + part for part in parts)
    return '{\n' + lines + '\n' + outer_indent + '}'


def _gen_property(node: dict, indent: int) -> str:
    key = generate(node['key'], indent)
    value = generate(node['value'], indent)
    return f'{key}: {value}'


def _gen_spread(node: dict, indent: int) -> str:
    return '...' + generate(node['argument'], indent)


def _escape_string(string_value: str, raw: str | None) -> str:
    """Escape a string value and wrap in the appropriate quotes."""
    if raw and len(raw) >= 2 and raw[0] in ('"', "'"):
        quote = raw[0]
    else:
        quote = '"'
    escaped = string_value.replace('\\', '\\\\')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\r', '\\r')
    escaped = escaped.replace('\t', '\\t')
    escaped = escaped.replace(quote, '\\' + quote)
    return f'{quote}{escaped}{quote}'


def _gen_literal(node: dict, indent: int) -> str:
    raw = node.get('raw')
    value = node.get('value')
    if isinstance(value, str):
        return _escape_string(value, raw)
    if raw is not None:
        return str(raw)
    match value:
        case None:
            return 'null'
        case bool():
            return 'true' if value else 'false'
        case int() | float():
            if isinstance(value, float) and value == int(value) and value >= 0:
                return str(int(value))
            return str(value)
        case _:
            return str(value)


def _gen_identifier(node: dict, indent: int) -> str:
    return node.get('name', '')


def _gen_this(node: dict, indent: int) -> str:
    return 'this'


def _gen_empty(node: dict, indent: int) -> str:
    return ';'


def _gen_template_literal(node: dict, indent: int) -> str:
    quasis = node.get('quasis', [])
    expressions = node.get('expressions', [])
    parts = []
    for index, quasi in enumerate(quasis):
        raw = quasi.get('value', {}).get('raw', '')
        parts.append(raw)
        if index < len(expressions):
            parts.append('${' + generate(expressions[index], indent) + '}')
    return '`' + ''.join(parts) + '`'


def _gen_tagged_template(node: dict, indent: int) -> str:
    tag = generate(node['tag'], indent)
    quasi = generate(node['quasi'], indent)
    return f'{tag}{quasi}'


def _gen_class_decl(node: dict, indent: int) -> str:
    name = generate(node['id'], indent) if node.get('id') else ''
    superclass_clause = ''
    if node.get('superClass'):
        superclass_clause = f' extends {generate(node["superClass"], indent)}'
    body = generate(node['body'], indent)
    if name:
        return f'class {name}{superclass_clause} {body}'
    return f'class{superclass_clause} {body}'


def _gen_class_body(node: dict, indent: int) -> str:
    if not node.get('body'):
        return '{}'
    lines = ['{']
    for method in node.get('body', []):
        lines.append(_indent_str(indent + 1) + generate(method, indent + 1))
    lines.append(_indent_str(indent) + '}')
    return '\n'.join(lines)


def _gen_method_def(node: dict, indent: int) -> str:
    key = generate(node['key'], indent)
    if node.get('computed') or node['key'].get('type') == 'Literal':
        key = f'[{key}]'
    static_prefix = 'static ' if node.get('static') else ''
    kind = node.get('kind', 'method')
    value = node.get('value', {})
    params = ', '.join(generate(param, indent) for param in value.get('params', []))
    body = generate(value.get('body'), indent)
    match kind:
        case 'constructor':
            return f'{static_prefix}constructor({params}) {body}'
        case 'get':
            return f'{static_prefix}get {key}({params}) {body}'
        case 'set':
            return f'{static_prefix}set {key}({params}) {body}'
        case _:
            async_prefix = 'async ' if value.get('async') else ''
            gen_prefix = '*' if value.get('generator') else ''
            return f'{static_prefix}{async_prefix}{gen_prefix}{key}({params}) {body}'


def _gen_yield(node: dict, indent: int) -> str:
    argument = generate(node.get('argument'), indent) if node.get('argument') else ''
    delegate = '*' if node.get('delegate') else ''
    if argument:
        return f'yield{delegate} {argument}'
    return f'yield{delegate}'


def _gen_await(node: dict, indent: int) -> str:
    return f'await {generate(node["argument"], indent)}'


def _gen_assignment_pattern(node: dict, indent: int) -> str:
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    return f'{left} = {right}'


def _gen_array_pattern(node: dict, indent: int) -> str:
    return _gen_bracket_list(node.get('elements', []), indent)


def _gen_object_pattern_part(property_node: dict, indent: int) -> str:
    """Generate a single destructuring pattern property."""
    if property_node.get('type') == 'RestElement':
        return '...' + generate(property_node['argument'], indent)
    key = generate(property_node['key'], indent)
    if property_node.get('shorthand'):
        return key
    value = generate(property_node['value'], indent)
    return f'{key}: {value}'


def _gen_object_pattern(node: dict, indent: int) -> str:
    properties = [_gen_object_pattern_part(property_node, indent + 1) for property_node in node.get('properties', [])]
    if not properties:
        return '{}'
    inner_indent = _indent_str(indent + 1)
    outer_indent = _indent_str(indent)
    lines = ',\n'.join(inner_indent + part for part in properties)
    return '{\n' + lines + '\n' + outer_indent + '}'


def _gen_rest_element(node: dict, indent: int) -> str:
    return '...' + generate(node['argument'], indent)


def _gen_import_specifier(specifier: dict, indent: int) -> str:
    """Generate a single import specifier."""
    specifier_type = specifier.get('type', '')
    if specifier_type == 'ImportDefaultSpecifier':
        return generate(specifier['local'], indent)
    if specifier_type == 'ImportNamespaceSpecifier':
        return '* as ' + generate(specifier['local'], indent)
    # ImportSpecifier
    imported = generate(specifier['imported'], indent)
    local = generate(specifier['local'], indent)
    if imported == local:
        return imported
    return f'{imported} as {local}'


def _gen_import_declaration(node: dict, indent: int) -> str:
    source = generate(node['source'], indent)
    specifiers = node.get('specifiers', [])
    if not specifiers:
        return f'import {source}'
    default_specifiers = [s for s in specifiers if s.get('type') == 'ImportDefaultSpecifier']
    namespace_specifiers = [s for s in specifiers if s.get('type') == 'ImportNamespaceSpecifier']
    named_specifiers = [s for s in specifiers if s.get('type') == 'ImportSpecifier']
    parts = []
    if default_specifiers:
        parts.append(_gen_import_specifier(default_specifiers[0], indent))
    if namespace_specifiers:
        parts.append(_gen_import_specifier(namespace_specifiers[0], indent))
    if named_specifiers:
        names = ', '.join(_gen_import_specifier(specifier, indent) for specifier in named_specifiers)
        parts.append('{' + names + '}')
    return f'import {", ".join(parts)} from {source}'


def _gen_export_specifier(specifier: dict, indent: int) -> str:
    exported = generate(specifier['exported'], indent)
    local = generate(specifier['local'], indent)
    if exported == local:
        return exported
    return f'{local} as {exported}'


def _gen_export_named(node: dict, indent: int) -> str:
    declaration = node.get('declaration')
    if declaration:
        return f'export {generate(declaration, indent)}'
    specifiers = node.get('specifiers', [])
    names = ', '.join(_gen_export_specifier(specifier, indent) for specifier in specifiers)
    source = node.get('source')
    if source:
        return f'export {{{names}}} from {generate(source, indent)}'
    return f'export {{{names}}}'


def _gen_export_default(node: dict, indent: int) -> str:
    declaration = node.get('declaration', {})
    return f'export default {generate(declaration, indent)}'


def _gen_export_all(node: dict, indent: int) -> str:
    source = generate(node['source'], indent)
    return f'export * from {source}'


def _expr_precedence(node: dict) -> int:
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
    'ImportDeclaration': _gen_import_declaration,
    'ExportNamedDeclaration': _gen_export_named,
    'ExportDefaultDeclaration': _gen_export_default,
    'ExportAllDeclaration': _gen_export_all,
}
