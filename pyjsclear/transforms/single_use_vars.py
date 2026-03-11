"""Inline single-use variables initialized with call expressions.

Targets patterns like:
    const _0x337161 = require("process");
    return _0x337161.env.LOCALAPPDATA;
→   return require("process").env.LOCALAPPDATA;

Only inlines when:
- The variable is constant (no reassignments)
- There is exactly one reference (used once)
- The init is a call expression (require(), etc.)
"""

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import SKIP
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_identifier
from .base import Transform


def _is_require_call(node):
    """Check if node is a require("module") call expression.

    Only require() calls are safe to inline because they are
    cached and deterministic — calling require("x") twice returns
    the same module object.
    """
    if not isinstance(node, dict) or node.get('type') != 'CallExpression':
        return False
    callee = node.get('callee')
    if not is_identifier(callee) or callee.get('name') != 'require':
        return False
    args = node.get('arguments', [])
    if len(args) != 1:
        return False
    arg = args[0]
    if not isinstance(arg, dict) or arg.get('type') != 'Literal':
        return False
    if not isinstance(arg.get('value'), str):
        return False
    return True


class SingleUseVarInliner(Transform):
    """Inline single-use variables initialized with call expressions."""

    rebuild_scope = True

    def execute(self):
        scope_tree, _ = build_scope_tree(self.ast)
        inlined = self._process_scope(scope_tree)
        if not inlined:
            return False
        self._remove_declarators(inlined)
        return self.has_changed()

    def _process_scope(self, scope):
        """Find and inline single-use call-expression bindings."""
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
            if not _is_require_call(init):
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
