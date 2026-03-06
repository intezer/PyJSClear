"""Proxy function detection and inlining.

Detects patterns like:
  function _proxy(a, b) { return a + b; }
  _proxy(x, y)  ->  x + y
"""

from ..scope import build_scope_tree
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy, is_identifier, replace_identifiers
from .base import Transform


class ProxyFunctionInliner(Transform):
    """Inline proxy function calls."""

    rebuild_scope = True

    def execute(self):
        scope_tree, node_scope = build_scope_tree(self.ast)

        # Find proxy functions
        proxy_fns = {}  # name -> (func_node, scope, binding)
        self._find_proxy_functions(scope_tree, proxy_fns)

        if not proxy_fns:
            return False

        # Collect call sites with depth info
        call_sites = []  # (call_node, parent, key, index, proxy_info, depth)
        depth_counter = [0]

        def enter(node, parent, key, index):
            depth_counter[0] += 1
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not is_identifier(callee):
                return
            name = callee.get('name', '')
            if name not in proxy_fns:
                return
            call_sites.append(
                (node, parent, key, index, proxy_fns[name], depth_counter[0])
            )

        traverse(self.ast, {'enter': enter})

        # Process innermost calls first
        call_sites.sort(key=lambda x: x[5], reverse=True)

        for (
            call_node,
            parent,
            key,
            index,
            (func_node, scope, binding),
            depth,
        ) in call_sites:
            replacement = self._get_replacement(
                func_node, call_node.get('arguments', [])
            )
            if replacement is None:
                continue
            # Replace the call with the inlined expression
            if index is not None:
                parent[key][index] = replacement
            else:
                parent[key] = replacement
            self.set_changed()

        return self.has_changed()

    def _find_proxy_functions(self, scope, result):
        """Find all proxy function bindings in the scope tree."""
        for name, binding in scope.bindings.items():
            if not binding.is_constant:
                continue
            func_node = self._get_function_expr(binding)
            if func_node and self._is_proxy_function(func_node):
                result[name] = (func_node, scope, binding)

        for child in scope.children:
            self._find_proxy_functions(child, result)

    def _get_function_expr(self, binding):
        """Get the function expression from a binding."""
        node = binding.node
        if isinstance(node, dict):
            ntype = node.get('type', '')
            if ntype in (
                'FunctionDeclaration',
                'FunctionExpression',
                'ArrowFunctionExpression',
            ):
                return node
            if ntype == 'VariableDeclarator':
                init = node.get('init')
                if init and init.get('type') in (
                    'FunctionExpression',
                    'ArrowFunctionExpression',
                ):
                    return init
        return None

    def _is_proxy_function(self, func_node):
        """Check if a function is a simple proxy (single return of an expression)."""
        params = func_node.get('params', [])
        if not all(p.get('type') == 'Identifier' for p in params):
            return False

        body = func_node.get('body')
        if not body:
            return False

        # Arrow function with expression body
        if (
            func_node.get('type') == 'ArrowFunctionExpression'
            and body.get('type') != 'BlockStatement'
        ):
            return self._is_proxy_value(body)

        # Block with single return
        if body.get('type') == 'BlockStatement':
            stmts = body.get('body', [])
            if len(stmts) != 1:
                return False
            stmt = stmts[0]
            if stmt.get('type') != 'ReturnStatement':
                return False
            arg = stmt.get('argument')
            if arg is None:
                return True  # returns undefined
            return self._is_proxy_value(arg)

        return False

    _DISALLOWED_PROXY_TYPES = frozenset(
        {
            'FunctionExpression',
            'FunctionDeclaration',
            'ArrowFunctionExpression',
            'BlockStatement',
            'SequenceExpression',
            'AssignmentExpression',
        }
    )

    def _is_proxy_value(self, node):
        """Check if an expression is a valid proxy return value (no side effects)."""
        if not isinstance(node, dict) or 'type' not in node:
            return False
        if node.get('type', '') in self._DISALLOWED_PROXY_TYPES:
            return False
        from ..utils.ast_helpers import get_child_keys

        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                if any(
                    isinstance(item, dict)
                    and item.get('type') in self._DISALLOWED_PROXY_TYPES
                    for item in child
                ):
                    return False
            elif (
                isinstance(child, dict)
                and child.get('type') in self._DISALLOWED_PROXY_TYPES
            ):
                return False
        return True

    def _get_replacement(self, func_node, args):
        """Get the replacement expression for a proxy function call."""
        body = func_node.get('body')
        if not body:
            return {'type': 'Identifier', 'name': 'undefined'}

        # Arrow with expression body
        if (
            func_node.get('type') == 'ArrowFunctionExpression'
            and body.get('type') != 'BlockStatement'
        ):
            expr = deep_copy(body)
        elif body.get('type') == 'BlockStatement':
            stmts = body.get('body', [])
            if not stmts or stmts[0].get('type') != 'ReturnStatement':
                return None
            arg = stmts[0].get('argument')
            if arg is None:
                return {'type': 'Identifier', 'name': 'undefined'}
            expr = deep_copy(arg)
        else:
            return None

        # Build parameter map
        params = func_node.get('params', [])
        param_map = {}
        for i, p in enumerate(params):
            if p.get('type') == 'Identifier':
                if i < len(args):
                    param_map[p['name']] = args[i]
                else:
                    param_map[p['name']] = {'type': 'Identifier', 'name': 'undefined'}

        replace_identifiers(expr, param_map)
        return expr
