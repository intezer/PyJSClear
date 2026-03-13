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
    """Replace aliases of well-known globals with the global name.

    Note: this transform does not use scope analysis and may incorrectly
    replace references if a local binding shadows the alias name.  This is
    acceptable for the obfuscated code this tool targets, where shadowing
    of mangled variable names is extremely unlikely.
    """

    def _find_var_aliases(self, node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
        """Collect `var alias = GLOBAL` patterns into self._aliases."""
        if node.get('type') != 'VariableDeclarator':
            return
        declaration_id = node.get('id')
        initializer = node.get('init')
        if not is_identifier(declaration_id) or not is_identifier(initializer):
            return
        if initializer['name'] in _WELL_KNOWN_GLOBALS:
            self._aliases[declaration_id['name']] = initializer['name']

    def _find_assignment_aliases(self, node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
        """Collect `alias = GLOBAL` assignment patterns into self._aliases."""
        if node.get('type') != 'AssignmentExpression':
            return
        if node.get('operator') != '=':
            return
        left_node = node.get('left')
        right_node = node.get('right')
        if not is_identifier(left_node) or not is_identifier(right_node):
            return
        if right_node['name'] in _WELL_KNOWN_GLOBALS:
            self._aliases[left_node['name']] = right_node['name']

    def _is_non_reference_position(self, parent: dict | None, key: str | None) -> bool:
        """Return True if the identifier is in a non-reference (definition/key) position."""
        if not parent:
            return False
        parent_type = parent.get('type')
        # Non-computed property name
        if parent_type == 'MemberExpression' and key == 'property' and not parent.get('computed'):
            return True
        # Variable declaration target
        if parent_type == 'VariableDeclarator' and key == 'id':
            return True
        # Assignment left-hand side
        if parent_type == 'AssignmentExpression' and key == 'left':
            return True
        # Function/method name
        if parent_type in ('FunctionDeclaration', 'FunctionExpression') and key == 'id':
            return True
        # Non-computed property key
        if parent_type == 'Property' and key == 'key' and not parent.get('computed'):
            return True
        return False

    def _replace_alias_refs(self, node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
        """Replace aliased identifier references with the global name."""
        if not is_identifier(node):
            return None
        if self._is_non_reference_position(parent, key):
            return None
        name = node.get('name')
        if name in self._aliases:
            self.set_changed()
            return make_identifier(self._aliases[name])
        return None

    def execute(self) -> bool:
        self._aliases: dict[str, str] = {}

        # Phase 1: collect `var X = GLOBAL` and `X = GLOBAL` patterns
        traverse(self.ast, {'enter': self._find_var_aliases})

        if not self._aliases:
            return False

        traverse(self.ast, {'enter': self._find_assignment_aliases})

        # Phase 2: replace all alias references
        traverse(self.ast, {'enter': self._replace_alias_refs})
        return self.has_changed()
