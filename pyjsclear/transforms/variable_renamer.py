"""Rename obfuscated _0x-prefixed identifiers to readable names.

Uses heuristic analysis of how variables are initialized and used to
pick meaningful names (e.g. require("fs") -> fs, loop counter -> i).
Falls back to sequential short names (a, b, c, ...) when no heuristic matches.

Only renames bindings tracked by scope analysis -- free variables and
globals are left untouched.
"""

from __future__ import annotations

import re
from collections.abc import Generator
from typing import TYPE_CHECKING

from ..scope import build_scope_tree
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


if TYPE_CHECKING:
    from ..scope import Binding
    from ..scope import Scope


_OBFUSCATED_PATTERN = re.compile(r'^_0x[0-9a-fA-F]+$')

_JS_RESERVED = frozenset(
    {
        'abstract',
        'arguments',
        'await',
        'boolean',
        'break',
        'byte',
        'case',
        'catch',
        'char',
        'class',
        'const',
        'continue',
        'debugger',
        'default',
        'delete',
        'do',
        'double',
        'else',
        'enum',
        'eval',
        'export',
        'extends',
        'false',
        'final',
        'finally',
        'float',
        'for',
        'function',
        'goto',
        'if',
        'implements',
        'import',
        'in',
        'instanceof',
        'int',
        'interface',
        'let',
        'long',
        'native',
        'new',
        'null',
        'package',
        'private',
        'protected',
        'public',
        'return',
        'short',
        'static',
        'super',
        'switch',
        'synchronized',
        'this',
        'throw',
        'throws',
        'transient',
        'true',
        'try',
        'typeof',
        'var',
        'void',
        'volatile',
        'while',
        'with',
        'yield',
        'undefined',
        'NaN',
        'Infinity',
    }
)

# Maps require('module') to preferred variable name
_REQUIRE_NAMES: dict[str, str] = {
    'fs': 'fs',
    'path': 'path',
    'os': 'os',
    'http': 'http',
    'https': 'https',
    'url': 'url',
    'crypto': 'crypto',
    'child_process': 'child_proc',
    'process': 'proc',
    'net': 'net',
    'dns': 'dns',
    'tls': 'tls',
    'zlib': 'zlib',
    'stream': 'stream',
    'events': 'events',
    'util': 'util',
    'buffer': 'buffer',
    'assert': 'assert',
    'querystring': 'query_string',
    'node-fetch': 'fetch',
    'axios': 'axios',
    'express': 'express',
}

# Maps constructor name to preferred variable name
_CONSTRUCTOR_NAMES: dict[str, str] = {
    'Date': 'date',
    'RegExp': 'regex',
    'Error': 'error',
    'TypeError': 'error',
    'RangeError': 'error',
    'Map': 'map',
    'Set': 'set',
    'WeakMap': 'weak_map',
    'WeakSet': 'weak_set',
    'Promise': 'promise',
    'Uint8Array': 'bytes',
    'ArrayBuffer': 'buffer',
    'URLSearchParams': 'params',
    'URL': 'url',
    'FormData': 'form',
}

# fs-like methods
_FS_METHODS: set[str] = {
    'readFileSync',
    'writeFileSync',
    'existsSync',
    'mkdirSync',
    'statSync',
    'readdirSync',
    'unlinkSync',
    'createWriteStream',
    'createReadStream',
    'readFile',
    'writeFile',
    'appendFileSync',
}

# path-like methods
_PATH_METHODS: set[str] = {'join', 'resolve', 'basename', 'dirname', 'extname', 'normalize'}

_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def _name_generator(reserved_names: set[str]) -> Generator[str, None, None]:
    """Yield short identifier names, skipping reserved and taken names."""
    for character in _ALPHABET:
        if character not in reserved_names:
            yield character
    for first_character in _ALPHABET:
        for second_character in _ALPHABET:
            name = first_character + second_character
            if name not in reserved_names:
                yield name
    for first_character in _ALPHABET:
        for second_character in _ALPHABET:
            for third_character in _ALPHABET:
                name = first_character + second_character + third_character
                if name not in reserved_names:
                    yield name


