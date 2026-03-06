"""Constant propagation — replace references to constant variables with their literal values."""

from ..scope import build_scope_tree
from ..traverser import REMOVE
from ..traverser import SKIP
from ..traverser import traverse
from ..utils.ast_helpers import deep_copy
from ..utils.ast_helpers import is_literal
from .base import Transform


def _should_skip_reference(ref_parent, ref_key):
    """Return True if this reference should not be replaced with its literal value."""
    if not ref_parent:
        return True
    match ref_parent.get('type'):
        case 'AssignmentExpression' if ref_key == 'left':
            return True
        case 'UpdateExpression':
            return True
        case 'VariableDeclarator' if ref_key == 'id':
            return True
    return False


class ConstantProp(Transform):
    """Find `const x = <literal>` and replace all references with the literal."""

    rebuild_scope = True

    def execute(self):
        scope_tree, node_scope = build_scope_tree(self.ast)

        replacements = dict(self._iter_constant_bindings(scope_tree))
        if not replacements:
            return False

        bindings_replaced = self._replace_references(replacements)
        self._remove_fully_propagated(replacements, bindings_replaced)
        return self.has_changed()

    def _iter_constant_bindings(self, scope):
        """Yield (binding_id, (binding, literal)) for constant bindings with literal values."""
        for name, binding in scope.bindings.items():
            if not binding.is_constant:
                continue
            node = binding.node
            if not isinstance(node, dict) or node.get('type') != 'VariableDeclarator':
                continue
            init_val = node.get('init')
            if not init_val or not is_literal(init_val):
                continue
            yield id(binding), (binding, init_val)

        for child in scope.children:
            yield from self._iter_constant_bindings(child)

    def _replace_references(self, replacements):
        """Replace all qualifying references with their literal values."""
        bindings_replaced = set()
        for bind_id, (binding, literal) in replacements.items():
            for ref_node, ref_parent, ref_key, ref_index in binding.references:
                if _should_skip_reference(ref_parent, ref_key):
                    continue
                new_node = deep_copy(literal)
                if ref_index is not None:
                    ref_parent[ref_key][ref_index] = new_node
                else:
                    ref_parent[ref_key] = new_node
                self.set_changed()
                bindings_replaced.add(bind_id)
        return bindings_replaced

    def _remove_fully_propagated(self, replacements, bindings_replaced):
        """Remove declarations whose bindings were fully propagated."""
        for bind_id in bindings_replaced:
            binding = replacements[bind_id][0]
            if binding.assignments:
                continue
            decl_node = binding.node
            if not isinstance(decl_node, dict):
                continue
            if decl_node.get('type') != 'VariableDeclarator':
                continue
            self._remove_declarator(decl_node)

    def _remove_declarator(self, declarator_node):
        """Remove a VariableDeclarator from its parent VariableDeclaration."""

        def enter(node, parent, key, index):
            if node.get('type') != 'VariableDeclaration':
                return
            decls = node.get('declarations', [])
            for i, declaration in enumerate(decls):
                if declaration is not declarator_node:
                    continue
                decls.pop(i)
                self.set_changed()
                if not decls:
                    return REMOVE
                return SKIP

        traverse(self.ast, {'enter': enter})
