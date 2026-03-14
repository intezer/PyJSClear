"""ESTree AST traversal with visitor pattern."""

from collections.abc import Callable
from enum import IntEnum

from .utils.ast_helpers import _CHILD_KEYS
from .utils.ast_helpers import get_child_keys


# Sentinel to signal node removal
REMOVE = object()
# Sentinel to skip traversing children
SKIP = object()

# Local aliases for hot-path performance (~15% faster traversal)
_dict_type = dict
_list_type = list
_builtin_type = type

# Max recursion depth before falling back to iterative traversal.
_MAX_RECURSIVE_DEPTH = 500


class _StackOp(IntEnum):
    """Opcodes for iterative traverse stack frames."""

    ENTER = 0
    EXIT = 1
    LIST_START = 2
    LIST_RESUME = 3


def _apply_remove(parent: dict | None, key: str | None, index: int | None) -> None:
    """Remove a child node from its parent, either by index or by key."""
    if parent is None:
        return
    if index is not None:
        parent[key].pop(index)
    else:
        parent[key] = None


def _apply_replacement(
    parent: dict | None,
    key: str | None,
    index: int | None,
    replacement: dict,
) -> None:
    """Replace a child node in its parent with a replacement node."""
    if parent is None:
        return
    if index is not None:
        parent[key][index] = replacement
    else:
        parent[key] = replacement


def _traverse_iterative(
    node: dict,
    enter_function: Callable | None,
    exit_function: Callable | None,
) -> None:
    """Iterative stack-based AST traverse supporting enter and exit callbacks."""
    child_keys_map = _CHILD_KEYS
    remove_sentinel = REMOVE
    skip_sentinel = SKIP
    get_keys = get_child_keys

    stack: list[tuple] = [(_StackOp.ENTER, node, None, None, None)]
    stack_pop = stack.pop
    stack_append = stack.append

    while stack:
        frame = stack_pop()
        operation = frame[0]

        match operation:
            case _StackOp.ENTER:
                current_node = frame[1]
                parent = frame[2]
                key = frame[3]
                index = frame[4]

                node_type = current_node.get('type')
                if node_type is None:
                    continue

                if enter_function:
                    result = enter_function(current_node, parent, key, index)
                    if result is remove_sentinel:
                        _apply_remove(parent, key, index)
                        continue
                    if result is skip_sentinel:
                        if exit_function:
                            exit_result = exit_function(current_node, parent, key, index)
                            if exit_result is remove_sentinel:
                                _apply_remove(parent, key, index)
                            elif _builtin_type(exit_result) is _dict_type and 'type' in exit_result:
                                _apply_replacement(parent, key, index, exit_result)
                        continue
                    if _builtin_type(result) is _dict_type and 'type' in result:
                        current_node = result
                        _apply_replacement(parent, key, index, current_node)
                        node_type = current_node.get('type')

                if exit_function:
                    stack_append((_StackOp.EXIT, current_node, parent, key, index))

                child_keys = child_keys_map.get(node_type)
                if child_keys is None:
                    child_keys = get_keys(current_node)

                for key_index in range(len(child_keys) - 1, -1, -1):
                    child_key = child_keys[key_index]
                    child = current_node.get(child_key)
                    if child is None:
                        continue
                    if _builtin_type(child) is _list_type:
                        stack_append((_StackOp.LIST_START, current_node, child_key, 0, None))
                    elif _builtin_type(child) is _dict_type and 'type' in child:
                        stack_append((_StackOp.ENTER, child, current_node, child_key, None))

            case _StackOp.EXIT:
                current_node = frame[1]
                parent = frame[2]
                key = frame[3]
                index = frame[4]
                result = exit_function(current_node, parent, key, index)
                if result is remove_sentinel:
                    _apply_remove(parent, key, index)
                elif _builtin_type(result) is _dict_type and 'type' in result:
                    _apply_replacement(parent, key, index, result)

            case _StackOp.LIST_START:
                parent_node = frame[1]
                child_key = frame[2]
                list_index = frame[3]
                child_list = parent_node[child_key]
                if list_index >= len(child_list):
                    continue
                item = child_list[list_index]
                if _builtin_type(item) is _dict_type and 'type' in item:
                    stack_append((_StackOp.LIST_RESUME, parent_node, child_key, list_index, len(child_list)))
                    stack_append((_StackOp.ENTER, item, parent_node, child_key, list_index))
                else:
                    stack_append((_StackOp.LIST_START, parent_node, child_key, list_index + 1, None))

            case _StackOp.LIST_RESUME:
                parent_node = frame[1]
                child_key = frame[2]
                list_index = frame[3]
                previous_length = frame[4]
                child_list = parent_node[child_key]
                current_length = len(child_list)
                next_index = list_index if current_length < previous_length else list_index + 1
                if next_index < current_length:
                    stack_append((_StackOp.LIST_START, parent_node, child_key, next_index, None))