def _dedupe_name(base_name: str, reserved_names: set[str]) -> str:
    """Return base_name or base_name2, base_name3, ... until a non-reserved name is found."""
    if base_name not in reserved_names:
        return base_name
    counter = 2
    while True:
        candidate = f'{base_name}{counter}'
        if candidate not in reserved_names:
            return candidate
        counter += 1


def _infer_from_init(initializer: dict | None) -> str | None:
    """Infer a variable name from its initializer expression."""
    if not isinstance(initializer, dict) or 'type' not in initializer:
        return None

    initializer_type = initializer.get('type')

    # require('fs') -> 'fs'
    if initializer_type == 'CallExpression':
        callee = initializer.get('callee')
        arguments = initializer.get('arguments', [])
        if is_identifier(callee) and callee.get('name') == 'require' and len(arguments) == 1:
            argument = arguments[0]
            if argument.get('type') == 'Literal' and isinstance(argument.get('value'), str):
                module_name = argument['value']
                if module_name in _REQUIRE_NAMES:
                    return _REQUIRE_NAMES[module_name]
                # Derive name from module path, sanitized to valid identifier
                base_name = module_name.split('/')[-1].split('\\')[-1]
                base_name = base_name.split('.')[0]
                base_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
                base_name = re.sub(r'^[0-9]+', '', base_name)
                base_name = base_name.strip('_')
                if base_name and base_name not in _JS_RESERVED:
                    return base_name
                return None

        # Buffer.from(...) -> 'buffer'
        if callee and callee.get('type') == 'MemberExpression':
            object_node = callee.get('object')
            property_node = callee.get('property')
            if is_identifier(object_node) and is_identifier(property_node):
                object_name = object_node.get('name')
                property_name = property_node.get('name')
                match (object_name, property_name):
                    case ('Buffer', 'from'):
                        return 'buffer'
                    case ('JSON', 'parse'):
                        return 'data'
                    case ('JSON', 'stringify'):
                        return 'json'
                    case ('Object', 'keys') | ('Object', 'getOwnPropertyNames'):
                        return 'keys'
                    case ('Object', 'values'):
                        return 'values'
                    case ('Object', 'entries'):
                        return 'entries'

    # new Date() -> 'date'
    if initializer_type == 'NewExpression':
        callee = initializer.get('callee')
        if is_identifier(callee):
            return _CONSTRUCTOR_NAMES.get(callee.get('name'))
        # new require('url').URLSearchParams() -> 'params'
        if callee and callee.get('type') == 'MemberExpression':
            property_node = callee.get('property')
            if is_identifier(property_node):
                return _CONSTRUCTOR_NAMES.get(property_node.get('name'))

    match initializer_type:
        case 'ArrayExpression':
            return 'array'
        case 'ObjectExpression':
            return 'object'
        case 'Literal':
            value = initializer.get('value')
            if isinstance(value, str):
                return 'string'
            if isinstance(value, bool):
                return 'flag'
        case 'AwaitExpression':
            return _infer_from_init(initializer.get('argument'))

    return None


def _infer_from_usage(binding: Binding) -> str | None:
    """Infer a variable name from how it is used at reference sites."""
    # Check what methods are called on this variable
    methods: set[str] = set()
    for reference_node, reference_parent, reference_key, _reference_index in binding.references:
        if not reference_parent:
            continue
        # variable.method() -- reference is object of MemberExpression
        if reference_parent.get('type') == 'MemberExpression' and reference_key == 'object':
            property_node = reference_parent.get('property')
            if is_identifier(property_node) and not reference_parent.get('computed'):
                methods.add(property_node.get('name'))

    if methods & _FS_METHODS:
        return 'fs'

    if methods & _PATH_METHODS and not (methods - _PATH_METHODS - {'sep'}):
        return 'path'

    # process-like
    if 'env' in methods or 'exit' in methods or 'cwd' in methods:
        return 'proc'

    # child_process-like
    if methods & {'spawn', 'exec', 'execSync', 'fork'}:
        return 'child_proc'

    # http/https-like (too ambiguous)
    if methods & {'get', 'request', 'createServer'} and 'statusCode' not in methods:
        return None

    # response-like
    if methods & {'statusCode', 'headers', 'pipe'}:
        return 'response'

    # error-like
    if 'message' in methods and 'stack' in methods:
        return 'error'

    return None


