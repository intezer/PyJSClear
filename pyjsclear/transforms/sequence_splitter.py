"""Split sequence expressions into individual statements.

Converts: (a(), b(), c()) in statement position -> a(); b(); c();
Also splits multi-declarator var statements: var a = 1, b = 2 -> var a = 1; var b = 2;
Also normalizes loop/if bodies to block statements.
"""

from __future__ import annotations

from enum import StrEnum

from ..traverser import traverse
from ..utils.ast_helpers import make_block_statement
from ..utils.ast_helpers import make_expression_statement
from .base import Transform


class _NodeType(StrEnum):
    """AST node types used in sequence splitting."""

    AWAIT_EXPRESSION = 'AwaitExpression'
    ASSIGNMENT_EXPRESSION = 'AssignmentExpression'
    BLOCK_STATEMENT = 'BlockStatement'
    CALL_EXPRESSION = 'CallExpression'
    DO_WHILE_STATEMENT = 'DoWhileStatement'
    EXPRESSION_STATEMENT = 'ExpressionStatement'
    FOR_IN_STATEMENT = 'ForInStatement'
    FOR_OF_STATEMENT = 'ForOfStatement'
    FOR_STATEMENT = 'ForStatement'
    IF_STATEMENT = 'IfStatement'
    RETURN_STATEMENT = 'ReturnStatement'
    SEQUENCE_EXPRESSION = 'SequenceExpression'
    VARIABLE_DECLARATION = 'VariableDeclaration'
    WHILE_STATEMENT = 'WhileStatement'


_LOOP_AND_IF_TYPES = frozenset(
    {
        _NodeType.IF_STATEMENT,
        _NodeType.WHILE_STATEMENT,
        _NodeType.DO_WHILE_STATEMENT,
        _NodeType.FOR_STATEMENT,
        _NodeType.FOR_IN_STATEMENT,
        _NodeType.FOR_OF_STATEMENT,
    }
)


