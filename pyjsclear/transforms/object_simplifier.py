"""Inline proxy object property accesses.

Detects: const o = {x: 1, y: "hello"}; ... o.x ... o.y ...
Replaces: ... 1 ... "hello" ...
"""

from ..scope import build_scope_tree
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import replace_identifiers
from .base import Transform


class ObjectSimplifier(Transform):
    """Replace proxy object property accesses with their literal values."""

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        self._process_scope(scope_tree)
        return self.has_changed()

    def _process_scope(self, scope):
        for name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            init = node.get('init')
            if not init or init.get('type') != 'ObjectExpression':
                continue

            # Build property map (only literals and simple function expressions)
            props = init.get('properties', [])
            if not self._is_proxy_object(props):
                continue

            prop_map = {}
            for p in props:
                key = self._get_property_key(p)
                if key is None:
                    continue
                val = p.get('value')
                if is_literal(val):
                    prop_map[key] = val
                elif val and val.get('type') in (
                    'FunctionExpression',
                    'ArrowFunctionExpression',
                ):
                    prop_map[key] = val

            if not prop_map:
                continue

            if self._has_property_assignment(binding):
                continue

            # Replace property accesses
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if not ref_parent or ref_parent.get('type') != 'MemberExpression':
                    continue
                if ref_key != 'object':
                    continue

                me = ref_parent
                prop_name = self._get_member_prop_name(me)
                if prop_name is None or prop_name not in prop_map:
                    continue

                val = prop_map[prop_name]
                if is_literal(val):
                    self._replace_node(me, deep_copy(val))
                    self.set_changed()
                    continue

                if val.get('type') not in (
                    'FunctionExpression',
                    'ArrowFunctionExpression',
                ):
                    continue
                self._try_inline_function_call(me, val)

        for child in scope.children:
            self._process_scope(child)

    def _has_property_assignment(self, binding):
        """Check if any reference to the binding is a property assignment target."""
        from ..traverser import find_parent

        for ref_node, ref_parent, ref_key, ref_index in binding.references:
            if not (ref_parent and ref_parent.get('type') == 'MemberExpression' and ref_key == 'object'):
                continue
            me_parent_info = find_parent(self.ast, ref_parent)
            if not me_parent_info:
                continue
            parent, key, _ = me_parent_info
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return True
        return False

    def _try_inline_function_call(self, member_expression, function_value):
        """Try to inline a function call at a MemberExpression site."""
        from ..traverser import find_parent

        me_parent_info = find_parent(self.ast, member_expression)
        if not me_parent_info:
            return
        parent, key, _ = me_parent_info
        if not (parent and parent.get('type') == 'CallExpression' and key == 'callee'):
            return
        replacement = self._inline_func(function_value, parent.get('arguments', []))
        if not replacement:
            return
        self._replace_node(parent, replacement)
        self.set_changed()

    def _is_proxy_object(self, props):
        """Check if all properties are literals or simple functions."""
        for p in props:
            if p.get('type') != 'Property':
                return False
            val = p.get('value')
            if not val:
                return False
            if is_literal(val):
                continue
            if val.get('type') in ('FunctionExpression', 'ArrowFunctionExpression'):
                continue
            return False
        return True

    def _get_property_key(self, prop):
        """Get the string key of a property."""
        key = prop.get('key')
        if not key:
            return None
        if key.get('type') == 'Identifier':
            return key['name']
        if is_string_literal(key):
            return key['value']
        return None

    def _get_member_prop_name(self, member_expr):
        """Get property name from a member expression."""
        prop = member_expr.get('property')
        if not prop:
            return None
        if member_expr.get('computed'):
            if is_string_literal(prop):
                return prop['value']
            return None
        if prop.get('type') == 'Identifier':
            return prop['name']
        return None

    def _replace_node(self, target, replacement):
        """Replace target node in the AST."""
        from ..traverser import find_parent

        result = find_parent(self.ast, target)
        if result:
            parent, key, index = result
            if index is not None:
                parent[key][index] = replacement
            else:
                parent[key] = replacement

    def _inline_func(self, func, args):
        """Inline a simple function call."""
        body = func.get('body')
        if not body:
            return None
        if func.get('type') == 'ArrowFunctionExpression' and body.get('type') != 'BlockStatement':
            expr = deep_copy(body)
        elif body.get('type') == 'BlockStatement':
            stmts = body.get('body', [])
            if len(stmts) != 1 or stmts[0].get('type') != 'ReturnStatement':
                return None
            arg = stmts[0].get('argument')
            if not arg:
                return None
            expr = deep_copy(arg)
        else:
            return None

        params = func.get('params', [])
        param_map = {}
        for i, p in enumerate(params):
            if p.get('type') == 'Identifier':
                param_map[p['name']] = args[i] if i < len(args) else {'type': 'Identifier', 'name': 'undefined'}

        replace_identifiers(expr, param_map)
        return expr
