"""Remove dead object property assignments.

Detects patterns like:
    var v = {};
    v.FOO = "bar";
    v.BAZ = 123;
    // v.FOO and v.BAZ are never read

And removes the assignment statements when the property is only written, never read.
"""

from __future__ import annotations

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_side_effect_free
from .base import Transform


# Pair of (object_name, property_name) for tracking member accesses.
type PropertyPair = tuple[str, str]

# Objects that may be externally observed; never remove their property assignments.
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

# AST node types whose parameters are externally provided.
_FUNCTION_NODE_TYPES = frozenset(
    {
        'FunctionDeclaration',
        'FunctionExpression',
        'ArrowFunctionExpression',
    }
)

# AST node types that pass identifiers as arguments.
_CALL_NODE_TYPES = frozenset(
    {
        'CallExpression',
        'NewExpression',
    }
)


def _collect_local_variables(
    node: dict,
    _parent: dict | None,
    local_variables: set[str],
    escaped_names: set[str],
) -> None:
    """Record locally declared variable names and mark function params as escaped."""
    if not isinstance(node, dict):
        return
    node_type = node.get('type')
    if node_type == 'VariableDeclarator':
        variable_id = node.get('id')
        if variable_id and is_identifier(variable_id):
            local_variables.add(variable_id['name'])
    if node_type in _FUNCTION_NODE_TYPES:
        for parameter in node.get('params', []):
            if is_identifier(parameter):
                escaped_names.add(parameter['name'])


def _track_escaped_identifier(
    node: dict,
    parent: dict,
    escaped_names: set[str],
) -> None:
    """Mark an identifier as escaped if it flows to an external context."""
    identifier_name = node.get('name', '')
    if identifier_name in _GLOBAL_OBJECTS:
        escaped_names.add(identifier_name)

    parent_type = parent.get('type')

    # RHS of assignment to a member (e.g., r.exports = object_ref)
    if parent_type == 'AssignmentExpression' and node is parent.get('right'):
        left_side = parent.get('left')
        if left_side and left_side.get('type') == 'MemberExpression':
            escaped_names.add(identifier_name)

    # Function/method argument
    if parent_type in _CALL_NODE_TYPES:
        if node in parent.get('arguments', []):
            escaped_names.add(identifier_name)

    # Return value
    if parent_type == 'ReturnStatement':
        escaped_names.add(identifier_name)


def _extract_member_pair(node: dict) -> PropertyPair | None:
    """Extract (object_name, property_name) from a non-computed MemberExpression."""
    if node.get('computed'):
        return None
    object_node = node.get('object')
    property_node = node.get('property')
    if not object_node or not is_identifier(object_node):
        return None
    if not property_node or not is_identifier(property_node):
        return None
    return (object_node['name'], property_node['name'])


def _collect_member_accesses(
    node: dict,
    parent: dict | None,
    write_counts: dict[PropertyPair, int],
    read_pairs: set[PropertyPair],
    escaped_names: set[str],
) -> None:
    """Collect member property writes, reads, and escaped identifiers."""
    if not isinstance(node, dict):
        return
    node_type = node.get('type')

    if node_type == 'Identifier' and parent:
        _track_escaped_identifier(node, parent, escaped_names)
        return

    if node_type != 'MemberExpression':
        return

    member_pair = _extract_member_pair(node)
    if member_pair is None:
        return

    # Write (assignment target) vs read
    if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
        write_counts[member_pair] = write_counts.get(member_pair, 0) + 1
    else:
        read_pairs.add(member_pair)


def _is_removable_dead_assignment(
    node: dict,
    dead_properties: set[PropertyPair],
) -> bool:
    """Check whether a node is a dead property assignment that can be removed."""
    if node.get('type') != 'ExpressionStatement':
        return False
    expression = node.get('expression')
    if not expression or expression.get('type') != 'AssignmentExpression':
        return False
    left_side = expression.get('left')
    if not left_side or left_side.get('type') != 'MemberExpression' or left_side.get('computed'):
        return False

    member_pair = _extract_member_pair(left_side)
    if member_pair is None or member_pair not in dead_properties:
        return False

    right_side = expression.get('right')
    return is_side_effect_free(right_side)


class DeadObjectPropRemover(Transform):
    """Remove object property assignments where the property is never read."""

    def execute(self) -> bool:
        """Scan for write-only object properties and remove their assignments."""
        write_counts: dict[PropertyPair, int] = {}
        read_pairs: set[PropertyPair] = set()
        escaped_names: set[str] = set()
        local_variables: set[str] = set()

        # Phase 1: collect locally declared variables and mark function params as escaped.
        simple_traverse(
            self.ast,
            lambda node, parent: _collect_local_variables(
                node,
                parent,
                local_variables,
                escaped_names,
            ),
        )

        # Phase 2: collect member property writes, reads, and escaped identifiers.
        simple_traverse(
            self.ast,
            lambda node, parent: _collect_member_accesses(
                node,
                parent,
                write_counts,
                read_pairs,
                escaped_names,
            ),
        )

        # Find properties that are written but never read on local, non-escaped objects.
        dead_properties: set[PropertyPair] = {
            property_pair
            for property_pair in write_counts
            if property_pair not in read_pairs
            and property_pair[0] in local_variables
            and property_pair[0] not in escaped_names
        }
        if not dead_properties:
            return False

        # Phase 3: remove dead assignment statements.
        def remove_dead(
            node: dict,
            _parent: dict | None,
            _key: str | None,
            _index: int | None,
        ) -> object | None:
            """Traverse callback that removes dead property assignments."""
            if _is_removable_dead_assignment(node, dead_properties):
                self.set_changed()
                return REMOVE
            return None

        traverse(self.ast, {'enter': remove_dead})
        return self.has_changed()
