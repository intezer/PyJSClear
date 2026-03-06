"""ESTree AST to JavaScript code generator."""

from .utils.ast_helpers import is_valid_identifier

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


def generate(node, indent=0):
    """Generate JavaScript source from an ESTree AST node."""
    if node is None:
        return ''
    if not isinstance(node, dict):
        return str(node)

    ntype = node.get('type', '')
    gen = _GENERATORS.get(ntype)
    if gen:
        return gen(node, indent)
    return f'/* unknown: {ntype} */'


def _indent_str(level):
    return '  ' * level


def _gen_program(node, indent):
    parts = []
    body = node.get('body', [])
    for i, stmt in enumerate(body):
        if stmt is None:
            continue
        if stmt.get('type') == 'EmptyStatement':
            continue  # Skip empty statements at top level
        s = _gen_stmt(stmt, indent)
        if s.strip():  # Skip empty lines from removed nodes
            parts.append(s)
            # Add blank line after directive strings (like 'use strict') — Babel style
            if (
                stmt.get('type') == 'ExpressionStatement'
                and isinstance(stmt.get('expression'), dict)
                and stmt['expression'].get('type') == 'Literal'
                and isinstance(stmt['expression'].get('value'), str)
                and i + 1 < len(body)
            ):
                parts.append('')
    return '\n'.join(parts)


