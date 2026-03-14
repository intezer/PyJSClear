"""Inline single-use variables.

Targets patterns like:
    const _0x337161 = require("process");
    return _0x337161.env.LOCALAPPDATA;
    return require("process").env.LOCALAPPDATA;

    const _0x27439f = Buffer.from(_0x162d6f);
    return _0x27439f.toString();
    return Buffer.from(_0x162d6f).toString();

Only inlines when:
- The variable is constant (no reassignments)
- There is exactly one reference (used once)
- The init expression is not too large (≤ 15 AST nodes)
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_identifier
from .base import Transform


if TYPE_CHECKING:
    from ..scope import Scope


class _NodeType(StrEnum):
    """AST node types used in single-use variable inlining."""

    ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
    IDENTIFIER = 'Identifier'
    MEMBER_EXPRESSION = 'MemberExpression'
    UPDATE_EXPRESSION = 'UpdateExpression'
    VARIABLE_DECLARATION = 'VariableDeclaration'
    VARIABLE_DECLARATOR = 'VariableDeclarator'


class _ParentKey(StrEnum):
    """Parent-child relationship keys used in inlining checks."""

    ID = 'id'
    LEFT = 'left'
    OBJECT = 'object'


def _count_nodes(node: dict) -> int:
    """Return the total number of AST nodes in a subtree."""
    count: list[int] = [0]

    def increment_count(_node: dict, _parent: dict | None) -> None:
        count[0] += 1

    simple_traverse(node, increment_count)
    return count[0]


def _is_simple_identifier(node: dict | None) -> bool:
    """Check whether a node is a plain Identifier (not a destructuring pattern)."""
    return bool(node and node.get('type') == _NodeType.IDENTIFIER)


def _has_valid_init(node: dict) -> bool:
    """Check whether a declarator has a non-empty dict init with a type field."""
    initializer = node.get('init')
    return bool(initializer and isinstance(initializer, dict) and 'type' in initializer)


def _is_declaration_site(reference_parent: dict | None, reference_key: str | None) -> bool:
    """Return True if the reference is the declaration-site identifier (id of a VariableDeclarator)."""
    return bool(
        reference_parent
        and reference_parent.get('type') == _NodeType.VARIABLE_DECLARATOR
        and reference_key == _ParentKey.ID
    )


def _is_assignment_target(reference_parent: dict | None, reference_key: str | None) -> bool:
    """Return True if the reference is being assigned to or updated."""
    if not reference_parent:
        return False
    parent_type = reference_parent.get('type')
    if parent_type == _NodeType.ASSIGNMENT_EXPRESSION and reference_key == _ParentKey.LEFT:
        return True
    if parent_type == _NodeType.UPDATE_EXPRESSION:
        return True
    return False


class SingleUseVarInliner(Transform):
    """Inline single-use constant variables at their usage site."""

    rebuild_scope = True

    # Max AST node count for an init expression to be inlined
    _MAX_INIT_NODES = 15

    def execute(self) -> bool:
        """Run the inlining pass and return whether any changes were made."""
        scope_tree = self.scope_tree if self.scope_tree is not None else build_scope_tree(self.ast)[0]
        inlined_declarators = self._collect_inlineable_declarators(scope_tree)
        if not inlined_declarators:
            return False
        self._remove_declarators(inlined_declarators)
        return self.has_changed()

    def _collect_inlineable_declarators(self, scope: Scope) -> list[dict]:
        """Recursively find and inline single-use constant bindings across all scopes."""
        inlined_declarators: list[dict] = []

        for _name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue
            if binding.kind == 'param':
                continue

            declarator_node = binding.node
            if not isinstance(declarator_node, dict) or declarator_node.get('type') != _NodeType.VARIABLE_DECLARATOR:
                continue
            if not _is_simple_identifier(declarator_node.get('id')):
                continue
            if not _has_valid_init(declarator_node):
                continue
            if _count_nodes(declarator_node['init']) > self._MAX_INIT_NODES:
                continue

            usage_references = self._get_usage_references(binding)
            if len(usage_references) != 1:
                continue

            reference_node, reference_parent, reference_key, reference_index = usage_references[0]
            if _is_assignment_target(reference_parent, reference_key):
                continue
            if self._is_mutated_member_object(reference_parent, reference_key):
                continue

            self._replace_reference(declarator_node['init'], reference_parent, reference_key, reference_index)
            inlined_declarators.append(declarator_node)

        for child_scope in scope.children:
            inlined_declarators.extend(self._collect_inlineable_declarators(child_scope))

        return inlined_declarators

    def _get_usage_references(self, binding: object) -> list[tuple[dict, dict | None, str | None, int | None]]:
        """Filter binding references to only usage sites (excluding declarations)."""
        return [
            (reference_node, reference_parent, reference_key, reference_index)
            for reference_node, reference_parent, reference_key, reference_index in binding.references
            if not _is_declaration_site(reference_parent, reference_key)
        ]

    def _replace_reference(
        self,
        initializer: dict,
        reference_parent: dict | None,
        reference_key: str | None,
        reference_index: int | None,
    ) -> None:
        """Replace a single reference node with a deep copy of the initializer."""
        replacement = deep_copy(initializer)
        if reference_index is not None:
            reference_parent[reference_key][reference_index] = replacement
        else:
            reference_parent[reference_key] = replacement
        self.set_changed()

    def _is_mutated_member_object(self, reference_parent: dict | None, reference_key: str | None) -> bool:
        """Check if ref is the object of a member expression that is an assignment target.

        Catches: obj[x] = val, obj.x = val, obj[x]++, etc.
        """
        if not reference_parent or reference_parent.get('type') != _NodeType.MEMBER_EXPRESSION:
            return False
        if reference_key != _ParentKey.OBJECT:
            return False

        parent_info = self.find_parent(reference_parent)
        if not parent_info:
            return False

        grandparent, grandparent_key, _ = parent_info
        grandparent_type = grandparent.get('type')
        if grandparent_type == _NodeType.ASSIGNMENT_EXPRESSION and grandparent_key == _ParentKey.LEFT:
            return True
        if grandparent_type == _NodeType.UPDATE_EXPRESSION:
            return True
        return False

    def _remove_declarators(self, declarator_nodes: list[dict]) -> None:
        """Remove inlined VariableDeclarators from their parent declarations."""
        declarator_identities = {id(declarator) for declarator in declarator_nodes}

        def enter(
            node: dict,
            parent: dict | None,
            key: str | None,
            index: int | None,
        ) -> object | None:
            """Traverse callback that strips inlined declarators from declarations."""
            if node.get('type') != _NodeType.VARIABLE_DECLARATION:
                return None
            declarations = node.get('declarations', [])
            original_length = len(declarations)
            declarations[:] = [declarator for declarator in declarations if id(declarator) not in declarator_identities]
            if len(declarations) == original_length:
                return None
            self.set_changed()
            if not declarations:
                return REMOVE
            return None

        traverse(self.ast, {'enter': enter})
