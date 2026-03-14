"""Remove calls to no-op methods (methods with empty body or just return).

Detects static methods like:
    static methodName(...) { return; }

And removes expression statements that call them:
    obj.methodName('...');  // removed
"""

from __future__ import annotations

from typing import Any

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


def _is_noop_body(function_expression: dict) -> bool:
    """Check whether a function expression has an empty or return-only body."""
    if function_expression.get('type') != 'FunctionExpression':
        return False
    if function_expression.get('async'):
        return False
    body = function_expression.get('body')
    if not body or body.get('type') != 'BlockStatement':
        return False
    statements = body.get('body', [])
    if not statements:
        return True
    if len(statements) == 1:
        statement = statements[0]
        return statement.get('type') == 'ReturnStatement' and statement.get('argument') is None
    return False


def _extract_noop_method_name(node: dict) -> str | None:
    """Return the method name if node is a no-op MethodDefinition, else None."""
    if node.get('type') != 'MethodDefinition':
        return None
    if node.get('kind') not in ('method', None):
        return None
    method_key = node.get('key')
    if not method_key or not is_identifier(method_key):
        return None
    function_expression = node.get('value')
    if not function_expression or not _is_noop_body(function_expression):
        return None
    return method_key['name']


def _extract_call_from_expression(node: dict) -> dict | None:
    """Extract the CallExpression from an ExpressionStatement, unwrapping await."""
    if node.get('type') != 'ExpressionStatement':
        return None
    expression = node.get('expression')
    if not expression:
        return None
    match expression.get('type'):
        case 'CallExpression':
            return expression
        case 'AwaitExpression':
            argument = expression.get('argument')
            if argument and argument.get('type') == 'CallExpression':
                return argument
    return None


def _get_member_call_name(call_node: dict) -> str | None:
    """Return the property name if call_node is a member call, else None."""
    callee = call_node.get('callee')
    if not callee or callee.get('type') != 'MemberExpression':
        return None
    property_node = callee.get('property')
    if not property_node or not is_identifier(property_node):
        return None
    return property_node['name']


class NoopCallRemover(Transform):
    """Remove expression-statement calls to no-op methods."""

    def execute(self) -> bool:
        """Find no-op methods and remove all call sites."""
        noop_methods = self._collect_noop_methods()
        if not noop_methods:
            return False
        self._remove_noop_calls(noop_methods)
        return self.has_changed()

    def _collect_noop_methods(self) -> set[str]:
        """Traverse the AST and collect names of no-op methods."""
        noop_methods: set[str] = set()

        def visitor(node: dict, parent: dict | None) -> None:
            method_name = _extract_noop_method_name(node)
            if method_name is not None:
                noop_methods.add(method_name)

        simple_traverse(self.ast, visitor)
        return noop_methods

    def _remove_noop_calls(self, noop_methods: set[str]) -> None:
        """Remove ExpressionStatement calls to the given no-op methods."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> Any:
            call_node = _extract_call_from_expression(node)
            if call_node is None:
                return None
            member_name = _get_member_call_name(call_node)
            if member_name not in noop_methods:
                return None
            self.set_changed()
            return REMOVE

        traverse(self.ast, {'enter': enter})