def _traverse_enter_only(node: dict, enter_function: Callable) -> None:
    """Recursive enter-only traverse with depth-limited fallback to iterative."""
    child_keys_map = _CHILD_KEYS
    remove_sentinel = REMOVE
    skip_sentinel = SKIP
    get_keys = get_child_keys
    max_depth = _MAX_RECURSIVE_DEPTH

    def _visit(
        current_node: dict,
        parent: dict | None,
        key: str | None,
        index: int | None,
        depth: int,
    ) -> None:
        node_type = current_node['type']
        if node_type is None:
            return

        result = enter_function(current_node, parent, key, index)
        if result is remove_sentinel:
            _apply_remove(parent, key, index)
            return
        if result is skip_sentinel:
            return
        if _builtin_type(result) is _dict_type and 'type' in result:
            current_node = result
            _apply_replacement(parent, key, index, current_node)
            node_type = current_node['type']

        # Fall back to iterative for deep subtrees
        if depth > max_depth:
            _traverse_iterative(current_node, enter_function, None)
            return

        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = get_keys(current_node)

        next_depth = depth + 1
        for child_key in child_keys:
            child = current_node.get(child_key)
            if child is None:
                continue
            if _builtin_type(child) is _list_type:
                child_length = len(child)
                item_index = 0
                while item_index < child_length:
                    item = child[item_index]
                    if _builtin_type(item) is _dict_type and 'type' in item:
                        _visit(item, current_node, child_key, item_index, next_depth)
                        new_length = len(child)
                        if new_length < child_length:
                            child_length = new_length
                            continue
                        child_length = new_length
                    item_index += 1
            elif _builtin_type(child) is _dict_type and 'type' in child:
                _visit(child, current_node, child_key, None, next_depth)

    if _builtin_type(node) is _dict_type and 'type' in node:
        _visit(node, None, None, None, 0)


def traverse(node: dict, visitor: dict | object) -> None:
    """Traverse an ESTree AST calling visitor enter/exit callbacks.

    The visitor can be a dict or object with 'enter' and/or 'exit' callables.
    Callbacks receive (node, parent, key, index) and may return REMOVE, SKIP,
    a replacement node dict, or None to continue normally.

    Uses recursive traversal for enter-only visitors (fast path) with
    automatic fallback to iterative for deep subtrees.
    """
    if isinstance(visitor, _dict_type):
        enter_function = visitor.get('enter')
        exit_function = visitor.get('exit')
    else:
        enter_function = getattr(visitor, 'enter', None)
        exit_function = getattr(visitor, 'exit', None)

    if exit_function is None and enter_function is not None:
        _traverse_enter_only(node, enter_function)
    else:
        _traverse_iterative(node, enter_function, exit_function)


def _simple_traverse_iterative(node: dict, callback: Callable) -> None:
    """Iterative stack-based simple traversal without replacement support."""
    child_keys_map = _CHILD_KEYS
    get_keys = get_child_keys

    stack: list[tuple[dict, dict | None]] = [(node, None)]
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
            child_keys = get_keys(current_node)
        for key in reversed(child_keys):
            child = current_node.get(key)
            if child is None:
                continue
            if _builtin_type(child) is _list_type:
                for item_index in range(len(child) - 1, -1, -1):
                    item = child[item_index]
                    if _builtin_type(item) is _dict_type and 'type' in item:
                        stack_append((item, current_node))
            elif _builtin_type(child) is _dict_type and 'type' in child:
                stack_append((child, current_node))


