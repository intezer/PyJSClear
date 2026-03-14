"""Variable scope and binding analysis for ESTree ASTs."""

from collections.abc import Callable
from enum import StrEnum

from .utils.ast_helpers import _CHILD_KEYS
from .utils.ast_helpers import get_child_keys


# Local aliases for hot-path performance
_type = type
_dict = dict
_list = list

# Maximum recursion depth before falling back to iterative traversal.
_MAX_RECURSIVE_DEPTH = 500


class BindingKind(StrEnum):
    """Kind of variable binding in a scope."""

    VAR = 'var'
    LET = 'let'
    CONST = 'const'
    FUNCTION = 'function'
    PARAM = 'param'


class Binding:
    """Single variable binding within a scope, tracking references and assignments."""

    __slots__ = ('name', 'node', 'kind', 'scope', 'references', 'assignments')

    def __init__(self, name: str, node: dict, kind: BindingKind, scope: 'Scope') -> None:
        self.name: str = name
        self.node: dict = node
        self.kind: BindingKind = kind
        self.scope: Scope = scope
        self.references: list[tuple[dict, dict | None, str | None, int | None]] = []
        self.assignments: list[dict] = []

    @property
    def is_constant(self) -> bool:
        """Return True if the binding is never reassigned after declaration."""
        match self.kind:
            case BindingKind.CONST:
                return True
            case BindingKind.FUNCTION:
                return len(self.assignments) == 0
            case _:
                return len(self.assignments) == 0


