"""Remove calls to no-op methods (methods with empty body or just return).

Detects static methods like:
    static methodName(...) { return; }

And removes expression statements that call them:
    obj.methodName('...');  // removed
"""

from typing import Any

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


class NoopCallRemover(Transform):
    """Remove expression-statement calls to no-op methods."""

    def execute(self) -> bool:
        # Phase 1: Find no-op methods (empty body or just 'return;')
        noop_methods: set[str] = set()

        def find_noops(node: dict, parent: dict | None) -> None:
            if node.get('type') != 'MethodDefinition':
                return
            if node.get('kind') not in ('method', None):
                return
            key = node.get('key')
            if not key or not is_identifier(key):
                return
            function_expression = node.get('value')
            if not function_expression or function_expression.get('type') != 'FunctionExpression':
                return
            # Async no-op still returns a promise, skip
            if function_expression.get('async'):
                return
            body = function_expression.get('body')
            if not body or body.get('type') != 'BlockStatement':
                return
            statements = body.get('body', [])
            if not statements:
                noop_methods.add(key['name'])
            elif len(statements) == 1:
                statement = statements[0]
                if statement.get('type') == 'ReturnStatement' and statement.get('argument') is None:
                    noop_methods.add(key['name'])

        simple_traverse(self.ast, find_noops)

        if not noop_methods:
            return False

        # Phase 2: Remove ExpressionStatement calls to no-op methods
        def remove_calls(node: dict, parent: dict | None, key: str | None, index: int | None) -> Any:
            if node.get('type') != 'ExpressionStatement':
                return
            expression = node.get('expression')
            if not expression or expression.get('type') not in ('CallExpression', 'AwaitExpression'):
                return
            call = expression
            if call.get('type') == 'AwaitExpression':
                call = call.get('argument')
                if not call or call.get('type') != 'CallExpression':
                    return
            callee = call.get('callee')
            if not callee or callee.get('type') != 'MemberExpression':
                return
            property_node = callee.get('property')
            if not property_node or not is_identifier(property_node):
                return
            if property_node['name'] in noop_methods:
                self.set_changed()
                return REMOVE

        traverse(self.ast, {'enter': remove_calls})
        return self.has_changed()
