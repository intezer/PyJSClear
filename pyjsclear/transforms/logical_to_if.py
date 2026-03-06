"""Convert logical expressions in statement position to if-statements.

Converts:
  a && b()           →  if (a) { b(); }
  a || b()           →  if (!a) { b(); }
  a && (b(), c())    →  if (a) { b(); c(); }
  return a || 0, b(), c  →  if (!a) { 0; b(); } return c;
  return await x(), y  →  await x(); return y;
"""

from ..utils.ast_helpers import make_block_statement, make_expression_statement
from .base import Transform


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

            # ExpressionStatement with LogicalExpression or ConditionalExpression
            if stmt.get('type') == 'ExpressionStatement':
                expr = stmt.get('expression')
                if isinstance(expr, dict):
                    if expr.get('type') == 'LogicalExpression':
                        replacement = self._logical_to_if(expr)
                        if replacement:
                            stmts[i : i + 1] = replacement
                            self.set_changed()
                            i += len(replacement)
                            continue
                    elif expr.get('type') == 'ConditionalExpression':
                        replacement = self._ternary_to_if(expr)
                        if replacement:
                            stmts[i : i + 1] = replacement
                            self.set_changed()
                            i += len(replacement)
                            continue

            # ReturnStatement with SequenceExpression: return a, b, c → a; b; return c;
            if stmt.get('type') == 'ReturnStatement':
                arg = stmt.get('argument')
                if isinstance(arg, dict) and arg.get('type') == 'SequenceExpression':
                    exprs = arg.get('expressions', [])
                    if len(exprs) > 1:
                        new_stmts = []
                        for e in exprs[:-1]:
                            # If sub-expression is a logical, convert to if
                            if (
                                isinstance(e, dict)
                                and e.get('type') == 'LogicalExpression'
                            ):
                                converted = self._logical_to_if(e)
                                if converted:
                                    new_stmts.extend(converted)
                                else:
                                    new_stmts.append(make_expression_statement(e))
                            else:
                                new_stmts.append(make_expression_statement(e))
                        # Last expression becomes the return value
                        last = exprs[-1]
                        ret = {'type': 'ReturnStatement', 'argument': last}
                        new_stmts.append(ret)
                        stmts[i : i + 1] = new_stmts
                        self.set_changed()
                        i += len(new_stmts)
                        continue

                # ReturnStatement with logical: return a || b → if (!a) { } return b;
                # (Only when the right side has side effects — sequence expressions)
                if isinstance(arg, dict) and arg.get('type') == 'LogicalExpression':
                    right = arg.get('right')
                    if (
                        isinstance(right, dict)
                        and right.get('type') == 'SequenceExpression'
                    ):
                        exprs = right.get('expressions', [])
                        if len(exprs) > 1:
                            op = arg.get('operator')
                            test = arg.get('left')
                            if op == '||':
                                test = {
                                    'type': 'UnaryExpression',
                                    'operator': '!',
                                    'prefix': True,
                                    'argument': test,
                                }
                            # elif op == '&&': test stays as-is

                            body_stmts = [
                                make_expression_statement(e) for e in exprs[:-1]
                            ]
                            if_stmt = {
                                'type': 'IfStatement',
                                'test': test,
                                'consequent': make_block_statement(body_stmts),
                                'alternate': None,
                            }
                            ret = {'type': 'ReturnStatement', 'argument': exprs[-1]}
                            stmts[i : i + 1] = [if_stmt, ret]
                            self.set_changed()
                            i += 2
                            continue

            i += 1

    def _logical_to_if(self, expr):
        """Convert a LogicalExpression to if-statement(s). Returns list of stmts or None."""
        op = expr.get('operator')
        left = expr.get('left')
        right = expr.get('right')

        if op == '&&':
            test = left
        elif op == '||':
            test = {
                'type': 'UnaryExpression',
                'operator': '!',
                'prefix': True,
                'argument': left,
            }
        else:
            return None

        # Expand the right-hand side into statement(s)
        body_stmts = self._expr_to_stmts(right)

        if_stmt = {
            'type': 'IfStatement',
            'test': test,
            'consequent': make_block_statement(body_stmts),
            'alternate': None,
        }
        return [if_stmt]

    def _ternary_to_if(self, expr):
        """Convert a ConditionalExpression to if-else. Returns list of stmts or None."""
        test = expr.get('test')
        consequent = expr.get('consequent')
        alternate = expr.get('alternate')

        cons_stmts = self._expr_to_stmts(consequent)
        alt_stmts = self._expr_to_stmts(alternate)

        if_stmt = {
            'type': 'IfStatement',
            'test': test,
            'consequent': make_block_statement(cons_stmts),
            'alternate': make_block_statement(alt_stmts),
        }
        return [if_stmt]

    def _expr_to_stmts(self, expr):
        """Convert an expression to a list of statements."""
        if isinstance(expr, dict) and expr.get('type') == 'SequenceExpression':
            return [make_expression_statement(e) for e in expr.get('expressions', [])]
        return [make_expression_statement(expr)]
