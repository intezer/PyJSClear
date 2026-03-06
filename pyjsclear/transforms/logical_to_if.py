"""Convert logical expressions in statement position to if-statements.

Converts:
  a && b()           →  if (a) { b(); }
  a || b()           →  if (!a) { b(); }
  a && (b(), c())    →  if (a) { b(); c(); }
  return a || 0, b(), c  →  if (!a) { 0; b(); } return c;
  return await x(), y  →  await x(); return y;
"""

from ..utils.ast_helpers import make_block_statement
from ..utils.ast_helpers import make_expression_statement
from .base import Transform


def _negate(expr):
    """Wrap an expression in a logical NOT."""
    return {
        'type': 'UnaryExpression',
        'operator': '!',
        'prefix': True,
        'argument': expr,
    }


class LogicalToIf(Transform):
    """Convert logical/comma expressions in statement position to if-statements."""

    def execute(self):
        self._transform_bodies(self.ast)
        return self.has_changed()

    def _transform_bodies(self, node):
        """Walk all statement arrays and apply transforms."""
        if not isinstance(node, dict):
            return
        for key, child in node.items():
            if isinstance(child, list):
                if child and isinstance(child[0], dict) and 'type' in child[0]:
                    self._process_stmt_array(child)
                    for item in child:
                        self._transform_bodies(item)
            elif isinstance(child, dict) and 'type' in child:
                self._transform_bodies(child)

    def _process_stmt_array(self, stmts):
        i = 0
        while i < len(stmts):
            stmt = stmts[i]
            if not isinstance(stmt, dict):
                i += 1
                continue

            replacement = self._try_convert_stmt(stmt)
            if replacement is not None:
                stmts[i : i + 1] = replacement
                self.set_changed()
                i += len(replacement)
                continue

            i += 1

    def _try_convert_stmt(self, stmt):
        """Try to convert a statement. Returns replacement list or None."""
        match stmt.get('type'):
            case 'ExpressionStatement':
                return self._handle_expression_stmt(stmt)
            case 'ReturnStatement':
                return self._handle_return_stmt(stmt)
        return None

    def _handle_expression_stmt(self, stmt):
        """Handle ExpressionStatement with logical or conditional."""
        expression = stmt.get('expression')
        if not isinstance(expression, dict):
            return None
        match expression.get('type'):
            case 'LogicalExpression':
                return self._logical_to_if(expression)
            case 'ConditionalExpression':
                return self._ternary_to_if(expression)
        return None

    def _handle_return_stmt(self, stmt):
        """Handle ReturnStatement with sequence or logical expressions."""
        argument = stmt.get('argument')
        if not isinstance(argument, dict):
            return None

        # return a, b, c → a; b; return c;
        if argument.get('type') == 'SequenceExpression':
            return self._split_return_sequence(argument)

        # return a || (b(), c) → if (!a) { b(); } return c;
        if argument.get('type') == 'LogicalExpression':
            return self._split_return_logical(argument)

        return None

    def _split_return_sequence(self, seq):
        """Split return (a, b, c) into a; b; return c."""
        exprs = seq.get('expressions', [])
        if len(exprs) <= 1:
            return None
        new_stmts = []
        for expression in exprs[:-1]:
            if isinstance(expression, dict) and expression.get('type') == 'LogicalExpression':
                converted = self._logical_to_if(expression)
                if converted:
                    new_stmts.extend(converted)
                    continue
            new_stmts.append(make_expression_statement(expression))
        new_stmts.append({'type': 'ReturnStatement', 'argument': exprs[-1]})
        return new_stmts

    def _split_return_logical(self, logical):
        """Split return a || (b(), c) into if (!a) { b(); } return c."""
        right = logical.get('right')
        if not (isinstance(right, dict) and right.get('type') == 'SequenceExpression'):
            return None
        exprs = right.get('expressions', [])
        if len(exprs) <= 1:
            return None

        test = logical.get('left')
        if logical.get('operator') == '||':
            test = _negate(test)

        body_stmts = [make_expression_statement(e) for e in exprs[:-1]]
        if_stmt = {
            'type': 'IfStatement',
            'test': test,
            'consequent': make_block_statement(body_stmts),
            'alternate': None,
        }
        ret = {'type': 'ReturnStatement', 'argument': exprs[-1]}
        return [if_stmt, ret]

    def _logical_to_if(self, expr):
        """Convert a LogicalExpression to if-statement(s). Returns list of stmts or None."""
        left = expr.get('left')
        match expr.get('operator'):
            case '&&':
                test = left
            case '||':
                test = _negate(left)
            case _:
                return None

        body_stmts = self._expr_to_stmts(expr.get('right'))
        if_stmt = {
            'type': 'IfStatement',
            'test': test,
            'consequent': make_block_statement(body_stmts),
            'alternate': None,
        }
        return [if_stmt]

    def _ternary_to_if(self, expr):
        """Convert a ConditionalExpression to if-else. Returns list of stmts or None."""
        if_stmt = {
            'type': 'IfStatement',
            'test': expr.get('test'),
            'consequent': make_block_statement(self._expr_to_stmts(expr.get('consequent'))),
            'alternate': make_block_statement(self._expr_to_stmts(expr.get('alternate'))),
        }
        return [if_stmt]

    def _expr_to_stmts(self, expr):
        """Convert an expression to a list of statements."""
        if isinstance(expr, dict) and expr.get('type') == 'SequenceExpression':
            return [make_expression_statement(e) for e in expr.get('expressions', [])]
        return [make_expression_statement(expr)]
