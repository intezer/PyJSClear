"""Proxy function detection and inlining.

Detects patterns like:
  function _proxy(a, b) { return a + b; }
  _proxy(x, y)  ->  x + y
"""

from ..scope import build_scope_tree
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import get_child_keys
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import replace_identifiers
from .base import Transform


# Max AST nodes in a proxy function body before we refuse to inline
_MAX_PROXY_BODY_NODES = 12


class ProxyFunctionInliner(Transform):
    """Inline proxy function calls."""

    rebuild_scope = True

    def execute(self):
        if self.scope_tree is not None:
            scope_tree, node_scope = self.scope_tree, self.node_scope
        else:
            scope_tree, node_scope = build_scope_tree(self.ast)

        # Find proxy functions
        proxy_functions = {}  # name -> (func_node, scope, binding)
        self._find_proxy_functions(scope_tree, proxy_functions)

        if not proxy_functions:
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
            if name not in proxy_functions:
                return
            call_sites.append((node, parent, key, index, proxy_functions[name], depth_counter[0]))

        traverse(self.ast, {'enter': enter})

        # Skip helper functions: many call sites + conditional body = not a true proxy
        call_counts = {}
        for call_site in call_sites:
            function_node_id = id(call_site[4][0])  # func_node
            call_counts[function_node_id] = call_counts.get(function_node_id, 0) + 1

        def _has_conditional(node):
            found = [False]

            def check_node(n, parent):
                if n.get('type') == 'ConditionalExpression':
                    found[0] = True

            simple_traverse(node, check_node)
            return found[0]

        helper_function_ids = set()
        for name, (func_node, _, _) in proxy_functions.items():
            if call_counts.get(id(func_node), 0) > 3 and _has_conditional(func_node):
                helper_function_ids.add(id(func_node))
        call_sites = [call_site for call_site in call_sites if id(call_site[4][0]) not in helper_function_ids]

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
            replacement = self._get_replacement(func_node, call_node.get('arguments', []))
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
            node_type = node.get('type', '')
            if node_type in (
                'FunctionDeclaration',
                'FunctionExpression',
                'ArrowFunctionExpression',
            ):
                return node
            if node_type == 'VariableDeclarator':
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
        if not all(parameter.get('type') == 'Identifier' for parameter in params):
            return False

        body = func_node.get('body')
        if not body:
            return False

        # Arrow function with expression body
        if func_node.get('type') == 'ArrowFunctionExpression' and body.get('type') != 'BlockStatement':
            if not self._is_proxy_value(body):
                return False
            return self._count_nodes(body) <= _MAX_PROXY_BODY_NODES

        # Block with single return
        if body.get('type') == 'BlockStatement':
            statements = body.get('body', [])
            if len(statements) != 1:
                return False
            stmt = statements[0]
            if stmt.get('type') != 'ReturnStatement':
                return False
            argument = stmt.get('argument')
            if argument is None:
                return True  # returns undefined
            if not self._is_proxy_value(argument):
                return False
            return self._count_nodes(argument) <= _MAX_PROXY_BODY_NODES

        return False

    @staticmethod
    def _count_nodes(node):
        """Count AST nodes in a subtree."""
        count = [0]

        def increment_count(n, parent):
            count[0] += 1

        simple_traverse(node, increment_count)
        return count[0]

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
        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                if any(isinstance(item, dict) and item.get('type') in self._DISALLOWED_PROXY_TYPES for item in child):
                    return False
            elif isinstance(child, dict) and child.get('type') in self._DISALLOWED_PROXY_TYPES:
                return False
        return True

    def _get_replacement(self, func_node, args):
        """Get the replacement expression for a proxy function call."""
        body = func_node.get('body')
        if not body:
            return {'type': 'Identifier', 'name': 'undefined'}

        # Arrow with expression body
        if func_node.get('type') == 'ArrowFunctionExpression' and body.get('type') != 'BlockStatement':
            expr = deep_copy(body)
        elif body.get('type') == 'BlockStatement':
            statements = body.get('body', [])
            if not statements or statements[0].get('type') != 'ReturnStatement':
                return None
            argument = statements[0].get('argument')
            if argument is None:
                return {'type': 'Identifier', 'name': 'undefined'}
            expr = deep_copy(argument)
        else:
            return None

        # Build parameter map
        params = func_node.get('params', [])
        parameter_map = {}
        for index, parameter in enumerate(params):
            if parameter.get('type') == 'Identifier':
                if index < len(args):
                    parameter_map[parameter['name']] = args[index]
                else:
                    parameter_map[parameter['name']] = {'type': 'Identifier', 'name': 'undefined'}

        replace_identifiers(expr, parameter_map)
        return expr
