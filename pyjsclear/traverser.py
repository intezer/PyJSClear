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

    def _visit(node, parent, key, index):
        ntype = node.get('type')
        if ntype is None:
            return node

        # Enter
        if enter_fn:
            result = enter_fn(node, parent, key, index)
            if result is _REMOVE:
                return _REMOVE
            if result is _SKIP:
                if not exit_fn:
                    return node
                exit_result = exit_fn(node, parent, key, index)
                if exit_result is _REMOVE:
                    return _REMOVE
                if _isinstance(exit_result, _dict) and 'type' in exit_result:
                    return exit_result
                return node
            if _isinstance(result, _dict) and 'type' in result:
                node = result
                if parent is not None:
                    if index is not None:
                        parent[key][index] = node
                    else:
                        parent[key] = node

        # Visit children
        ckeys = child_keys_map.get(node.get('type'))
        if ckeys is None:
            from .utils.ast_helpers import get_child_keys

            ckeys = get_child_keys(node)
        for ckey in ckeys:
            child = node.get(ckey)
            if child is None:
                continue
            if _isinstance(child, _list):
                i = 0
                while i < len(child):
                    item = child[i]
                    if _isinstance(item, _dict) and 'type' in item:
                        result = _visit(item, node, ckey, i)
                        if result is _REMOVE:
                            child.pop(i)
                            continue
                        elif result is not item:
                            child[i] = result
                    i += 1
            elif _isinstance(child, _dict) and 'type' in child:
                result = _visit(child, node, ckey, None)
                if result is _REMOVE:
                    node[ckey] = None
                elif result is not child:
                    node[ckey] = result

        # Exit
        if exit_fn:
            result = exit_fn(node, parent, key, index)
            if result is _REMOVE:
                return _REMOVE
            if _isinstance(result, _dict) and 'type' in result:
                return result

        return node

    _visit(node, None, None, None)


def simple_traverse(node, callback):
    """Simple traversal that calls callback(node, parent) for every node.
    No replacement support - just visiting.
    """
    child_keys_map = _CHILD_KEYS

    def _visit(n, parent):
        ntype = n.get('type')
        if ntype is None:
            return
        callback(n, parent)
        ckeys = child_keys_map.get(ntype)
        if ckeys is None:
            from .utils.ast_helpers import get_child_keys

            ckeys = get_child_keys(n)
        for key in ckeys:
            child = n.get(key)
            if child is None:
                continue
            if _isinstance(child, _list):
                for item in child:
                    if _isinstance(item, _dict) and 'type' in item:
                        _visit(item, n)
            elif _isinstance(child, _dict) and 'type' in child:
                _visit(child, n)

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
        for ckey in get_child_keys(node):
            child = node.get(ckey)
            if child is None:
                continue
            if isinstance(child, list):
                for i, item in enumerate(child):
                    if item is target_node:
                        raise _FoundParent((node, ckey, i))
                    _visit(item)
            elif isinstance(child, dict):
                if child is target_node:
                    raise _FoundParent((node, ckey, None))
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