class SequenceSplitter(Transform):
    """Split sequence expressions and normalize control flow bodies."""

    def execute(self) -> bool:
        """Run all splitting and normalization passes on the AST."""
        self._normalize_bodies(self.ast)
        self._split_in_body_arrays(self.ast)
        return self.has_changed()

    def _normalize_bodies(self, syntax_tree: dict) -> None:
        """Ensure if/while/for bodies are BlockStatements."""

        def enter(
            node: dict,
            parent: dict | None,
            field_key: str | None,
            field_index: int | None,
        ) -> None:
            """Visitor that wraps non-block bodies in BlockStatements."""
            node_type = node.get('type', '')
            if node_type not in _LOOP_AND_IF_TYPES:
                return
            body = node.get('body')
            if body and body.get('type') != _NodeType.BLOCK_STATEMENT:
                node['body'] = make_block_statement([body])
                self.set_changed()
            if node_type == _NodeType.IF_STATEMENT:
                self._normalize_if_branches(node)

        traverse(syntax_tree, {'enter': enter})

    def _normalize_if_branches(self, node: dict) -> None:
        """Wrap non-block consequent/alternate of IfStatement in BlockStatements."""
        consequent = node.get('consequent')
        if consequent and consequent.get('type') != _NodeType.BLOCK_STATEMENT:
            node['consequent'] = make_block_statement([consequent])
            self.set_changed()

        alternate = node.get('alternate')
        if not alternate:
            return
        if alternate.get('type') not in (_NodeType.BLOCK_STATEMENT, _NodeType.IF_STATEMENT, None):
            node['alternate'] = make_block_statement([alternate])
            self.set_changed()

    def _split_in_body_arrays(self, node: dict) -> None:
        """Recursively find statement arrays and split sequences + var decls in them."""
        if not isinstance(node, dict):
            return
        for _field_key, child in node.items():
            if isinstance(child, list):
                if child and isinstance(child[0], dict) and 'type' in child[0]:
                    self._process_statement_array(child)
                    for item in child:
                        self._split_in_body_arrays(item)
            elif isinstance(child, dict) and 'type' in child:
                self._split_in_body_arrays(child)

    def _extract_indirect_call_prefixes(self, statement: dict) -> list[dict]:
        """Extract dead prefix expressions from (0, fn)(args) patterns.

        Only extracts from:
        - Direct expression of ExpressionStatement
        - Direct init of VariableDeclarator
        - Argument of AwaitExpression in those positions
        - Argument of ReturnStatement
        """
        prefixes: list[dict] = []

        def extract_from_call(node: dict | None) -> None:
            """If node is a CallExpression with SequenceExpression callee, extract prefixes."""
            if not isinstance(node, dict):
                return
            target = node
            if target.get('type') == _NodeType.AWAIT_EXPRESSION and isinstance(target.get('argument'), dict):
                target = target['argument']
            if target.get('type') != _NodeType.CALL_EXPRESSION:
                return
            callee = target.get('callee')
            if not isinstance(callee, dict) or callee.get('type') != _NodeType.SEQUENCE_EXPRESSION:
                return
            expressions = callee.get('expressions', [])
            if len(expressions) <= 1:
                return
            prefixes.extend(expressions[:-1])
            target['callee'] = expressions[-1]

        statement_type = statement.get('type', '')
        match statement_type:
            case _NodeType.EXPRESSION_STATEMENT:
                extract_from_call(statement.get('expression'))
                expression = statement.get('expression')
                if isinstance(expression, dict) and expression.get('type') == _NodeType.ASSIGNMENT_EXPRESSION:
                    extract_from_call(expression.get('right'))
            case _NodeType.VARIABLE_DECLARATION:
                for declarator in statement.get('declarations', []):
                    extract_from_call(declarator.get('init'))
            case _NodeType.RETURN_STATEMENT:
                extract_from_call(statement.get('argument'))

        return prefixes

    def _process_statement_array(self, statements: list[dict]) -> None:
        """Split sequence expressions and multi-var declarations in a statement array."""
        index = 0
        while index < len(statements):
            statement = statements[index]
            if not isinstance(statement, dict):
                index += 1
                continue

            replacement = self._try_expand_statement(statement)
            if replacement is not None:
                statements[index : index + 1] = replacement
                index += len(replacement)
                self.set_changed()
                continue

            index += 1

    def _try_expand_statement(self, statement: dict) -> list[dict] | None:
        """Attempt to expand a single statement into multiple statements.

        Returns a list of replacement statements, or None if no expansion applies.
        """
        # Extract dead prefix from indirect call patterns: (0, fn)(args) -> 0; fn(args);
        prefixes = self._extract_indirect_call_prefixes(statement)
        if prefixes:
            expanded = [make_expression_statement(expression) for expression in prefixes]
            expanded.append(statement)
            return expanded

        # Split SequenceExpression in ExpressionStatement
        if statement.get('type') == _NodeType.EXPRESSION_STATEMENT:
            return self._try_split_expression_statement(statement)

        # Split multi-declarator VariableDeclaration
        if statement.get('type') == _NodeType.VARIABLE_DECLARATION:
            return self._try_split_variable_declaration(statement)

        return None

    @staticmethod
    def _try_split_expression_statement(statement: dict) -> list[dict] | None:
        """Split a SequenceExpression inside an ExpressionStatement into separate statements."""
        expression = statement.get('expression')
        if not isinstance(expression, dict):
            return None
        if expression.get('type') != _NodeType.SEQUENCE_EXPRESSION:
            return None
        expressions = expression.get('expressions', [])
        if len(expressions) <= 1:
            return None
        return [make_expression_statement(expr) for expr in expressions]

    def _try_split_variable_declaration(self, statement: dict) -> list[dict] | None:
        """Split multi-declarator VariableDeclarations or sequence inits."""
        declarations = statement.get('declarations', [])
        if len(declarations) > 1:
            kind = statement.get('kind', 'var')
            return [
                {
                    'type': _NodeType.VARIABLE_DECLARATION,
                    'kind': kind,
                    'declarations': [declaration],
                }
                for declaration in declarations
            ]

        if len(declarations) == 1:
            return self._try_split_single_declarator_init(statement, declarations[0])

        return None

    @staticmethod
    def _try_split_single_declarator_init(
        statement: dict,
        declarator: dict,
    ) -> list[dict] | None:
        """Split SequenceExpression from a single VariableDeclarator init.

        Handles both direct sequences and sequences inside AwaitExpression.
        Returns a list of replacement statements, or None.
        """
        init = declarator.get('init')
        if not isinstance(init, dict):
            return None

        # Direct: const x = (a, b, expr()) -> a; b; const x = expr();
        if init.get('type') == _NodeType.SEQUENCE_EXPRESSION:
            expressions = init.get('expressions', [])
            if len(expressions) <= 1:
                return None
            prefix_statements = [make_expression_statement(expression) for expression in expressions[:-1]]
            declarator['init'] = expressions[-1]
            prefix_statements.append(statement)
            return prefix_statements

        # Await-wrapped: var x = await (a, b, expr()) -> a; b; var x = await expr();
        if (
            init.get('type') == _NodeType.AWAIT_EXPRESSION
            and isinstance(init.get('argument'), dict)
            and init['argument'].get('type') == _NodeType.SEQUENCE_EXPRESSION
        ):
            expressions = init['argument'].get('expressions', [])
            if len(expressions) <= 1:
                return None
            prefix_statements = [make_expression_statement(expression) for expression in expressions[:-1]]
            init['argument'] = expressions[-1]
            prefix_statements.append(statement)
            return prefix_statements

        return None
