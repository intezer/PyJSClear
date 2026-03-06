"""Control flow flattening recovery.

Detects patterns like:
  var _array = "1|0|3|2|4".split("|"), _index = 0;
  while(true) { switch(_array[_index++]) { case "0": ...; continue; ... } break; }

And reconstructs the linear statement sequence.
"""

from ..utils.ast_helpers import get_child_keys
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from .base import Transform


class ControlFlowRecoverer(Transform):
    """Recover control flow from flattened switch/loop dispatchers."""

    rebuild_scope = True

    def execute(self):
        self._recover_in_bodies(self.ast)
        return self.has_changed()

    def _recover_in_bodies(self, root):
        """Walk through the AST looking for bodies containing CFF patterns."""
        stack = [root]
        visited = set()
        while stack:
            node = stack.pop()
            if not isinstance(node, dict) or 'type' not in node:
                continue

            node_id = id(node)
            if node_id in visited:
                continue
            visited.add(node_id)

            node_type = node.get('type', '')

            # Check in body arrays
            if node_type in ('Program', 'BlockStatement'):
                self._try_recover_body(node, 'body', node.get('body', []))

            # Queue children for processing
            for key in get_child_keys(node):
                child = node.get(key)
                if child is None:
                    continue
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, dict) and 'type' in item:
                            stack.append(item)
                elif isinstance(child, dict) and 'type' in child:
                    stack.append(child)

    def _try_recover_body(self, parent_node, body_key, body):
        """Try to find and recover CFF patterns in a body array."""
        i = 0
        while i < len(body):
            statement = body[i]
            if not isinstance(statement, dict):
                i += 1
                continue

            if self._try_recover_variable_pattern(body, i, statement):
                continue
            if self._try_recover_expression_pattern(body, i, statement):
                continue

            i += 1

    def _try_recover_variable_pattern(self, body, i, stmt):
        """Try Pattern 1: VariableDeclaration with split + loop. Returns True if recovered."""
        if stmt.get('type') != 'VariableDeclaration':
            return False
        state_info = self._find_state_array_in_decl(stmt)
        if not state_info:
            return False
        states, state_var, counter_var = state_info
        next_idx = i + 1
        if next_idx >= len(body):
            return False
        recovered = self._try_recover_from_loop(body[next_idx], states, state_var, counter_var)
        if recovered is None:
            return False
        body[i : next_idx + 1] = recovered
        self.set_changed()
        return True

    def _try_recover_expression_pattern(self, body, i, stmt):
        """Try Pattern 2: ExpressionStatement with split assignment + loop."""
        if stmt.get('type') != 'ExpressionStatement':
            return False
        expr = stmt.get('expression')
        if not expr or expr.get('type') != 'AssignmentExpression':
            return False
        state_info = self._find_state_from_assignment(expr)
        if not state_info:
            return False
        states, state_var = state_info
        next_idx = i + 1
        counter_var = None
        if next_idx < len(body):
            counter_variable = self._find_counter_init(body[next_idx])
            if counter_variable is not None:
                counter_var = counter_variable
                next_idx += 1
        if next_idx >= len(body):
            return False
        recovered = self._try_recover_from_loop(body[next_idx], states, state_var, counter_var or '_index')
        if recovered is None:
            return False
        body[i : next_idx + 1] = recovered
        self.set_changed()
        return True

    def _find_state_array_in_decl(self, decl):
        """Find "X".split("|") pattern in a VariableDeclaration."""
        for declaration in decl.get('declarations', []):
            initializer = declaration.get('init')
            if not initializer or not self._is_split_call(initializer):
                continue
            states = self._extract_split_states(initializer)
            if not states:
                continue
            if declaration.get('id', {}).get('type') != 'Identifier':
                continue
            state_var = declaration['id']['name']
            counter_var = self._find_counter_in_declaration(decl, exclude=declaration)
            return states, state_var, counter_var
        return None

    def _find_counter_in_declaration(self, decl, exclude):
        """Find a numeric-initialized counter variable in a declaration, skipping *exclude*."""
        for declaration in decl.get('declarations', []):
            if declaration is exclude:
                continue
            if declaration.get('id', {}).get('type') != 'Identifier':
                continue
            initializer = declaration.get('init')
            if (
                initializer
                and initializer.get('type') == 'Literal'
                and isinstance(initializer.get('value'), (int, float))
            ):
                return declaration['id']['name']
        return None

    def _find_state_from_assignment(self, expr):
        """Find state array from assignment expression."""
        if expr.get('type') != 'AssignmentExpression':
            return None
        if not is_identifier(expr.get('left')):
            return None
        right = expr.get('right')
        if self._is_split_call(right):
            states = self._extract_split_states(right)
            if states:
                return states, expr['left']['name']
        return None

    def _find_counter_init(self, statement):
        """Find counter variable initialization."""
        if not isinstance(statement, dict):
            return None
        if statement.get('type') == 'VariableDeclaration':
            for declaration in statement.get('declarations', []):
                if declaration.get('id', {}).get('type') == 'Identifier':
                    initializer = declaration.get('init')
                    if (
                        initializer
                        and initializer.get('type') == 'Literal'
                        and isinstance(initializer.get('value'), (int, float))
                    ):
                        return declaration['id']['name']
        if statement.get('type') == 'ExpressionStatement':
            expr = statement.get('expression')
            if (
                expr
                and expr.get('type') == 'AssignmentExpression'
                and is_identifier(expr.get('left'))
                and is_literal(expr.get('right'))
                and isinstance(expr['right'].get('value'), (int, float))
            ):
                return expr['left']['name']
        return None

    def _is_split_call(self, node):
        """Check if node is "X".split("|")."""
        if not isinstance(node, dict):
            return False
        if node.get('type') != 'CallExpression':
            return False
        callee = node.get('callee')
        if not callee or callee.get('type') != 'MemberExpression':
            return False
        object_expression = callee.get('object')
        property_expression = callee.get('property')
        if not is_string_literal(object_expression):
            return False
        if not (is_identifier(property_expression) and property_expression.get('name') == 'split') and not (
            is_string_literal(property_expression) and property_expression.get('value') == 'split'
        ):
            return False
        args = node.get('arguments', [])
        if len(args) != 1 or not is_string_literal(args[0]):
            return False
        return True

    def _extract_split_states(self, node):
        """Extract states from "1|0|3|2|4".split("|")."""
        callee = node['callee']
        string = callee['object']['value']
        separator = node['arguments'][0]['value']
        return string.split(separator)

    def _try_recover_from_loop(self, loop, states, state_var, counter_var):
        """Try to recover statements from a for/while loop with switch dispatcher."""
        if not isinstance(loop, dict):
            return None

        loop_type = loop.get('type', '')
        switch_body = None
        initial_value = 0

        if loop_type == 'ForStatement':
            # for(var _i = 0; ...) { switch(_array[_i++]) { ... } break; }
            initializer = loop.get('init')
            if initializer:
                if initializer.get('type') == 'VariableDeclaration':
                    for declaration in initializer.get('declarations', []):
                        if declaration.get('init') and declaration['init'].get('type') == 'Literal':
                            initial_value = int(declaration['init'].get('value', 0))
                elif initializer.get('type') == 'AssignmentExpression' and is_literal(initializer.get('right')):
                    initial_value = int(initializer['right'].get('value', 0))
            switch_body = self._extract_switch_from_loop_body(loop.get('body'))

        elif loop_type == 'WhileStatement':
            test = loop.get('test')
            if self._is_truthy(test):
                switch_body = self._extract_switch_from_loop_body(loop.get('body'))

        if switch_body is None:
            return None

        cases = switch_body.get('cases', [])
        # Build map from case test value to consequent statements
        cases_map = {}
        for case in cases:
            test = case.get('test')
            if test and test.get('type') == 'Literal':
                test_value = test['value']
                # Normalize key: float 1.0 -> '1', string '1' -> '1'
                if isinstance(test_value, float) and test_value == int(test_value):
                    key = str(int(test_value))
                else:
                    key = str(test_value)
                # Filter out continue and break statements
                statements = [
                    statement
                    for statement in case.get('consequent', [])
                    if statement.get('type') not in ('ContinueStatement', 'BreakStatement')
                ]
                cases_map[key] = (statements, case.get('consequent', []))

        # Reconstruct statement sequence
        recovered = []
        for idx in range(initial_value, len(states)):
            state = states[idx]
            if state not in cases_map:
                break
            statements, original = cases_map[state]
            recovered.extend(statements)
            # Stop if there's a return statement
            if original and original[-1].get('type') == 'ReturnStatement':
                recovered.append(original[-1])
                break

        if not recovered:
            return None
        return recovered

    def _extract_switch_from_loop_body(self, body):
        """Extract SwitchStatement from loop body."""
        if not isinstance(body, dict):
            return None
        if body.get('type') == 'BlockStatement':
            stmts = body.get('body', [])
            for stmt in stmts:
                if stmt.get('type') == 'SwitchStatement':
                    return stmt
        elif body.get('type') == 'SwitchStatement':
            return body
        return None

    def _is_truthy(self, node):
        """Check if a test expression is always truthy."""
        if not isinstance(node, dict):
            return False
        if node.get('type') == 'Literal':
            return bool(node.get('value'))
        # !0 = true, !![] = true
        if node.get('type') == 'UnaryExpression' and node.get('operator') == '!':
            arg = node.get('argument')
            if arg and arg.get('type') == 'Literal' and arg.get('value') == 0:
                return True
            if arg and arg.get('type') == 'ArrayExpression':
                return False  # ![] = false, but !![] = true
            if arg and arg.get('type') == 'UnaryExpression' and arg.get('operator') == '!':
                # !!something
                inner = arg.get('argument')
                if inner and inner.get('type') == 'ArrayExpression':
                    return True
        return False
