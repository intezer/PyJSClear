"""Resolve class static property accesses and inline static identity methods.

Handles two patterns common in esbuild-bundled obfuscated code:

1. Static constant propagation:
     var C = class {}; C.X = 100;
     ... C.X + 1 ...   →   ... 100 + 1 ...

2. Static identity method inlining:
     var C = class { static id(x) { return x; } };
     ... C.id(expr) ...   →   ... expr ...
"""

from ..traverser import find_parent
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import replace_identifiers
from .base import Transform


class ClassStaticResolver(Transform):
    """Inline class static constant properties and identity methods."""

    def execute(self):
        # Step 1: Find class variables (var X = class { ... })
        class_vars = {}  # name -> ClassExpression node

        def find_classes(node, parent):
            if node.get('type') != 'VariableDeclarator':
                return
            init = node.get('init')
            if not init or init.get('type') != 'ClassExpression':
                return
            decl_id = node.get('id')
            if decl_id and is_identifier(decl_id):
                class_vars[decl_id['name']] = init

        simple_traverse(self.ast, find_classes)

        if not class_vars:
            return False

        # Step 2: Collect static properties assigned after class definition
        # Pattern: ClassName.prop = literal;
        static_props = {}  # (class_name, prop_name) -> value node
        # Track properties that are reassigned (not safe to inline)
        assigned_props = set()  # (class_name, prop_name)

        def collect_static_props(node, parent):
            if node.get('type') != 'AssignmentExpression' or node.get('operator') != '=':
                return
            left = node.get('left')
            if not left or left.get('type') != 'MemberExpression':
                return
            obj = left.get('object')
            if not obj or not is_identifier(obj):
                return
            obj_name = obj['name']
            if obj_name not in class_vars:
                return
            prop = left.get('property')
            if not prop:
                return
            if left.get('computed'):
                if not is_string_literal(prop):
                    return
                prop_name = prop['value']
            elif is_identifier(prop):
                prop_name = prop['name']
            else:
                return
            key = (obj_name, prop_name)
            value = node.get('right')
            if key in static_props:
                # Reassigned — not safe to inline
                assigned_props.add(key)
            elif value and is_literal(value):
                static_props[key] = value

        simple_traverse(self.ast, collect_static_props)

        # Remove reassigned props
        for key in assigned_props:
            static_props.pop(key, None)

        # Step 3: Collect static methods from class body
        # Pattern: static methodName(x) { return x; }  (identity function)
        static_methods = {}  # (class_name, method_name) -> method node

        for class_name, class_node in class_vars.items():
            body = class_node.get('body')
            if not body or body.get('type') != 'ClassBody':
                continue
            for member in body.get('body', []):
                if member.get('type') != 'MethodDefinition':
                    continue
                if not member.get('static'):
                    continue
                key = member.get('key')
                if not key or not is_identifier(key):
                    continue
                method_name = key['name']
                value = member.get('value')
                if not value:
                    continue
                if self._is_identity_function(value):
                    static_methods[(class_name, method_name)] = value

        if not static_props and not static_methods:
            return False

        # Step 4: Replace accesses
        def enter(node, parent, key, index):
            if node.get('type') != 'MemberExpression':
                return
            obj = node.get('object')
            if not obj or not is_identifier(obj):
                return
            obj_name = obj['name']
            if obj_name not in class_vars:
                return
            prop_name = self._get_prop_name(node)
            if prop_name is None:
                return

            pair = (obj_name, prop_name)

            # Skip if this is the LHS of an assignment (definition site)
            if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
                return

            # Try constant propagation
            if pair in static_props:
                replacement = deep_copy(static_props[pair])
                self._replace_in_parent(node, replacement, parent, key, index)
                self.set_changed()
                return replacement

            # Try identity method inlining
            if pair in static_methods:
                self._try_inline_identity(node, static_methods[pair])

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _get_prop_name(self, member_expr):
        """Get the property name from a MemberExpression."""
        prop = member_expr.get('property')
        if not prop:
            return None
        if member_expr.get('computed'):
            if is_string_literal(prop):
                return prop['value']
            return None
        if is_identifier(prop):
            return prop['name']
        return None

    def _is_identity_function(self, func_node):
        """Check if a function simply returns its first argument."""
        params = func_node.get('params', [])
        if len(params) != 1:
            return False
        param = params[0]
        if not is_identifier(param):
            return False
        body = func_node.get('body')
        if not body or body.get('type') != 'BlockStatement':
            return False
        stmts = body.get('body', [])
        if len(stmts) != 1 or stmts[0].get('type') != 'ReturnStatement':
            return False
        arg = stmts[0].get('argument')
        if not arg or not is_identifier(arg):
            return False
        return arg['name'] == param['name']

    def _try_inline_identity(self, member_expr, method_node):
        """Inline Class.identity(arg) → arg."""
        result = find_parent(self.ast, member_expr)
        if not result:
            return
        call_parent, call_key, call_index = result
        if not call_parent or call_parent.get('type') != 'CallExpression' or call_key != 'callee':
            return
        args = call_parent.get('arguments', [])
        if len(args) != 1:
            return
        replacement = deep_copy(args[0])
        # Replace the CallExpression with the argument
        grandparent_result = find_parent(self.ast, call_parent)
        if not grandparent_result:
            return
        gp, gp_key, gp_index = grandparent_result
        self._replace_in_parent(call_parent, replacement, gp, gp_key, gp_index)
        self.set_changed()

    def _replace_in_parent(self, target, replacement, parent, key, index):
        """Replace target node in the AST using known parent info."""
        if index is not None:
            parent[key][index] = replacement
        else:
            parent[key] = replacement
