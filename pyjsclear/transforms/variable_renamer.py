"""Rename obfuscated _0x-prefixed identifiers to readable names.

Uses heuristic analysis of how variables are initialized and used to
pick meaningful names (e.g. require("fs") → fs, loop counter → i).
Falls back to sequential short names (a, b, c, ...) when no heuristic matches.

Only renames bindings tracked by scope analysis — free variables and
globals are left untouched.
"""

import re

from ..scope import build_scope_tree
from ..traverser import simple_traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


_OBF_RE = re.compile(r'^_0x[0-9a-fA-F]+$')

_JS_RESERVED = frozenset({
    'abstract', 'arguments', 'await', 'boolean', 'break', 'byte', 'case',
    'catch', 'char', 'class', 'const', 'continue', 'debugger', 'default',
    'delete', 'do', 'double', 'else', 'enum', 'eval', 'export', 'extends',
    'false', 'final', 'finally', 'float', 'for', 'function', 'goto', 'if',
    'implements', 'import', 'in', 'instanceof', 'int', 'interface', 'let',
    'long', 'native', 'new', 'null', 'package', 'private', 'protected',
    'public', 'return', 'short', 'static', 'super', 'switch', 'synchronized',
    'this', 'throw', 'throws', 'transient', 'true', 'try', 'typeof', 'var',
    'void', 'volatile', 'while', 'with', 'yield', 'undefined', 'NaN',
    'Infinity',
})

# Maps require("module") → preferred variable name
_REQUIRE_NAMES = {
    'fs': 'fs',
    'path': 'path',
    'os': 'os',
    'http': 'http',
    'https': 'https',
    'url': 'url',
    'crypto': 'crypto',
    'child_process': 'cp',
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
    'querystring': 'qs',
    'node-fetch': 'fetch',
    'axios': 'axios',
    'express': 'express',
}

# Maps constructor name → preferred variable name
_CONSTRUCTOR_NAMES = {
    'Date': 'date',
    'RegExp': 'regex',
    'Error': 'err',
    'TypeError': 'err',
    'RangeError': 'err',
    'Map': 'map',
    'Set': 'set',
    'WeakMap': 'wm',
    'WeakSet': 'ws',
    'Promise': 'promise',
    'Uint8Array': 'bytes',
    'ArrayBuffer': 'buf',
    'URLSearchParams': 'params',
    'URL': 'url',
    'FormData': 'form',
}


def _name_generator(reserved):
    """Yield short identifier names, skipping reserved and taken names."""
    for c in 'abcdefghijklmnopqrstuvwxyz':
        if c not in reserved:
            yield c
    for c1 in 'abcdefghijklmnopqrstuvwxyz':
        for c2 in 'abcdefghijklmnopqrstuvwxyz':
            name = c1 + c2
            if name not in reserved:
                yield name
    for c1 in 'abcdefghijklmnopqrstuvwxyz':
        for c2 in 'abcdefghijklmnopqrstuvwxyz':
            for c3 in 'abcdefghijklmnopqrstuvwxyz':
                name = c1 + c2 + c3
                if name not in reserved:
                    yield name


def _dedupe_name(base, reserved):
    """Return base or base2, base3, ... until a non-reserved name is found."""
    if base not in reserved:
        return base
    n = 2
    while True:
        candidate = f'{base}{n}'
        if candidate not in reserved:
            return candidate
        n += 1