def _gen_stmt(node, indent):
    """Generate a statement with indentation."""
    if node is None:
        return ''
    prefix = _indent_str(indent)
    code = generate(node, indent)
    ntype = node.get('type', '')
    # These statement types don't need semicolons
    no_semi = {
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
    if ntype in no_semi:
        return prefix + code
    # Avoid double semicolons
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
        # Add blank line after directive strings (like 'use strict') — Babel style
        if (
            stmt.get('type') == 'ExpressionStatement'
            and isinstance(stmt.get('expression'), dict)
            and stmt['expression'].get('type') == 'Literal'
            and isinstance(stmt['expression'].get('value'), str)
            and i + 1 < len(body)
        ):
            lines.append('')
    lines.append(_indent_str(indent) + '}')
    return '\n'.join(lines)


def _gen_var_declaration(node, indent):
    kind = node.get('kind', 'var')
    decls = []
    for d in node.get('declarations', []):
        name = generate(d['id'], indent)
        init = d.get('init')
        if init:
            decls.append(f'{name} = {generate(init, indent)}')
        else:
            decls.append(name)
    return f'{kind} {", ".join(decls)}'


def _gen_function_decl(node, indent):
    name = generate(node['id'], indent) if node.get('id') else ''
    params = ', '.join(generate(p, indent) for p in node.get('params', []))
    async_prefix = 'async ' if node.get('async') else ''
    gen_prefix = '*' if node.get('generator') else ''
    body = generate(node['body'], indent)
    return f'{async_prefix}function{gen_prefix} {name}({params}) {body}'


def _gen_function_expr(node, indent):
    name = generate(node['id'], indent) if node.get('id') else ''
    params = ', '.join(generate(p, indent) for p in node.get('params', []))
    async_prefix = 'async ' if node.get('async') else ''
    gen_prefix = '*' if node.get('generator') else ''
    body = generate(node['body'], indent)
    # Always put space before parens (Babel style)
    if name:
        return f'{async_prefix}function{gen_prefix} {name}({params}) {body}'
    return f'{async_prefix}function{gen_prefix} ({params}) {body}'


def _gen_arrow(node, indent):
    params = node.get('params', [])
    async_prefix = 'async ' if node.get('async') else ''
    # Always wrap params in parens (Babel style)
    param_str = '(' + ', '.join(generate(p, indent) for p in params) + ')'
    body = node.get('body', {})
    if body.get('type') == 'BlockStatement':
        body_str = generate(body, indent)
    else:
        body_str = generate(body, indent)
        # Wrap object literal in parens
        if body.get('type') == 'ObjectExpression':
            body_str = '(' + body_str + ')'
    return f'{async_prefix}{param_str} => {body_str}'


def _gen_return(node, indent):
    arg = node.get('argument')
    if arg:
        return f'return {generate(arg, indent)}'
    return 'return'


def _gen_if(node, indent):
    test = generate(node['test'], indent)
    cons = generate(node['consequent'], indent)
    if node['consequent'].get('type') != 'BlockStatement':
        cons = '\n' + _gen_stmt(node['consequent'], indent + 1)
    alt = node.get('alternate')
    if alt:
        if alt.get('type') == 'IfStatement':
            alt_str = ' else ' + generate(alt, indent)
        elif alt.get('type') == 'BlockStatement':
            alt_str = ' else ' + generate(alt, indent)
        else:
            alt_str = ' else\n' + _gen_stmt(alt, indent + 1)
        return f'if ({test}) {cons}{alt_str}'
    return f'if ({test}) {cons}'


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
    disc = generate(node['discriminant'], indent)
    lines = [f'switch ({disc}) {{']
    for case in node.get('cases', []):
        if case.get('test'):
            lines.append(
                _indent_str(indent + 1) + f'case {generate(case["test"], indent + 1)}:'
            )
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
        hbody = generate(handler['body'], indent)
        if param:
            result += f' catch ({param}) {hbody}'
        else:
            result += f' catch {hbody}'
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
    op = node.get('operator', '')
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    # Parenthesize children with lower precedence
    my_prec = _PRECEDENCE.get(op, 1)
    left_prec = _expr_precedence(node['left'])
    right_prec = _expr_precedence(node['right'])
    if left_prec < my_prec:
        left = f'({left})'
    if right_prec < my_prec or (
        right_prec == my_prec and op not in ('+', '*', '|', '&', '^')
    ):
        right = f'({right})'
    return f'{left} {op} {right}'


def _gen_logical(node, indent):
    return _gen_binary(node, indent)


def _gen_unary(node, indent):
    op = node.get('operator', '')
    arg = generate(node['argument'], indent)
    arg_prec = _expr_precedence(node['argument'])
    if arg_prec < _UNARY_PRECEDENCE:
        arg = f'({arg})'
    if op in ('typeof', 'void', 'delete'):
        return f'{op} {arg}'
    if node.get('prefix', True):
        return f'{op}{arg}'
    return f'{arg}{op}'


def _gen_update(node, indent):
    arg = generate(node['argument'], indent)
    op = node.get('operator', '++')
    if node.get('prefix'):
        return f'{op}{arg}'
    return f'{arg}{op}'


def _gen_assignment(node, indent):
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    op = node.get('operator', '=')
    return f'{left} {op} {right}'


def _gen_member(node, indent):
    obj = generate(node['object'], indent)
    # Parenthesize numeric literals and some expressions
    obj_type = node['object'].get('type', '')
    computed = node.get('computed')
    if obj_type in (
        'Literal',
        'BinaryExpression',
        'UnaryExpression',
        'ConditionalExpression',
        'AssignmentExpression',
        'SequenceExpression',
        'ArrowFunctionExpression',
    ):
        if obj_type == 'Literal' and isinstance(
            node['object'].get('value'), (int, float)
        ):
            # Only need parens for dot access (42.foo is ambiguous), not bracket (42[foo] is fine)
            if not computed:
                obj = f'({obj})'
        elif obj_type not in ('Literal',):
            if _expr_precedence(node['object']) < 19:
                obj = f'({obj})'
    prop = generate(node['property'], indent)
    if computed:
        return f'{obj}[{prop}]'
    return f'{obj}.{prop}'


def _gen_call(node, indent):
    callee = generate(node['callee'], indent)
    # Parenthesize non-simple callees
    ctype = node['callee'].get('type', '')
    if ctype in ('FunctionExpression', 'ArrowFunctionExpression', 'SequenceExpression'):
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


def _gen_conditional(node, indent):
    test = generate(node['test'], indent)
    cons = generate(node['consequent'], indent)
    alt = generate(node['alternate'], indent)
    # Wrap SequenceExpression in parens to avoid comma ambiguity
    if (
        isinstance(node.get('consequent'), dict)
        and node['consequent'].get('type') == 'SequenceExpression'
    ):
        cons = f'({cons})'
    if (
        isinstance(node.get('alternate'), dict)
        and node['alternate'].get('type') == 'SequenceExpression'
    ):
        alt = f'({alt})'
    return f'{test} ? {cons} : {alt}'


def _gen_sequence(node, indent):
    exprs = ', '.join(generate(e, indent) for e in node.get('expressions', []))
    return exprs


def _gen_array(node, indent):
    elems = []
    for e in node.get('elements', []):
        if e is None:
            elems.append('')
        else:
            elems.append(generate(e, indent))
    return '[' + ', '.join(elems) + ']'


def _gen_object(node, indent):
    props = node.get('properties', [])
    if not props:
        return '{}'
    parts = []
    for p in props:
        if p.get('type') == 'SpreadElement':
            parts.append('...' + generate(p['argument'], indent + 1))
            continue
        key = generate(p['key'], indent + 1)
        if p.get('computed'):
            key = f'[{key}]'
        val = generate(p['value'], indent + 1)
        if p.get('kind') == 'get':
            params = ', '.join(
                generate(pp, indent + 1) for pp in p['value'].get('params', [])
            )
            body = generate(p['value'].get('body'), indent + 1)
            parts.append(f'get {key}({params}) {body}')
        elif p.get('kind') == 'set':
            params = ', '.join(
                generate(pp, indent + 1) for pp in p['value'].get('params', [])
            )
            body = generate(p['value'].get('body'), indent + 1)
            parts.append(f'set {key}({params}) {body}')
        elif p.get('method'):
            params = ', '.join(
                generate(pp, indent + 1) for pp in p['value'].get('params', [])
            )
            body = generate(p['value'].get('body'), indent + 1)
            parts.append(f'{key}({params}) {body}')
        elif p.get('shorthand'):
            parts.append(key)
        else:
            # Quote non-computed identifier keys (Babel quotes them)
            if p['key'].get('type') == 'Identifier' and not p.get('computed'):
                key = f"'{p['key']['name']}'"
            parts.append(f'{key}: {val}')
    # Multi-line format for objects (Babel style)
    inner = _indent_str(indent + 1)
    outer = _indent_str(indent)
    lines = ',\n'.join(inner + p for p in parts)
    return '{\n' + lines + '\n' + outer + '}'


def _gen_property(node, indent):
    # Handled within _gen_object
    key = generate(node['key'], indent)
    val = generate(node['value'], indent)
    return f'{key}: {val}'


def _gen_spread(node, indent):
    return '...' + generate(node['argument'], indent)


def _gen_literal(node, indent):
    raw = node.get('raw')
    val = node.get('value')
    # For strings, re-generate from value to normalize escape sequences,
    # but preserve the original quote character from raw.
    if isinstance(val, str):
        # Preserve original quote style from raw when available
        if raw and len(raw) >= 2 and raw[0] in ('"', "'"):
            quote = raw[0]
        else:
            # No raw: string was created by transforms — use double quotes like Babel
            quote = '"'
        # Escape the string content
        escaped = val.replace('\\', '\\\\')
        escaped = escaped.replace('\n', '\\n')
        escaped = escaped.replace('\r', '\\r')
        escaped = escaped.replace('\t', '\\t')
        escaped = escaped.replace(quote, '\\' + quote)
        return f'{quote}{escaped}{quote}'
    if raw is not None:
        return str(raw)
    if val is None:
        return 'null'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, (int, float)):
        if isinstance(val, float) and val == int(val) and val >= 0:
            return str(int(val))
        return str(val)
    return str(val)


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
    sup = ''
    if node.get('superClass'):
        sup = f' extends {generate(node["superClass"], indent)}'
    body = generate(node['body'], indent)
    if name:
        return f'class {name}{sup} {body}'
    return f'class{sup} {body}'


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
    val = node.get('value', {})
    params = ', '.join(generate(p, indent) for p in val.get('params', []))
    body = generate(val.get('body'), indent)
    if kind == 'constructor':
        return f'{static}constructor({params}) {body}'
    if kind == 'get':
        return f'{static}get {key}({params}) {body}'
    if kind == 'set':
        return f'{static}set {key}({params}) {body}'
    async_prefix = 'async ' if val.get('async') else ''
    gen_prefix = '*' if val.get('generator') else ''
    return f'{static}{async_prefix}{gen_prefix}{key}({params}) {body}'


