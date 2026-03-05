"""ESTree AST traversal with visitor pattern."""

from .utils.ast_helpers import get_child_keys

# Sentinel to signal node removal
REMOVE = object()
# Sentinel to skip traversing children
SKIP = object()


def traverse(node, visitor):
    """Traverse an ESTree AST calling visitor callbacks.

    visitor should be a dict or object with optional 'enter' and 'exit' callables.
    Each callback receives (node, parent, key, index) and can return:
      - None: continue normally
      - REMOVE: remove this node from parent
      - SKIP: (enter only) skip traversing children
      - a dict (node): replace this node with the returned node
    """
    if isinstance(visitor, dict):
        enter_fn = visitor.get('enter')
        exit_fn = visitor.get('exit')
    else:
        enter_fn = getattr(visitor, 'enter', None)
        exit_fn = getattr(visitor, 'exit', None)

    def _visit(node, parent, key, index):
        if not isinstance(node, dict) or 'type' not in node:
            return node

        # Enter
        if enter_fn:
            result = enter_fn(node, parent, key, index)
            if result is REMOVE:
                return REMOVE
            if result is SKIP:
                # Skip children but still call exit
                if exit_fn:
                    exit_result = exit_fn(node, parent, key, index)
                    if exit_result is REMOVE:
                        return REMOVE
                    if isinstance(exit_result, dict) and 'type' in exit_result:
                        return exit_result
                return node
            if isinstance(result, dict) and 'type' in result:
                node = result
                # Update in parent
                if parent is not None:
                    if index is not None:
                        parent[key][index] = node
                    else:
                        parent[key] = node

        # Visit children
        child_keys = get_child_keys(node)
        for ckey in child_keys:
            child = node.get(ckey)
            if child is None:
                continue
            if isinstance(child, list):
                i = 0
                while i < len(child):
                    item = child[i]
                    if isinstance(item, dict) and 'type' in item:
                        result = _visit(item, node, ckey, i)
                        if result is REMOVE:
                            child.pop(i)
                            continue
                        elif isinstance(result, dict) and result is not item:
                            child[i] = result
                    i += 1
            elif isinstance(child, dict) and 'type' in child:
                result = _visit(child, node, ckey, None)
                if result is REMOVE:
                    node[ckey] = None
                elif isinstance(result, dict) and result is not child:
                    node[ckey] = result

        # Exit
        if exit_fn:
            result = exit_fn(node, parent, key, index)
            if result is REMOVE:
                return REMOVE
            if isinstance(result, dict) and 'type' in result:
                return result

        return node

    _visit(node, None, None, None)


def simple_traverse(node, callback):
    """Simple traversal that calls callback(node, parent) for every node.
    No replacement support - just visiting.
    """
    def _visit(n, parent):
        if not isinstance(n, dict) or 'type' not in n:
            return
        callback(n, parent)
        for key in get_child_keys(n):
            child = n.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, dict) and 'type' in item:
                        _visit(item, n)
            elif isinstance(child, dict) and 'type' in child:
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


def find_parent(ast, target_node):
    """Find the parent of a node in the AST. Returns (parent, key, index) or None."""
    result = [None]

    def _visit(n, parent, key, index):
        if n is target_node:
            result[0] = (parent, key, index)
            return
        if not isinstance(n, dict) or 'type' not in n:
            return
        for ckey in get_child_keys(n):
            child = n.get(ckey)
            if child is None:
                continue
            if isinstance(child, list):
                for i, item in enumerate(child):
                    if item is target_node:
                        result[0] = (n, ckey, i)
                        return
                    _visit(item, n, ckey, i)
                    if result[0]:
                        return
            elif isinstance(child, dict):
                if child is target_node:
                    result[0] = (n, ckey, None)
                    return
                _visit(child, n, ckey, None)
                if result[0]:
                    return

    _visit(ast, None, None, None)
    return result[0]


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
