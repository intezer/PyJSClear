"""Inline single-use variables.

Targets patterns like:
    const _0x337161 = require("process");
    return _0x337161.env.LOCALAPPDATA;
→   return require("process").env.LOCALAPPDATA;

    const _0x27439f = Buffer.from(_0x162d6f);
    return _0x27439f.toString();
→   return Buffer.from(_0x162d6f).toString();

Only inlines when:
- The variable is constant (no reassignments)
- There is exactly one reference (used once)
- The init expression is not too large (≤ 15 AST nodes)
"""

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import traverse
from ..traverser import simple_traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_identifier
from .base import Transform


def _count_nodes(node):
    """Count AST nodes in a subtree."""
    count = [0]

    def cb(n, parent):
        count[0] += 1

    simple_traverse(node, cb)
    return count[0]


class SingleUseVarInliner(Transform):
    """Inline single-use constant variables at their usage site."""

    rebuild_scope = True

    # Maximum AST node count for an init expression to be inlined.
    # Keeps inlined expressions readable; avoids ballooning line length.
    _MAX_INIT_NODES = 15

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        inlined = self._process_scope(scope_tree)
        if not inlined:
            return False
        self._remove_declarators(inlined)
        return self.has_changed()

    def _process_scope(self, scope):
        """Find and inline single-use constant bindings."""
        inlined_declarators = []

        for name, binding in list(scope.bindings.items()):
            if not binding.is_constant:
                continue
            if binding.kind == 'param':
                continue

            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue

            init = node.get('init')
            if not init or not isinstance(init, dict) or 'type' not in init:
                continue

            # Skip very large init expressions — they'd hurt readability
            if _count_nodes(init) > self._MAX_INIT_NODES:
                continue

            # Must have exactly one reference (the single usage site)
            refs = [
                (ref_node, ref_parent, ref_key, ref_index)
                for ref_node, ref_parent, ref_key, ref_index in binding.references
                if not (ref_parent and ref_parent.get('type') == 'VariableDeclarator' and ref_key == 'id')
            ]
            if len(refs) != 1:
                continue

            # Don't inline if the reference is an assignment target or update
            ref_node, ref_parent, ref_key, ref_index = refs[0]
            if ref_parent and ref_parent.get('type') == 'AssignmentExpression' and ref_key == 'left':
                continue
            if ref_parent and ref_parent.get('type') == 'UpdateExpression':
                continue

            # Don't inline if the reference is the object of a mutated member:
            # e.g. obj[x] = val  or  obj.x = val
            if self._is_mutated_member_object(ref_parent, ref_key):
                continue

            # Inline: replace the reference with the init expression
            replacement = deep_copy(init)
            if ref_index is not None:
                ref_parent[ref_key][ref_index] = replacement
            else:
                ref_parent[ref_key] = replacement
            self.set_changed()
            inlined_declarators.append(node)

        for child in scope.children:
            inlined_declarators.extend(self._process_scope(child))

        return inlined_declarators

    def _is_mutated_member_object(self, ref_parent, ref_key):
        """Check if ref is the object of a member expression that is an assignment target.

        Catches: obj[x] = val, obj.x = val, obj[x]++, etc.
        where `obj` is the identifier we'd be inlining.
        """
        if not ref_parent or ref_parent.get('type') != 'MemberExpression':
            return False
        if ref_key != 'object':
            return False
        # Now check if this MemberExpression is an assignment target
        # We need to find the MemberExpression's parent in the AST
        from ..traverser import find_parent

        parent_info = find_parent(self.ast, ref_parent)
        if not parent_info:
            return False
        grandparent, gp_key, _ = parent_info
        if grandparent.get('type') == 'AssignmentExpression' and gp_key == 'left':
            return True
        if grandparent.get('type') == 'UpdateExpression':
            return True
        return False

    def _remove_declarators(self, declarator_nodes):
        """Remove inlined VariableDeclarators from their parent declarations."""
        declarator_ids = {id(d) for d in declarator_nodes}

        def enter(node, parent, key, index):
            if node.get('type') != 'VariableDeclaration':
                return
            decls = node.get('declarations', [])
            original_len = len(decls)
            decls[:] = [d for d in decls if id(d) not in declarator_ids]
            if len(decls) == original_len:
                return  # No match — continue traversing children
            self.set_changed()
            if not decls:
                return REMOVE

        traverse(self.ast, {'enter': enter})
