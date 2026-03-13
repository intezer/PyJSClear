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

    def execute(self) -> bool:
        polyfill_names: set[str] = set()

        # Phase 1: Detect require polyfill pattern.
        # We look for: var X = (...)(function(Y) { ... require ... })
        # Heuristic: a VariableDeclarator whose init is a CallExpression,
        # and somewhere in its body there's `typeof require !== "undefined" ? require : ...`
        def find_polyfills(node: dict, parent: dict | None) -> None:
            if node.get('type') != 'VariableDeclarator':
                return
            declaration_id = node.get('id')
            init = node.get('init')
            if not is_identifier(declaration_id):
                return
            if not init or init.get('type') != 'CallExpression':
                return
            if self._contains_typeof_require(init):
                polyfill_names.add(declaration_id['name'])

        simple_traverse(self.ast, find_polyfills)

        if not polyfill_names:
            return False

        # Phase 2: Replace _0x544bfe(X) with require(X)
        def replace_calls(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
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
            node['callee'] = make_identifier('require')
            self.set_changed()

        traverse(self.ast, {'enter': replace_calls})
        return self.has_changed()

    def _contains_typeof_require(self, node: dict) -> bool:
        """Check if a subtree contains `typeof require`."""
        found = [False]

        def scan(current_node: dict, parent: dict | None) -> None:
            if found[0]:
                return
            if not isinstance(current_node, dict):
                return
            if current_node.get('type') == 'UnaryExpression' and current_node.get('operator') == 'typeof':
                argument = current_node.get('argument')
                if is_identifier(argument) and argument.get('name') == 'require':
                    found[0] = True

        simple_traverse(node, scan)
        return found[0]
