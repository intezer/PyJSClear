"""Inline proxy object property accesses.

Detects: const o = {x: 1, y: "hello"}; ... o.x ... o.y ...
Replaces: ... 1 ... "hello" ...
"""

import copy
from .base import Transform
from ..scope import build_scope_tree
from ..utils.ast_helpers import is_literal, is_string_literal, is_identifier, deep_copy


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
                elif val and val.get('type') in ('FunctionExpression', 'ArrowFunctionExpression'):
                    prop_map[key] = val

            if not prop_map:
                continue

            # Check no modifications to the object
            modified = False
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if (ref_parent and ref_parent.get('type') == 'MemberExpression' and
                        ref_key == 'object'):
                    # Check if this member expression is an assignment target
                    from ..traverser import find_parent
                    me = ref_parent
                    me_parent_info = find_parent(self.ast, me)
                    if me_parent_info:
                        mp, mk, mi = me_parent_info
                        if mp and mp.get('type') == 'AssignmentExpression' and mk == 'left':
                            modified = True
                            break

            if modified:
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
                    replacement = deep_copy(val)
                    self._replace_member_expr(me, replacement)
                    self.set_changed()
                elif val.get('type') in ('FunctionExpression', 'ArrowFunctionExpression'):
                    # Check if the MemberExpression is called
                    from ..traverser import find_parent
                    me_parent_info = find_parent(self.ast, me)
                    if me_parent_info:
                        mp, mk, mi = me_parent_info
                        if mp and mp.get('type') == 'CallExpression' and mk == 'callee':
                            # Inline the function call
                            from .proxy_functions import ProxyFunctionInliner
                            func = val
                            args = mp.get('arguments', [])
                            replacement = self._inline_func(func, args)
                            if replacement:
                                self._replace_node(mp, replacement)
                                self.set_changed()

        for child in scope.children:
            self._process_scope(child)

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

    def _replace_member_expr(self, target, replacement):
        """Replace a MemberExpression with a replacement node."""
        self._replace_node(target, replacement)

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

        self._replace_params(expr, param_map)
        return expr

    def _replace_params(self, node, param_map):
        """Replace parameter identifiers."""
        if not isinstance(node, dict) or 'type' not in node:
            return
        from ..utils.ast_helpers import get_child_keys
        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                for i, item in enumerate(child):
                    if isinstance(item, dict) and item.get('type') == 'Identifier':
                        name = item.get('name', '')
                        if key == 'property' and node.get('type') == 'MemberExpression' and not node.get('computed'):
                            continue
                        if name in param_map:
                            child[i] = deep_copy(param_map[name])
                    elif isinstance(item, dict) and 'type' in item:
                        self._replace_params(item, param_map)
            elif isinstance(child, dict):
                if child.get('type') == 'Identifier':
                    name = child.get('name', '')
                    if key == 'property' and node.get('type') == 'MemberExpression' and not node.get('computed'):
                        continue
                    if name in param_map:
                        node[key] = deep_copy(param_map[name])
                elif 'type' in child:
                    self._replace_params(child, param_map)
