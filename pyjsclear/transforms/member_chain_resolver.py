"""Resolve multi-level member expression chains to literal values.

Detects patterns like:
    _0x47f3fa.i4B82NN = _0x279589;     (export alias)
    _0x279589.XXX = "literal";           (class constant)

    _0x285ccd = _0x3b922a();             (module call)
    _0x285ccd.i4B82NN.XXX               (access chain)

Resolves _0x285ccd.i4B82NN.XXX → "literal" by:
1. Building a map of (class_name, prop) → literal from X.prop = literal assignments
2. Building a map of prop_name → class_name from X.prop = Identifier assignments
3. Resolving A.B.C chains: B → class_name, then (class_name, C) → literal
"""

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import get_member_names
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_string_literal
from .base import Transform


def _is_constant_expr(node):
    """Check if a node is a constant expression safe to inline."""
    if not isinstance(node, dict):
        return False
    match node.get('type'):
        case 'Literal':
            return True
        case 'UnaryExpression' if node.get('operator') in ('-', '+', '!', '~'):
            return _is_constant_expr(node.get('argument'))
        case 'ArrayExpression':
            return all(_is_constant_expr(el) for el in (node.get('elements') or []) if el)
    return False


class MemberChainResolver(Transform):
    """Resolve multi-level member chains (A.B.C) to literal values."""

    def execute(self):
        # Maps: (class_name, prop_name) → AST node (constant expression)
        class_constants = {}
        # Maps: prop_name → class_name (from X.prop = ClassIdentifier assignments)
        prop_to_class = {}

        # Phase 1: Collect X.prop = constant_expr and X.prop = Identifier assignments
        def collect(node, parent):
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return
            left = node.get('left')
            right = node.get('right')
            obj_name, prop_name = get_member_names(left)
            if not obj_name:
                return

            if _is_constant_expr(right):
                class_constants[(obj_name, prop_name)] = right
            elif is_identifier(right):
                # X.prop = SomeClass — record prop_name → SomeClass
                prop_to_class[prop_name] = right['name']

        simple_traverse(self.ast, collect)

        if not class_constants:
            return False

        # Phase 1b: Invalidate constants that are reassigned through alias chains.
        # Pattern: A.B.C = expr where B → class_name via prop_to_class
        # means (class_name, C) is NOT a true constant.
        def invalidate_chain_assignments(node, parent):
            if node.get('type') != 'AssignmentExpression':
                return
            left = node.get('left')
            if not left or left.get('type') != 'MemberExpression':
                return
            inner = left.get('object')
            if not inner or inner.get('type') != 'MemberExpression':
                return
            # Get C (outer property)
            outer_prop = left.get('property')
            if not outer_prop:
                return
            if left.get('computed'):
                if not is_string_literal(outer_prop):
                    return
                c_name = outer_prop['value']
            elif is_identifier(outer_prop):
                c_name = outer_prop['name']
            else:
                return
            # Get B (middle property)
            inner_prop = inner.get('property')
            if not inner_prop:
                return
            if inner.get('computed'):
                if not is_string_literal(inner_prop):
                    return
                b_name = inner_prop['value']
            elif is_identifier(inner_prop):
                b_name = inner_prop['name']
            else:
                return
            # If B resolves to a class, invalidate (class, C)
            class_name = prop_to_class.get(b_name)
            if class_name and (class_name, c_name) in class_constants:
                del class_constants[(class_name, c_name)]

        simple_traverse(self.ast, invalidate_chain_assignments)

        if not class_constants:
            return False

        # Phase 2: Replace A.B.C member chains where B resolves to a class
        # and (class, C) maps to a constant expression
        def resolve(node, parent, key, index):
            if node.get('type') != 'MemberExpression':
                return
            # Skip assignment targets
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return

            # Get C (the outer property)
            outer_prop = node.get('property')
            if not outer_prop:
                return
            if node.get('computed'):
                if not is_string_literal(outer_prop):
                    return
                c_name = outer_prop['value']
            elif is_identifier(outer_prop):
                c_name = outer_prop['name']
            else:
                return

            # Get the inner member expression (A.B)
            inner = node.get('object')
            if not inner or inner.get('type') != 'MemberExpression':
                return

            # Get B (the middle property)
            inner_prop = inner.get('property')
            if not inner_prop:
                return
            if inner.get('computed'):
                if not is_string_literal(inner_prop):
                    return
                b_name = inner_prop['value']
            elif is_identifier(inner_prop):
                b_name = inner_prop['name']
            else:
                return

            # Resolve B → class_name
            class_name = prop_to_class.get(b_name)
            if not class_name:
                return

            # Resolve (class_name, C) → constant expression
            const_node = class_constants.get((class_name, c_name))
            if const_node is None:
                return

            self.set_changed()
            return deep_copy(const_node)

        traverse(self.ast, {'enter': resolve})
        return self.has_changed()
