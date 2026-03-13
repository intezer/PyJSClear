"""ESTree AST traversal with visitor pattern."""

from collections.abc import Callable
from typing import Any

from .utils.ast_helpers import _CHILD_KEYS
from .utils.ast_helpers import get_child_keys


# Sentinel to signal node removal
REMOVE = object()
# Sentinel to skip traversing children
SKIP = object()

# Local aliases for hot-path performance (~15% faster traversal)
_dict = dict
_list = list
_type = type

# Maximum recursion depth before falling back to iterative traversal.
# CPython default recursion limit is ~1000; we switch well before that.
_MAX_RECURSIVE_DEPTH = 500

# Stack frame opcodes for iterative traverse
_OP_ENTER = 0
_OP_EXIT = 1
_OP_LIST_START = 2
_OP_LIST_RESUME = 3


def _traverse_iterative(node: dict, enter_fn: Callable | None, exit_fn: Callable | None) -> None:
    """Iterative stack-based traverse. Handles both enter and exit callbacks."""
    child_keys_map = _CHILD_KEYS
    _REMOVE = REMOVE
    _SKIP = SKIP
    _get_child_keys = get_child_keys

    stack = [(_OP_ENTER, node, None, None, None)]
    stack_pop = stack.pop
    stack_append = stack.append

    while stack:
        frame = stack_pop()
        op = frame[0]

        if op == _OP_ENTER:
            current_node = frame[1]
            parent = frame[2]
            key = frame[3]
            index = frame[4]

            node_type = current_node.get('type')
            if node_type is None:
                continue

            if enter_fn:
                result = enter_fn(current_node, parent, key, index)
                if result is _REMOVE:
                    if parent is not None:
                        if index is not None:
                            parent[key].pop(index)
                        else:
                            parent[key] = None
                    continue
                if result is _SKIP:
                    if exit_fn:
                        exit_result = exit_fn(current_node, parent, key, index)
                        if exit_result is _REMOVE:
                            if parent is not None:
                                if index is not None:
                                    parent[key].pop(index)
                                else:
                                    parent[key] = None
                        elif _type(exit_result) is _dict and 'type' in exit_result:
                            if parent is not None:
                                if index is not None:
                                    parent[key][index] = exit_result
                                else:
                                    parent[key] = exit_result
                    continue
                if _type(result) is _dict and 'type' in result:
                    current_node = result
                    if parent is not None:
                        if index is not None:
                            parent[key][index] = current_node
                        else:
                            parent[key] = current_node
                    node_type = current_node.get('type')

            if exit_fn:
                stack_append((_OP_EXIT, current_node, parent, key, index))

            child_keys = child_keys_map.get(node_type)
            if child_keys is None:
                child_keys = _get_child_keys(current_node)

            for index in range(len(child_keys) - 1, -1, -1):
                child_key = child_keys[index]
                child = current_node.get(child_key)
                if child is None:
                    continue
                if _type(child) is _list:
                    stack_append((_OP_LIST_START, current_node, child_key, 0, None))
                elif _type(child) is _dict and 'type' in child:
                    stack_append((_OP_ENTER, child, current_node, child_key, None))

        elif op == _OP_EXIT:
            current_node = frame[1]
            parent = frame[2]
            key = frame[3]
            index = frame[4]
            result = exit_fn(current_node, parent, key, index)
            if result is _REMOVE:
                if parent is not None:
                    if index is not None:
                        parent[key].pop(index)
                    else:
                        parent[key] = None
            elif _type(result) is _dict and 'type' in result:
                if parent is not None:
                    if index is not None:
                        parent[key][index] = result
                    else:
                        parent[key] = result

        elif op == _OP_LIST_START:
            parent_node = frame[1]
            child_key = frame[2]
            idx = frame[3]
            child_list = parent_node[child_key]
            if idx >= len(child_list):
                continue
            item = child_list[idx]
            if _type(item) is _dict and 'type' in item:
                stack_append((_OP_LIST_RESUME, parent_node, child_key, idx, len(child_list)))
                stack_append((_OP_ENTER, item, parent_node, child_key, idx))
            else:
                stack_append((_OP_LIST_START, parent_node, child_key, idx + 1, None))

        else:  # _OP_LIST_RESUME
            parent_node = frame[1]
            child_key = frame[2]
            idx = frame[3]
            pre_len = frame[4]
            child_list = parent_node[child_key]
            current_len = len(child_list)
            if current_len < pre_len:
                next_idx = idx
            else:
                next_idx = idx + 1
            if next_idx < current_len:
                stack_append((_OP_LIST_START, parent_node, child_key, next_idx, None))


