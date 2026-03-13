"""Split sequence expressions into individual statements.

Converts: (a(), b(), c()) in statement position → a(); b(); c();
Also splits multi-declarator var statements: var a = 1, b = 2 → var a = 1; var b = 2;
Also normalizes loop/if bodies to block statements.
"""

from ..traverser import traverse
from ..utils.ast_helpers import make_block_statement
from ..utils.ast_helpers import make_expression_statement
from .base import Transform


class SequenceSplitter(Transform):
    """Split sequence expressions and normalize control flow bodies."""

    def execute(self) -> bool:
        self._normalize_bodies(self.ast)
        self._split_in_body_arrays(self.ast)
        return self.has_changed()

    def _normalize_bodies(self, ast: dict) -> None:
        """Ensure if/while/for bodies are BlockStatements."""

        def enter(node: dict, parent: dict | None, key: str | None, index: int | None) -> None:
            node_type = node.get('type', '')
            if node_type not in (
                'IfStatement',
                'WhileStatement',
                'DoWhileStatement',
                'ForStatement',
                'ForInStatement',
                'ForOfStatement',
            ):
                return
            body = node.get('body')
            if body and body.get('type') != 'BlockStatement':
                node['body'] = make_block_statement([body])
                self.set_changed()
            if node_type == 'IfStatement':
                self._normalize_if_branches(node)

        traverse(ast, {'enter': enter})

    def _normalize_if_branches(self, node: dict) -> None:
        """Wrap non-block consequent/alternate of IfStatement in BlockStatements."""
        consequent = node.get('consequent')
        if consequent and consequent.get('type') != 'BlockStatement':
            node['consequent'] = make_block_statement([consequent])
            self.set_changed()
        alternate = node.get('alternate')
        if alternate and alternate.get('type') not in ('BlockStatement', 'IfStatement', None):
            node['alternate'] = make_block_statement([alternate])
            self.set_changed()

    def _split_in_body_arrays(self, node: dict) -> None:
        """Find all arrays that contain statements and split sequences + var decls in them."""
        if not isinstance(node, dict):
            return
        for key, child in node.items():
            if isinstance(child, list):
                # Check if this looks like a statement array
                if child and isinstance(child[0], dict) and 'type' in child[0]:
                    self._process_stmt_array(child)
                    for item in child:
                        self._split_in_body_arrays(item)
            elif isinstance(child, dict) and 'type' in child:
                self._split_in_body_arrays(child)

    def _extract_indirect_call_prefixes(self, statement: dict) -> list:
        """Extract dead prefix expressions from (0, fn)(args) patterns.

        Only extracts from:
        - Direct expression of ExpressionStatement
        - Direct init of VariableDeclarator
        - Argument of AwaitExpression in those positions
        - Argument of ReturnStatement
        """
        prefixes = []

        def extract_from_call(node: dict | None) -> None:
            """If node is a CallExpression with SequenceExpression callee, extract prefixes."""
            if not isinstance(node, dict):
                return
            target = node
            if target.get('type') == 'AwaitExpression' and isinstance(target.get('argument'), dict):
                target = target['argument']
            if target.get('type') != 'CallExpression':
                return
            callee = target.get('callee')
            if not isinstance(callee, dict) or callee.get('type') != 'SequenceExpression':
                return
            expressions = callee.get('expressions', [])
            if len(expressions) <= 1:
                return
            prefixes.extend(expressions[:-1])
            target['callee'] = expressions[-1]

        statement_type = statement.get('type', '')
        match statement_type:
            case 'ExpressionStatement':
                extract_from_call(statement.get('expression'))
                # Also check assignment: x = (0, fn)(args)
                expression = statement.get('expression')
                if isinstance(expression, dict) and expression.get('type') == 'AssignmentExpression':
                    extract_from_call(expression.get('right'))
            case 'VariableDeclaration':
                for declarator in statement.get('declarations', []):
                    extract_from_call(declarator.get('init'))
            case 'ReturnStatement':
                extract_from_call(statement.get('argument'))

        return prefixes

    def _process_stmt_array(self, statements: list) -> None:
        """Split sequence expressions and multi-var declarations in a statement array."""
        index = 0
        while index < len(statements):
            statement = statements[index]
            if not isinstance(statement, dict):
                index += 1
                continue

            # Extract dead prefix from indirect call patterns: (0, fn)(args) → 0; fn(args);
            prefixes = self._extract_indirect_call_prefixes(statement)
            if prefixes:
                new_statements = [make_expression_statement(expression) for expression in prefixes]
                new_statements.append(statement)
                statements[index : index + 1] = new_statements
                index += len(new_statements)
                self.set_changed()
                continue

            # Split SequenceExpression in ExpressionStatement
            if (
                statement.get('type') == 'ExpressionStatement'
                and isinstance(statement.get('expression'), dict)
                and statement['expression'].get('type') == 'SequenceExpression'
            ):
                expressions = statement['expression'].get('expressions', [])
                if len(expressions) > 1:
                    new_statements = [make_expression_statement(expression) for expression in expressions]
                    statements[index : index + 1] = new_statements
                    index += len(new_statements)
                    self.set_changed()
                    continue

            # Split multi-declarator VariableDeclaration
            # (but not inside for-loop init — those aren't in body arrays)
            if statement.get('type') == 'VariableDeclaration':
                declarations = statement.get('declarations', [])
                if len(declarations) > 1:
                    kind = statement.get('kind', 'var')
                    new_statements = [
                        {
                            'type': 'VariableDeclaration',
                            'kind': kind,
                            'declarations': [declaration],
                        }
                        for declaration in declarations
                    ]
                    statements[index : index + 1] = new_statements
                    index += len(new_statements)
                    self.set_changed()
                    continue

                # Split SequenceExpression in single declarator init
                if len(declarations) == 1:
                    split_result = self._try_split_single_declarator_init(statement, declarations[0])
                    if split_result:
                        statements[index : index + 1] = split_result
                        index += len(split_result)
                        self.set_changed()
                        continue

            index += 1

    @staticmethod
    def _try_split_single_declarator_init(statement: dict, declarator: dict) -> list | None:
        """Split SequenceExpression from a single VariableDeclarator init.

        Handles both direct sequences and sequences inside AwaitExpression.
        Returns a list of replacement statements, or None.
        """
        init = declarator.get('init')
        if not isinstance(init, dict):
            return None

        # Direct: const x = (a, b, expr()) → a; b; const x = expr();
        if init.get('type') == 'SequenceExpression':
            expressions = init.get('expressions', [])
            if len(expressions) <= 1:
                return None
            prefix = [make_expression_statement(expression) for expression in expressions[:-1]]
            declarator['init'] = expressions[-1]
            prefix.append(statement)
            return prefix

        # Await-wrapped: var x = await (a, b, expr()) → a; b; var x = await expr();
        if (
            init.get('type') == 'AwaitExpression'
            and isinstance(init.get('argument'), dict)
            and init['argument'].get('type') == 'SequenceExpression'
        ):
            expressions = init['argument'].get('expressions', [])
            if len(expressions) <= 1:
                return None
            prefix = [make_expression_statement(expression) for expression in expressions[:-1]]
            init['argument'] = expressions[-1]
            prefix.append(statement)
            return prefix

        return None
