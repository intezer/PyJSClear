"""ESTree AST traversal with visitor pattern."""

from .utils.ast_helpers import _CHILD_KEYS
from .utils.ast_helpers import get_child_keys


# Sentinel to signal node removal
REMOVE = object()
# Sentinel to skip traversing children
SKIP = object()

# Local aliases for hot-path performance (~15% faster traversal)
_dict = dict
_list = list
_isinstance = isinstance


def traverse(node, visitor):
    """Traverse an ESTree AST calling visitor callbacks.

    visitor should be a dict or object with optional 'enter' and 'exit' callables.
    Each callback receives (node, parent, key, index) and can return:
      - None: continue normally
      - REMOVE: remove this node from parent
      - SKIP: (enter only) skip traversing children
      - a dict (node): replace this node with the returned node
    """
    if _isinstance(visitor, _dict):
        enter_fn = visitor.get('enter')
        exit_fn = visitor.get('exit')
    else:
        enter_fn = getattr(visitor, 'enter', None)
        exit_fn = getattr(visitor, 'exit', None)

    child_keys_map = _CHILD_KEYS
    _REMOVE = REMOVE
    _SKIP = SKIP

    def _visit(current_node, parent, key, index):
        node_type = current_node.get('type')
        if node_type is None:
            return current_node

        # Enter
        if enter_fn:
            result = enter_fn(current_node, parent, key, index)
            if result is _REMOVE:
                return _REMOVE
            if result is _SKIP:
                if not exit_fn:
                    return current_node
                exit_result = exit_fn(current_node, parent, key, index)
                if exit_result is _REMOVE:
                    return _REMOVE
                if _isinstance(exit_result, _dict) and 'type' in exit_result:
                    return exit_result
                return current_node
            if _isinstance(result, _dict) and 'type' in result:
                current_node = result
                if parent is not None:
                    if index is not None:
                        parent[key][index] = current_node
                    else:
                        parent[key] = current_node

        # Visit children
        child_keys = child_keys_map.get(current_node.get('type'))
        if child_keys is None:
            child_keys = get_child_keys(current_node)
        for child_key in child_keys:
            child = current_node.get(child_key)
            if child is None:
                continue
            if _isinstance(child, _list):
                i = 0
                while i < len(child):
                    item = child[i]
                    if _isinstance(item, _dict) and 'type' in item:
                        result = _visit(item, current_node, child_key, i)
                        if result is _REMOVE:
                            child.pop(i)
                            continue
                        elif result is not item:
                            child[i] = result
                    i += 1
            elif _isinstance(child, _dict) and 'type' in child:
                result = _visit(child, current_node, child_key, None)
                if result is _REMOVE:
                    current_node[child_key] = None
                elif result is not child:
                    current_node[child_key] = result

        # Exit
        if exit_fn:
            result = exit_fn(current_node, parent, key, index)
            if result is _REMOVE:
                return _REMOVE
            if _isinstance(result, _dict) and 'type' in result:
                return result

        return current_node

    _visit(node, None, None, None)


def simple_traverse(node, callback):
    """Simple traversal that calls callback(node, parent) for every node.
    No replacement support - just visiting.
    """
    child_keys_map = _CHILD_KEYS

    def _visit(current_node, parent):
        node_type = current_node.get('type')
        if node_type is None:
            return
        callback(current_node, parent)
        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = get_child_keys(current_node)
        for key in child_keys:
            child = current_node.get(key)
            if child is None:
                continue
            if _isinstance(child, _list):
                for item in child:
                    if _isinstance(item, _dict) and 'type' in item:
                        _visit(item, current_node)
            elif _isinstance(child, _dict) and 'type' in child:
                _visit(child, current_node)

    _visit(node, None)


def collect_nodes(ast, node_type):
    """Collect all nodes of a given type."""
    result = []

    def cb(node, parent):
        if node.get('type') == node_type:
            result.append(node)

    simple_traverse(ast, cb)
    return result


class _FoundParent(Exception):
    """Raised to short-circuit find_parent search."""

    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


def find_parent(ast, target_node):
    """Find the parent of a node in the AST. Returns (parent, key, index) or None."""

    def _visit(node):
        if not isinstance(node, dict) or 'type' not in node:
            return
        for child_key in get_child_keys(node):
            child = node.get(child_key)
            if child is None:
                continue
            if isinstance(child, list):
                for i, item in enumerate(child):
                    if item is target_node:
                        raise _FoundParent((node, child_key, i))
                    _visit(item)
            elif isinstance(child, dict):
                if child is target_node:
                    raise _FoundParent((node, child_key, None))
                _visit(child)

    try:
        _visit(ast)
    except _FoundParent as found:
        return found.value
    return None


def replace_in_parent(parent, key, index, new_node):
    """Replace a node within its parent."""
    if index is not None:
        parent[key][index] = new_node
    else:
        parent[key] = new_node


def remove_from_parent(parent, key, index):
    """Remove a node from its parent."""
    if index is not None:
        parent[key].pop(index)
    else:
        parent[key] = None