def _gen_yield(node, indent):
    arg = generate(node.get('argument'), indent) if node.get('argument') else ''
    delegate = '*' if node.get('delegate') else ''
    if arg:
        return f'yield{delegate} {arg}'
    return f'yield{delegate}'


def _gen_await(node, indent):
    return f'await {generate(node["argument"], indent)}'


def _gen_assignment_pattern(node, indent):
    left = generate(node['left'], indent)
    right = generate(node['right'], indent)
    return f'{left} = {right}'


def _gen_array_pattern(node, indent):
    elems = []
    for e in node.get('elements', []):
        if e is None:
            elems.append('')
        else:
            elems.append(generate(e, indent))
    return '[' + ', '.join(elems) + ']'


def _gen_object_pattern(node, indent):
    props = []
    for p in node.get('properties', []):
        if p.get('type') == 'RestElement':
            props.append('...' + generate(p['argument'], indent + 1))
        else:
            key = generate(p['key'], indent + 1)
            val = generate(p['value'], indent + 1)
            if p.get('shorthand'):
                props.append(key)
            else:
                props.append(f'{key}: {val}')
    if not props:
        return '{}'
    # Multi-line format (Babel style)
    inner = _indent_str(indent + 1)
    outer = _indent_str(indent)
    lines = ',\n'.join(inner + p for p in props)
    return '{\n' + lines + '\n' + outer + '}'


def _gen_rest_element(node, indent):
    return '...' + generate(node['argument'], indent)


def _expr_precedence(node):
    """Get the precedence level of an expression node."""
    if not isinstance(node, dict):
        return 20
    ntype = node.get('type', '')
    if ntype in (
        'Literal',
        'Identifier',
        'ThisExpression',
        'ArrayExpression',
        'ObjectExpression',
        'FunctionExpression',
        'ClassExpression',
        'TemplateLiteral',
    ):
        return 20
    if ntype in (
        'MemberExpression',
        'CallExpression',
        'NewExpression',
        'TaggedTemplateExpression',
    ):
        return 19
    if ntype == 'UpdateExpression':
        return 17 if node.get('prefix') else 18
    if ntype == 'UnaryExpression':
        return _UNARY_PRECEDENCE
    if ntype in ('BinaryExpression', 'LogicalExpression'):
        return _PRECEDENCE.get(node.get('operator', ''), 1)
    if ntype == 'ConditionalExpression':
        return 4
    if ntype == 'AssignmentExpression':
        return 3
    if ntype == 'YieldExpression':
        return 2
    if ntype == 'SequenceExpression':
        return 1
    if ntype == 'ArrowFunctionExpression':
        return 3
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
