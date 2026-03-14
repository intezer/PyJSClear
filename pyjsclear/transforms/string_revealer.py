"""String array detection, rotation, and decoding for obfuscator.io patterns."""

import math
import re
from typing import Any

from ..generator import generate
from ..scope import build_scope_tree
from ..traverser import REMOVE
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


_BASE_64_REGEX = re.compile(r"""['"]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\+/=['"]""")
_RC4_REGEX = re.compile(r"""fromCharCode.{0,30}\^""")


def _eval_numeric(node: Any) -> int | float | None:
    """Evaluate an AST node to a numeric value if it's a constant expression."""
    if not isinstance(node, dict):
        return None
    match node.get('type', ''):
        case 'Literal':
            value = node.get('value')
            return value if isinstance(value, (int, float)) else None
        case 'UnaryExpression':
            argument_value = _eval_numeric(node.get('argument'))
            if argument_value is None:
                return None
            match node.get('operator'):
                case '-':
                    return -argument_value
                case '+':
                    return +argument_value
            return None
        case 'BinaryExpression':
            left = _eval_numeric(node.get('left'))
            right = _eval_numeric(node.get('right'))
            if left is None or right is None:
                return None
            return _apply_arith(node.get('operator'), left, right)
    return None


def _js_parse_int(string: str) -> float:
    """Mimic JavaScript's parseInt: extract leading integer from string."""
    if not isinstance(string, str):
        return float('nan')
    string = string.strip()
    match = re.match(r'^[+-]?\d+', string)
    if match:
        return int(match.group())
    return float('nan')


def _apply_arith(operator: str, left: int | float, right: int | float) -> int | float | None:
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


def _collect_object_literals(ast: dict) -> dict[tuple[str, str], int | float | str]:
    """Collect simple object literal assignments: var o = {a: 0x1b1, b: 'str'}.

    Returns a dict mapping (object_name, property_name) -> value (int or str).
    """
    result: dict[tuple[str, str], int | float | str] = {}

    def visitor(node: dict, parent: dict | None) -> None:
        if node.get('type') != 'VariableDeclarator':
            return
        name_node = node.get('id')
        initializer = node.get('init')
        if not is_identifier(name_node) or not initializer or initializer.get('type') != 'ObjectExpression':
            return
        object_name = name_node['name']
        for property_entry in initializer.get('properties', []):
            if property_entry.get('type') != 'Property':
                continue
            key = property_entry.get('key')
            value = property_entry.get('value')
            if not key or not value:
                continue
            if is_identifier(key):
                property_name = key.get('name')
            elif is_string_literal(key):
                property_name = key.get('value')
            else:
                continue
            numeric_value = _eval_numeric(value)
            if numeric_value is not None:
                result[(object_name, property_name)] = numeric_value
            elif is_string_literal(value):
                result[(object_name, property_name)] = value['value']

    simple_traverse(ast, visitor)
    return result


def _resolve_arg_value(arg: dict, object_literals: dict) -> int | float | None:
    """Try to resolve a call argument to a numeric value.

    Handles numeric literals, string hex literals, and member expressions
    referencing known object literal properties.
    """
    numeric_value = _eval_numeric(arg)
    if numeric_value is not None:
        return numeric_value

    if is_string_literal(arg):
        try:
            string_value = arg['value']
            return int(string_value, 16) if string_value.startswith('0x') else int(string_value)
        except (ValueError, TypeError):
            pass

    if arg.get('type') == 'MemberExpression' and not arg.get('computed'):
        object_node = arg.get('object')
        property_node = arg.get('property')
        if is_identifier(object_node) and is_identifier(property_node):
            looked_up = object_literals.get((object_node['name'], property_node['name']))
            if isinstance(looked_up, (int, float)):
                return looked_up
            if isinstance(looked_up, str):
                try:
                    return int(looked_up, 16) if looked_up.startswith('0x') else int(looked_up)
                except (ValueError, TypeError):
                    pass

    return None


def _resolve_string_arg(arg: dict, object_literals: dict) -> str | None:
    """Try to resolve a call argument to a string value.

    Handles string literals and member expressions referencing known object properties.
    """
    if is_string_literal(arg):
        return arg['value']
    if arg.get('type') == 'MemberExpression' and not arg.get('computed'):
        object_node = arg.get('object')
        property_node = arg.get('property')
        if is_identifier(object_node) and is_identifier(property_node):
            looked_up = object_literals.get((object_node['name'], property_node['name']))
            if isinstance(looked_up, str):
                return looked_up
    return None