def _simple_traverse_recursive(node: dict, callback: Callable) -> None:
    """Recursive simple traversal with depth-limited fallback to iterative."""
    child_keys_map = _CHILD_KEYS
    get_keys = get_child_keys
    max_depth = _MAX_RECURSIVE_DEPTH

    def _visit(current_node: dict, parent: dict | None, depth: int) -> None:
        node_type = current_node['type']
        if node_type is None:
            return
        callback(current_node, parent)

        if depth > max_depth:
            # Fall back to iterative for deep subtrees
            child_keys = child_keys_map.get(node_type)
            if child_keys is None:
                child_keys = get_keys(current_node)
            for key in child_keys:
                child = current_node.get(key)
                if child is None:
                    continue
                if _builtin_type(child) is _list_type:
                    for item in child:
                        if _builtin_type(item) is _dict_type and 'type' in item:
                            _simple_traverse_iterative(item, callback)
                elif _builtin_type(child) is _dict_type and 'type' in child:
                    _simple_traverse_iterative(child, callback)
            return

        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = get_keys(current_node)
        next_depth = depth + 1
        for key in child_keys:
            child = current_node.get(key)
            if child is None:
                continue
            if _builtin_type(child) is _list_type:
                for item in child:
                    if _builtin_type(item) is _dict_type and 'type' in item:
                        _visit(item, current_node, next_depth)
            elif _builtin_type(child) is _dict_type and 'type' in child:
                _visit(child, current_node, next_depth)

    if _builtin_type(node) is _dict_type and 'type' in node:
        _visit(node, None, 0)


def simple_traverse(node: dict, callback: Callable) -> None:
    """Visit every node in the AST via callback(node, parent). No replacement support."""
    _simple_traverse_recursive(node, callback)


def collect_nodes(ast: dict, node_type: str) -> list[dict]:
    """Return all nodes matching the given type string."""
    collected: list[dict] = []

    def collect_callback(node: dict, parent: dict | None) -> None:
        if node.get('type') == node_type:
            collected.append(node)

    simple_traverse(ast, collect_callback)
    return collected


def build_parent_map(ast: dict) -> dict[int, tuple[dict | None, str | None, int | None]]:
    """Build a mapping of id(node) -> (parent, key, index) for O(1) parent lookups."""
    parent_map: dict[int, tuple[dict | None, str | None, int | None]] = {}
    child_keys_map = _CHILD_KEYS
    get_keys = get_child_keys

    stack: list[tuple] = [(ast, None, None, None)]
    while stack:
        current_node, parent, key, index = stack.pop()
        node_type = current_node['type']
        if node_type is None:
            continue
        parent_map[id(current_node)] = (parent, key, index)
        child_keys = child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = get_keys(current_node)
        for child_key in child_keys:
            child = current_node.get(child_key)
            if child is None:
                continue
            if _builtin_type(child) is _list_type:
                for item_index in range(len(child) - 1, -1, -1):
                    item = child[item_index]
                    if _builtin_type(item) is _dict_type and 'type' in item:
                        stack.append((item, current_node, child_key, item_index))
            elif _builtin_type(child) is _dict_type and 'type' in child:
                stack.append((child, current_node, child_key, None))

    return parent_map


class _FoundParent(Exception):
    """Raised to short-circuit find_parent search."""

    __slots__ = ('value',)

    def __init__(self, value: tuple[dict, str, int | None]) -> None:
        self.value = value


def find_parent(ast: dict, target_node: dict) -> tuple[dict, str, int | None] | None:
    """Find the parent of target_node in the AST.

    Returns (parent, key, index) or None. For repeated lookups, prefer
    build_parent_map() instead.
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
    except _FoundParent as found:
        return found.value
    return None


def replace_in_parent(parent: dict, key: str, index: int | None, new_node: dict) -> None:
    """Replace a child node in its parent with new_node."""
    if index is not None:
        parent[key][index] = new_node
    else:
        parent[key] = new_node


def remove_from_parent(parent: dict, key: str, index: int | None) -> None:
    """Remove a child node from its parent by key and optional index."""
    if index is not None:
        parent[key].pop(index)
    else:
        parent[key] = None
