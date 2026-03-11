"""Inline global alias assignments.

Detects patterns like:
    var _0x3bbd10 = JSON;

And replaces all references to _0x3bbd10 with JSON throughout the AST.
Works without scope analysis by scanning for VariableDeclarator nodes.
"""

from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import make_identifier
from .base import Transform


_WELL_KNOWN_GLOBALS = frozenset(
    {
        'JSON',
        'Object',
        'Array',
        'String',
        'Number',
        'Boolean',
        'Math',
        'Date',
        'RegExp',
        'Error',
        'Map',
        'Set',
        'WeakMap',
        'WeakSet',
        'Promise',
        'Symbol',
        'Proxy',
        'Reflect',
        'console',
        'parseInt',
        'parseFloat',
        'isNaN',
        'isFinite',
        'Buffer',
        'process',
        'require',
    }
)


class GlobalAliasInliner(Transform):
    """Replace aliases of well-known globals with the global name."""

    def execute(self):
        aliases = {}

        # Phase 1: Find `var X = GLOBAL` patterns
        def find_aliases(node, parent, key, index):
            if node.get('type') != 'VariableDeclarator':
                return
            decl_id = node.get('id')
            init = node.get('init')
            if not is_identifier(decl_id) or not is_identifier(init):
                return
            if init['name'] in _WELL_KNOWN_GLOBALS:
                aliases[decl_id['name']] = init['name']

        traverse(self.ast, {'enter': find_aliases})

        if not aliases:
            return False

        # Also find assignment aliases: X = GLOBAL (not just var X = GLOBAL)
        def find_assignment_aliases(node, parent, key, index):
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return
            left = node.get('left')
            right = node.get('right')
            if not is_identifier(left) or not is_identifier(right):
                return
            if right['name'] in _WELL_KNOWN_GLOBALS:
                aliases[left['name']] = right['name']

        traverse(self.ast, {'enter': find_assignment_aliases})

        # Phase 2: Replace all references
        def replace_refs(node, parent, key, index):
            if not is_identifier(node):
                return
            # Skip non-computed property names
            if parent and parent.get('type') == 'MemberExpression' and key == 'property' and not parent.get('computed'):
                return
            # Skip declaration targets
            if parent and parent.get('type') == 'VariableDeclarator' and key == 'id':
                return
            # Skip assignment left-hand sides
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return
            # Skip function/method names
            if parent and parent.get('type') in ('FunctionDeclaration', 'FunctionExpression') and key == 'id':
                return
            # Skip property keys
            if parent and parent.get('type') == 'Property' and key == 'key' and not parent.get('computed'):
                return

            name = node.get('name')
            if name in aliases:
                self.set_changed()
                return make_identifier(aliases[name])

        traverse(self.ast, {'enter': replace_refs})
        return self.has_changed()