def _infer_loop_var(binding: Binding) -> bool | None:
    """Check if this binding is a for-loop counter."""
    node = binding.node
    if not isinstance(node, dict):
        return None
    if node.get('type') != 'VariableDeclarator':
        return None
    initializer = node.get('init')
    if not initializer or initializer.get('type') != 'Literal':
        return None
    value = initializer.get('value')
    if not isinstance(value, (int, float)):
        return None
    # Check if any assignment is an UpdateExpression (i++, i--)
    if binding.assignments:
        for assignment in binding.assignments:
            if isinstance(assignment, dict) and assignment.get('type') == 'UpdateExpression':
                return True
    # Also check references for UpdateExpression parents
    for _reference_node, reference_parent, _reference_key, _reference_index in binding.references:
        if reference_parent and reference_parent.get('type') == 'UpdateExpression':
            return True
    return None


def _collect_pattern_identifiers(pattern: dict | None, result: list[dict]) -> None:
    """Collect all Identifier nodes from a destructuring pattern."""
    if not isinstance(pattern, dict):
        return
    match pattern.get('type'):
        case 'Identifier':
            result.append(pattern)
        case 'ArrayPattern':
            for element in pattern.get('elements', []):
                if element:
                    _collect_pattern_identifiers(element, result)
        case 'ObjectPattern':
            for property_node in pattern.get('properties', []):
                value = property_node.get('value', property_node.get('argument'))
                if value:
                    _collect_pattern_identifiers(value, result)
        case 'RestElement':
            _collect_pattern_identifiers(pattern.get('argument'), result)
        case 'AssignmentPattern':
            _collect_pattern_identifiers(pattern.get('left'), result)


