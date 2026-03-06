"""Split sequence expressions into individual statements.

Converts: (a(), b(), c()) in statement position → a(); b(); c();
Also splits multi-declarator var statements: var a = 1, b = 2 → var a = 1; var b = 2;
Also normalizes loop/if bodies to block statements.
"""

from .base import Transform
from ..traverser import traverse
from ..utils.ast_helpers import make_expression_statement, make_block_statement


class SequenceSplitter(Transform):
    """Split sequence expressions and normalize control flow bodies."""

    def execute(self):
        self._normalize_bodies(self.ast)
        self._split_in_body_arrays(self.ast)
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

    def _split_in_body_arrays(self, node):
        """Find all arrays that contain statements and split sequences + var decls in them."""
        if not isinstance(node, dict):
            return
        for key, child in node.items():
            if isinstance(child, list):
                # Check if this looks like a statement array
                if child and isinstance(child[0], dict) and 'type' in child[0]:
                    self._process_stmt_array(child)
                    # Recurse into items
                    for item in child:
                        self._split_in_body_arrays(item)
            elif isinstance(child, dict) and 'type' in child:
                self._split_in_body_arrays(child)

    def _extract_indirect_call_prefixes(self, stmt):
        """Extract dead prefix expressions from (0, fn)(args) patterns.

        Only extracts from:
        - Direct expression of ExpressionStatement
        - Direct init of VariableDeclarator
        - Argument of AwaitExpression in those positions
        - Argument of ReturnStatement
        """
        prefixes = []

        def extract_from_call(node):
            """If node is a CallExpression with SequenceExpression callee, extract prefixes."""
            if not isinstance(node, dict):
                return
            # Handle await wrapping
            target = node
            if target.get('type') == 'AwaitExpression' and isinstance(target.get('argument'), dict):
                target = target['argument']
            if (target.get('type') == 'CallExpression' and
                    isinstance(target.get('callee'), dict) and
                    target['callee'].get('type') == 'SequenceExpression'):
                exprs = target['callee'].get('expressions', [])
                if len(exprs) > 1:
                    prefixes.extend(exprs[:-1])
                    target['callee'] = exprs[-1]

        stype = stmt.get('type', '')
        if stype == 'ExpressionStatement':
            extract_from_call(stmt.get('expression'))
        elif stype == 'VariableDeclaration':
            for d in stmt.get('declarations', []):
                extract_from_call(d.get('init'))
        elif stype == 'ReturnStatement':
            extract_from_call(stmt.get('argument'))
        # Also check assignment expressions in ExpressionStatements:
        # x = (0, fn)(args)
        if stype == 'ExpressionStatement':
            expr = stmt.get('expression')
            if isinstance(expr, dict) and expr.get('type') == 'AssignmentExpression':
                extract_from_call(expr.get('right'))

        return prefixes

    def _process_stmt_array(self, stmts):
        """Split sequence expressions and multi-var declarations in a statement array."""
        i = 0
        while i < len(stmts):
            stmt = stmts[i]
            if not isinstance(stmt, dict):
                i += 1
                continue

            # Extract dead prefix from indirect call patterns: (0, fn)(args) → 0; fn(args);
            prefixes = self._extract_indirect_call_prefixes(stmt)
            if prefixes:
                new_stmts = [make_expression_statement(e) for e in prefixes]
                new_stmts.append(stmt)
                stmts[i:i+1] = new_stmts
                i += len(new_stmts)
                self.set_changed()
                continue

            # Split SequenceExpression in ExpressionStatement
            if (stmt.get('type') == 'ExpressionStatement' and
                    isinstance(stmt.get('expression'), dict) and
                    stmt['expression'].get('type') == 'SequenceExpression'):
                exprs = stmt['expression'].get('expressions', [])
                if len(exprs) > 1:
                    new_stmts = [make_expression_statement(e) for e in exprs]
                    stmts[i:i + 1] = new_stmts
                    i += len(new_stmts)
                    self.set_changed()
                    continue

            # Split multi-declarator VariableDeclaration
            # (but not inside for-loop init — those aren't in body arrays)
            if stmt.get('type') == 'VariableDeclaration':
                decls = stmt.get('declarations', [])
                if len(decls) > 1:
                    kind = stmt.get('kind', 'var')
                    new_stmts = [{
                        'type': 'VariableDeclaration',
                        'kind': kind,
                        'declarations': [d],
                    } for d in decls]
                    stmts[i:i + 1] = new_stmts
                    i += len(new_stmts)
                    self.set_changed()
                    continue

                # Split SequenceExpression in single declarator init:
                # const x = (0, expr()) → 0; const x = expr();
                if len(decls) == 1:
                    init = decls[0].get('init')
                    if isinstance(init, dict):
                        # Direct SequenceExpression in init
                        if init.get('type') == 'SequenceExpression':
                            exprs = init.get('expressions', [])
                            if len(exprs) > 1:
                                new_stmts = [make_expression_statement(e) for e in exprs[:-1]]
                                decls[0]['init'] = exprs[-1]
                                new_stmts.append(stmt)
                                stmts[i:i+1] = new_stmts
                                i += len(new_stmts)
                                self.set_changed()
                                continue
                        # AwaitExpression wrapping SequenceExpression:
                        # var x = await (0, expr()) → 0; var x = await expr();
                        if (init.get('type') == 'AwaitExpression' and
                                isinstance(init.get('argument'), dict) and
                                init['argument'].get('type') == 'SequenceExpression'):
                            exprs = init['argument'].get('expressions', [])
                            if len(exprs) > 1:
                                new_stmts = [make_expression_statement(e) for e in exprs[:-1]]
                                init['argument'] = exprs[-1]
                                new_stmts.append(stmt)
                                stmts[i:i+1] = new_stmts
                                i += len(new_stmts)
                                self.set_changed()
                                continue

            i += 1