def _traverse_enter_only(node: dict, enter_fn: Callable) -> None:
    """Recursive enter-only traverse with depth-limited fallback to iterative."""
    child_keys_map = _CHILD_KEYS
    _REMOVE = REMOVE
    _SKIP = SKIP
    _get_child_keys = get_child_keys
    _max_depth = _MAX_RECURSIVE_DEPTH

    def _visit(current_node: dict, parent: dict | None, key: str | None, index: int | None, depth: int) -> None:
        node_type = current_node['type']
        if node_type is None:
            return

        result = enter_fn(current_node, parent, key, index)
        if result is _REMOVE:
            if parent is not None:
                if index is not None:
                    parent[key].pop(index)
                else:
                    parent[key] = None
            return
        if result is _SKIP:
            return
        if _type(result) is _dict and 'type' in result:
            current_node = result
            if parent is not None:
                if index is not None:
                    parent[key][index] = current_node
                else:
                    parent[key] = current_node
            node_type = current_node['type']

        # Depth check: fall back to iterative for deep subtrees
        if depth > _max_depth:
            _traverse_iterative(current_node, enter_fn, None)
            return

        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(current_node)

        next_depth = depth + 1
        for child_key in child_keys:
            child = current_node.get(child_key)
            if child is None:
                continue
            if _type(child) is _list:
                child_len = len(child)
                i = 0
                while i < child_len:
                    item = child[i]
                    if _type(item) is _dict and 'type' in item:
                        _visit(item, current_node, child_key, i, next_depth)
                        new_len = len(child)
                        if new_len < child_len:
                            child_len = new_len
                            continue
                        child_len = new_len
                    i += 1
            elif _type(child) is _dict and 'type' in child:
                _visit(child, current_node, child_key, None, next_depth)

    if _type(node) is _dict and 'type' in node:
        _visit(node, None, None, None, 0)


def traverse(node: dict, visitor: dict | object) -> None:
    """Traverse an ESTree AST calling visitor callbacks.

    visitor should be a dict or object with optional 'enter' and 'exit' callables.
    Each callback receives (node, parent, key, index) and can return:
      - None: continue normally
      - REMOVE: remove this node from parent
      - SKIP: (enter only) skip traversing children
      - a dict (node): replace this node with the returned node

    Uses recursive traversal for enter-only visitors (fast path) with
    automatic fallback to iterative for deep subtrees. Uses iterative
    traversal when an exit callback is present.
    """
    if isinstance(visitor, _dict):
        enter_fn = visitor.get('enter')
        exit_fn = visitor.get('exit')
    else:
        enter_fn = getattr(visitor, 'enter', None)
        exit_fn = getattr(visitor, 'exit', None)

    if exit_fn is None and enter_fn is not None:
        _traverse_enter_only(node, enter_fn)
    else:
        _traverse_iterative(node, enter_fn, exit_fn)


def _simple_traverse_iterative(node: dict, callback: Callable) -> None:
    """Iterative stack-based simple traversal."""
    child_keys_map = _CHILD_KEYS
    _get_child_keys = get_child_keys

    stack = [(node, None)]
    stack_pop = stack.pop
    stack_append = stack.append

    while stack:
        current_node, parent = stack_pop()
        node_type = current_node['type']
        if node_type is None:
            continue
        callback(current_node, parent)
        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(current_node)
        for key in reversed(child_keys):
            child = current_node.get(key)
            if child is None:
                continue
            if _type(child) is _list:
                for i in range(len(child) - 1, -1, -1):
                    item = child[i]
                    if _type(item) is _dict and 'type' in item:
                        stack_append((item, current_node))
            elif _type(child) is _dict and 'type' in child:
                stack_append((child, current_node))


