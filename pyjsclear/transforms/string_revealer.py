"""String array detection, rotation, and decoding for obfuscator.io patterns."""

import math
import re

from ..generator import generate
from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import find_parent
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_numeric_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import make_literal
from ..utils.string_decoders import Base64StringDecoder
from ..utils.string_decoders import BasicStringDecoder
from ..utils.string_decoders import DecoderType
from ..utils.string_decoders import Rc4StringDecoder
from .base import Transform


_BASE_64_REGEX = re.compile(r"""['"]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\+/=['"]\.indexOf""")
_RC4_REGEX = re.compile(r"""[a-zA-Z$_]?[a-zA-Z0-9$_]+\s?\+=\s?String\.fromCharCode\(""")


def _eval_numeric(node):
    """Evaluate an AST node to a numeric value if it's a constant expression."""
    if not isinstance(node, dict):
        return None
    match node.get('type', ''):
        case 'Literal':
            val = node.get('value')
            return val if isinstance(val, (int, float)) else None
        case 'UnaryExpression':
            arg = _eval_numeric(node.get('argument'))
            if arg is None:
                return None
            match node.get('operator'):
                case '-':
                    return -arg
                case '+':
                    return +arg
            return None
        case 'BinaryExpression':
            left = _eval_numeric(node.get('left'))
            right = _eval_numeric(node.get('right'))
            if left is None or right is None:
                return None
            return _apply_arith(node.get('operator'), left, right)
    return None


def _js_parse_int(s):
    """Mimic JavaScript's parseInt: extract leading integer from string."""
    if not isinstance(s, str):
        return float('nan')
    s = s.strip()
    m = re.match(r'^[+-]?\d+', s)
    if m:
        return int(m.group())
    return float('nan')


def _apply_arith(operator, left, right):
    """Apply a binary arithmetic operator."""
    match operator:
        case '+':
            return left + right
        case '-':
            return left - right
        case '*':
            return left * right
        case '/':
            return left / right if right != 0 else None
        case '%':
            return left % right if right != 0 else None
        case _:
            return None


class WrapperInfo:
    """Info about a wrapper function that calls the decoder."""

    def __init__(self, name, param_index, wrapper_offset, func_node, key_param_index=None):
        self.name = name
        self.param_index = param_index
        self.wrapper_offset = wrapper_offset
        self.func_node = func_node
        self.key_param_index = key_param_index

    def get_effective_index(self, call_args):
        """Given call argument values, compute the effective decoder index."""
        if self.param_index >= len(call_args):
            return None
        value = call_args[self.param_index]
        if not isinstance(value, (int, float)):
            return None
        return int(value) + self.wrapper_offset

    def get_key(self, call_args):
        """Get the RC4 key argument if applicable."""
        if self.key_param_index is not None and self.key_param_index < len(call_args):
            return call_args[self.key_param_index]
        return None


