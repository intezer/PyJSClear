"""Inline esbuild require polyfill wrappers.

Detects the esbuild require polyfill pattern:
    var _0x544bfe = ((_0x4b989b) => typeof require !== "undefined" ? require : ...

And replaces all calls like _0x544bfe("fs") with require("fs").
"""

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import make_identifier
from .base import Transform


class RequireInliner(Transform):
    """Replace require polyfill calls with direct require() calls."""

    def execute(self):
        polyfill_names = set()

        # Phase 1: Detect require polyfill pattern.
        # We look for: var X = (...)(function(Y) { ... require ... })
        # Heuristic: a VariableDeclarator whose init is a CallExpression,
        # and somewhere in its body there's `typeof require !== "undefined" ? require : ...`
        def find_polyfills(node, parent):
            if node.get('type') != 'VariableDeclarator':
                return
            decl_id = node.get('id')
            init = node.get('init')
            if not is_identifier(decl_id):
                return
            if not init or init.get('type') != 'CallExpression':
                return

            # Check if the init tree contains `typeof require`
            if self._contains_typeof_require(init):
                polyfill_names.add(decl_id['name'])

        simple_traverse(self.ast, find_polyfills)

        if not polyfill_names:
            return False

        # Phase 2: Replace _0x544bfe(X) with require(X)
        def replace_calls(node, parent, key, index):
            if node.get('type') != 'CallExpression':
                return
            callee = node.get('callee')
            if not is_identifier(callee):
                return
            if callee['name'] not in polyfill_names:
                return
            args = node.get('arguments', [])
            if len(args) != 1:
                return

            # Replace the callee with require
            node['callee'] = make_identifier('require')
            self.set_changed()

        traverse(self.ast, {'enter': replace_calls})
        return self.has_changed()

    def _contains_typeof_require(self, node):
        """Check if a subtree contains `typeof require`."""
        found = [False]

        def scan(n, parent):
            if found[0]:
                return
            if not isinstance(n, dict):
                return
            if n.get('type') == 'UnaryExpression' and n.get('operator') == 'typeof':
                arg = n.get('argument')
                if is_identifier(arg) and arg.get('name') == 'require':
                    found[0] = True

        simple_traverse(node, scan)
        return found[0]
