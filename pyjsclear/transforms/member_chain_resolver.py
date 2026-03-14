"""Resolve multi-level member expression chains to literal values.

Detects patterns like:
    _0x47f3fa.i4B82NN = _0x279589;     (export alias)
    _0x279589.XXX = "literal";           (class constant)

    _0x285ccd = _0x3b922a();             (module call)
    _0x285ccd.i4B82NN.XXX               (access chain)

Resolves _0x285ccd.i4B82NN.XXX to the literal by:
1. Building a map of (class_name, prop) to literal from X.prop = literal assignments
2. Building a map of prop_name to class_name from X.prop = Identifier assignments
3. Resolving A.B.C chains: B to class_name, then (class_name, C) to literal
"""

from __future__ import annotations

from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import get_member_names
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_string_literal
from .base import Transform


def _is_constant_expression(node: dict) -> bool:
    """Return True if the AST node is a constant expression safe to inline."""
    if not isinstance(node, dict):
        return False
    match node.get('type'):
        case 'Literal':
            return True
        case 'UnaryExpression' if node.get('operator') in ('-', '+', '!', '~'):
            return _is_constant_expression(node.get('argument'))
        case 'ArrayExpression':
            elements = node.get('elements') or []
            return all(_is_constant_expression(element) for element in elements if element)
    return False


def _get_property_name(member_expression: dict, property_key: str) -> str | None:
    """Extract the string name from a member expression's property."""
    property_node = member_expression.get(property_key)
    if not property_node:
        return None
    if member_expression.get('computed'):
        if not is_string_literal(property_node):
            return None
        return property_node['value']
    if is_identifier(property_node):
        return property_node['name']
    return None


def _collect_constants_and_aliases(
    ast: dict,
    class_constants: dict[tuple[str, str], dict],
    property_to_class: dict[str, str],
) -> None:
    """Collect X.prop = constant and X.prop = Identifier assignments from the AST."""

    def visitor(node: dict, parent: dict | None) -> None:
        if node.get('type') != 'AssignmentExpression':
            return
        if node.get('operator') != '=':
            return
        left = node.get('left')
        right = node.get('right')
        object_name, property_name = get_member_names(left)
        if not object_name:
            return

        if _is_constant_expression(right):
            class_constants[(object_name, property_name)] = right
        elif is_identifier(right):
            property_to_class[property_name] = right['name']

    simple_traverse(ast, visitor)


def _invalidate_reassigned_chain_constants(
    ast: dict,
    class_constants: dict[tuple[str, str], dict],
    property_to_class: dict[str, str],
) -> None:
    """Remove constants that are reassigned through alias chains (A.B.C = expr)."""

    def visitor(node: dict, parent: dict | None) -> None:
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
        class_name = property_to_class.get(middle_property_name)
        if class_name and (class_name, outer_property_name) in class_constants:
            del class_constants[(class_name, outer_property_name)]

    simple_traverse(ast, visitor)


class MemberChainResolver(Transform):
    """Resolve multi-level member chains (A.B.C) to literal values."""

    def execute(self) -> bool:
        """Run the transform, returning True if the AST was modified."""
        class_constants: dict[tuple[str, str], dict] = {}
        property_to_class: dict[str, str] = {}

        _collect_constants_and_aliases(self.ast, class_constants, property_to_class)
        if not class_constants:
            return False

        _invalidate_reassigned_chain_constants(self.ast, class_constants, property_to_class)
        if not class_constants:
            return False

        self._resolve_member_chains(class_constants, property_to_class)
        return self.has_changed()

    def _resolve_member_chains(
        self,
        class_constants: dict[tuple[str, str], dict],
        property_to_class: dict[str, str],
    ) -> None:
        """Replace A.B.C member chains where B resolves to a class constant."""

        def resolver(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> dict | None:
            if node.get('type') != 'MemberExpression':
                return None
            if parent and parent.get('type') == 'AssignmentExpression' and key == 'left':
                return None

            outer_property_name = _get_property_name(node, 'property')
            if outer_property_name is None:
                return None

            inner = node.get('object')
            if not inner or inner.get('type') != 'MemberExpression':
                return None

            middle_property_name = _get_property_name(inner, 'property')
            if middle_property_name is None:
                return None

            class_name = property_to_class.get(middle_property_name)
            if not class_name:
                return None

            constant_node = class_constants.get((class_name, outer_property_name))
            if constant_node is None:
                return None

            self.set_changed()
            return deep_copy(constant_node)

        traverse(self.ast, {'enter': resolver})
