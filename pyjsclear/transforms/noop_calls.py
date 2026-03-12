"""Remove calls to no-op methods (methods with empty body or just return).

Detects static methods like:
    static methodName(...) { return; }

And removes expression statements that call them:
    obj.methodName('...');  // removed
"""

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


class NoopCallRemover(Transform):
    """Remove expression-statement calls to no-op methods."""

    def execute(self):
        # Phase 1: Find no-op methods (empty body or just 'return;')
        noop_methods = set()

        def find_noops(node, parent):
            if node.get('type') != 'MethodDefinition':
                return
            if node.get('kind') not in ('method', None):
                return
            key = node.get('key')
            if not key or not is_identifier(key):
                return
            fn = node.get('value')
            if not fn or fn.get('type') != 'FunctionExpression':
                return
            # Check if async — async no-op still returns a promise, skip
            if fn.get('async'):
                return
            body = fn.get('body')
            if not body or body.get('type') != 'BlockStatement':
                return
            stmts = body.get('body', [])
            if len(stmts) == 0:
                noop_methods.add(key['name'])
            elif len(stmts) == 1:
                stmt = stmts[0]
                if stmt.get('type') == 'ReturnStatement' and stmt.get('argument') is None:
                    noop_methods.add(key['name'])

        simple_traverse(self.ast, find_noops)

        if not noop_methods:
            return False

        # Phase 2: Remove ExpressionStatement calls to no-op methods
        def remove_calls(node, parent, key, index):
            if node.get('type') != 'ExpressionStatement':
                return
            expr = node.get('expression')
            if not expr or expr.get('type') not in ('CallExpression', 'AwaitExpression'):
                return
            call = expr
            if call.get('type') == 'AwaitExpression':
                call = call.get('argument')
                if not call or call.get('type') != 'CallExpression':
                    return
            callee = call.get('callee')
            if not callee or callee.get('type') != 'MemberExpression':
                return
            prop = callee.get('property')
            if not prop or not is_identifier(prop):
                return
            if prop['name'] in noop_methods:
                self.set_changed()
                return REMOVE

        traverse(self.ast, {'enter': remove_calls})
        return self.has_changed()
