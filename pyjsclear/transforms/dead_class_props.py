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
        # Step 1: Find class variable names, aliases, and class-id-to-name mapping
        # in a single traversal
        class_vars = set()
        class_aliases = {}  # inner_name -> outer_name
        reverse_aliases = {}  # outer_name -> set of inner_names
        class_node_to_name = {}  # id(ClassExpression node) -> outer name

        def find_classes(node, parent):
            if node.get('type') == 'VariableDeclarator':
                init = node.get('init')
                if init and init.get('type') == 'ClassExpression':
                    decl_id = node.get('id')
                    if decl_id and is_identifier(decl_id):
                        outer = decl_id['name']
                        class_vars.add(outer)
                        class_node_to_name[id(init)] = outer
                        class_id = init.get('id')
                        if class_id and is_identifier(class_id):
                            inner = class_id['name']
                            if inner != outer:
                                class_vars.add(inner)
                                class_aliases[inner] = outer
                                reverse_aliases.setdefault(outer, set()).add(inner)
            elif node.get('type') == 'AssignmentExpression':
                right = node.get('right')
                if right and right.get('type') == 'ClassExpression':
                    left = node.get('left')
                    if left and is_identifier(left):
                        outer = left['name']
                        class_vars.add(outer)
                        class_node_to_name[id(right)] = outer
                        class_id = right.get('id')
                        if class_id and is_identifier(class_id):
                            inner = class_id['name']
                            if inner != outer:
                                class_vars.add(inner)
                                class_aliases[inner] = outer
                                reverse_aliases.setdefault(outer, set()).add(inner)

        simple_traverse(self.ast, find_classes)

        if not class_vars:
            return False

        def _normalize(obj_name):
            """Resolve class aliases to their canonical (outer) name."""
            return class_aliases.get(obj_name, obj_name)

        def _has_standalone(name):
            if standalone_refs.get(name, 0) > 0:
                return True
            canonical = class_aliases.get(name, name)
            if standalone_refs.get(canonical, 0) > 0:
                return True
            for inner in reverse_aliases.get(name, ()):
                if standalone_refs.get(inner, 0) > 0:
                    return True
            return False

        # Step 2: Classify identifier references and collect this.prop reads
        # in a single traversal
        member_refs = {v: 0 for v in class_vars}
        standalone_refs = {v: 0 for v in class_vars}
        this_reads = set()

        def classify_and_collect(node, parent):
            # Collect this.prop reads inside class bodies
            if node.get('type') == 'ClassExpression':
                class_name = class_node_to_name.get(id(node))
                if class_name:
                    _collect_this_reads_in_class(node, class_name)
                return

            if not is_identifier(node):
                return
            name = node.get('name')
            if name not in class_vars:
                return
            # Skip declaration, assignment-to-class, and class expression id sites
            if parent and parent.get('type') == 'VariableDeclarator' and node is parent.get('id'):
                return
            if (
                parent
                and parent.get('type') == 'AssignmentExpression'
                and node is parent.get('left')
                and parent.get('right', {}).get('type') == 'ClassExpression'
            ):
                return
            if parent and parent.get('type') == 'ClassExpression' and node is parent.get('id'):
                return
            # Check if this is the object of a MemberExpression
            if parent and parent.get('type') == 'MemberExpression' and node is parent.get('object'):
                member_refs[name] = member_refs.get(name, 0) + 1
            # RHS of a member assignment (X.prop = classVar) is an export/escape —
            # the class becomes reachable through a different path, so its
            # properties may be read via that path (e.g. module.S559FZQ.propName)
            elif (
                parent
                and parent.get('type') == 'AssignmentExpression'
                and node is parent.get('right')
                and parent.get('left', {}).get('type') == 'MemberExpression'
            ):
                standalone_refs[name] = standalone_refs.get(name, 0) + 1
            else:
                standalone_refs[name] = standalone_refs.get(name, 0) + 1

        def _collect_this_reads_in_class(class_node, class_name):
            def _inner(n, p):
                if n.get('type') != 'MemberExpression':
                    return
                obj = n.get('object')
                if not obj or obj.get('type') != 'ThisExpression':
                    return
                prop = n.get('property')
                if not prop:
                    return
                if n.get('computed'):
                    if is_string_literal(prop):
                        this_reads.add((class_name, prop['value']))
                elif is_identifier(prop):
                    this_reads.add((class_name, prop['name']))

            simple_traverse(class_node.get('body', {}), _inner)

        simple_traverse(self.ast, classify_and_collect)

        # Classes with `this.prop` reads use their own properties — not fully dead
        classes_with_this = set()
        for name, prop in this_reads:
            classes_with_this.add(name)
            classes_with_this.add(class_aliases.get(name, name))

        # Classes that never escape (only used as X.prop) — all their props are dead
        fully_dead_classes = {v for v in class_vars if not _has_standalone(v) and v not in classes_with_this}

        # Classes that have escaped — skip individual prop dead-code analysis
        escaped_classes = {_normalize(v) for v in class_vars if _has_standalone(v)}

        # Step 3: For non-fully-dead classes, find individually dead properties
        writes = set()
        reads = set()

        def count_prop_refs(node, parent):
            if node.get('type') != 'MemberExpression':
                return
            obj_name, prop_name = _get_member_names(node)
            if not obj_name or obj_name not in class_vars:
                return
            canonical = _normalize(obj_name)
            if canonical in fully_dead_classes:
                return  # already handled
            if canonical in escaped_classes:
                return  # escaped — can't determine dead props safely

            pair = (canonical, prop_name)
            if parent and parent.get('type') == 'AssignmentExpression' and node is parent.get('left'):
                writes.add(pair)
            else:
                reads.add(pair)

        simple_traverse(self.ast, count_prop_refs)
        # Merge this.prop reads (normalize names)
        reads |= {(_normalize(name), prop) for name, prop in this_reads}

        # Dead props: written but never read, OR belonging to fully dead classes
        dead_props = set()
        for pair in writes:
            if pair not in reads:
                dead_props.add(pair)

        # Collect all props of fully dead classes in a single traversal
        if fully_dead_classes:
            fully_dead_canonical = {_normalize(v) for v in fully_dead_classes} | fully_dead_classes

            def collect_all_dead(node, parent):
                if node.get('type') != 'AssignmentExpression' or node.get('operator') != '=':
                    return
                obj_name, prop_name = _get_member_names(node.get('left'))
                if obj_name and obj_name in fully_dead_canonical:
                    dead_props.add((_normalize(obj_name), prop_name))

            simple_traverse(self.ast, collect_all_dead)

        if not dead_props:
            return False

        # Step 4: Remove dead assignment expressions
        def _is_dead(obj_name, prop_name):
            canonical = _normalize(obj_name)
            return (canonical, prop_name) in dead_props or (obj_name, prop_name) in dead_props

        def remove_dead_stmts(node, parent, key, index):
            if node.get('type') != 'ExpressionStatement':
                return
            expr = node.get('expression')
            if not expr:
                return
            if expr.get('type') == 'AssignmentExpression' and expr.get('operator') == '=':
                obj_name, prop_name = _get_member_names(expr.get('left'))
                if obj_name and _is_dead(obj_name, prop_name):
                    self.set_changed()
                    return REMOVE
            if expr.get('type') == 'SequenceExpression':
                exprs = expr.get('expressions', [])
                remaining = []
                for e in exprs:
                    if e.get('type') == 'AssignmentExpression' and e.get('operator') == '=':
                        obj_name, prop_name = _get_member_names(e.get('left'))
                        if obj_name and _is_dead(obj_name, prop_name):
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
