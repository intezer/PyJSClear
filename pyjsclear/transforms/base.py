"""Base transform class."""


class Transform:
    """Base class for all AST transforms."""

    # Subclasses can set this to True to trigger scope rebuild after execution
    rebuild_scope = False

    def __init__(self, ast, scope_tree=None, node_scope=None):
        self.ast = ast
        self.scope_tree = scope_tree
        self.node_scope = node_scope
        self._changed = False

    def execute(self):
        """Execute the transform. Returns True if the AST was modified."""
        raise NotImplementedError

    def set_changed(self):
        self._changed = True

    def has_changed(self):
        return self._changed