class VariableRenamer(Transform):
    """Rename _0x-prefixed identifiers to readable names using heuristics."""

    rebuild_scope = True

    def execute(self) -> bool:
        """Run the renaming transform on the AST, returning True if any changes were made."""
        if self.scope_tree is not None:
            scope_tree = self.scope_tree
        else:
            scope_tree, _ = build_scope_tree(self.ast)

        # Collect all non-obfuscated names across the entire tree to avoid conflicts
        reserved_names: set[str] = set(_JS_RESERVED)
        self._collect_reserved_names(scope_tree, reserved_names)

        # Rename bindings scope by scope
        generator = _name_generator(reserved_names)
        # Track loop var counter for i, j, k assignment
        self._loop_letters: list[str] = list('ijklmn')
        self._loop_index: int = 0
        self._rename_scope(scope_tree, generator, reserved_names)

        # Fix duplicate names in destructuring patterns (from broken obfuscated input)
        self._fix_destructuring_dupes(reserved_names)

        return self.has_changed()

    def _collect_reserved_names(self, scope: Scope, reserved_names: set[str]) -> None:
        """Collect all non-_0x binding names so we never generate a conflict."""
        for name in scope.bindings:
            if not _OBFUSCATED_PATTERN.match(name):
                reserved_names.add(name)
        for child_scope in scope.children:
            self._collect_reserved_names(child_scope, reserved_names)

    def _rename_scope(
        self,
        scope: Scope,
        generator: Generator[str, None, None],
        reserved_names: set[str],
    ) -> None:
        """Rename all _0x bindings in this scope and its children."""
        for name, binding in list(scope.bindings.items()):
            if not _OBFUSCATED_PATTERN.match(name):
                continue

            new_name = self._pick_name(binding, generator, reserved_names)
            reserved_names.add(new_name)
            self._apply_rename(binding, new_name)
            self.set_changed()

        for child_scope in scope.children:
            self._rename_scope(child_scope, generator, reserved_names)

    def _pick_name(
        self,
        binding: Binding,
        generator: Generator[str, None, None],
        reserved_names: set[str],
    ) -> str:
        """Pick the best name for a binding using heuristics, with fallback."""
        # 1. Check if it is a loop counter -> i, j, k
        if _infer_loop_var(binding):
            while self._loop_index < len(self._loop_letters):
                letter = self._loop_letters[self._loop_index]
                self._loop_index += 1
                candidate = _dedupe_name(letter, reserved_names)
                if candidate not in reserved_names:
                    return candidate

        # 2. Check init expression (require, new, [], {}, etc.)
        if binding.kind in ('var', 'let', 'const'):
            node = binding.node
            if isinstance(node, dict) and node.get('type') == 'VariableDeclarator':
                initializer = node.get('init')
                hint = _infer_from_init(initializer)
                if hint:
                    return _dedupe_name(hint, reserved_names)

        # 3. Check usage patterns (what methods are called on it)
        hint = _infer_from_usage(binding)
        if hint:
            return _dedupe_name(hint, reserved_names)

        # 4. For catch clause params, use 'error'
        if binding.kind == 'param':
            node = binding.node
            if isinstance(node, dict) and node.get('type') == 'Identifier':
                # Catch params typically have _0x... names and are rarely used
                pass

        # 5. Fallback: sequential name from generator
        return next(generator)

    def _apply_rename(self, binding: Binding, new_name: str) -> None:
        """Rename a binding at its declaration site and all reference sites."""
        old_name = binding.name

        # Rename at declaration site
        node = binding.node
        if isinstance(node, dict):
            match binding.kind:
                case 'var' | 'let' | 'const':
                    declaration_id = node.get('id')
                    if (
                        declaration_id
                        and declaration_id.get('type') == 'Identifier'
                        and declaration_id.get('name') == old_name
                    ):
                        declaration_id['name'] = new_name
                case 'function':
                    function_id = node.get('id')
                    if function_id and function_id.get('type') == 'Identifier' and function_id.get('name') == old_name:
                        function_id['name'] = new_name
                case 'param':
                    match node.get('type'):
                        case 'Identifier' if node.get('name') == old_name:
                            node['name'] = new_name
                        case 'AssignmentPattern':
                            left_node = node.get('left')
                            if (
                                left_node
                                and left_node.get('type') == 'Identifier'
                                and left_node.get('name') == old_name
                            ):
                                left_node['name'] = new_name
                        case 'RestElement':
                            argument_node = node.get('argument')
                            if (
                                argument_node
                                and argument_node.get('type') == 'Identifier'
                                and argument_node.get('name') == old_name
                            ):
                                argument_node['name'] = new_name

        # Rename at all reference sites
        for reference_node, _reference_parent, _reference_key, _reference_index in binding.references:
            if reference_node.get('type') == 'Identifier' and reference_node.get('name') == old_name:
                reference_node['name'] = new_name

        # Update binding.name
        binding.name = new_name

    def _fix_destructuring_dupes(self, reserved_names: set[str]) -> None:
        """Fix duplicate identifier names in destructuring patterns.

        Obfuscators sometimes produce invalid code like `const [a, a, a] = x;`.
        This walks the AST and renames duplicates within each pattern.

        Note: this mutates AST nodes directly without updating scope bindings,
        so scope data is stale after this point. This is fine since it runs as
        the last step of the renamer post-pass.
        """

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            if node.get('type') != 'VariableDeclarator':
                return
            pattern = node.get('id')
            if not pattern or pattern.get('type') not in ('ArrayPattern', 'ObjectPattern'):
                return
            identifiers: list[dict] = []
            _collect_pattern_identifiers(pattern, identifiers)
            seen_names: dict[str, dict] = {}
            for identifier_node in identifiers:
                name = identifier_node.get('name')
                if name in seen_names:
                    # Duplicate -- assign a unique name
                    unique_name = _dedupe_name(name, reserved_names)
                    reserved_names.add(unique_name)
                    identifier_node['name'] = unique_name
                    self.set_changed()
                else:
                    seen_names[name] = identifier_node

        traverse(self.ast, {'enter': enter})