def _simple_traverse_recursive(node: dict, callback: Callable) -> None:
    """Recursive simple traversal with depth-limited fallback to iterative."""
    child_keys_map = _CHILD_KEYS
    _get_child_keys = get_child_keys
    _max_depth = _MAX_RECURSIVE_DEPTH

    def _visit(current_node: dict, parent: dict | None, depth: int) -> None:
        node_type = current_node['type']
        if node_type is None:
            return
        callback(current_node, parent)

        if depth > _max_depth:
            # Fall back to iterative for this subtree's children
            child_keys = child_keys_map.get(node_type)
            if child_keys is None:
                child_keys = _get_child_keys(current_node)
            for key in child_keys:
                child = current_node.get(key)
                if child is None:
                    continue
                if _type(child) is _list:
                    for item in child:
                        if _type(item) is _dict and 'type' in item:
                            _simple_traverse_iterative(item, callback)
                elif _type(child) is _dict and 'type' in child:
                    _simple_traverse_iterative(child, callback)
            return

        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(current_node)
        next_depth = depth + 1
        for key in child_keys:
            child = current_node.get(key)
            if child is None:
                continue
            if _type(child) is _list:
                for item in child:
                    if _type(item) is _dict and 'type' in item:
                        _visit(item, current_node, next_depth)
            elif _type(child) is _dict and 'type' in child:
                _visit(child, current_node, next_depth)

    if _type(node) is _dict and 'type' in node:
        _visit(node, None, 0)


def simple_traverse(node: dict, callback: Callable) -> None:
    """Simple traversal that calls callback(node, parent) for every node.
    No replacement support - just visiting.

    Uses recursive traversal with automatic fallback to iterative for deep subtrees.
    """
    _simple_traverse_recursive(node, callback)


def collect_nodes(ast: dict, node_type: str) -> list[dict]:
    """Collect all nodes of a given type."""
    collected = []

    def collect_callback(node: dict, parent: dict | None) -> None:
        if node.get('type') == node_type:
            collected.append(node)

    simple_traverse(ast, collect_callback)
    return collected


def build_parent_map(ast: dict) -> dict:
    """Build a map from id(node) -> (parent, key, index) for all nodes in the AST.

    This allows O(1) parent lookups instead of O(n) find_parent() calls.
    """
    parent_map = {}
    child_keys_map = _CHILD_KEYS
    _get_child_keys = get_child_keys

    stack = [(ast, None, None, None)]
    while stack:
        current_node, parent, key, index = stack.pop()
        node_type = current_node['type']
        if node_type is None:
            continue
        parent_map[id(current_node)] = (parent, key, index)
        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(current_node)
        for child_key in child_keys:
            child = current_node.get(child_key)
            if child is None:
                continue
            if _type(child) is _list:
                for i in range(len(child) - 1, -1, -1):
                    item = child[i]
                    if _type(item) is _dict and 'type' in item:
                        stack.append((item, current_node, child_key, i))
            elif _type(child) is _dict and 'type' in child:
                stack.append((child, current_node, child_key, None))

    return parent_map


class _FoundParent(Exception):
    """Raised to short-circuit find_parent search."""

    __slots__ = ('value',)

    def __init__(self, value: tuple) -> None:
        self.value = value


def find_parent(ast: dict, target_node: dict) -> tuple | None:
    """Find the parent of a node in the AST. Returns (parent, key, index) or None.

    For multiple lookups, consider using build_parent_map() instead.
    """

    def _visit(node: dict) -> None:
        if not isinstance(node, dict) or 'type' not in node:
            return
        for child_key in get_child_keys(node):
            child = node.get(child_key)
            if child is None:
                continue
            if isinstance(child, list):
                for child_index, item in enumerate(child):
                    if item is target_node:
                        raise _FoundParent((node, child_key, child_index))
                    _visit(item)
            elif isinstance(child, dict):
                if child is target_node:
                    raise _FoundParent((node, child_key, None))
                _visit(child)

    try:
        _visit(ast)
    except _FoundParent as found_parent:
        return found_parent.value
    return None


def replace_in_parent(parent: dict, key: str, index: int | None, new_node: dict) -> None:
    """Replace a node within its parent."""
    if index is not None:
        parent[key][index] = new_node
    else:
        parent[key] = new_node


def remove_from_parent(parent: dict, key: str, index: int | None) -> None:
    """Remove a node from its parent."""
    if index is not None:
        parent[key].pop(index)
    else:
        parent[key] = None