def _infer_from_init(init):
    """Infer a variable name from its initializer expression."""
    if not isinstance(init, dict) or 'type' not in init:
        return None

    init_type = init.get('type')

    # require("fs") → "fs"
    if init_type == 'CallExpression':
        callee = init.get('callee')
        args = init.get('arguments', [])
        if is_identifier(callee) and callee.get('name') == 'require' and len(args) == 1:
            arg = args[0]
            if arg.get('type') == 'Literal' and isinstance(arg.get('value'), str):
                mod = arg['value']
                if mod in _REQUIRE_NAMES:
                    return _REQUIRE_NAMES[mod]
                # Derive name from module path, sanitized to valid identifier
                base = mod.split('/')[-1].split('\\')[-1]
                base = base.split('.')[0]  # strip file extension
                base = re.sub(r'[^a-zA-Z0-9_]', '_', base)
                base = re.sub(r'^[0-9]+', '', base)  # can't start with digit
                base = base.strip('_')
                if base and base not in _JS_RESERVED:
                    return base
                return None  # fall through to other heuristics

        # Buffer.from(...) → "buf"
        if callee and callee.get('type') == 'MemberExpression':
            obj = callee.get('object')
            prop = callee.get('property')
            if is_identifier(obj) and is_identifier(prop):
                obj_name = obj.get('name')
                prop_name = prop.get('name')
                if obj_name == 'Buffer' and prop_name == 'from':
                    return 'buf'
                if obj_name == 'JSON' and prop_name == 'parse':
                    return 'data'
                if obj_name == 'JSON' and prop_name == 'stringify':
                    return 'json'
                if obj_name == 'Object' and prop_name == 'keys':
                    return 'keys'
                if obj_name == 'Object' and prop_name == 'values':
                    return 'values'
                if obj_name == 'Object' and prop_name == 'entries':
                    return 'entries'
                if obj_name == 'Object' and prop_name == 'getOwnPropertyNames':
                    return 'keys'

    # new Date() → "date"
    if init_type == 'NewExpression':
        callee = init.get('callee')
        if is_identifier(callee):
            return _CONSTRUCTOR_NAMES.get(callee.get('name'))
        # new require("url").URLSearchParams() → "params"
        if callee and callee.get('type') == 'MemberExpression':
            prop = callee.get('property')
            if is_identifier(prop):
                return _CONSTRUCTOR_NAMES.get(prop.get('name'))

    # [] → "arr"
    if init_type == 'ArrayExpression':
        return 'arr'

    # {} → "obj"
    if init_type == 'ObjectExpression':
        return 'obj'

    # "string" → "str"
    if init_type == 'Literal':
        val = init.get('value')
        if isinstance(val, str):
            return 'str'
        if isinstance(val, bool):
            return 'flag'

    # await expr → infer from the inner expression
    if init_type == 'AwaitExpression':
        return _infer_from_init(init.get('argument'))

    return None


def _infer_from_usage(binding):
    """Infer a variable name from how it's used at reference sites."""
    # Check what methods are called on this variable
    methods = set()
    for ref_node, ref_parent, ref_key, ref_index in binding.references:
        if not ref_parent:
            continue
        # x.method() — ref is object of MemberExpression
        if ref_parent.get('type') == 'MemberExpression' and ref_key == 'object':
            prop = ref_parent.get('property')
            if is_identifier(prop) and not ref_parent.get('computed'):
                methods.add(prop.get('name'))

    # fs-like methods
    _FS_METHODS = {'readFileSync', 'writeFileSync', 'existsSync', 'mkdirSync',
                   'statSync', 'readdirSync', 'unlinkSync', 'createWriteStream',
                   'createReadStream', 'readFile', 'writeFile', 'appendFileSync'}
    if methods & _FS_METHODS:
        return 'fs'

    # path-like methods
    _PATH_METHODS = {'join', 'resolve', 'basename', 'dirname', 'extname', 'normalize'}
    if methods & _PATH_METHODS and not (methods - _PATH_METHODS - {'sep'}):
        return 'path'

    # process-like
    if 'env' in methods or 'exit' in methods or 'cwd' in methods:
        return 'proc'

    # child_process-like
    if methods & {'spawn', 'exec', 'execSync', 'fork'}:
        return 'cp'

    # http/https-like
    if methods & {'get', 'request', 'createServer'} and 'statusCode' not in methods:
        return None  # too ambiguous

    # response-like
    if methods & {'statusCode', 'headers', 'pipe'}:
        return 'res'

    # error-like
    if 'message' in methods and 'stack' in methods:
        return 'err'

    return None


