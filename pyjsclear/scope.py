"""Variable scope and binding analysis for ESTree ASTs."""

from collections.abc import Callable
from typing import Any

from .utils.ast_helpers import _CHILD_KEYS
from .utils.ast_helpers import get_child_keys


# Local aliases for hot-path performance
_isinstance = isinstance
_dict = dict
_list = list

# Maximum recursion depth before falling back to iterative traversal.
_MAX_RECURSIVE_DEPTH = 500


class Binding:
    """Represents a variable binding in a scope."""

    __slots__ = ('name', 'node', 'kind', 'scope', 'references', 'assignments')

    def __init__(self, name: str, node: dict, kind: str, scope: 'Scope') -> None:
        self.name = name
        self.node = node  # The declaration node
        self.kind = kind  # 'var', 'let', 'const', 'function', 'param'
        self.scope = scope
        self.references: list = []  # List of (node, parent, key, index) where name is referenced
        self.assignments: list = []  # List of assignment nodes

    @property
    def is_constant(self) -> bool:
        """True if the binding is never reassigned after declaration."""
        if self.kind == 'const':
            return True
        if self.kind == 'function':
            return len(self.assignments) == 0
        # var/let/param: constant if exactly one init and no reassignments
        return len(self.assignments) == 0


class Scope:
    """Represents a lexical scope."""

    __slots__ = ('parent', 'node', 'bindings', 'children', 'is_function')

    def __init__(self, parent: 'Scope | None', node: dict, is_function: bool = False) -> None:
        self.parent = parent
        self.node = node
        self.bindings: dict[str, Binding] = {}  # name -> Binding
        self.children: list['Scope'] = []
        self.is_function = is_function
        if parent:
            parent.children.append(self)

    def add_binding(self, name: str, node: dict, kind: str) -> Binding:
        binding = Binding(name, node, kind, self)
        self.bindings[name] = binding
        return binding

    def get_binding(self, name: str) -> 'Binding | None':
        """Look up a binding, walking up the scope chain."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get_binding(name)
        return None

    def get_own_binding(self, name: str) -> 'Binding | None':
        return self.bindings.get(name)


def _nearest_function_scope(scope: 'Scope | None') -> 'Scope | None':
    """Walk up to the nearest function (or root) scope."""
    while scope and not scope.is_function:
        scope = scope.parent
    return scope


def _is_non_reference_identifier(parent: dict | None, parent_key: str | None) -> bool:
    """Return True if this Identifier usage is not a variable reference."""
    if not parent:
        return False
    match parent.get('type'):
        case 'MemberExpression' if parent_key == 'property' and not parent.get('computed'):
            return True
        case 'Property' if parent_key == 'key' and not parent.get('computed'):
            return True
        case 'FunctionDeclaration' | 'FunctionExpression' | 'ClassDeclaration' | 'ClassExpression' if (
            parent_key == 'id'
        ):
            return True
        case 'VariableDeclarator' if parent_key == 'id':
            return True
    return False


def _collect_pattern_names(
    pattern: dict | None,
    scope: 'Scope',
    kind: str,
    declaration: dict,
) -> None:
    """Collect binding names from destructuring patterns."""
    if not _isinstance(pattern, _dict):
        return
    match pattern.get('type', ''):
        case 'ArrayPattern':
            for element in pattern.get('elements', []):
                if not element:
                    continue
                if element.get('type') == 'Identifier':
                    scope.add_binding(element['name'], declaration, kind)
                else:
                    _collect_pattern_names(element, scope, kind, declaration)
        case 'ObjectPattern':
            for property_node in pattern.get('properties', []):
                value_node = property_node.get('value', property_node.get('argument'))
                if not value_node:
                    continue
                if value_node.get('type') == 'Identifier':
                    scope.add_binding(value_node['name'], declaration, kind)
                else:
                    _collect_pattern_names(value_node, scope, kind, declaration)
        case 'RestElement':
            argument_node = pattern.get('argument')
            if argument_node and argument_node.get('type') == 'Identifier':
                scope.add_binding(argument_node['name'], declaration, kind)
        case 'AssignmentPattern':
            left = pattern.get('left')
            if left and left.get('type') == 'Identifier':
                scope.add_binding(left['name'], declaration, kind)


def _push_children_to_stack(
    node: dict,
    scope: 'Scope',
    stack: list,
    child_keys_map: dict,
) -> None:
    """Push child nodes onto a stack in reversed order for left-to-right processing."""
    node_type = node.get('type')
    child_keys = child_keys_map.get(node_type)
    if child_keys is None:
        child_keys = get_child_keys(node)
    for key in reversed(child_keys):
        child = node.get(key)
        if child is None:
            continue
        if _isinstance(child, _list):
            for index in range(len(child) - 1, -1, -1):
                item = child[index]
                if _isinstance(item, _dict) and 'type' in item:
                    stack.append((item, scope))
        elif _isinstance(child, _dict) and 'type' in child:
            stack.append((child, scope))


def _process_declaration_node(
    node: dict,
    node_type: str,
    scope: 'Scope',
    node_scope: dict[int, 'Scope'],
    all_scopes: list['Scope'],
    push_target: list,
    push_children_fn: Callable,
) -> None:
    """Process a single node for declaration collection.

    push_target: a list to append (node, scope) tuples to.
    push_children_fn: callable(node, scope, push_target) to push child nodes.
    """
    if node_type in ('FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'):
        new_scope = Scope(scope, node, is_function=True)
        node_scope[id(node)] = new_scope
        all_scopes.append(new_scope)

        if node_type == 'FunctionDeclaration' and node.get('id'):
            scope.add_binding(node['id']['name'], node, 'function')
        elif node_type == 'FunctionExpression' and node.get('id'):
            new_scope.add_binding(node['id']['name'], node, 'function')

        for param in node.get('params', []):
            param_type = param.get('type')
            if param_type == 'Identifier':
                new_scope.add_binding(param['name'], param, 'param')
            elif param_type == 'AssignmentPattern':
                left = param.get('left', {})
                if left.get('type') == 'Identifier':
                    new_scope.add_binding(left['name'], param, 'param')
            elif param_type == 'RestElement':
                argument = param.get('argument')
                if argument and argument.get('type') == 'Identifier':
                    new_scope.add_binding(argument['name'], param, 'param')

        body = node.get('body')
        if not body:
            return
        if _isinstance(body, _dict) and body.get('type') == 'BlockStatement':
            node_scope[id(body)] = new_scope
            statements = body.get('body', [])
            for index in range(len(statements) - 1, -1, -1):
                push_target.append((statements[index], new_scope))
        else:
            push_target.append((body, new_scope))

    elif node_type in ('ClassExpression', 'ClassDeclaration'):
        class_id = node.get('id')
        inner_scope = scope
        if class_id and class_id.get('type') == 'Identifier':
            name = class_id['name']
            if node_type == 'ClassDeclaration':
                scope.add_binding(name, node, 'function')
            else:
                inner_scope = Scope(scope, node)
                node_scope[id(node)] = inner_scope
                all_scopes.append(inner_scope)
                inner_scope.add_binding(name, node, 'function')
        superclass = node.get('superClass')
        body = node.get('body')
        if body:
            push_target.append((body, inner_scope))
        if superclass:
            push_target.append((superclass, scope))

    elif node_type == 'VariableDeclaration':
        kind = node.get('kind', 'var')
        target_scope = (_nearest_function_scope(scope) or scope) if kind == 'var' else scope
        declarations = node.get('declarations', [])
        inits_to_push = []
        for declaration in declarations:
            declaration_id = declaration.get('id')
            if declaration_id and declaration_id.get('type') == 'Identifier':
                target_scope.add_binding(declaration_id['name'], declaration, kind)
            _collect_pattern_names(declaration_id, target_scope, kind, declaration)
            init = declaration.get('init')
            if init:
                inits_to_push.append((init, scope))
        for index in range(len(inits_to_push) - 1, -1, -1):
            push_target.append(inits_to_push[index])

    elif node_type == 'BlockStatement' and id(node) not in node_scope:
        new_scope = Scope(scope, node)
        node_scope[id(node)] = new_scope
        all_scopes.append(new_scope)
        statements = node.get('body', [])
        for index in range(len(statements) - 1, -1, -1):
            push_target.append((statements[index], new_scope))

    elif node_type == 'ForStatement':
        new_scope = Scope(scope, node)
        node_scope[id(node)] = new_scope
        all_scopes.append(new_scope)
        if node.get('body'):
            push_target.append((node['body'], new_scope))
        if node.get('init'):
            push_target.append((node['init'], new_scope))

    elif node_type == 'CatchClause':
        catch_body = node.get('body')
        if catch_body and catch_body.get('type') == 'BlockStatement':
            catch_scope = Scope(scope, catch_body)
            node_scope[id(catch_body)] = catch_scope
            all_scopes.append(catch_scope)
            param = node.get('param')
            if param and param.get('type') == 'Identifier':
                catch_scope.add_binding(param['name'], param, 'param')
            statements = catch_body.get('body', [])
            for index in range(len(statements) - 1, -1, -1):
                push_target.append((statements[index], catch_scope))

    else:
        push_children_fn(node, scope, push_target)


def build_scope_tree(ast: dict) -> tuple[Scope, dict[int, Scope]]:
    """Build a scope tree from an AST, collecting bindings and references.

    Returns the root Scope and a dict mapping node id -> Scope.
    Uses recursive traversal with automatic fallback to iterative for deep subtrees.
    """
    root_scope = Scope(None, ast, is_function=True)
    node_scope: dict[int, Scope] = {id(ast): root_scope}
    all_scopes: list[Scope] = [root_scope]

    _child_keys_map = _CHILD_KEYS
    _get_child_keys = get_child_keys
    _max_depth = _MAX_RECURSIVE_DEPTH

    # ---- Pass 1: Collect declarations (recursive with iterative fallback) ----

    def _push_children(node: dict, scope: Scope, target_list: list) -> None:
        """Push child nodes onto a list."""
        node_type = node.get('type')
        child_keys = _child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(node)
        for key in reversed(child_keys):
            child = node.get(key)
            if child is None:
                continue
            if _isinstance(child, _list):
                for index in range(len(child) - 1, -1, -1):
                    item = child[index]
                    if _isinstance(item, _dict) and 'type' in item:
                        target_list.append((item, scope))
            elif _isinstance(child, _dict) and 'type' in child:
                target_list.append((child, scope))

    def _visit_declaration(node: dict, scope: Scope, depth: int) -> None:
        if not _isinstance(node, _dict):
            return
        node_type = node.get('type')
        if node_type is None:
            return

        if depth > _max_depth:
            # Fall back to iterative for this subtree
            _collect_declarations_iterative_from(node, scope)
            return

        # Collect children into a local list, then recurse
        children: list = []
        _process_declaration_node(node, node_type, scope, node_scope, all_scopes, children, _push_children)
        next_depth = depth + 1
        # Children were appended in stack order (reversed), so iterate
        # in reverse to get left-to-right processing order.
        for index in range(len(children) - 1, -1, -1):
            _visit_declaration(children[index][0], children[index][1], next_depth)

    def _collect_declarations_iterative_from(start_node: dict, start_scope: Scope) -> None:
        """Run iterative declaration collection starting from a specific node/scope."""
        decl_stack = [(start_node, start_scope)]
        while decl_stack:
            node, scope = decl_stack.pop()
            if not _isinstance(node, _dict):
                continue
            node_type = node.get('type')
            if node_type is None:
                continue
            _process_declaration_node(
                node, node_type, scope, node_scope, all_scopes, decl_stack, _push_children
            )

    _visit_declaration(ast, root_scope, 0)

    # ---- Pass 2: Collect references (recursive with iterative fallback) ----

    def _visit_reference(
        node: dict,
        scope: Scope,
        parent: dict | None,
        parent_key: str | None,
        parent_index: int | None,
        depth: int,
    ) -> None:
        if not _isinstance(node, _dict):
            return
        node_type = node.get('type')
        if node_type is None:
            return

        node_id = id(node)
        if node_id in node_scope:
            scope = node_scope[node_id]

        if node_type == 'Identifier':
            name = node.get('name', '')
            if _is_non_reference_identifier(parent, parent_key):
                return
            binding = scope.get_binding(name)
            if not binding:
                return
            binding.references.append((node, parent, parent_key, parent_index))
            if parent and parent.get('type') == 'AssignmentExpression' and parent_key == 'left':
                binding.assignments.append(parent)
            elif parent and parent.get('type') == 'UpdateExpression':
                binding.assignments.append(parent)
            return

        if depth > _max_depth:
            _collect_references_iterative_from(node, scope)
            return

        child_keys = _child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(node)
        next_depth = depth + 1
        for key in child_keys:
            child = node.get(key)
            if child is None:
                continue
            if _isinstance(child, _list):
                for child_index, item in enumerate(child):
                    if _isinstance(item, _dict) and 'type' in item:
                        _visit_reference(item, scope, node, key, child_index, next_depth)
            elif _isinstance(child, _dict) and 'type' in child:
                _visit_reference(child, scope, node, key, None, next_depth)

    def _collect_references_iterative_from(start_node: dict, start_scope: Scope) -> None:
        """Run iterative reference collection starting from a specific node/scope."""
        ref_stack = [(start_node, start_scope, None, None, None)]
        while ref_stack:
            node, scope, parent, parent_key, parent_index = ref_stack.pop()
            if not _isinstance(node, _dict):
                continue
            node_type = node.get('type')
            if node_type is None:
                continue
            node_id = id(node)
            if node_id in node_scope:
                scope = node_scope[node_id]
            if node_type == 'Identifier':
                name = node.get('name', '')
                if _is_non_reference_identifier(parent, parent_key):
                    continue
                binding = scope.get_binding(name)
                if not binding:
                    continue
                binding.references.append((node, parent, parent_key, parent_index))
                if parent and parent.get('type') == 'AssignmentExpression' and parent_key == 'left':
                    binding.assignments.append(parent)
                elif parent and parent.get('type') == 'UpdateExpression':
                    binding.assignments.append(parent)
                continue
            child_keys = _child_keys_map.get(node_type)
            if child_keys is None:
                child_keys = _get_child_keys(node)
            for key in reversed(child_keys):
                child = node.get(key)
                if child is None:
                    continue
                if _isinstance(child, _list):
                    for index in range(len(child) - 1, -1, -1):
                        item = child[index]
                        if _isinstance(item, _dict) and 'type' in item:
                            ref_stack.append((item, scope, node, key, index))
                elif _isinstance(child, _dict) and 'type' in child:
                    ref_stack.append((child, scope, node, key, None))

    _visit_reference(ast, root_scope, None, None, None, 0)

    return root_scope, node_scope
