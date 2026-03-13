"""Remove dead object property assignments.

Detects patterns like:
    var v = {};
    v.FOO = "bar";
    v.BAZ = 123;
    // v.FOO and v.BAZ are never read

And removes the assignment statements when the property is only written, never read.
"""

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_side_effect_free
from .base import Transform


# Objects that may be externally observed — never remove their property assignments.
_GLOBAL_OBJECTS = frozenset(
    {
        'module',
        'exports',
        'window',
        'global',
        'globalThis',
        'self',
        'document',
        'console',
        'process',
        'require',
        'Object',
        'Array',
        'Math',
        'JSON',
        'Date',
        'RegExp',
        'Error',
        'Promise',
        'Symbol',
    }
)


class DeadObjectPropRemover(Transform):
    """Remove object property assignments where the property is never read."""

    def execute(self) -> bool:
        # Phase 1: Find all obj.PROP = value statements and all obj.PROP reads.
        # Also track which objects "escape" (are assigned to external refs, passed as
        # function arguments, or returned) — their properties may be read externally.
        writes: dict[tuple[str, str], int] = {}  # (obj_name, prop_name) -> count
        reads: set[tuple[str, str]] = set()  # set of (obj_name, prop_name)
        escaped: set[str] = set()  # set of obj_name that escape

        # Phase 0: Collect locally declared variable names (var/let/const).
        # Only properties on locally declared objects are candidates for removal.
        local_vars: set[str] = set()

        def collect_locals(node: dict, parent: dict | None) -> None:
            if not isinstance(node, dict):
                return
            node_type = node.get('type')
            if node_type == 'VariableDeclarator':
                variable_id = node.get('id')
                if variable_id and is_identifier(variable_id):
                    local_vars.add(variable_id['name'])
            # Function/arrow params are externally provided — mark as escaped
            if node_type in ('FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'):
                for param in node.get('params', []):
                    if is_identifier(param):
                        escaped.add(param['name'])

        simple_traverse(self.ast, collect_locals)

        def collect(node: dict, parent: dict | None) -> None:
            if not isinstance(node, dict):
                return
            node_type = node.get('type')

            # Track identifiers that escape
            if node_type == 'Identifier' and parent:
                name = node.get('name', '')
                if name in _GLOBAL_OBJECTS:
                    escaped.add(name)
                parent_type = parent.get('type')
                # RHS of assignment to a member (e.g., r.exports = obj)
                if parent_type == 'AssignmentExpression' and node is parent.get('right'):
                    left = parent.get('left')
                    if left and left.get('type') == 'MemberExpression':
                        escaped.add(name)
                # Function/method argument
                if parent_type in ('CallExpression', 'NewExpression'):
                    if node in parent.get('arguments', []):
                        escaped.add(name)
                # Return value
                if parent_type == 'ReturnStatement':
                    escaped.add(name)

            # Track member access patterns
            if node_type != 'MemberExpression':
                return
            if node.get('computed'):
                return
            obj = node.get('object')
            prop = node.get('property')
            if not obj or not is_identifier(obj) or not prop or not is_identifier(prop):
                return
            pair = (obj['name'], prop['name'])

            # Check if this is a write (assignment target)
            if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
                writes[pair] = writes.get(pair, 0) + 1
            else:
                reads.add(pair)

        simple_traverse(self.ast, collect)

        # Find properties that are written but never read.
        # Only consider locally declared objects that haven't escaped.
        dead_props = {pair for pair in writes if pair not in reads and pair[0] in local_vars and pair[0] not in escaped}
        if not dead_props:
            return False

        # Phase 2: Remove dead assignment statements
        def remove_dead(node: dict, parent: dict | None, key: str | None, index: int | None) -> object:
            if node.get('type') != 'ExpressionStatement':
                return
            expr = node.get('expression')
            if not expr or expr.get('type') != 'AssignmentExpression':
                return
            left = expr.get('left')
            if not left or left.get('type') != 'MemberExpression' or left.get('computed'):
                return
            obj = left.get('object')
            prop = left.get('property')
            if not obj or not is_identifier(obj) or not prop or not is_identifier(prop):
                return
            pair = (obj['name'], prop['name'])
            if pair not in dead_props:
                return
            # Only remove if the RHS is side-effect-free
            rhs = expr.get('right')
            if is_side_effect_free(rhs):
                self.set_changed()
                return REMOVE

        traverse(self.ast, {'enter': remove_dead})
        return self.has_changed()