def _infer_loop_var(binding):
    """Check if this binding is a for-loop counter."""
    node = binding.node
    if not isinstance(node, dict):
        return None
    # For var/let declarations, check if the VariableDeclarator is inside a ForStatement init
    if node.get('type') != 'VariableDeclarator':
        return None
    init = node.get('init')
    if not init or init.get('type') != 'Literal':
        return None
    val = init.get('value')
    if not isinstance(val, (int, float)):
        return None
    # Check if any assignment is an UpdateExpression (i++, i--)
    if binding.assignments:
        for assign in binding.assignments:
            if isinstance(assign, dict) and assign.get('type') == 'UpdateExpression':
                return True
    # Also check references for UpdateExpression parents
    for ref_node, ref_parent, ref_key, ref_index in binding.references:
        if ref_parent and ref_parent.get('type') == 'UpdateExpression':
            return True
    return None


class VariableRenamer(Transform):
    """Rename _0x-prefixed identifiers to readable names using heuristics."""

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)

        # Collect all non-obfuscated names across the entire tree to avoid conflicts
        reserved = set(_JS_RESERVED)
        self._collect_reserved(scope_tree, reserved)

        # Rename bindings scope by scope
        gen = _name_generator(reserved)
        # Track loop var counter for i, j, k assignment
        self._loop_counter = iter('ijklmn')
        self._rename_scope(scope_tree, gen, reserved)
        return self.has_changed()

    def _collect_reserved(self, scope, reserved):
        """Collect all non-_0x binding names so we never generate a conflict."""
        for name in scope.bindings:
            if not _OBF_RE.match(name):
                reserved.add(name)
        for child in scope.children:
            self._collect_reserved(child, reserved)

    def _rename_scope(self, scope, gen, reserved):
        """Rename all _0x bindings in this scope and its children."""
        for name, binding in list(scope.bindings.items()):
            if not _OBF_RE.match(name):
                continue

            new_name = self._pick_name(binding, gen, reserved)
            reserved.add(new_name)
            self._apply_rename(binding, new_name)
            self.set_changed()

        for child in scope.children:
            self._rename_scope(child, gen, reserved)

    def _pick_name(self, binding, gen, reserved):
        """Pick the best name for a binding using heuristics, with fallback."""
        # 1. Check if it's a loop counter → i, j, k
        if _infer_loop_var(binding):
            for letter in self._loop_counter:
                candidate = _dedupe_name(letter, reserved)
                if candidate not in reserved:
                    return candidate

        # 2. Check init expression (require, new, [], {}, etc.)
        if binding.kind in ('var', 'let', 'const'):
            node = binding.node
            if isinstance(node, dict) and node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                hint = _infer_from_init(init)
                if hint:
                    return _dedupe_name(hint, reserved)

        # 3. Check usage patterns (what methods are called on it)
        hint = _infer_from_usage(binding)
        if hint:
            return _dedupe_name(hint, reserved)

        # 4. For catch clause params, use "err"
        if binding.kind == 'param':
            # Check if this is a catch param by looking at context
            node = binding.node
            if isinstance(node, dict) and node.get('type') == 'Identifier':
                # We can't easily tell from scope alone, but catch params typically
                # have names like _0x... and are rarely used — try "err"
                pass  # Fall through to sequential

        # 5. Fallback: sequential name from generator
        return next(gen)

    def _apply_rename(self, binding, new_name):
        """Rename a binding at its declaration site and all reference sites."""
        old_name = binding.name

        # 1. Rename at declaration site
        node = binding.node
        if isinstance(node, dict):
            kind = binding.kind
            if kind in ('var', 'let', 'const'):
                decl_id = node.get('id')
                if decl_id and decl_id.get('type') == 'Identifier' and decl_id.get('name') == old_name:
                    decl_id['name'] = new_name
            elif kind == 'function':
                func_id = node.get('id')
                if func_id and func_id.get('type') == 'Identifier' and func_id.get('name') == old_name:
                    func_id['name'] = new_name
            elif kind == 'param':
                if node.get('type') == 'Identifier' and node.get('name') == old_name:
                    node['name'] = new_name
                elif node.get('type') == 'AssignmentPattern':
                    left = node.get('left')
                    if left and left.get('type') == 'Identifier' and left.get('name') == old_name:
                        left['name'] = new_name

        # 2. Rename at all reference sites
        for ref_node, ref_parent, ref_key, ref_index in binding.references:
            if ref_node.get('type') == 'Identifier' and ref_node.get('name') == old_name:
                ref_node['name'] = new_name

        # 3. Update binding.name
        binding.name = new_name
