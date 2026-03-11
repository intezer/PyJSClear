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

    def execute(self):
        # Phase 1: Find all obj.PROP = value statements and all obj.PROP reads.
        # Also track which objects "escape" (are assigned to external refs, passed as
        # function arguments, or returned) — their properties may be read externally.
        writes = {}  # (obj_name, prop_name) -> count
        reads = set()  # set of (obj_name, prop_name)
        escaped = set()  # set of obj_name that escape

        # Phase 0: Collect locally declared variable names (var/let/const).
        # Only properties on locally declared objects are candidates for removal.
        local_vars = set()

        def collect_locals(node, parent):
            if not isinstance(node, dict):
                return
            t = node.get('type')
            if t == 'VariableDeclarator':
                vid = node.get('id')
                if vid and is_identifier(vid):
                    local_vars.add(vid['name'])
            # Function/arrow params are externally provided — mark as escaped
            if t in ('FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'):
                for param in node.get('params', []):
                    if is_identifier(param):
                        escaped.add(param['name'])

        simple_traverse(self.ast, collect_locals)

        def collect(node, parent):
            if not isinstance(node, dict):
                return
            t = node.get('type')

            # Track identifiers that escape
            if t == 'Identifier' and parent:
                name = node.get('name', '')
                if name in _GLOBAL_OBJECTS:
                    escaped.add(name)
                pt = parent.get('type')
                # RHS of assignment to a member (e.g., r.exports = obj)
                if pt == 'AssignmentExpression' and node is parent.get('right'):
                    left = parent.get('left')
                    if left and left.get('type') == 'MemberExpression':
                        escaped.add(name)
                # Function/method argument
                if pt == 'CallExpression' or pt == 'NewExpression':
                    args = parent.get('arguments', [])
                    if node in args:
                        escaped.add(name)
                # Return value
                if pt == 'ReturnStatement':
                    escaped.add(name)

            # Track member access patterns
            if t != 'MemberExpression':
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
        def remove_dead(node, parent, key, index):
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
            if pair in dead_props:
                # Only remove if the RHS is side-effect-free
                rhs = expr.get('right')
                if self._is_side_effect_free(rhs):
                    self.set_changed()
                    return REMOVE

        traverse(self.ast, {'enter': remove_dead})
        return self.has_changed()

    @staticmethod
    def _is_side_effect_free(node):
        """Check if an expression node is side-effect-free (safe to remove)."""
        if not node:
            return False
        t = node.get('type')
        if t == 'Literal':
            return True
        if t == 'Identifier':
            return True
        if t == 'MemberExpression':
            return True
        if t == 'UnaryExpression':
            op = node.get('operator')
            if op in ('-', '+', '!', '~', 'typeof', 'void'):
                return DeadObjectPropRemover._is_side_effect_free(node.get('argument'))
        if t == 'BinaryExpression':
            return DeadObjectPropRemover._is_side_effect_free(
                node.get('left')
            ) and DeadObjectPropRemover._is_side_effect_free(node.get('right'))
        if t == 'ArrayExpression':
            return all(DeadObjectPropRemover._is_side_effect_free(el) for el in (node.get('elements') or []) if el)
        if t == 'ObjectExpression':
            for prop in node.get('properties') or []:
                if not DeadObjectPropRemover._is_side_effect_free(prop.get('value')):
                    return False
            return True
        if t == 'TemplateLiteral':
            return all(DeadObjectPropRemover._is_side_effect_free(expr) for expr in (node.get('expressions') or []))
        return False
