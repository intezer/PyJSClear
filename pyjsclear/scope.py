"""Variable scope and binding analysis for ESTree ASTs."""

from .utils.ast_helpers import _CHILD_KEYS, get_child_keys


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
        nid = id(node)
        if nid in node_scope:
            return node_scope[nid]
        return current_scope

    _child_keys_map = _CHILD_KEYS

    def _collect_declarations(node, scope):
        """Walk the AST collecting variable declarations into scopes."""
        if not isinstance(node, dict):
            return
        ntype = node.get('type')
        if ntype is None:
            return

        # Create new scope for functions
        if ntype in ('FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'):
            new_scope = Scope(scope, node, is_function=True)
            node_scope[id(node)] = new_scope
            all_scopes.append(new_scope)

            # Function name goes in outer scope (for declarations) or inner (for expressions)
            if ntype == 'FunctionDeclaration' and node.get('id'):
                scope.add_binding(node['id']['name'], node, 'function')
            elif ntype == 'FunctionExpression' and node.get('id'):
                new_scope.add_binding(node['id']['name'], node, 'function')

            # Params go in function scope
            for param in node.get('params', []):
                if param.get('type') == 'Identifier':
                    new_scope.add_binding(param['name'], param, 'param')
                elif param.get('type') == 'AssignmentPattern' and param.get('left', {}).get('type') == 'Identifier':
                    new_scope.add_binding(param['left']['name'], param, 'param')

            # Body - use the new scope
            body = node.get('body')
            if body:
                if isinstance(body, dict) and body.get('type') == 'BlockStatement':
                    node_scope[id(body)] = new_scope
                    for stmt in body.get('body', []):
                        _collect_declarations(stmt, new_scope)
                else:
                    _collect_declarations(body, new_scope)
            return

        # Variable declarations
        if ntype == 'VariableDeclaration':
            kind = node.get('kind', 'var')
            target_scope = scope
            # var is function-scoped, let/const are block-scoped
            if kind == 'var':
                s = scope
                while s and not s.is_function:
                    s = s.parent
                if s:
                    target_scope = s
            for decl in node.get('declarations', []):
                decl_id = decl.get('id')
                if decl_id and decl_id.get('type') == 'Identifier':
                    target_scope.add_binding(decl_id['name'], decl, kind)
                # Handle destructuring patterns
                _collect_pattern_names(decl_id, target_scope, kind, decl)

        # Block scopes (for, if, etc. with block statements)
        if ntype == 'BlockStatement' and id(node) not in node_scope:
            # Only create block scope if parent is not a function (handled above)
            new_scope = Scope(scope, node)
            node_scope[id(node)] = new_scope
            all_scopes.append(new_scope)
            for stmt in node.get('body', []):
                _collect_declarations(stmt, new_scope)
            return

        if ntype == 'ForStatement':
            new_scope = Scope(scope, node)
            node_scope[id(node)] = new_scope
            all_scopes.append(new_scope)
            if node.get('init'):
                _collect_declarations(node['init'], new_scope)
            if node.get('body'):
                _collect_declarations(node['body'], new_scope)
            return

        # Recurse into children
        ckeys = _child_keys_map.get(ntype)
        if ckeys is None:
            ckeys = get_child_keys(node)
        for key in ckeys:
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, dict) and 'type' in item:
                        _collect_declarations(item, scope)
            elif isinstance(child, dict) and 'type' in child:
                _collect_declarations(child, scope)

    def _collect_pattern_names(pattern, scope, kind, decl):
        """Collect binding names from destructuring patterns."""
        if not isinstance(pattern, dict):
            return
        ptype = pattern.get('type', '')
        if ptype == 'ArrayPattern':
            for elem in pattern.get('elements', []):
                if elem and elem.get('type') == 'Identifier':
                    scope.add_binding(elem['name'], decl, kind)
                elif elem:
                    _collect_pattern_names(elem, scope, kind, decl)
        elif ptype == 'ObjectPattern':
            for prop in pattern.get('properties', []):
                val = prop.get('value', prop.get('argument'))
                if val and val.get('type') == 'Identifier':
                    scope.add_binding(val['name'], decl, kind)
                elif val:
                    _collect_pattern_names(val, scope, kind, decl)
        elif ptype == 'RestElement':
            arg = pattern.get('argument')
            if arg and arg.get('type') == 'Identifier':
                scope.add_binding(arg['name'], decl, kind)
        elif ptype == 'AssignmentPattern':
            left = pattern.get('left')
            if left and left.get('type') == 'Identifier':
                scope.add_binding(left['name'], decl, kind)

    _collect_declarations(ast, root_scope)

    # Second pass: collect references and assignments
    def _collect_references(node, scope, parent=None, parent_key=None, parent_index=None):
        if not isinstance(node, dict):
            return
        ntype = node.get('type')
        if ntype is None:
            return

        # Look up scope for this node
        scope = _get_scope_for(node, scope)

        if ntype == 'Identifier':
            name = node.get('name', '')
            # Skip property names in member expressions (non-computed)
            if parent and parent.get('type') == 'MemberExpression' and parent_key == 'property' and not parent.get('computed'):
                return
            # Skip property keys in object literals
            if parent and parent.get('type') == 'Property' and parent_key == 'key' and not parent.get('computed'):
                return
            # Skip function/class names at declaration site
            if parent and parent.get('type') in ('FunctionDeclaration', 'FunctionExpression', 'ClassDeclaration') and parent_key == 'id':
                return
            # Skip VariableDeclarator id
            if parent and parent.get('type') == 'VariableDeclarator' and parent_key == 'id':
                return

            binding = scope.get_binding(name)
            if binding:
                binding.references.append((node, parent, parent_key, parent_index))
                # Check if this is an assignment target
                if parent and parent.get('type') == 'AssignmentExpression' and parent_key == 'left':
                    binding.assignments.append(parent)
                elif parent and parent.get('type') == 'UpdateExpression':
                    binding.assignments.append(parent)
            return

        # Recurse
        ckeys = _child_keys_map.get(ntype)
        if ckeys is None:
            ckeys = get_child_keys(node)
        for key in ckeys:
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
