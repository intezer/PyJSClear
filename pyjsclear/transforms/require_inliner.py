"""Inline esbuild require polyfill wrappers.

Detects the esbuild require polyfill pattern:
    var _0x544bfe = ((_0x4b989b) => typeof require !== "undefined" ? require : ...

And replaces all calls like _0x544bfe("fs") with require("fs").
"""

from __future__ import annotations

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_string_literal
from ..utils.ast_helpers import make_identifier
from .base import Transform


class RequireInliner(Transform):
    """Replace require polyfill calls with direct require() calls."""

    def execute(self) -> bool:
        """Detect require polyfill declarations and inline them as require()."""
        polyfill_names: set[str] = self._find_polyfill_names()

        if not polyfill_names:
            return False

        self._replace_polyfill_calls(polyfill_names)
        return self.has_changed()

    def _find_polyfill_names(self) -> set[str]:
        """Scan the AST for variable declarations that wrap a require polyfill."""
        polyfill_names: set[str] = set()

        def visit_declarator(node: dict, parent: dict | None) -> None:
            """Collect names of variables that are require polyfill wrappers."""
            if node.get('type') != 'VariableDeclarator':
                return

            declaration_identifier = node.get('id')
            initializer = node.get('init')

            if not is_identifier(declaration_identifier):
                return
            if not initializer or initializer.get('type') != 'CallExpression':
                return
            if self._contains_typeof_require(initializer):
                polyfill_names.add(declaration_identifier['name'])

        simple_traverse(self.ast, visit_declarator)
        return polyfill_names

    def _replace_polyfill_calls(self, polyfill_names: set[str]) -> None:
        """Replace polyfill wrapper calls with direct require() calls."""

        def replace_call(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> None:
            """Rewrite a single polyfill call to require()."""
            if node.get('type') != 'CallExpression':
                return

            callee = node.get('callee')
            if not is_identifier(callee):
                return
            if callee['name'] not in polyfill_names:
                return

            arguments_list = node.get('arguments', [])
            if len(arguments_list) != 1:
                return

            node['callee'] = make_identifier('require')
            self.set_changed()

        traverse(self.ast, {'enter': replace_call})

    def _contains_typeof_require(self, node: dict) -> bool:
        """Check if a subtree contains a `typeof require` expression."""
        found = False

        def scan(current_node: dict, parent: dict | None) -> None:
            """Walk the subtree looking for typeof require."""
            nonlocal found
            if found:
                return
            if not isinstance(current_node, dict):
                return
            if current_node.get('type') != 'UnaryExpression':
                return
            if current_node.get('operator') != 'typeof':
                return

            argument = current_node.get('argument')
            if is_identifier(argument) and argument.get('name') == 'require':
                found = True

        simple_traverse(node, scan)
        return found
