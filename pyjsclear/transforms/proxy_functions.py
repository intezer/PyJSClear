"""Proxy function detection and inlining.

Detects patterns like:
  function _proxy(a, b) { return a + b; }
  _proxy(x, y)  ->  x + y
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..scope import Binding
from ..scope import build_scope_tree
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import get_child_keys
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import replace_identifiers
from .base import Transform


if TYPE_CHECKING:
    from ..scope import Scope


# Max AST nodes in a proxy function body before we refuse to inline
_MAX_PROXY_BODY_NODES = 12

_FUNCTION_TYPES = frozenset(
    {
        'FunctionDeclaration',
        'FunctionExpression',
        'ArrowFunctionExpression',
    }
)

_FUNCTION_EXPR_TYPES = frozenset(
    {
        'FunctionExpression',
        'ArrowFunctionExpression',
    }
)

# Proxy info tuple: (func_node, scope, binding)
ProxyInfo = tuple[dict, 'Scope', Binding]

# Call site tuple: (call_node, parent, key, index, proxy_info, depth)
CallSite = tuple[dict, dict, str, int | None, ProxyInfo, int]


class ProxyFunctionInliner(Transform):
    """Inline trivial proxy function calls to simplify the AST."""

    rebuild_scope = True

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

    def execute(self) -> bool:
        """Run proxy function inlining. Returns True if any calls were inlined."""
        if self.scope_tree is not None:
            scope_tree = self.scope_tree
        else:
            scope_tree, _ = build_scope_tree(self.ast)

        proxy_functions: dict[str, ProxyInfo] = {}
        self._find_proxy_functions(scope_tree, proxy_functions)

        if not proxy_functions:
            return False

        call_sites = self._collect_call_sites(proxy_functions)
        call_sites = self._filter_helper_functions(call_sites, proxy_functions)

        # Process innermost calls first
        call_sites.sort(key=lambda site: site[5], reverse=True)

        for (
            _call_node,
            parent,
            key,
            index,
            (function_node, _scope, _binding),
            _depth,
        ) in call_sites:
            replacement = self._get_replacement(function_node, _call_node.get('arguments', []))
            if replacement is None:
                continue
            if index is not None:
                parent[key][index] = replacement
            else:
                parent[key] = replacement
            self.set_changed()

        return self.has_changed()

    def _collect_call_sites(self, proxy_functions: dict[str, ProxyInfo]) -> list[CallSite]:
        """Walk the AST and collect all call sites targeting proxy functions."""
        call_sites: list[CallSite] = []
        depth_counter = [0]

        def on_enter(node: dict, parent: dict, key: str, index: int | None) -> None:
            depth_counter[0] += 1
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not is_identifier(callee):
                return
            callee_name = callee.get('name', '')
            if callee_name not in proxy_functions:
                return
            call_sites.append((node, parent, key, index, proxy_functions[callee_name], depth_counter[0]))

        traverse(self.ast, {'enter': on_enter})
        return call_sites

    def _filter_helper_functions(
        self,
        call_sites: list[CallSite],
        proxy_functions: dict[str, ProxyInfo],
    ) -> list[CallSite]:
        """Remove call sites for helper functions (many callers + conditional body)."""
        call_counts: dict[int, int] = {}
        for call_site in call_sites:
            function_node_id = id(call_site[4][0])
            call_counts[function_node_id] = call_counts.get(function_node_id, 0) + 1

        helper_function_ids: set[int] = set()
        for _name, (function_node, _, _) in proxy_functions.items():
            if call_counts.get(id(function_node), 0) > 3 and self._has_conditional(function_node):
                helper_function_ids.add(id(function_node))

        return [call_site for call_site in call_sites if id(call_site[4][0]) not in helper_function_ids]

    @staticmethod
    def _has_conditional(node: dict) -> bool:
        """Check whether the subtree contains a ConditionalExpression."""
        found = [False]

        def check_node(current_node: dict, parent: dict) -> None:
            if current_node.get('type') == 'ConditionalExpression':
                found[0] = True

        simple_traverse(node, check_node)
        return found[0]

    def _find_proxy_functions(self, scope: Scope, result: dict[str, ProxyInfo]) -> None:
        """Recursively find all proxy function bindings in the scope tree."""
        for name, binding in scope.bindings.items():
            if not binding.is_constant:
                continue
            function_node = self._get_function_expression(binding)
            if function_node and self._is_proxy_function(function_node):
                result[name] = (function_node, scope, binding)

        for child in scope.children:
            self._find_proxy_functions(child, result)

    def _get_function_expression(self, binding: Binding) -> dict | None:
        """Extract the function node from a binding, if it is a function."""
        node = binding.node
        if not isinstance(node, dict):
            return None

        node_type = node.get('type', '')
        match node_type:
            case t if t in _FUNCTION_TYPES:
                return node
            case 'VariableDeclarator':
                initializer = node.get('init')
                if initializer and initializer.get('type') in _FUNCTION_EXPR_TYPES:
                    return initializer
                return None
            case _:
                return None

    def _is_proxy_function(self, function_node: dict) -> bool:
        """Check if a function is a simple proxy (single return of an expression)."""
        parameters = function_node.get('params', [])
        if not all(parameter.get('type') == 'Identifier' for parameter in parameters):
            return False

        body = function_node.get('body')
        if not body:
            return False

        # Arrow function with expression body
        if function_node.get('type') == 'ArrowFunctionExpression' and body.get('type') != 'BlockStatement':
            if not self._is_proxy_value(body):
                return False
            return self._count_nodes(body) <= _MAX_PROXY_BODY_NODES

        # Block with single return
        if body.get('type') != 'BlockStatement':
            return False

        statements = body.get('body', [])
        if len(statements) != 1:
            return False

        statement = statements[0]
        if statement.get('type') != 'ReturnStatement':
            return False

        argument = statement.get('argument')
        if argument is None:
            return True  # returns undefined

        if not self._is_proxy_value(argument):
            return False
        return self._count_nodes(argument) <= _MAX_PROXY_BODY_NODES

    @staticmethod
    def _count_nodes(node: dict) -> int:
        """Count AST nodes in a subtree."""
        count = [0]

        def increment_count(current_node: dict, parent: dict) -> None:
            count[0] += 1

        simple_traverse(node, increment_count)
        return count[0]

    def _is_proxy_value(self, node: dict) -> bool:
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

    def _get_replacement(self, function_node: dict, arguments: list[dict]) -> dict | None:
        """Build the replacement expression for inlining a proxy function call."""
        body = function_node.get('body')
        if not body:
            return {'type': 'Identifier', 'name': 'undefined'}

        # Arrow with expression body
        if function_node.get('type') == 'ArrowFunctionExpression' and body.get('type') != 'BlockStatement':
            expression = deep_copy(body)
        elif body.get('type') == 'BlockStatement':
            statements = body.get('body', [])
            if not statements or statements[0].get('type') != 'ReturnStatement':
                return None
            argument = statements[0].get('argument')
            if argument is None:
                return {'type': 'Identifier', 'name': 'undefined'}
            expression = deep_copy(argument)
        else:
            return None

        parameters = function_node.get('params', [])
        parameter_map: dict[str, dict] = {}
        for parameter_index, parameter in enumerate(parameters):
            if parameter.get('type') != 'Identifier':
                continue
            if parameter_index < len(arguments):
                parameter_map[parameter['name']] = arguments[parameter_index]
            else:
                parameter_map[parameter['name']] = {'type': 'Identifier', 'name': 'undefined'}

        replace_identifiers(expression, parameter_map)
        return expression
