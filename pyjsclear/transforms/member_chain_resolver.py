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


def _is_constant_expr(node: dict) -> bool:
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


def _get_property_name(member_expr: dict, property_key: str) -> str | None:
    """Extract the string name of a member expression's property."""
    prop = member_expr.get(property_key)
    if not prop:
        return None
    if member_expr.get('computed'):
        if not is_string_literal(prop):
            return None
        return prop['value']
    if is_identifier(prop):
        return prop['name']
    return None


class MemberChainResolver(Transform):
    """Resolve multi-level member chains (A.B.C) to literal values."""

    def execute(self) -> bool:
        # Maps: (class_name, property_name) → AST node (constant expression)
        class_constants: dict[tuple[str, str], dict] = {}
        # Maps: property_name → class_name (from X.prop = ClassIdentifier assignments)
        property_to_class: dict[str, str] = {}

        # Phase 1: Collect X.prop = constant_expr and X.prop = Identifier assignments
        def collect(node: dict, parent: dict | None) -> None:
            if node.get('type') != 'AssignmentExpression':
                return
            if node.get('operator') != '=':
                return
            left = node.get('left')
            right = node.get('right')
            object_name, property_name = get_member_names(left)
            if not object_name:
                return

            if _is_constant_expr(right):
                class_constants[(object_name, property_name)] = right
            elif is_identifier(right):
                # X.prop = SomeClass — record property_name → SomeClass
                property_to_class[property_name] = right['name']

        simple_traverse(self.ast, collect)

        if not class_constants:
            return False

        # Phase 1b: Invalidate constants that are reassigned through alias chains.
        # Pattern: A.B.C = expr where B → class_name via property_to_class
        # means (class_name, C) is NOT a true constant.
        def invalidate_chain_assignments(node: dict, parent: dict | None) -> None:
            if node.get('type') != 'AssignmentExpression':
                return
            left = node.get('left')
            if not left or left.get('type') != 'MemberExpression':
                return
            inner = left.get('object')
            if not inner or inner.get('type') != 'MemberExpression':
                return
            outer_property_name = _get_property_name(left, 'property')
            if outer_property_name is None:
                return
            middle_property_name = _get_property_name(inner, 'property')
            if middle_property_name is None:
                return
            # If B resolves to a class, invalidate (class, C)
            class_name = property_to_class.get(middle_property_name)
            if class_name and (class_name, outer_property_name) in class_constants:
                del class_constants[(class_name, outer_property_name)]

        simple_traverse(self.ast, invalidate_chain_assignments)

        if not class_constants:
            return False

        # Phase 2: Replace A.B.C member chains where B resolves to a class
        # and (class, C) maps to a constant expression
        def resolve(node: dict, parent: dict | None, key: str | None, index: int | None) -> dict | None:
            if node.get('type') != 'MemberExpression':
                return None
            # Skip assignment targets
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return None

            outer_property_name = _get_property_name(node, 'property')
            if outer_property_name is None:
                return None

            # Get the inner member expression (A.B)
            inner = node.get('object')
            if not inner or inner.get('type') != 'MemberExpression':
                return None

            middle_property_name = _get_property_name(inner, 'property')
            if middle_property_name is None:
                return None

            # Resolve B → class_name
            class_name = property_to_class.get(middle_property_name)
            if not class_name:
                return None

            # Resolve (class_name, C) → constant expression
            constant_node = class_constants.get((class_name, outer_property_name))
            if constant_node is None:
                return None

            self.set_changed()
            return deep_copy(constant_node)

        traverse(self.ast, {'enter': resolve})
        return self.has_changed()