class Scope:
    """Lexical scope node in the scope tree, holding bindings and child scopes."""

    __slots__ = ('parent', 'node', 'bindings', 'children', 'is_function')

    def __init__(self, parent: 'Scope | None', node: dict, is_function: bool = False) -> None:
        self.parent: Scope | None = parent
        self.node: dict = node
        self.bindings: dict[str, Binding] = {}
        self.children: list[Scope] = []
        self.is_function: bool = is_function
        if parent:
            parent.children.append(self)

    def add_binding(self, name: str, node: dict, kind: BindingKind | str) -> Binding:
        """Create and register a new binding in this scope."""
        binding = Binding(name, node, BindingKind(kind), self)
        self.bindings[name] = binding
        return binding

    def get_binding(self, name: str) -> Binding | None:
        """Look up a binding by name, walking up the scope chain."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get_binding(name)
        return None

    def get_own_binding(self, name: str) -> Binding | None:
        """Look up a binding only in this scope, ignoring parents."""
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
    if not isinstance(pattern, _dict):
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
            left_node = pattern.get('left')
            if left_node and left_node.get('type') == 'Identifier':
                scope.add_binding(left_node['name'], declaration, kind)


def _collect_declarations_iterative(
    ast: dict,
    root_scope: Scope,
    node_scope: dict[int, Scope],
    all_scopes: list[Scope],
) -> None:
    """Iteratively collect all declarations in the AST into scopes."""
    _child_keys_map = _CHILD_KEYS
    _get_child_keys = get_child_keys

    def _push_children(node: dict, scope: Scope, stack: list[tuple[dict, Scope]]) -> None:
        """Append child AST nodes onto the traversal stack."""
        node_type = node.get('type')
        child_keys = _child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(node)
        for key in reversed(child_keys):
            child = node.get(key)
            if child is None:
                continue
            if _type(child) is _list:
                for index in range(len(child) - 1, -1, -1):
                    item = child[index]
                    if _type(item) is _dict and 'type' in item:
                        stack.append((item, scope))
            elif _type(child) is _dict and 'type' in child:
                stack.append((child, scope))

    declaration_stack = [(ast, root_scope)]

    while declaration_stack:
        node, scope = declaration_stack.pop()

        if _type(node) is not _dict:
            continue
        node_type = node.get('type')
        if node_type is None:
            continue
        _process_declaration_node(node, node_type, scope, node_scope, all_scopes, declaration_stack, _push_children)


def _process_declaration_node(
    node: dict,
    node_type: str,
    scope: Scope,
    node_scope: dict[int, Scope],
    all_scopes: list[Scope],
    push_target: list[tuple[dict, Scope]],
    push_children_fn: Callable[[dict, Scope, list], None],
) -> None:
    """Process a single AST node, registering any declarations it introduces."""
    match node_type:
        case 'FunctionDeclaration' | 'FunctionExpression' | 'ArrowFunctionExpression':
            _process_function_declaration(node, node_type, scope, node_scope, all_scopes, push_target)

        case 'ClassExpression' | 'ClassDeclaration':
            _process_class_declaration(node, node_type, scope, node_scope, all_scopes, push_target)

        case 'VariableDeclaration':
            _process_variable_declaration(node, scope, node_scope, push_target)

        case 'BlockStatement' if id(node) not in node_scope:
            new_scope = Scope(scope, node)
            node_scope[id(node)] = new_scope
            all_scopes.append(new_scope)
            statements = node.get('body', [])
            for index in range(len(statements) - 1, -1, -1):
                push_target.append((statements[index], new_scope))

        case 'ForStatement':
            new_scope = Scope(scope, node)
            node_scope[id(node)] = new_scope
            all_scopes.append(new_scope)
            if node.get('body'):
                push_target.append((node['body'], new_scope))
            if node.get('init'):
                push_target.append((node['init'], new_scope))

        case 'CatchClause':
            _process_catch_clause(node, scope, node_scope, all_scopes, push_target)

        case _:
            push_children_fn(node, scope, push_target)


def _process_function_declaration(
    node: dict,
    node_type: str,
    scope: Scope,
    node_scope: dict[int, Scope],
    all_scopes: list[Scope],
    push_target: list[tuple[dict, Scope]],
) -> None:
    """Register function/arrow bindings, parameters, and schedule body traversal."""
    new_scope = Scope(scope, node, is_function=True)
    node_scope[id(node)] = new_scope
    all_scopes.append(new_scope)

    if node_type == 'FunctionDeclaration' and node.get('id'):
        scope.add_binding(node['id']['name'], node, BindingKind.FUNCTION)
    elif node_type == 'FunctionExpression' and node.get('id'):
        new_scope.add_binding(node['id']['name'], node, BindingKind.FUNCTION)

    for parameter in node.get('params', []):
        parameter_type = parameter.get('type')
        if parameter_type == 'Identifier':
            new_scope.add_binding(parameter['name'], parameter, BindingKind.PARAM)
        elif parameter_type == 'AssignmentPattern':
            left_node = parameter.get('left', {})
            if left_node.get('type') == 'Identifier':
                new_scope.add_binding(left_node['name'], parameter, BindingKind.PARAM)
        elif parameter_type == 'RestElement':
            argument_node = parameter.get('argument')
            if argument_node and argument_node.get('type') == 'Identifier':
                new_scope.add_binding(argument_node['name'], parameter, BindingKind.PARAM)

    body_node = node.get('body')
    if not body_node:
        return
    if _type(body_node) is _dict and body_node.get('type') == 'BlockStatement':
        node_scope[id(body_node)] = new_scope
        statements = body_node.get('body', [])
        for index in range(len(statements) - 1, -1, -1):
            push_target.append((statements[index], new_scope))
    else:
        push_target.append((body_node, new_scope))


def _process_class_declaration(
    node: dict,
    node_type: str,
    scope: Scope,
    node_scope: dict[int, Scope],
    all_scopes: list[Scope],
    push_target: list[tuple[dict, Scope]],
) -> None:
    """Register class bindings and schedule body/superclass traversal."""
    class_identifier = node.get('id')
    inner_scope = scope
    if class_identifier and class_identifier.get('type') == 'Identifier':
        binding_name = class_identifier['name']
        if node_type == 'ClassDeclaration':
            scope.add_binding(binding_name, node, BindingKind.FUNCTION)
        else:
            inner_scope = Scope(scope, node)
            node_scope[id(node)] = inner_scope
            all_scopes.append(inner_scope)
            inner_scope.add_binding(binding_name, node, BindingKind.FUNCTION)
    superclass_node = node.get('superClass')
    body_node = node.get('body')
    if body_node:
        push_target.append((body_node, inner_scope))
    if superclass_node:
        push_target.append((superclass_node, scope))


def _process_variable_declaration(
    node: dict,
    scope: Scope,
    node_scope: dict[int, Scope],
    push_target: list[tuple[dict, Scope]],
) -> None:
    """Register variable declarator bindings and schedule initializer traversal."""
    kind = node.get('kind', 'var')
    target_scope = (_nearest_function_scope(scope) or scope) if kind == 'var' else scope
    declarators = node.get('declarations', [])
    initializers_to_push: list[tuple[dict, Scope]] = []
    for declarator in declarators:
        declarator_id = declarator.get('id')
        if declarator_id and declarator_id.get('type') == 'Identifier':
            target_scope.add_binding(declarator_id['name'], declarator, kind)
        _collect_pattern_names(declarator_id, target_scope, kind, declarator)
        initializer = declarator.get('init')
        if initializer:
            initializers_to_push.append((initializer, scope))
    for index in range(len(initializers_to_push) - 1, -1, -1):
        push_target.append(initializers_to_push[index])


def _process_catch_clause(
    node: dict,
    scope: Scope,
    node_scope: dict[int, Scope],
    all_scopes: list[Scope],
    push_target: list[tuple[dict, Scope]],
) -> None:
    """Register catch clause parameter binding and schedule body traversal."""
    catch_body = node.get('body')
    if not catch_body or catch_body.get('type') != 'BlockStatement':
        return
    catch_scope = Scope(scope, catch_body)
    node_scope[id(catch_body)] = catch_scope
    all_scopes.append(catch_scope)
    catch_parameter = node.get('param')
    if catch_parameter and catch_parameter.get('type') == 'Identifier':
        catch_scope.add_binding(catch_parameter['name'], catch_parameter, BindingKind.PARAM)
    statements = catch_body.get('body', [])
    for index in range(len(statements) - 1, -1, -1):
        push_target.append((statements[index], catch_scope))


def _collect_references_iterative(ast: dict, root_scope: Scope, node_scope: dict[int, Scope]) -> None:
    """Iteratively collect identifier references and assignment tracking."""
    _child_keys_map = _CHILD_KEYS
    _get_child_keys = get_child_keys

    reference_stack: list[tuple[dict, Scope, dict | None, str | None, int | None]] = [
        (ast, root_scope, None, None, None),
    ]

    while reference_stack:
        node, scope, parent, parent_key, parent_index = reference_stack.pop()

        if _type(node) is not _dict:
            continue
        node_type = node.get('type')
        if node_type is None:
            continue

        node_id = id(node)
        if node_id in node_scope:
            scope = node_scope[node_id]

        if node_type == 'Identifier':
            identifier_name = node.get('name', '')
            if _is_non_reference_identifier(parent, parent_key):
                continue
            binding = scope.get_binding(identifier_name)
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
            if _type(child) is _list:
                for index in range(len(child) - 1, -1, -1):
                    item = child[index]
                    if _type(item) is _dict and 'type' in item:
                        reference_stack.append((item, scope, node, key, index))
            elif _type(child) is _dict and 'type' in child:
                reference_stack.append((child, scope, node, key, None))


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

    def _push_children(node: dict, scope: Scope, target_list: list[tuple[dict, Scope]]) -> None:
        """Append child AST nodes onto the traversal target list."""
        node_type = node['type']
        child_keys = _child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = _get_child_keys(node)
        for key in reversed(child_keys):
            child = node.get(key)
            if child is None:
                continue
            if _type(child) is _list:
                for index in range(len(child) - 1, -1, -1):
                    item = child[index]
                    if _type(item) is _dict and 'type' in item:
                        target_list.append((item, scope))
            elif _type(child) is _dict and 'type' in child:
                target_list.append((child, scope))

    def _visit_declaration(node: dict, scope: Scope, depth: int) -> None:
        """Recursively visit declarations, falling back to iterative at max depth."""
        if _type(node) is not _dict:
            return
        node_type = node.get('type')
        if node_type is None:
            return

        if depth > _max_depth:
            _collect_declarations_iterative_from(node, scope)
            return

        # Collect children into a local list, then recurse
        child_entries: list[tuple[dict, Scope]] = []
        _process_declaration_node(node, node_type, scope, node_scope, all_scopes, child_entries, _push_children)
        next_depth = depth + 1
        # Children appended in stack order (reversed); iterate in reverse for left-to-right.
        for index in range(len(child_entries) - 1, -1, -1):
            _visit_declaration(child_entries[index][0], child_entries[index][1], next_depth)

    def _collect_declarations_iterative_from(start_node: dict, start_scope: Scope) -> None:
        """Iterative fallback for declaration collection on deep subtrees."""
        declaration_stack = [(start_node, start_scope)]
        while declaration_stack:
            node, scope = declaration_stack.pop()
            if _type(node) is not _dict:
                continue
            node_type = node.get('type')
            if node_type is None:
                continue
            _process_declaration_node(node, node_type, scope, node_scope, all_scopes, declaration_stack, _push_children)

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
        """Recursively visit references, falling back to iterative at max depth."""
        if _type(node) is not _dict:
            return
        node_type = node.get('type')
        if node_type is None:
            return

        node_id = id(node)
        if node_id in node_scope:
            scope = node_scope[node_id]

        if node_type == 'Identifier':
            identifier_name = node.get('name', '')
            if _is_non_reference_identifier(parent, parent_key):
                return
            binding = scope.get_binding(identifier_name)
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
            if _type(child) is _list:
                for child_index, item in enumerate(child):
                    if _type(item) is _dict and 'type' in item:
                        _visit_reference(item, scope, node, key, child_index, next_depth)
            elif _type(child) is _dict and 'type' in child:
                _visit_reference(child, scope, node, key, None, next_depth)

    def _collect_references_iterative_from(start_node: dict, start_scope: Scope) -> None:
        """Iterative fallback for reference collection on deep subtrees."""
        reference_stack: list[tuple[dict, Scope, dict | None, str | None, int | None]] = [
            (start_node, start_scope, None, None, None),
        ]
        while reference_stack:
            node, scope, parent, parent_key, parent_index = reference_stack.pop()
            if _type(node) is not _dict:
                continue
            node_type = node.get('type')
            if node_type is None:
                continue
            node_id = id(node)
            if node_id in node_scope:
                scope = node_scope[node_id]
            if node_type == 'Identifier':
                identifier_name = node.get('name', '')
                if _is_non_reference_identifier(parent, parent_key):
                    continue
                binding = scope.get_binding(identifier_name)
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
                if _type(child) is _list:
                    for index in range(len(child) - 1, -1, -1):
                        item = child[index]
                        if _type(item) is _dict and 'type' in item:
                            reference_stack.append((item, scope, node, key, index))
                elif _type(child) is _dict and 'type' in child:
                    reference_stack.append((child, scope, node, key, None))

    _visit_reference(ast, root_scope, None, None, None, 0)

    return root_scope, node_scope
