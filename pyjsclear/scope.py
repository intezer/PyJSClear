"""Variable scope and binding analysis for ESTree ASTs."""

from .utils.ast_helpers import _CHILD_KEYS
from .utils.ast_helpers import get_child_keys


class Binding:
    """Represents a variable binding in a scope."""

    __slots__ = ('name', 'node', 'kind', 'scope', 'references', 'assignments')

    def __init__(self, name, node, kind, scope):
        self.name = name
        self.node = node  # The declaration node
        self.kind = kind  # 'var', 'let', 'const', 'function', 'param'
        self.scope = scope
        self.references = []  # List of (node, parent, key, index) where name is referenced
        self.assignments = []  # List of assignment nodes

    @property
    def is_constant(self):
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

    def __init__(self, parent, node, is_function=False):
        self.parent = parent
        self.node = node
        self.bindings = {}  # name -> Binding
        self.children = []
        self.is_function = is_function
        if parent:
            parent.children.append(self)

    def add_binding(self, name, node, kind):
        binding = Binding(name, node, kind, self)
        self.bindings[name] = binding
        return binding

    def get_binding(self, name):
        """Look up a binding, walking up the scope chain."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get_binding(name)
        return None

    def get_own_binding(self, name):
        return self.bindings.get(name)


def _nearest_function_scope(scope):
    """Walk up to the nearest function (or root) scope."""
    while scope and not scope.is_function:
        scope = scope.parent
    return scope


def _is_non_reference_identifier(parent, parent_key):
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


def _recurse_into_children(node, child_keys_map, callback):
    """Walk child nodes, calling callback(child_node) for each dict with 'type'."""
    node_type = node.get('type')
    child_keys = child_keys_map.get(node_type)
    if child_keys is None:
        child_keys = get_child_keys(node)
    for key in child_keys:
        child = node.get(key)
        if child is None:
            continue
        if isinstance(child, list):
            for item in child:
                if isinstance(item, dict) and 'type' in item:
                    callback(item)
        elif isinstance(child, dict) and 'type' in child:
            callback(child)


def build_scope_tree(ast):
    """Build a scope tree from an AST, collecting bindings and references.

    Returns the root Scope and a dict mapping node id -> Scope.
    """
    root_scope = Scope(None, ast, is_function=True)
    # Maps id(node) -> scope for function/block scope nodes
    node_scope = {id(ast): root_scope}
    # We need to collect all declarations first, then references
    all_scopes = [root_scope]

    def _get_scope_for(node, current_scope):
        """Get or create the scope for a node."""
        node_id = id(node)
        if node_id in node_scope:
            return node_scope[node_id]
        return current_scope

    _child_keys_map = _CHILD_KEYS

    def _collect_declarations(node, scope):
        """Walk the AST collecting variable declarations into scopes."""
        if not isinstance(node, dict):
            return
        node_type = node.get('type')
        if node_type is None:
            return

        match node_type:
            case 'FunctionDeclaration' | 'FunctionExpression' | 'ArrowFunctionExpression':
                new_scope = Scope(scope, node, is_function=True)
                node_scope[id(node)] = new_scope
                all_scopes.append(new_scope)

                # Function name goes in outer scope (for declarations) or inner (for expressions)
                if node_type == 'FunctionDeclaration' and node.get('id'):
                    scope.add_binding(node['id']['name'], node, 'function')
                elif node_type == 'FunctionExpression' and node.get('id'):
                    new_scope.add_binding(node['id']['name'], node, 'function')

                # Params go in function scope
                for param in node.get('params', []):
                    match param.get('type'):
                        case 'Identifier':
                            new_scope.add_binding(param['name'], param, 'param')
                        case 'AssignmentPattern' if param.get('left', {}).get('type') == 'Identifier':
                            new_scope.add_binding(param['left']['name'], param, 'param')
                        case 'RestElement':
                            arg = param.get('argument')
                            if arg and arg.get('type') == 'Identifier':
                                new_scope.add_binding(arg['name'], param, 'param')

                # Body - use the new scope
                body = node.get('body')
                if not body:
                    return
                if isinstance(body, dict) and body.get('type') == 'BlockStatement':
                    node_scope[id(body)] = new_scope
                    for statement in body.get('body', []):
                        _collect_declarations(statement, new_scope)
                else:
                    _collect_declarations(body, new_scope)

            case 'ClassExpression' | 'ClassDeclaration':
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
                body = node.get('body')
                if body:
                    _collect_declarations(body, inner_scope)
                superclass = node.get('superClass')
                if superclass:
                    _collect_declarations(superclass, scope)

            case 'VariableDeclaration':
                kind = node.get('kind', 'var')
                target_scope = (_nearest_function_scope(scope) or scope) if kind == 'var' else scope
                for declaration in node.get('declarations', []):
                    declaration_id = declaration.get('id')
                    if declaration_id and declaration_id.get('type') == 'Identifier':
                        target_scope.add_binding(declaration_id['name'], declaration, kind)
                    _collect_pattern_names(declaration_id, target_scope, kind, declaration)
                    init = declaration.get('init')
                    if init:
                        _collect_declarations(init, scope)

            case 'BlockStatement' if id(node) not in node_scope:
                new_scope = Scope(scope, node)
                node_scope[id(node)] = new_scope
                all_scopes.append(new_scope)
                for statement in node.get('body', []):
                    _collect_declarations(statement, new_scope)

            case 'ForStatement':
                new_scope = Scope(scope, node)
                node_scope[id(node)] = new_scope
                all_scopes.append(new_scope)
                if node.get('init'):
                    _collect_declarations(node['init'], new_scope)
                if node.get('body'):
                    _collect_declarations(node['body'], new_scope)

            case 'CatchClause':
                catch_body = node.get('body')
                if catch_body and catch_body.get('type') == 'BlockStatement':
                    catch_scope = Scope(scope, catch_body)
                    node_scope[id(catch_body)] = catch_scope
                    all_scopes.append(catch_scope)
                    param = node.get('param')
                    if param and param.get('type') == 'Identifier':
                        catch_scope.add_binding(param['name'], param, 'param')
                    for statement in catch_body.get('body', []):
                        _collect_declarations(statement, catch_scope)

            case _:
                _recurse_into_children(
                    node, _child_keys_map, lambda child_node: _collect_declarations(child_node, scope)
                )

    def _collect_pattern_names(pattern, scope, kind, declaration):
        """Collect binding names from destructuring patterns."""
        if not isinstance(pattern, dict):
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

    _collect_declarations(ast, root_scope)

    # Second pass: collect references and assignments
    def _collect_references(node, scope, parent=None, parent_key=None, parent_index=None):
        if not isinstance(node, dict):
            return
        node_type = node.get('type')
        if node_type is None:
            return

        # Look up scope for this node
        scope = _get_scope_for(node, scope)

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

        # Recurse — can't use _recurse_into_children here because we need
        # per-child (key, index) args for reference tracking
        child_keys = _child_keys_map.get(node_type)
        if child_keys is None:
            child_keys = get_child_keys(node)
        for key in child_keys:
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                for i, item in enumerate(child):
                    if isinstance(item, dict) and 'type' in item:
                        _collect_references(item, scope, node, key, i)
            elif isinstance(child, dict) and 'type' in child:
                _collect_references(child, scope, node, key, None)

    _collect_references(ast, root_scope)

    return root_scope, node_scope