class StringRevealer(Transform):
    """Decode obfuscated string arrays and replace wrapper calls with literals."""

    rebuild_scope = True

    def execute(self):
        scope_tree, node_scope = build_scope_tree(self.ast)

        # Strategy 1: Direct string array declarations (var arr = ["a","b","c"])
        self._process_direct_arrays(scope_tree)

        # Strategy 2: Obfuscator.io function-wrapped string arrays
        self._process_obfuscatorio_pattern()

        # Strategy 2b: Var-based string array with rotation + decoder
        self._process_var_array_pattern()

        # Strategy 3: Simple static array unpacking (js-deob --su)
        self._process_static_arrays()

        return self.has_changed()

    # ================================================================
    # Strategy 2: Obfuscator.io pattern
    # ================================================================

    def _process_obfuscatorio_pattern(self):
        """Handle obfuscator.io: array func -> decoder func -> wrapper funcs -> rotation."""
        body = self.ast.get('body', [])

        # Step 1: Find string array function
        array_func_name, string_array, array_func_idx = self._find_string_array_function(body)
        if array_func_name is None:
            return

        # Step 2: Find decoder function (calls the array function)
        decoder_name, decoder_offset, decoder_idx, decoder_type = self._find_decoder_function(body, array_func_name)
        if decoder_name is None:
            return

        # Step 3: Create base decoder
        decoder = self._create_base_decoder(string_array, decoder_offset, decoder_type)

        # Step 4: Find ALL wrapper functions that call the decoder
        wrappers = self._find_all_wrappers(decoder_name)

        # Step 4b: Find all decoder aliases (const x = decoderName) throughout the AST.
        # These are simple variable assignments to the decoder function, not wrapper
        # functions. They appear as direct decoder calls in rotation IIFEs and code.
        decoder_aliases = self._find_decoder_aliases(decoder_name)

        # Step 5: Find and execute rotation
        rotation_idx = self._find_and_execute_rotation(
            body, array_func_name, string_array, decoder, wrappers, decoder_aliases
        )

        # Update the AST array to reflect rotation so future passes
        # re-extract the correct (rotated) array.
        if rotation_idx is not None:
            self._update_ast_array(body[array_func_idx], string_array)

        # Step 6: Replace all wrapper calls with decoded strings
        all_replaced = self._replace_all_wrapper_calls(wrappers, decoder)

        # Step 7: Replace direct decoder calls (including aliases)
        self._replace_direct_decoder_calls(decoder_name, decoder, decoder_aliases)

        # Step 8: Remove decoder aliases (const x = decoderName)
        self._remove_decoder_aliases(decoder_name, decoder_aliases)

        # Step 9: Remove rotation IIFE. Also remove the decoder and array
        # functions — they are no longer needed since all calls have been
        # replaced with string literals.
        indices_to_remove = set()
        if rotation_idx is not None:
            indices_to_remove.add(rotation_idx)
        # Only remove decoder/array funcs if we actually decoded strings
        if self.has_changed():
            indices_to_remove.add(decoder_idx)
            indices_to_remove.add(array_func_idx)
        self._remove_body_indices(body, *indices_to_remove)

    def _find_string_array_function(self, body):
        """Find the string array function declaration.

        Pattern: function X() { var a = ['s1','s2',...]; X = function(){return a;}; return X(); }
        """
        for i, stmt in enumerate(body):
            if stmt.get('type') != 'FunctionDeclaration':
                continue
            func_name = stmt.get('id', {}).get('name')
            if not func_name:
                continue
            func_body = stmt.get('body', {}).get('body', [])
            if len(func_body) < 2:
                continue

            string_array = self._extract_array_from_statement(func_body[0])
            if string_array is not None and len(string_array) >= 5:
                return func_name, string_array, i

        return None, None, None

    @staticmethod
    def _string_array_from_expression(node):
        """Return list of string values if node is an ArrayExpression of all string literals."""
        if not node or node.get('type') != 'ArrayExpression':
            return None
        elements = node.get('elements', [])
        if not elements or not all(is_string_literal(e) for e in elements):
            return None
        return [e['value'] for e in elements]

    def _extract_array_from_statement(self, stmt):
        """Extract string array from a variable declaration or assignment."""
        if stmt.get('type') == 'VariableDeclaration':
            for declaration in stmt.get('declarations', []):
                result = self._string_array_from_expression(declaration.get('init'))
                if result is not None:
                    return result
        elif stmt.get('type') == 'ExpressionStatement':
            expr = stmt.get('expression')
            if expr and expr.get('type') == 'AssignmentExpression':
                return self._string_array_from_expression(expr.get('right'))
        return None

    def _find_decoder_function(self, body, array_func_name):
        """Find the decoder function that calls the array function.

        Pattern: function D(a,b) { var arr = ARRAY_FUNC(); D = function(i,k){i=i-OFFSET; return arr[i];}; return D(a,b); }
        """
        for i, stmt in enumerate(body):
            if stmt.get('type') != 'FunctionDeclaration':
                continue
            func_name = stmt.get('id', {}).get('name')
            if not func_name or func_name == array_func_name:
                continue

            if not self._function_calls(stmt, array_func_name):
                continue

            offset = self._extract_decoder_offset(stmt)

            source = generate(stmt)
            if _BASE_64_REGEX.search(source):
                dtype = DecoderType.RC4 if _RC4_REGEX.search(source) else DecoderType.BASE_64
            else:
                dtype = DecoderType.BASIC

            return func_name, offset, i, dtype

        return None, None, None, None

    def _function_calls(self, func_node, callee_name):
        """Check if a function body contains a call to callee_name."""
        found = [False]

        def visitor(node, parent):
            if found[0]:
                return
            if (
                node.get('type') == 'CallExpression'
                and is_identifier(node.get('callee'))
                and node['callee']['name'] == callee_name
            ):
                found[0] = True

        simple_traverse(func_node, visitor)
        return found[0]

    def _extract_decoder_offset(self, func_node):
        """Extract offset from decoder's inner param = param OP EXPR pattern."""
        found_offset = [None]

        def find_offset(node, parent):
            if found_offset[0] is not None:
                return
            if node.get('type') != 'AssignmentExpression':
                return
            left = node.get('left')
            right = node.get('right')
            if not left or not right:
                return
            if not is_identifier(left):
                return
            if right.get('type') != 'BinaryExpression':
                return
            if not (is_identifier(right.get('left')) and right['left']['name'] == left['name']):
                return
            operator = right.get('operator')
            if operator not in ('+', '-'):
                return
            right_value = _eval_numeric(right.get('right'))
            if right_value is not None:
                found_offset[0] = int(-right_value) if operator == '-' else int(right_value)

        simple_traverse(func_node, find_offset)
        return found_offset[0] if found_offset[0] is not None else 0

    def _create_base_decoder(self, string_array, offset, dtype):
        """Create the appropriate decoder instance."""
        match dtype:
            case DecoderType.RC4:
                return Rc4StringDecoder(string_array, offset)
            case DecoderType.BASE_64:
                return Base64StringDecoder(string_array, offset)
            case _:
                return BasicStringDecoder(string_array, offset)

    def _find_all_wrappers(self, decoder_name):
        """Find all wrapper functions throughout the AST that call the decoder.

        Pattern: function W(p0,..,pN) { return DECODER(p_i OP OFFSET, p_j); }
        """
        wrappers = {}

        def visitor(node, parent):
            if node.get('type') == 'FunctionDeclaration':
                info = self._analyze_wrapper(node, decoder_name)
                if info:
                    wrappers[info.name] = info
            elif node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                name_node = node.get('id')
                if (
                    init
                    and init.get('type') in ('FunctionExpression', 'ArrowFunctionExpression')
                    and is_identifier(name_node)
                ):
                    info = self._analyze_wrapper_expr(name_node['name'], init, decoder_name)
                    if info:
                        wrappers[info.name] = info

        simple_traverse(self.ast, visitor)
        return wrappers

    def _analyze_wrapper(self, func_node, decoder_name):
        """Check if a FunctionDeclaration is a wrapper. Returns WrapperInfo or None."""
        func_name = func_node.get('id', {}).get('name')
        if not func_name:
            return None
        return self._analyze_wrapper_expr(func_name, func_node, decoder_name)

    def _analyze_wrapper_expr(self, func_name, func_node, decoder_name):
        """Analyze a function node (declaration or expression) as a potential wrapper."""
        func_body = func_node.get('body', {})
        if func_body.get('type') == 'BlockStatement':
            statements = func_body.get('body', [])
        else:
            return None

        if len(statements) != 1:
            return None

        return_statement = statements[0]
        if return_statement.get('type') != 'ReturnStatement':
            return None

        argument = return_statement.get('argument')
        if not argument or argument.get('type') != 'CallExpression':
            return None

        callee = argument.get('callee')
        if not (is_identifier(callee) and callee['name'] == decoder_name):
            return None

        call_args = argument.get('arguments', [])
        if not call_args:
            return None

        params = func_node.get('params', [])
        param_names = [p['name'] for p in params if is_identifier(p)]

        param_index, wrapper_offset = self._extract_wrapper_offset(call_args[0], param_names)
        if param_index is None:
            return None

        key_param_index = None
        if len(call_args) > 1:
            second = call_args[1]
            if is_identifier(second) and second['name'] in param_names:
                key_param_index = param_names.index(second['name'])

        return WrapperInfo(func_name, param_index, wrapper_offset, func_node, key_param_index)

    def _extract_wrapper_offset(self, expr, param_names):
        """Extract (param_index, offset) from wrapper's first argument to decoder.

        Handles: p_N, p_N + LIT, p_N - LIT, p_N - -LIT, p_N + -LIT
        """
        if is_identifier(expr) and expr['name'] in param_names:
            return param_names.index(expr['name']), 0

        if expr.get('type') != 'BinaryExpression':
            return None, None
        operator = expr.get('operator')
        if operator not in ('+', '-'):
            return None, None

        left = expr.get('left')
        if not (is_identifier(left) and left['name'] in param_names):
            return None, None

        right_value = _eval_numeric(expr.get('right'))
        if right_value is None:
            return None, None

        param_idx = param_names.index(left['name'])
        offset = int(-right_value) if operator == '-' else int(right_value)
        return param_idx, offset

    def _remove_decoder_aliases(self, decoder_name, aliases):
        """Remove variable declarations that are aliases for the decoder.

        Removes: const _0xABC = _0x22e6;  and transitive: const _0xDEF = _0xABC;
        """
        if not aliases:
            return
        # The set of names to remove includes the decoder and all aliases
        removable_inits = aliases | {decoder_name}

        def enter(node, parent, key, index):
            if node.get('type') != 'VariableDeclaration':
                return
            decls = node.get('declarations', [])
            i = 0
            while i < len(decls):
                declaration = decls[i]
                name_node = declaration.get('id')
                init = declaration.get('init')
                if (
                    is_identifier(name_node)
                    and name_node['name'] in aliases
                    and init
                    and is_identifier(init)
                    and init['name'] in removable_inits
                ):
                    decls.pop(i)
                    self.set_changed()
                else:
                    i += 1
            if not decls:
                return REMOVE

        traverse(self.ast, {'enter': enter})

    def _find_decoder_aliases(self, decoder_name):
        """Find all variable declarations that are aliases for the decoder.

        Handles transitive aliases: const a = decoder; const b = a; const c = b;
        Returns a set of all alias names.
        """
        # First pass: collect all simple assignments (const x = y)
        assignments = {}  # name -> init_name

        def visitor(node, parent):
            if node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                name_node = node.get('id')
                if init and is_identifier(init) and is_identifier(name_node):
                    assignments[name_node['name']] = init['name']

        simple_traverse(self.ast, visitor)

        # Resolve transitively: follow chains back to decoder_name
        aliases = set()
        for name, init_name in assignments.items():
            # Walk the chain: name -> init_name -> ... -> decoder_name?
            seen = set()
            current = init_name
            while current and current not in seen:
                if current == decoder_name:
                    aliases.add(name)
                    break
                seen.add(current)
                current = assignments.get(current)

        return aliases

    # ---- Rotation ----

    def _find_and_execute_rotation(
        self,
        body,
        array_func_name,
        string_array,
        decoder,
        wrappers,
        decoder_aliases=None,
    ):
        """Find rotation IIFE and execute it. Returns body index or None."""
        for i, stmt in enumerate(body):
            if stmt.get('type') != 'ExpressionStatement':
                continue
            expr = stmt.get('expression')
            if not expr or expr.get('type') != 'CallExpression':
                continue

            callee = expr.get('callee')
            args = expr.get('arguments', [])

            if not callee or callee.get('type') != 'FunctionExpression':
                continue
            if len(args) != 2:
                continue

            if not (is_identifier(args[0]) and args[0]['name'] == array_func_name):
                continue

            stop_value = _eval_numeric(args[1])
            if stop_value is None:
                continue
            stop_value = int(stop_value)

            rotation_expr = self._extract_rotation_expression(callee)
            if rotation_expr is None:
                continue

            operation = self._parse_rotation_op(rotation_expr, wrappers, decoder_aliases)
            if operation is None:
                continue

            self._execute_rotation(string_array, operation, wrappers, decoder, stop_value)
            return i

        return None

    def _extract_rotation_expression(self, iife_func):
        """Extract the arithmetic expression from the try block in the rotation loop."""
        func_body = iife_func.get('body', {}).get('body', [])
        if not func_body:
            return None

        loop = None
        for stmt in func_body:
            if stmt.get('type') in ('WhileStatement', 'ForStatement'):
                loop = stmt

        if loop is None:
            return None

        loop_body = loop.get('body', {})
        stmts = loop_body.get('body', []) if loop_body.get('type') == 'BlockStatement' else [loop_body]

        for stmt in stmts:
            if stmt.get('type') != 'TryStatement':
                continue
            block = stmt.get('block', {}).get('body', [])
            if not block:
                continue
            result = self._expression_from_try_block(block[0])
            if result is not None:
                return result
        return None

    @staticmethod
    def _expression_from_try_block(first_statement):
        """Extract the init/rhs expression from the first statement in a try block."""
        if first_statement.get('type') == 'VariableDeclaration':
            decls = first_statement.get('declarations', [])
            return decls[0].get('init') if decls else None
        if first_statement.get('type') == 'ExpressionStatement':
            expr = first_statement.get('expression')
            if expr and expr.get('type') == 'AssignmentExpression':
                return expr.get('right')
        return None

    def _parse_rotation_op(self, expr, wrappers, decoder_aliases=None):
        """Parse a rotation expression into an operation tree."""
        if not isinstance(expr, dict):
            return None
        aliases = decoder_aliases or set()

        match expr.get('type', ''):
            case 'Literal' if isinstance(expr.get('value'), (int, float)):
                return {'op': 'literal', 'value': expr['value']}

            case 'UnaryExpression' if expr.get('operator') == '-':
                child = self._parse_rotation_op(expr.get('argument'), wrappers, decoder_aliases)
                return {'op': 'negate', 'child': child} if child else None

            case 'BinaryExpression' if expr.get('operator') in (
                '+',
                '-',
                '*',
                '/',
                '%',
            ):
                left = self._parse_rotation_op(expr.get('left'), wrappers, decoder_aliases)
                right = self._parse_rotation_op(expr.get('right'), wrappers, decoder_aliases)
                if left and right:
                    return {
                        'op': 'binary',
                        'operator': expr['operator'],
                        'left': left,
                        'right': right,
                    }
                return None

            case 'CallExpression':
                return self._parse_parseInt_call(expr, wrappers, aliases)

        return None

    def _parse_parseInt_call(self, expr, wrappers, aliases):
        """Parse parseInt(wrapperOrDecoder(...)) into an operation node."""
        callee = expr.get('callee')
        args = expr.get('arguments', [])
        if not (is_identifier(callee) and callee['name'] == 'parseInt' and len(args) == 1):
            return None
        inner = args[0]
        if inner.get('type') != 'CallExpression':
            return None
        inner_callee = inner.get('callee')
        if not is_identifier(inner_callee):
            return None
        cname = inner_callee['name']
        arg_values = []
        for a in inner.get('arguments', []):
            val = _eval_numeric(a)
            if val is not None:
                arg_values.append(int(val))
            elif is_string_literal(a):
                arg_values.append(a['value'])
            else:
                return None
        if cname in wrappers:
            return {'op': 'call', 'wrapper_name': cname, 'args': arg_values}
        if cname in aliases:
            return {'op': 'direct_decoder_call', 'args': arg_values}
        return None

    def _decode_and_parse_int(self, decoder, idx, key=None):
        """Decode a string and parse it as an integer. Raises on failure."""
        decoded = decoder.get_string(int(idx), key) if key is not None else decoder.get_string(int(idx))
        if decoded is None:
            raise ValueError('Decoder returned None')
        result = _js_parse_int(decoded)
        if math.isnan(result):
            raise ValueError('NaN from parseInt')
        return result

    def _apply_rotation_op(self, operation, wrappers, decoder):
        """Evaluate a parsed rotation operation tree."""
        match operation['op']:
            case 'literal':
                return operation['value']
            case 'negate':
                return -self._apply_rotation_op(operation['child'], wrappers, decoder)
            case 'binary':
                left = self._apply_rotation_op(operation['left'], wrappers, decoder)
                right = self._apply_rotation_op(operation['right'], wrappers, decoder)
                return _apply_arith(operation['operator'], left, right)
            case 'call':
                wrapper = wrappers[operation['wrapper_name']]
                call_args = operation['args']
                effective_idx = wrapper.get_effective_index(call_args)
                if effective_idx is None:
                    raise ValueError('Invalid wrapper args')
                return self._decode_and_parse_int(decoder, effective_idx, wrapper.get_key(call_args))
            case 'direct_decoder_call':
                call_args = operation['args']
                if not call_args:
                    raise ValueError('No args for direct decoder call')
                key = call_args[1] if len(call_args) > 1 else None
                return self._decode_and_parse_int(decoder, int(call_args[0]), key)
            case _:
                raise ValueError(f'Unknown op: {operation["op"]}')

    def _execute_rotation(self, string_array, operation, wrappers, decoder, stop_value):
        """Rotate array until the expression evaluates to stop_value."""
        for _ in range(100001):
            try:
                value = self._apply_rotation_op(operation, wrappers, decoder)
                if int(value) == stop_value:
                    return True
                string_array.append(string_array.pop(0))
            except Exception:
                string_array.append(string_array.pop(0))
        return False

    # ---- Replacement ----

    def _replace_all_wrapper_calls(self, wrappers, decoder):
        """Replace all calls to wrapper functions with decoded string literals."""
        if not wrappers:
            return True
        all_replaced = [True]

        def enter(node, parent, key, index):
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not is_identifier(callee):
                return
            if callee['name'] not in wrappers:
                return

            wrapper = wrappers[callee['name']]
            call_args = node.get('arguments', [])

            # Only need the active param (index) and optionally the key param
            if wrapper.param_index >= len(call_args):
                all_replaced[0] = False
                return

            index_value = _eval_numeric(call_args[wrapper.param_index])
            if index_value is None and is_string_literal(call_args[wrapper.param_index]):
                try:
                    s = call_args[wrapper.param_index]['value']
                    index_value = int(s, 16) if s.startswith('0x') else int(s)
                except (ValueError, TypeError):
                    pass
            if index_value is None:
                all_replaced[0] = False
                return

            effective_idx = int(index_value) + wrapper.wrapper_offset

            key = None
            if wrapper.key_param_index is not None and wrapper.key_param_index < len(call_args):
                key_argument = call_args[wrapper.key_param_index]
                if is_string_literal(key_argument):
                    key = key_argument['value']
                else:
                    key_value = _eval_numeric(key_argument)
                    if key_value is not None:
                        key = str(int(key_value))

            try:
                decoded = (
                    decoder.get_string(int(effective_idx), key)
                    if key is not None
                    else decoder.get_string(int(effective_idx))
                )
                if isinstance(decoded, str):
                    self.set_changed()
                    return make_literal(decoded)
                all_replaced[0] = False
            except Exception:
                all_replaced[0] = False

        traverse(self.ast, {'enter': enter})
        return all_replaced[0]

    def _replace_direct_decoder_calls(self, decoder_name, decoder, decoder_aliases=None):
        """Replace direct calls to the decoder function (and its aliases) with literals."""
        names = {decoder_name}
        if decoder_aliases:
            names.update(decoder_aliases)

        def enter(node, parent, key, index):
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not (is_identifier(callee) and callee['name'] in names):
                return
            args = node.get('arguments', [])
            if not args:
                return

            first_val = _eval_numeric(args[0])
            # Also handle string hex arguments like '0x0', '0xa' (JS coerces to number)
            if first_val is None and is_string_literal(args[0]):
                try:
                    first_val = (
                        int(args[0]['value'], 16) if args[0]['value'].startswith('0x') else int(args[0]['value'])
                    )
                except (ValueError, TypeError):
                    pass
            if first_val is None:
                return

            key = None
            if len(args) > 1 and is_string_literal(args[1]):
                key = args[1]['value']

            try:
                decoded = (
                    decoder.get_string(int(first_val), key) if key is not None else decoder.get_string(int(first_val))
                )
                if isinstance(decoded, str):
                    self.set_changed()
                    return make_literal(decoded)
            except Exception:
                pass

        traverse(self.ast, {'enter': enter})

    @staticmethod
    def _find_array_expression_in_statement(stmt):
        """Find the first ArrayExpression node in a variable declaration or assignment."""
        if stmt.get('type') == 'VariableDeclaration':
            for declaration in stmt.get('declarations', []):
                init = declaration.get('init')
                if init and init.get('type') == 'ArrayExpression':
                    return init
        elif stmt.get('type') == 'ExpressionStatement':
            expr = stmt.get('expression')
            if expr and expr.get('type') == 'AssignmentExpression':
                right = expr.get('right')
                if right and right.get('type') == 'ArrayExpression':
                    return right
        return None

    def _update_ast_array(self, func_node, rotated_array):
        """Update the AST's array function to contain the rotated string array."""
        func_body = func_node.get('body', {}).get('body', [])
        if not func_body:
            return
        arr_expr = self._find_array_expression_in_statement(func_body[0])
        if arr_expr is not None:
            arr_expr['elements'] = [make_literal(s) for s in rotated_array]

    def _remove_body_indices(self, body, *indices):
        """Remove statements at given indices from body."""
        for idx in sorted(set(i for i in indices if i is not None), reverse=True):
            if 0 <= idx < len(body):
                body.pop(idx)
                self.set_changed()

    # ================================================================
    # Strategy 2b: Var-based string array + rotation IIFE + decoder
    # Pattern:
    #   var _0xARR = ['s1', 's2', ...];
    #   (function(arr, count) { var f = function(n) { while(--n) arr.push(arr.shift()); }; f(++count); })(_0xARR, 0xNN);
    #   var _0xDEC = function(a, b) { a = a - OFFSET; var x = _0xARR[a]; return x; };
    # ================================================================

    def _process_var_array_pattern(self):
        """Handle var-based string array with simple rotation and decoder."""
        body = self.ast.get('body', [])
        if len(body) < 3:
            return

        # Step 1: Find var _0x... = [string array] at top level
        array_name, string_array, array_idx = self._find_var_string_array(body)
        if array_name is None:
            return

        # Step 2: Find rotation IIFE that references the array var
        rotation_idx, rotation_count = self._find_simple_rotation(body, array_name)

        # Step 3: Execute rotation if found
        if rotation_idx is not None and rotation_count is not None:
            for _ in range(rotation_count):
                string_array.append(string_array.pop(0))

        # Step 4: Find decoder function (var _0x... = function(a,b) { a=a-OFFSET; ... _0xARR[a] ... })
        decoder_name, decoder_offset, decoder_idx = self._find_var_decoder(body, array_name)
        if decoder_name is None:
            return

        # Step 5: Create decoder and find wrappers
        decoder = BasicStringDecoder(string_array, decoder_offset)
        wrappers = self._find_all_wrappers(decoder_name)
        decoder_aliases = self._find_decoder_aliases(decoder_name)

        # Step 6: Replace wrapper calls
        self._replace_all_wrapper_calls(wrappers, decoder)

        # Step 7: Replace direct decoder calls (including aliases)
        self._replace_direct_decoder_calls(decoder_name, decoder, decoder_aliases)

        # Step 8: Remove aliases
        self._remove_decoder_aliases(decoder_name, decoder_aliases)

        # Step 9: Remove infrastructure (array, rotation, decoder)
        if self.has_changed():
            indices_to_remove = {array_idx, decoder_idx}
            if rotation_idx is not None:
                indices_to_remove.add(rotation_idx)
            self._remove_body_indices(body, *indices_to_remove)

    def _find_var_string_array(self, body):
        """Find var _0x... = ['s1', 's2', ...] at top of body."""
        for i, stmt in enumerate(body[:3]):
            if stmt.get('type') != 'VariableDeclaration':
                continue
            for declaration in stmt.get('declarations', []):
                name_node = declaration.get('id')
                if not is_identifier(name_node):
                    continue
                init = declaration.get('init')
                if not init or init.get('type') != 'ArrayExpression':
                    continue
                elements = init.get('elements', [])
                if len(elements) < 3:
                    continue
                if not all(is_string_literal(e) for e in elements):
                    continue
                return name_node['name'], [e['value'] for e in elements], i
        return None, None, None

    def _find_simple_rotation(self, body, array_name):
        """Find (function(arr, count) { ...push/shift... })(array, N) rotation IIFE."""
        for i, stmt in enumerate(body):
            if stmt.get('type') != 'ExpressionStatement':
                continue
            expr = stmt.get('expression')
            if not expr or expr.get('type') != 'CallExpression':
                continue
            callee = expr.get('callee')
            args = expr.get('arguments', [])
            if not callee or callee.get('type') != 'FunctionExpression':
                continue
            if len(args) != 2:
                continue
            if not (is_identifier(args[0]) and args[0]['name'] == array_name):
                continue

            # Evaluate the count argument
            count_val = _eval_numeric(args[1])
            if count_val is None:
                continue

            # Verify the IIFE body has push/shift pattern
            src = generate(callee)
            if 'push' in src and 'shift' in src:
                # The rotation does `while(--n) { arr.push(arr.shift()); }`
                # called with `++count`, so effective rotations = count + 1
                # But the pattern is: f(++count) inside the IIFE, where f
                # does while(--n). So n starts at count+1, decrements to 1.
                # That's count rotations.
                return i, int(count_val)

        return None, None

    def _find_var_decoder(self, body, array_name):
        """Find var _0xDEC = function(a) { a = a - OFFSET; var x = ARR[a]; return x; }."""
        for i, stmt in enumerate(body):
            if stmt.get('type') != 'VariableDeclaration':
                continue
            for declaration in stmt.get('declarations', []):
                name_node = declaration.get('id')
                if not is_identifier(name_node):
                    continue
                init = declaration.get('init')
                if not init or init.get('type') != 'FunctionExpression':
                    continue
                source = generate(init)
                if array_name not in source:
                    continue
                offset = self._extract_decoder_offset(init)
                return name_node['name'], offset, i
        return None, None, None

    # ================================================================
    # Strategy 1: Direct string array declarations
    # ================================================================

    def _try_replace_array_access(self, ref_parent, ref_key, string_array):
        """Replace arr[N] member expression with the string literal if valid."""
        if not ref_parent or ref_parent.get('type') != 'MemberExpression':
            return
        if ref_key != 'object' or not ref_parent.get('computed'):
            return
        prop = ref_parent.get('property')
        if not is_numeric_literal(prop):
            return
        idx = int(prop['value'])
        if not (0 <= idx < len(string_array)):
            return
        self._replace_node_in_ast(ref_parent, make_literal(string_array[idx]))
        self.set_changed()

    def _process_direct_arrays(self, scope_tree):
        """Find direct array declarations and replace indexed accesses."""
        for name, binding in list(scope_tree.bindings.items()):
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            init = node.get('init')
            if not init or init.get('type') != 'ArrayExpression':
                continue
            elements = init.get('elements', [])
            if not elements or not all(is_string_literal(e) for e in elements):
                continue

            string_array = [e['value'] for e in elements]
            for reference_node, reference_parent, reference_key, ref_index in binding.references[:]:
                self._try_replace_array_access(reference_parent, reference_key, string_array)
            for child in scope_tree.children:
                self._process_direct_arrays_in_scope(child, name, string_array)

    def _process_direct_arrays_in_scope(self, scope, name, string_array):
        """Process direct array accesses in child scopes."""
        binding = scope.get_binding(name)
        if not binding:
            return
        for reference_node, reference_parent, reference_key, ref_index in binding.references[:]:
            self._try_replace_array_access(reference_parent, reference_key, string_array)

    def _replace_node_in_ast(self, target, replacement):
        """Replace a node in the AST with a replacement."""
        result = find_parent(self.ast, target)
        if result:
            parent, key, index = result
            if index is not None:
                parent[key][index] = replacement
            else:
                parent[key] = replacement

    # ================================================================
    # Strategy 3: Simple static array unpacking
    # ================================================================

    def _process_static_arrays(self):
        """No-op: static array unpacking is handled by _process_direct_arrays."""
        pass
