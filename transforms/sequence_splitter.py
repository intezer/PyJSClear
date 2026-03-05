"""Split sequence expressions into individual statements.

Converts: (a(), b(), c()) in statement position → a(); b(); c();
Also normalizes loop/if bodies to block statements.
"""

from .base import Transform
from ..traverser import traverse
from ..utils.ast_helpers import make_expression_statement, make_block_statement


class SequenceSplitter(Transform):
    """Split sequence expressions and normalize control flow bodies."""

    def execute(self):
        self._normalize_bodies(self.ast)
        self._split_sequences(self.ast)
        return self.has_changed()

    def _normalize_bodies(self, ast):
        """Ensure if/while/for bodies are BlockStatements."""
        def enter(node, parent, key, index):
            ntype = node.get('type', '')
            if ntype in ('IfStatement', 'WhileStatement', 'DoWhileStatement', 'ForStatement', 'ForInStatement', 'ForOfStatement'):
                body = node.get('body')
                if body and body.get('type') != 'BlockStatement':
                    node['body'] = make_block_statement([body])
                    self.set_changed()
                if ntype == 'IfStatement':
                    cons = node.get('consequent')
                    if cons and cons.get('type') != 'BlockStatement':
                        node['consequent'] = make_block_statement([cons])
                        self.set_changed()
                    alt = node.get('alternate')
                    if alt and alt.get('type') not in ('BlockStatement', 'IfStatement', None):
                        node['alternate'] = make_block_statement([alt])
                        self.set_changed()

        traverse(ast, {'enter': enter})

    def _split_sequences(self, ast):
        """Split SequenceExpressions in statement position into separate statements."""
        self._split_in_bodies(ast)

    def _split_in_bodies(self, node):
        """Walk bodies and split sequence expressions."""
        if not isinstance(node, dict) or 'type' not in node:
            return

        from ..utils.ast_helpers import get_child_keys
        for key in get_child_keys(node):
            child = node.get(key)
            if child is None:
                continue
            if isinstance(child, list) and key in ('body', 'consequent'):
                i = 0
                while i < len(child):
                    stmt = child[i]
                    if (isinstance(stmt, dict) and
                            stmt.get('type') == 'ExpressionStatement' and
                            isinstance(stmt.get('expression'), dict) and
                            stmt['expression'].get('type') == 'SequenceExpression'):
                        exprs = stmt['expression'].get('expressions', [])
                        if len(exprs) > 1:
                            new_stmts = [make_expression_statement(e) for e in exprs]
                            child[i:i + 1] = new_stmts
                            i += len(new_stmts)
                            self.set_changed()
                            continue
                    i += 1
                for item in child:
                    self._split_in_bodies(item)
            elif isinstance(child, dict) and 'type' in child:
                self._split_in_bodies(child)
