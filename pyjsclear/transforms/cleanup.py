"""Miscellaneous cleanup transforms.

- Optional catch binding: `catch (e) {}` → `catch {}` when e is unused
- Return undefined: `return undefined;` → `return;`
"""

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from .base import Transform


class OptionalCatchBinding(Transform):
    """Remove unused catch clause parameters (ES2019 optional catch binding)."""

    def execute(self):

        def enter(node, parent, key, index):
            if node.get('type') != 'CatchClause':
                return
            param = node.get('param')
            if not param or not is_identifier(param):
                return
            param_name = param['name']
            body = node.get('body')
            if not body:
                return
            # Check if param_name is referenced anywhere in the catch body
            if not self._is_name_used(body, param_name):
                node['param'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()

    def _is_name_used(self, body, name):
        """Check if an identifier name is used anywhere in the subtree."""
        found = [False]

        def cb(node, parent):
            if found[0]:
                return
            if is_identifier(node) and node.get('name') == name:
                found[0] = True

        simple_traverse(body, cb)
        return found[0]


class ReturnUndefinedCleanup(Transform):
    """Simplify `return undefined;` to `return;`."""

    def execute(self):

        def enter(node, parent, key, index):
            if node.get('type') != 'ReturnStatement':
                return
            arg = node.get('argument')
            if not arg:
                return
            if is_identifier(arg) and arg.get('name') == 'undefined':
                node['argument'] = None
                self.set_changed()

        traverse(self.ast, {'enter': enter})
        return self.has_changed()