class WrapperInfo:
    """Info about a wrapper function that calls the decoder."""

    def __init__(
        self,
        name: str,
        param_index: int,
        wrapper_offset: int,
        func_node: dict,
        key_param_index: int | None = None,
    ) -> None:
        self.name = name
        self.param_index = param_index
        self.wrapper_offset = wrapper_offset
        self.func_node = func_node
        self.key_param_index = key_param_index

    def get_effective_index(self, call_args: list) -> int | None:
        """Given call argument values, compute the effective decoder index."""
        if self.param_index >= len(call_args):
            return None
        value = call_args[self.param_index]
        if not isinstance(value, (int, float)):
            return None
        return int(value) + self.wrapper_offset

    def get_key(self, call_args: list) -> str | None:
        """Get the RC4 key argument if applicable."""
        if self.key_param_index is not None and self.key_param_index < len(call_args):
            return call_args[self.key_param_index]
        return None


class StringRevealer(Transform):
    """Decode obfuscated string arrays and replace wrapper calls with literals."""

    rebuild_scope = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize transform with empty rotation locals."""
        super().__init__(*args, **kwargs)
        self._rotation_locals: dict[str, dict] = {}

    def execute(self) -> bool:
        """Run all string-revealing strategies and return whether changes were made."""
        if self.scope_tree is not None:
            scope_tree, node_scope = self.scope_tree, self.node_scope
        else:
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

    def _process_obfuscatorio_pattern(self) -> None:
        """Handle obfuscator.io: array func -> decoder func(s) -> wrapper funcs -> rotation."""
        body = self.ast.get('body', [])

        # Step 1: Find string array function
        array_func_name, string_array, array_func_idx = self._find_string_array_function(body)
        if array_func_name is None:
            return

        # Step 2: Find ALL decoder functions that call the array function
        decoder_infos = self._find_all_decoder_functions(body, array_func_name)
        if not decoder_infos:
            return

        # Step 3: Create decoders, wrappers, and aliases for each decoder function
        decoders = {}  # decoder_name -> decoder instance
        decoder_wrappers = {}  # decoder_name -> {wrapper_name: WrapperInfo}
        all_wrappers = {}  # all wrappers combined
        all_decoder_aliases = set()
        decoder_indices = set()
        for decoder_func_name, decoder_offset, decoder_body_index, decoder_type in decoder_infos:
            decoder = self._create_base_decoder(string_array, decoder_offset, decoder_type)
            decoders[decoder_func_name] = decoder
            decoder_indices.add(decoder_body_index)
            wrappers = self._find_all_wrappers(decoder_func_name)
            decoder_wrappers[decoder_func_name] = wrappers
            all_wrappers.update(wrappers)
            all_decoder_aliases.update(self._find_decoder_aliases(decoder_func_name))

        # Use the first decoder as the primary (for rotation — all share the same array)
        primary_decoder = decoders[decoder_infos[0][0]]

        # Build a combined alias-to-decoder map for rotation evaluation
        alias_decoder_map = {}
        for decoder_func_name, decoder in decoders.items():
            alias_decoder_map[decoder_func_name] = decoder
            for alias in self._find_decoder_aliases(decoder_func_name):
                alias_decoder_map[alias] = decoder

        # Step 5: Find and execute rotation
        rotation_result = self._find_and_execute_rotation(
            body,
            array_func_name,
            string_array,
            primary_decoder,
            all_wrappers,
            all_decoder_aliases,
            alias_decoder_map=alias_decoder_map,
            all_decoders=decoders,
        )

        # Update the AST array to reflect rotation so future passes
        # re-extract the correct (rotated) array.
        if rotation_result is not None:
            self._update_ast_array(body[array_func_idx], string_array)

        # Collect object literals for member expression resolution
        object_literals = _collect_object_literals(self.ast)

        # Step 6-8: Replace calls and remove aliases for each decoder
        for decoder_func_name, decoder in decoders.items():
            aliases_for_decoder = self._find_decoder_aliases(decoder_func_name)

            self._replace_all_wrapper_calls(decoder_wrappers[decoder_func_name], decoder, object_literals)
            self._replace_direct_decoder_calls(decoder_func_name, decoder, aliases_for_decoder, object_literals)
            self._remove_decoder_aliases(decoder_func_name, aliases_for_decoder)

        # Step 9: Remove rotation IIFE, decoder and array functions
        indices_to_remove = set()
        if rotation_result is not None:
            rotation_idx, rotation_call_expr = rotation_result
            if rotation_call_expr is not None:
                # Rotation was inside a SequenceExpression — remove only that sub-expression
                sequence_expression = body[rotation_idx]['expression']
                expressions = sequence_expression.get('expressions', [])
                try:
                    expressions.remove(rotation_call_expr)
                    self.set_changed()
                except ValueError:
                    pass
                # If only one expression remains, unwrap the SequenceExpression
                if len(expressions) == 1:
                    body[rotation_idx]['expression'] = expressions[0]
                    self.set_changed()
            else:
                indices_to_remove.add(rotation_idx)
        # Only remove decoder/array funcs if we actually decoded strings
        if self.has_changed():
            indices_to_remove.update(decoder_indices)
            indices_to_remove.add(array_func_idx)
        self._remove_body_indices(body, *indices_to_remove)

    def _find_string_array_function(self, body: list) -> tuple[str | None, list | None, int | None]:
        """Find the string array function declaration.

        Pattern: function X() { var a = ['s1','s2',...]; X = function(){return a;}; return X(); }
        """
        for i, statement in enumerate(body):
            if statement.get('type') != 'FunctionDeclaration':
                continue
            func_name = statement.get('id', {}).get('name')
            if not func_name:
                continue
            func_body = statement.get('body', {}).get('body', [])
            if len(func_body) < 2:
                continue

            string_array = self._extract_array_from_statement(func_body[0])
            if string_array is not None and len(string_array) >= 2:
                return func_name, string_array, i

        return None, None, None

    @staticmethod
    def _string_array_from_expression(node: dict | None) -> list[str] | None:
        """Return list of string values if node is an ArrayExpression of all string literals."""
        if not node or node.get('type') != 'ArrayExpression':
            return None
        elements = node.get('elements', [])
        if not elements or not all(is_string_literal(element) for element in elements):
            return None
        return [element['value'] for element in elements]

    def _extract_array_from_statement(self, statement: dict) -> list[str] | None:
        """Extract string array from a variable declaration or assignment."""
        match statement.get('type'):
            case 'VariableDeclaration':
                for declaration in statement.get('declarations', []):
                    result = self._string_array_from_expression(declaration.get('init'))
                    if result is not None:
                        return result
            case 'ExpressionStatement':
                expression = statement.get('expression')
                if expression and expression.get('type') == 'AssignmentExpression':
                    return self._string_array_from_expression(expression.get('right'))
        return None

    def _find_all_decoder_functions(self, body: list, array_func_name: str) -> list[tuple[str, int, int, DecoderType]]:
        """Find all decoder functions that call the array function.

        Returns list of (func_name, offset, body_index, decoder_type) tuples.
        """
        results = []
        for i, statement in enumerate(body):
            if statement.get('type') != 'FunctionDeclaration':
                continue
            func_name = statement.get('id', {}).get('name')
            if not func_name or func_name == array_func_name:
                continue

            if not self._function_calls(statement, array_func_name):
                continue

            offset = self._extract_decoder_offset(statement)

            source = generate(statement)
            if _BASE_64_REGEX.search(source):
                decoder_type = DecoderType.RC4 if _RC4_REGEX.search(source) else DecoderType.BASE_64
            else:
                decoder_type = DecoderType.BASIC

            results.append((func_name, offset, i, decoder_type))

        return results

    def _function_calls(self, func_node: dict, callee_name: str) -> bool:
        """Check if a function body contains a call to the given callee."""
        found = [False]

        def visitor(node: dict, parent: dict | None) -> None:
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

    def _extract_decoder_offset(self, func_node: dict) -> int:
        """Extract offset from decoder's inner param = param OP EXPR pattern."""
        found_offset: list[int | None] = [None]

        def find_offset(node: dict, parent: dict | None) -> None:
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

    def _create_base_decoder(
        self, string_array: list[str], offset: int, dtype: DecoderType
    ) -> BasicStringDecoder | Base64StringDecoder | Rc4StringDecoder:
        """Create the appropriate decoder instance."""
        match dtype:
            case DecoderType.RC4:
                return Rc4StringDecoder(string_array, offset)
            case DecoderType.BASE_64:
                return Base64StringDecoder(string_array, offset)
            case _:
                return BasicStringDecoder(string_array, offset)

    def _find_all_wrappers(self, decoder_name: str) -> dict[str, 'WrapperInfo']:
        """Find all wrapper functions throughout the AST that call the decoder.

        Pattern: function W(p0,..,pN) { return DECODER(p_i OP OFFSET, p_j); }
        """
        wrappers: dict[str, WrapperInfo] = {}

        def visitor(node: dict, parent: dict | None) -> None:
            if node.get('type') == 'FunctionDeclaration':
                info = self._analyze_wrapper(node, decoder_name)
                if info:
                    wrappers[info.name] = info
            elif node.get('type') == 'VariableDeclarator':
                initializer = node.get('init')
                name_node = node.get('id')
                if (
                    initializer
                    and initializer.get('type') in ('FunctionExpression', 'ArrowFunctionExpression')
                    and is_identifier(name_node)
                ):
                    info = self._analyze_wrapper_expr(name_node['name'], initializer, decoder_name)
                    if info:
                        wrappers[info.name] = info

        simple_traverse(self.ast, visitor)
        return wrappers

    def _analyze_wrapper(self, func_node: dict, decoder_name: str) -> 'WrapperInfo | None':
        """Check if a FunctionDeclaration is a wrapper. Returns WrapperInfo or None."""
        func_name = func_node.get('id', {}).get('name')
        if not func_name:
            return None
        return self._analyze_wrapper_expr(func_name, func_node, decoder_name)

    def _analyze_wrapper_expr(self, func_name: str, func_node: dict, decoder_name: str) -> 'WrapperInfo | None':
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

    def _extract_wrapper_offset(self, expression: dict, param_names: list[str]) -> tuple[int | None, int | None]:
        """Extract (param_index, offset) from wrapper's first argument to decoder.

        Handles: p_N, p_N + LIT, p_N - LIT, p_N - -LIT, p_N + -LIT
        """
        if is_identifier(expression) and expression['name'] in param_names:
            return param_names.index(expression['name']), 0

        if expression.get('type') != 'BinaryExpression':
            return None, None
        operator = expression.get('operator')
        if operator not in ('+', '-'):
            return None, None

        left = expression.get('left')
        if not (is_identifier(left) and left['name'] in param_names):
            return None, None

        right_value = _eval_numeric(expression.get('right'))
        if right_value is None:
            return None, None

        param_index = param_names.index(left['name'])
        offset = int(-right_value) if operator == '-' else int(right_value)
        return param_index, offset

    def _remove_decoder_aliases(self, decoder_name: str, aliases: set[str]) -> None:
        """Remove variable declarations that are aliases for the decoder.

        Removes: const _0xABC = _0x22e6;  and transitive: const _0xDEF = _0xABC;
        """
        if not aliases:
            return
        # The set of names to remove includes the decoder and all aliases
        removable_initializers = aliases | {decoder_name}

        def enter(node: dict, parent: dict, key: str, index: int | None) -> Any:
            if node.get('type') != 'VariableDeclaration':
                return None
            declarations = node.get('declarations', [])
            cursor = 0
            while cursor < len(declarations):
                declaration = declarations[cursor]
                name_node = declaration.get('id')
                initializer = declaration.get('init')
                if (
                    is_identifier(name_node)
                    and name_node['name'] in aliases
                    and initializer
                    and is_identifier(initializer)
                    and initializer['name'] in removable_initializers
                ):
                    declarations.pop(cursor)
                    self.set_changed()
                else:
                    cursor += 1
            if not declarations:
                return REMOVE

        traverse(self.ast, {'enter': enter})

    def _find_decoder_aliases(self, decoder_name: str) -> set[str]:
        """Find all variable declarations that are aliases for the decoder.

        Handles transitive aliases: const a = decoder; const b = a; const c = b;
        Returns a set of all alias names.
        """
        # First pass: collect all simple assignments (const x = y)
        assignments: dict[str, str] = {}

        def visitor(node: dict, parent: dict | None) -> None:
            if node.get('type') == 'VariableDeclarator':
                initializer = node.get('init')
                name_node = node.get('id')
                if initializer and is_identifier(initializer) and is_identifier(name_node):
                    assignments[name_node['name']] = initializer['name']

        simple_traverse(self.ast, visitor)

        # Resolve transitively: follow chains back to decoder_name
        aliases = set()
        for name, initializer_name in assignments.items():
            # Walk the chain: name -> initializer_name -> ... -> decoder_name?
            seen = set()
            current = initializer_name
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
        body: list,
        array_func_name: str,
        string_array: list[str],
        decoder: Any,
        wrappers: dict,
        decoder_aliases: set[str] | None = None,
        alias_decoder_map: dict | None = None,
        all_decoders: dict | None = None,
    ) -> tuple[int, Any] | None:
        """Find rotation IIFE and execute it.

        Returns (body_index, rotation_call_expr_or_none) on success, or None.
        When the rotation is inside a SequenceExpression, rotation_call_expr is
        the specific sub-expression to remove (not the whole statement).
        """
        for i, statement in enumerate(body):
            if statement.get('type') != 'ExpressionStatement':
                continue
            expression = statement.get('expression')
            if not expression:
                continue

            if expression.get('type') == 'CallExpression':
                if self._try_execute_rotation_call(
                    expression,
                    array_func_name,
                    string_array,
                    decoder,
                    wrappers,
                    decoder_aliases,
                    alias_decoder_map=alias_decoder_map,
                    all_decoders=all_decoders,
                ):
                    return (i, None)

            elif expression.get('type') == 'SequenceExpression':
                for subexpression in expression.get('expressions', []):
                    if subexpression.get('type') != 'CallExpression':
                        continue
                    if self._try_execute_rotation_call(
                        subexpression,
                        array_func_name,
                        string_array,
                        decoder,
                        wrappers,
                        decoder_aliases,
                        alias_decoder_map=alias_decoder_map,
                        all_decoders=all_decoders,
                    ):
                        return (i, subexpression)

        return None

    def _try_execute_rotation_call(
        self,
        call_expr: dict,
        array_func_name: str,
        string_array: list[str],
        decoder: Any,
        wrappers: dict,
        decoder_aliases: set[str] | None,
        alias_decoder_map: dict | None = None,
        all_decoders: dict | None = None,
    ) -> bool:
        """Try to parse and execute a single rotation call expression. Returns True on success."""
        callee = call_expr.get('callee')
        args = call_expr.get('arguments', [])

        if not callee or callee.get('type') != 'FunctionExpression':
            return False
        if len(args) != 2:
            return False
        if not (is_identifier(args[0]) and args[0]['name'] == array_func_name):
            return False

        stop_value = _eval_numeric(args[1])
        if stop_value is None:
            return False
        stop_value = int(stop_value)

        rotation_expr = self._extract_rotation_expression(callee)
        if rotation_expr is None:
            return False

        # Collect local object literals from the rotation IIFE for argument resolution
        self._rotation_locals = self._collect_rotation_locals(callee)

        operation = self._parse_rotation_op(rotation_expr, wrappers, decoder_aliases)
        if operation is None:
            return False

        self._execute_rotation(
            string_array,
            operation,
            wrappers,
            decoder,
            stop_value,
            alias_decoder_map=alias_decoder_map,
        )
        return True

    @staticmethod
    def _collect_rotation_locals(iife_func: dict) -> dict[str, dict]:
        """Collect local object literal assignments from the rotation IIFE.

        Returns dict: var_name -> {prop_name: value}.
        Handles: var J = {A: 0xb9, S: 0xa7, D: 'M8Y&'};
        """
        result = {}
        func_body = iife_func.get('body', {}).get('body', [])
        for statement in func_body:
            if statement.get('type') != 'VariableDeclaration':
                continue
            for declaration in statement.get('declarations', []):
                name_node = declaration.get('id')
                initializer = declaration.get('init')
                if not is_identifier(name_node) or not initializer or initializer.get('type') != 'ObjectExpression':
                    continue
                object_properties = {}
                for property_entry in initializer.get('properties', []):
                    key = property_entry.get('key')
                    value = property_entry.get('value')
                    if not key or not value:
                        continue
                    if is_identifier(key):
                        property_name = key['name']
                    elif is_string_literal(key):
                        property_name = key['value']
                    else:
                        continue
                    numeric_value = _eval_numeric(value)
                    if numeric_value is not None:
                        object_properties[property_name] = int(numeric_value)
                    elif is_string_literal(value):
                        object_properties[property_name] = value['value']
                if object_properties:
                    result[name_node['name']] = object_properties
        return result

    def _extract_rotation_expression(self, iife_func: dict) -> dict | None:
        """Extract the arithmetic expression from the try block in the rotation loop."""
        func_body = iife_func.get('body', {}).get('body', [])
        if not func_body:
            return None

        loop = None
        for statement in func_body:
            if statement.get('type') in ('WhileStatement', 'ForStatement'):
                loop = statement

        if loop is None:
            return None

        loop_body = loop.get('body', {})
        statements = loop_body.get('body', []) if loop_body.get('type') == 'BlockStatement' else [loop_body]

        for statement in statements:
            if statement.get('type') != 'TryStatement':
                continue
            block = statement.get('block', {}).get('body', [])
            if not block:
                continue
            result = self._expression_from_try_block(block[0])
            if result is not None:
                return result
        return None

    @staticmethod
    def _expression_from_try_block(first_statement: dict) -> dict | None:
        """Extract the init/rhs expression from the first statement in a try block."""
        match first_statement.get('type'):
            case 'VariableDeclaration':
                declarations = first_statement.get('declarations', [])
                return declarations[0].get('init') if declarations else None
            case 'ExpressionStatement':
                expression = first_statement.get('expression')
                if expression and expression.get('type') == 'AssignmentExpression':
                    return expression.get('right')
        return None

    def _parse_rotation_op(
        self, expression: dict, wrappers: dict, decoder_aliases: set[str] | None = None
    ) -> dict | None:
        """Parse a rotation expression into an operation tree."""
        if not isinstance(expression, dict):
            return None
        aliases = decoder_aliases or set()

        match expression.get('type', ''):
            case 'Literal' if isinstance(expression.get('value'), (int, float)):
                return {'op': 'literal', 'value': expression['value']}

            case 'UnaryExpression' if expression.get('operator') == '-':
                child = self._parse_rotation_op(expression.get('argument'), wrappers, decoder_aliases)
                return {'op': 'negate', 'child': child} if child else None

            case 'BinaryExpression' if expression.get('operator') in (
                '+',
                '-',
                '*',
                '/',
                '%',
            ):
                left = self._parse_rotation_op(expression.get('left'), wrappers, decoder_aliases)
                right = self._parse_rotation_op(expression.get('right'), wrappers, decoder_aliases)
                if left and right:
                    return {
                        'op': 'binary',
                        'operator': expression['operator'],
                        'left': left,
                        'right': right,
                    }
                return None

            case 'CallExpression':
                return self._parse_parseInt_call(expression, wrappers, aliases)

        return None

    def _parse_parseInt_call(self, expression: dict, wrappers: dict, aliases: set[str]) -> dict | None:
        """Parse parseInt(wrapperOrDecoder(...)) into an operation node."""
        callee = expression.get('callee')
        args = expression.get('arguments', [])
        if not (is_identifier(callee) and callee['name'] == 'parseInt' and len(args) == 1):
            return None
        inner = args[0]
        if inner.get('type') != 'CallExpression':
            return None
        inner_callee = inner.get('callee')
        if not is_identifier(inner_callee):
            return None
        callee_name = inner_callee['name']
        argument_values = []
        for argument in inner.get('arguments', []):
            resolved = self._resolve_rotation_arg(argument)
            if resolved is not None:
                argument_values.append(resolved)
            else:
                return None
        if callee_name in wrappers:
            return {'op': 'call', 'wrapper_name': callee_name, 'args': argument_values}
        if callee_name in aliases:
            return {'op': 'direct_decoder_call', 'alias_name': callee_name, 'args': argument_values}
        return None

    def _resolve_rotation_arg(self, arg: dict) -> int | str | None:
        """Resolve a rotation call argument to a numeric or string value.

        Handles literals, string hex, and MemberExpression referencing local objects.
        """
        numeric_value = _eval_numeric(arg)
        if numeric_value is not None:
            return int(numeric_value)
        if is_string_literal(arg):
            string_value = arg['value']
            try:
                return int(string_value, 16) if string_value.startswith('0x') else int(string_value)
            except (ValueError, TypeError):
                return string_value
        # MemberExpression: J.A or J['A']
        if arg.get('type') == 'MemberExpression':
            object_node = arg.get('object')
            property_node = arg.get('property')
            if is_identifier(object_node) and object_node['name'] in self._rotation_locals:
                local_object = self._rotation_locals[object_node['name']]
                if not arg.get('computed') and is_identifier(property_node):
                    return local_object.get(property_node['name'])
                elif is_string_literal(property_node):
                    return local_object.get(property_node['value'])
        return None

    def _decode_and_parse_int(self, decoder: Any, array_index: int | float, key: str | None = None) -> float:
        """Decode a string at the given index and parse it as an integer."""
        decoded = decoder.get_string(int(array_index), key) if key is not None else decoder.get_string(int(array_index))
        if decoded is None:
            raise ValueError('Decoder returned None')
        result = _js_parse_int(decoded)
        if math.isnan(result):
            raise ValueError('NaN from parseInt')
        return result

    def _apply_rotation_op(
        self, operation: dict, wrappers: dict, decoder: Any, alias_decoder_map: dict | None = None
    ) -> int | float:
        """Evaluate a parsed rotation operation tree."""
        match operation['op']:
            case 'literal':
                return operation['value']
            case 'negate':
                return -self._apply_rotation_op(operation['child'], wrappers, decoder, alias_decoder_map)
            case 'binary':
                left = self._apply_rotation_op(operation['left'], wrappers, decoder, alias_decoder_map)
                right = self._apply_rotation_op(operation['right'], wrappers, decoder, alias_decoder_map)
                return _apply_arith(operation['operator'], left, right)
            case 'call':
                wrapper = wrappers[operation['wrapper_name']]
                call_args = operation['args']
                effective_index = wrapper.get_effective_index(call_args)
                if effective_index is None:
                    raise ValueError('Invalid wrapper args')
                return self._decode_and_parse_int(decoder, effective_index, wrapper.get_key(call_args))
            case 'direct_decoder_call':
                call_args = operation['args']
                if not call_args:
                    raise ValueError('No args for direct decoder call')
                key = call_args[1] if len(call_args) > 1 else None
                # Use alias-specific decoder if available
                alias_name = operation.get('alias_name')
                target_decoder = decoder
                if alias_name and alias_decoder_map and alias_name in alias_decoder_map:
                    target_decoder = alias_decoder_map[alias_name]
                return self._decode_and_parse_int(target_decoder, int(call_args[0]), key)
            case _:
                raise ValueError(f'Unknown op: {operation["op"]}')

    def _execute_rotation(
        self,
        string_array: list[str],
        operation: dict,
        wrappers: dict,
        decoder: Any,
        stop_value: int,
        alias_decoder_map: dict | None = None,
    ) -> bool:
        """Rotate array until the expression evaluates to stop_value."""
        # Collect all decoders that need cache clearing on each rotation
        all_decoders = set()
        all_decoders.add(decoder)
        if alias_decoder_map:
            all_decoders.update(alias_decoder_map.values())

        for _ in range(100001):
            try:
                value = self._apply_rotation_op(operation, wrappers, decoder, alias_decoder_map)
                if int(value) == stop_value:
                    return True
                string_array.append(string_array.pop(0))
            except Exception:
                string_array.append(string_array.pop(0))
            # Clear decoder caches after rotation since array contents shifted
            for decoder_instance in all_decoders:
                if hasattr(decoder_instance, '_cache'):
                    decoder_instance._cache.clear()
        return False

    # ---- Replacement ----

    def _replace_all_wrapper_calls(self, wrappers: dict, decoder: Any, object_literals: dict | None = None) -> bool:
        """Replace all calls to wrapper functions with decoded string literals."""
        if not wrappers:
            return True
        all_replaced = [True]
        resolved_object_literals = object_literals or {}

        def enter(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            if node.get('type') != 'CallExpression':
                return None
            callee = node.get('callee')
            if not is_identifier(callee):
                return None
            if callee['name'] not in wrappers:
                return None

            wrapper = wrappers[callee['name']]
            call_args = node.get('arguments', [])

            # Only need the active param (index) and optionally the key param
            if wrapper.param_index >= len(call_args):
                all_replaced[0] = False
                return None

            index_value = _resolve_arg_value(call_args[wrapper.param_index], resolved_object_literals)
            if index_value is None:
                all_replaced[0] = False
                return None

            effective_index = int(index_value) + wrapper.wrapper_offset

            key = None
            if wrapper.key_param_index is not None and wrapper.key_param_index < len(call_args):
                key = _resolve_string_arg(call_args[wrapper.key_param_index], resolved_object_literals)

            try:
                decoded = (
                    decoder.get_string(int(effective_index), key)
                    if key is not None
                    else decoder.get_string(int(effective_index))
                )
                if isinstance(decoded, str):
                    self.set_changed()
                    return make_literal(decoded)
                all_replaced[0] = False
            except Exception:
                all_replaced[0] = False
            return None

        traverse(self.ast, {'enter': enter})
        return all_replaced[0]

    def _replace_direct_decoder_calls(
        self,
        decoder_name: str,
        decoder: Any,
        decoder_aliases: set[str] | None = None,
        object_literals: dict | None = None,
    ) -> None:
        """Replace direct calls to the decoder function (and its aliases) with literals."""
        names = {decoder_name}
        if decoder_aliases:
            names.update(decoder_aliases)
        resolved_object_literals = object_literals or {}

        def enter(node: dict, parent: dict, key: str, index: int | None) -> dict | None:
            if node.get('type') != 'CallExpression':
                return None
            callee = node.get('callee')
            if not (is_identifier(callee) and callee['name'] in names):
                return None
            args = node.get('arguments', [])
            if not args:
                return None

            first_value = _resolve_arg_value(args[0], resolved_object_literals)
            if first_value is None:
                return None

            key = None
            if len(args) > 1:
                key = _resolve_string_arg(args[1], resolved_object_literals)

            try:
                decoded = (
                    decoder.get_string(int(first_value), key)
                    if key is not None
                    else decoder.get_string(int(first_value))
                )
                if isinstance(decoded, str):
                    self.set_changed()
                    return make_literal(decoded)
            except Exception:
                pass
            return None

        traverse(self.ast, {'enter': enter})

    @staticmethod
    def _find_array_expression_in_statement(statement: dict) -> dict | None:
        """Find the first ArrayExpression node in a variable declaration or assignment."""
        match statement.get('type'):
            case 'VariableDeclaration':
                for declaration in statement.get('declarations', []):
                    initializer = declaration.get('init')
                    if initializer and initializer.get('type') == 'ArrayExpression':
                        return initializer
            case 'ExpressionStatement':
                expression = statement.get('expression')
                if expression and expression.get('type') == 'AssignmentExpression':
                    right_side = expression.get('right')
                    if right_side and right_side.get('type') == 'ArrayExpression':
                        return right_side
        return None

    def _update_ast_array(self, func_node: dict, rotated_array: list[str]) -> None:
        """Update the AST's array function to contain the rotated string array."""
        func_body = func_node.get('body', {}).get('body', [])
        if not func_body:
            return
        array_expression = self._find_array_expression_in_statement(func_body[0])
        if array_expression is not None:
            array_expression['elements'] = [make_literal(value) for value in rotated_array]

    def _remove_body_indices(self, body: list, *indices: int | None) -> None:
        """Remove statements at given indices from body."""
        for body_index in sorted(set(index for index in indices if index is not None), reverse=True):
            if 0 <= body_index < len(body):
                body.pop(body_index)
                self.set_changed()

    # ================================================================
    # Strategy 2b: Var-based string array + rotation IIFE + decoder
    # Pattern:
    #   var _0xARR = ['s1', 's2', ...];
    #   (function(arr, count) { var f = function(n) { while(--n) arr.push(arr.shift()); }; f(++count); })(_0xARR, 0xNN);
    #   var _0xDEC = function(a, b) { a = a - OFFSET; var x = _0xARR[a]; return x; };
    # ================================================================

    def _process_var_array_pattern(self) -> None:
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
        object_literals = _collect_object_literals(self.ast)

        # Step 6: Replace wrapper calls
        self._replace_all_wrapper_calls(wrappers, decoder, object_literals)

        # Step 7: Replace direct decoder calls (including aliases)
        self._replace_direct_decoder_calls(decoder_name, decoder, decoder_aliases, object_literals)

        # Step 8: Remove aliases
        self._remove_decoder_aliases(decoder_name, decoder_aliases)

        # Step 9: Remove infrastructure (array, rotation, decoder)
        if self.has_changed():
            indices_to_remove = {array_idx, decoder_idx}
            if rotation_idx is not None:
                indices_to_remove.add(rotation_idx)
            self._remove_body_indices(body, *indices_to_remove)

    def _find_var_string_array(self, body: list) -> tuple[str | None, list[str] | None, int | None]:
        """Find var _0x... = ['s1', 's2', ...] at top of body."""
        for i, statement in enumerate(body[:3]):
            if statement.get('type') != 'VariableDeclaration':
                continue
            for declaration in statement.get('declarations', []):
                name_node = declaration.get('id')
                if not is_identifier(name_node):
                    continue
                initializer = declaration.get('init')
                if not initializer or initializer.get('type') != 'ArrayExpression':
                    continue
                elements = initializer.get('elements', [])
                if len(elements) < 3:
                    continue
                if not all(is_string_literal(element) for element in elements):
                    continue
                return name_node['name'], [element['value'] for element in elements], i
        return None, None, None

    def _find_simple_rotation(self, body: list, array_name: str) -> tuple[int | None, int | None]:
        """Find (function(arr, count) { ...push/shift... })(array, N) rotation IIFE."""
        for i, statement in enumerate(body):
            if statement.get('type') != 'ExpressionStatement':
                continue
            expression = statement.get('expression')
            if not expression:
                continue

            candidates = []
            if expression.get('type') == 'CallExpression':
                candidates.append(expression)
            elif expression.get('type') == 'SequenceExpression':
                candidates.extend(
                    subexpression
                    for subexpression in expression.get('expressions', [])
                    if subexpression.get('type') == 'CallExpression'
                )

            for call_expr in candidates:
                callee = call_expr.get('callee')
                args = call_expr.get('arguments', [])
                if not callee or callee.get('type') != 'FunctionExpression':
                    continue
                if len(args) != 2:
                    continue
                if not (is_identifier(args[0]) and args[0]['name'] == array_name):
                    continue

                count_value = _eval_numeric(args[1])
                if count_value is None:
                    continue

                source = generate(callee)
                if 'push' in source and 'shift' in source:
                    return i, int(count_value)

        return None, None

    def _find_var_decoder(self, body: list, array_name: str) -> tuple[str | None, int | None, int | None]:
        """Find var _0xDEC = function(a) { a = a - OFFSET; var x = ARR[a]; return x; }."""
        for i, statement in enumerate(body):
            if statement.get('type') != 'VariableDeclaration':
                continue
            for declaration in statement.get('declarations', []):
                name_node = declaration.get('id')
                if not is_identifier(name_node):
                    continue
                initializer = declaration.get('init')
                if not initializer or initializer.get('type') != 'FunctionExpression':
                    continue
                source = generate(initializer)
                if array_name not in source:
                    continue
                offset = self._extract_decoder_offset(initializer)
                return name_node['name'], offset, i
        return None, None, None

    # ================================================================
    # Strategy 1: Direct string array declarations
    # ================================================================

    def _try_replace_array_access(self, ref_parent: dict | None, ref_key: str, string_array: list[str]) -> None:
        """Replace arr[N] member expression with the string literal if valid."""
        if not ref_parent or ref_parent.get('type') != 'MemberExpression':
            return
        if ref_key != 'object' or not ref_parent.get('computed'):
            return
        property_node = ref_parent.get('property')
        if not is_numeric_literal(property_node):
            return
        array_index = int(property_node['value'])
        if not (0 <= array_index < len(string_array)):
            return
        self._replace_node_in_ast(ref_parent, make_literal(string_array[array_index]))
        self.set_changed()

    def _process_direct_arrays(self, scope_tree: Any) -> None:
        """Find direct array declarations and replace indexed accesses."""
        for name, binding in list(scope_tree.bindings.items()):
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            initializer = node.get('init')
            if not initializer or initializer.get('type') != 'ArrayExpression':
                continue
            elements = initializer.get('elements', [])
            if not elements or not all(is_string_literal(element) for element in elements):
                continue

            string_array = [element['value'] for element in elements]
            for reference_node, reference_parent, reference_key, ref_index in binding.references[:]:
                self._try_replace_array_access(reference_parent, reference_key, string_array)
            for child in scope_tree.children:
                self._process_direct_arrays_in_scope(child, name, string_array)

    def _process_direct_arrays_in_scope(self, scope: Any, name: str, string_array: list[str]) -> None:
        """Process direct array accesses in child scopes."""
        binding = scope.get_binding(name)
        if not binding:
            return
        for reference_node, reference_parent, reference_key, ref_index in binding.references[:]:
            self._try_replace_array_access(reference_parent, reference_key, string_array)

    def _replace_node_in_ast(self, target: dict, replacement: dict) -> None:
        """Replace a node in the AST with a replacement."""
        result = self.find_parent(target)
        if result:
            parent, key, index = result
            if index is not None:
                parent[key][index] = replacement
            else:
                parent[key] = replacement
            self.invalidate_parent_map()

    # ================================================================
    # Strategy 3: Simple static array unpacking
    # ================================================================

    def _process_static_arrays(self) -> None:
        """No-op: static array unpacking is handled by _process_direct_arrays."""
        pass
