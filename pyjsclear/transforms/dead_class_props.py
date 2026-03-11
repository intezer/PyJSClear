"""Remove dead class property assignments.

After ClassStringDecoder inlines decoded constants, assignments like:
    _0x3bb8cb.prop = "value";
    _0x279589.XXX = "literal";

become dead code. This transform detects class variables and removes
their property assignments when the properties are dead.

Uses two strategies:
1. Properties that are written but never read are dead.
2. If a class variable is only referenced in its own property assignments
   and inside class bodies (never passed around or called), all its
   properties are considered dead.
"""

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_string_literal
from .base import Transform


def _get_member_names(node):
    """Extract (object_name, property_name) from a MemberExpression."""
    if not node or node.get('type') != 'MemberExpression':
        return None, None
    obj = node.get('object')
    prop = node.get('property')
    if not obj or not is_identifier(obj):
        return None, None
    if not prop:
        return None, None
    if node.get('computed'):
        if is_string_literal(prop):
            return obj['name'], prop['value']
        return None, None
    if is_identifier(prop):
        return obj['name'], prop['name']
    return None, None


class DeadClassPropRemover(Transform):
    """Remove dead property assignments on class variables."""

    def execute(self):
        # Step 1: Find class variable names
        class_vars = set()

        def find_classes(node, parent):
            if node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                if init and init.get('type') == 'ClassExpression':
                    decl_id = node.get('id')
                    if decl_id and is_identifier(decl_id):
                        class_vars.add(decl_id['name'])
            elif node.get('type') == 'AssignmentExpression':
                right = node.get('right')
                if right and right.get('type') == 'ClassExpression':
                    left = node.get('left')
                    if left and is_identifier(left):
                        class_vars.add(left['name'])

        simple_traverse(self.ast, find_classes)

        if not class_vars:
            return False

        # Step 2: For each class var, classify identifier references
        # "member_only" = identifier only appears as object of MemberExpression
        # If a class var identifier appears standalone (not as obj.prop), it's "escaped"
        member_refs = {v: 0 for v in class_vars}  # count of X.prop references
        standalone_refs = {v: 0 for v in class_vars}  # count of bare X references

        def classify_refs(node, parent):
            if not is_identifier(node):
                return
            name = node.get('name')
            if name not in class_vars:
                return
            # Skip declaration sites
            if parent and parent.get('type') == 'VariableDeclarator' and node is parent.get('id'):
                return
            # Check if this is the object of a MemberExpression
            if parent and parent.get('type') == 'MemberExpression' and node is parent.get('object'):
                member_refs[name] = member_refs.get(name, 0) + 1
            # RHS of a member assignment (X.prop = classVar) is an alias, not an escape
            elif (
                parent
                and parent.get('type') == 'AssignmentExpression'
                and node is parent.get('right')
                and parent.get('left', {}).get('type') == 'MemberExpression'
            ):
                member_refs[name] = member_refs.get(name, 0) + 1
            else:
                standalone_refs[name] = standalone_refs.get(name, 0) + 1

        simple_traverse(self.ast, classify_refs)

        # Classes that never escape (only used as X.prop) — all their props are dead
        fully_dead_classes = {v for v in class_vars if standalone_refs.get(v, 0) == 0}

        # Step 3: For non-fully-dead classes, find individually dead properties
        writes = set()
        reads = set()

        def count_prop_refs(node, parent):
            if node.get('type') != 'MemberExpression':
                return
            obj_name, prop_name = _get_member_names(node)
            if not obj_name or obj_name not in class_vars:
                return
            if obj_name in fully_dead_classes:
                return  # already handled

            pair = (obj_name, prop_name)
            if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
                writes.add(pair)
            else:
                reads.add(pair)

        simple_traverse(self.ast, count_prop_refs)

        # Dead props: written but never read, OR belonging to fully dead classes
        dead_props = set()
        for pair in writes:
            if pair not in reads:
                dead_props.add(pair)

        # Add all props of fully dead classes
        for v in fully_dead_classes:
            # Collect all props written on this class
            def collect_dead(node, parent):
                if node.get('type') != 'AssignmentExpression' or node.get('operator') != '=':
                    return
                obj_name, prop_name = _get_member_names(node.get('left'))
                if obj_name == v:
                    dead_props.add((obj_name, prop_name))

            simple_traverse(self.ast, collect_dead)

        if not dead_props:
            return False

        # Step 4: Remove dead assignment expressions
        def remove_dead_stmts(node, parent, key, index):
            if node.get('type') != 'ExpressionStatement':
                return
            expr = node.get('expression')
            if not expr:
                return
            if expr.get('type') == 'AssignmentExpression' and expr.get('operator') == '=':
                obj_name, prop_name = _get_member_names(expr.get('left'))
                if obj_name and (obj_name, prop_name) in dead_props:
                    self.set_changed()
                    return REMOVE
            if expr.get('type') == 'SequenceExpression':
                exprs = expr.get('expressions', [])
                remaining = []
                for e in exprs:
                    if e.get('type') == 'AssignmentExpression' and e.get('operator') == '=':
                        obj_name, prop_name = _get_member_names(e.get('left'))
                        if obj_name and (obj_name, prop_name) in dead_props:
                            self.set_changed()
                            continue
                    remaining.append(e)
                if not remaining:
                    return REMOVE
                if len(remaining) < len(exprs):
                    if len(remaining) == 1:
                        node['expression'] = remaining[0]
                    else:
                        expr['expressions'] = remaining

        traverse(self.ast, {'enter': remove_dead_stmts})
        return self.has_changed()
