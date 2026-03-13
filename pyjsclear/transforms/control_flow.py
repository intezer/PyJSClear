"""Control flow flattening recovery.

Detects patterns like:
  var _array = "1|0|3|2|4".split("|"), _index = 0;
  while(true) { switch(_array[_index++]) { case "0": ...; continue; ... } break; }

And reconstructs the linear statement sequence.
"""

from ..utils.ast_helpers import get_child_keys, is_identifier, is_literal, is_string_literal
from .base import Transform


class ControlFlowRecoverer(Transform):
    """Recover control flow from flattened switch/loop dispatchers."""

    rebuild_scope = True

    def execute(self) -> bool:
        self._recover_in_bodies(self.ast)
        return self.has_changed()

    def _recover_in_bodies(self, root: dict) -> None:
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
            self._queue_children(node, stack)

    @staticmethod
    def _queue_children(node: dict, stack: list) -> None:
        """Add all child nodes to the traversal stack."""
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

    def _try_recover_body(self, parent_node: dict, body_key: str, body: list) -> None:
        """Try to find and recover CFF patterns in a body array."""
        index = 0
        while index < len(body):
            statement = body[index]
            if not isinstance(statement, dict):
                index += 1
                continue

            if self._try_recover_variable_pattern(body, index, statement):
                continue
            if self._try_recover_expression_pattern(body, index, statement):
                continue

            index += 1

    def _try_recover_variable_pattern(self, body: list, index: int, statement: dict) -> bool:
        """Try Pattern 1: VariableDeclaration with split + loop. Returns True if recovered."""
        if statement.get('type') != 'VariableDeclaration':
            return False
        state_info = self._find_state_array_in_decl(statement)
        if not state_info:
            return False
        states, state_var, counter_var = state_info
        next_index = index + 1
        if next_index >= len(body):
            return False
        recovered = self._try_recover_from_loop(body[next_index], states, state_var, counter_var)
        if recovered is None:
            return False
        body[index : next_index + 1] = recovered
        self.set_changed()
        return True

    def _try_recover_expression_pattern(self, body: list, index: int, statement: dict) -> bool:
        """Try Pattern 2: ExpressionStatement with split assignment + loop."""
        if statement.get('type') != 'ExpressionStatement':
            return False
        expression = statement.get('expression')
        if not expression or expression.get('type') != 'AssignmentExpression':
            return False
        state_info = self._find_state_from_assignment(expression)
        if not state_info:
            return False
        states, state_var = state_info
        next_index = index + 1
        counter_var = None
        if next_index < len(body):
            counter_variable = self._find_counter_init(body[next_index])
            if counter_variable is not None:
                counter_var = counter_variable
                next_index += 1
        if next_index >= len(body):
            return False
        recovered = self._try_recover_from_loop(body[next_index], states, state_var, counter_var or '_index')
        if recovered is None:
            return False
        body[index : next_index + 1] = recovered
        self.set_changed()
        return True

    def _find_state_array_in_decl(self, declaration: dict) -> tuple | None:
        """Find "X".split("|") pattern in a VariableDeclaration."""
        for declarator in declaration.get('declarations', []):
            initializer = declarator.get('init')
            if not initializer or not self._is_split_call(initializer):
                continue
            states = self._extract_split_states(initializer)
            if not states:
                continue
            if declarator.get('id', {}).get('type') != 'Identifier':
                continue
            state_var = declarator['id']['name']
            counter_var = self._find_counter_in_declaration(declaration, exclude=declarator)
            return states, state_var, counter_var
        return None

    def _find_counter_in_declaration(self, declaration: dict, exclude: dict) -> str | None:
        """Find a numeric-initialized counter variable in a declaration, skipping *exclude*."""
        for declarator in declaration.get('declarations', []):
            if declarator is exclude:
                continue
            if declarator.get('id', {}).get('type') != 'Identifier':
                continue
            initializer = declarator.get('init')
            if (
                initializer
                and initializer.get('type') == 'Literal'
                and isinstance(initializer.get('value'), (int, float))
            ):
                return declarator['id']['name']
        return None

    def _find_state_from_assignment(self, expression: dict) -> tuple | None:
        """Find state array from assignment expression."""
        if expression.get('type') != 'AssignmentExpression':
            return None
        if not is_identifier(expression.get('left')):
            return None
        right = expression.get('right')
        if self._is_split_call(right):
            states = self._extract_split_states(right)
            if states:
                return states, expression['left']['name']
        return None

    def _find_counter_init(self, statement: dict) -> str | None:
        """Find counter variable initialization."""
        if not isinstance(statement, dict):
            return None
        match statement.get('type'):
            case 'VariableDeclaration':
                for declarator in statement.get('declarations', []):
                    if declarator.get('id', {}).get('type') == 'Identifier':
                        initializer = declarator.get('init')
                        if (
                            initializer
                            and initializer.get('type') == 'Literal'
                            and isinstance(initializer.get('value'), (int, float))
                        ):
                            return declarator['id']['name']
            case 'ExpressionStatement':
                expression = statement.get('expression')
                if (
                    expression
                    and expression.get('type') == 'AssignmentExpression'
                    and is_identifier(expression.get('left'))
                    and is_literal(expression.get('right'))
                    and isinstance(expression['right'].get('value'), (int, float))
                ):
                    return expression['left']['name']
        return None

    def _is_split_call(self, node: dict) -> bool:
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
        arguments = node.get('arguments', [])
        if len(arguments) != 1 or not is_string_literal(arguments[0]):
            return False
        return True

    def _extract_split_states(self, node: dict) -> list:
        """Extract states from "1|0|3|2|4".split("|")."""
        callee = node['callee']
        string = callee['object']['value']
        separator = node['arguments'][0]['value']
        return string.split(separator)

    def _try_recover_from_loop(
        self, loop: dict, states: list, state_var: str, counter_var: str | None
    ) -> list | None:
        """Try to recover statements from a for/while loop with switch dispatcher."""
        if not isinstance(loop, dict):
            return None

        initial_value = 0
        switch_body = None

        match loop.get('type', ''):
            case 'ForStatement':
                # for(var _i = 0; ...) { switch(_array[_i++]) { ... } break; }
                initial_value = self._extract_for_init_value(loop.get('init'))
                switch_body = self._extract_switch_from_loop_body(loop.get('body'))
            case 'WhileStatement':
                if self._is_truthy(loop.get('test')):
                    switch_body = self._extract_switch_from_loop_body(loop.get('body'))

        if switch_body is None:
            return None

        cases_map = self._build_case_map(switch_body.get('cases', []))
        return self._reconstruct_statements(cases_map, states, initial_value)

    @staticmethod
    def _extract_for_init_value(initializer: dict | None) -> int:
        """Extract the initial counter value from a for-loop init clause."""
        if not initializer:
            return 0
        if initializer.get('type') == 'VariableDeclaration':
            for declarator in initializer.get('declarations', []):
                if declarator.get('init') and declarator['init'].get('type') == 'Literal':
                    return int(declarator['init'].get('value', 0))
        elif initializer.get('type') == 'AssignmentExpression' and is_literal(initializer.get('right')):
            return int(initializer['right'].get('value', 0))
        return 0

    @staticmethod
    def _build_case_map(cases: list) -> dict:
        """Build map from case test value to (filtered statements, original statements)."""
        cases_map = {}
        for case in cases:
            test = case.get('test')
            if not (test and test.get('type') == 'Literal'):
                continue
            test_value = test['value']
            if isinstance(test_value, float) and test_value == int(test_value):
                key = str(int(test_value))
            else:
                key = str(test_value)
            statements = [
                statement
                for statement in case.get('consequent', [])
                if statement.get('type') not in ('ContinueStatement', 'BreakStatement')
            ]
            cases_map[key] = (statements, case.get('consequent', []))
        return cases_map

    @staticmethod
    def _reconstruct_statements(cases_map: dict, states: list, initial_value: int) -> list | None:
        """Reconstruct linear statement sequence from case map and state order."""
        recovered = []
        for index in range(initial_value, len(states)):
            state = states[index]
            if state not in cases_map:
                break
            statements, original = cases_map[state]
            recovered.extend(statements)
            if original and original[-1].get('type') == 'ReturnStatement':
                recovered.append(original[-1])
                break
        return recovered or None

    def _extract_switch_from_loop_body(self, body: dict | None) -> dict | None:
        """Extract SwitchStatement from loop body."""
        if not isinstance(body, dict):
            return None
        if body.get('type') == 'BlockStatement':
            statements = body.get('body', [])
            for statement in statements:
                if statement.get('type') == 'SwitchStatement':
                    return statement
        elif body.get('type') == 'SwitchStatement':
            return body
        return None

    def _is_truthy(self, node: dict | None) -> bool:
        """Check if a test expression is always truthy."""
        if not isinstance(node, dict):
            return False
        if node.get('type') == 'Literal':
            return bool(node.get('value'))
        # !0 = true, !![] = true
        if node.get('type') == 'UnaryExpression' and node.get('operator') == '!':
            argument = node.get('argument')
            if argument and argument.get('type') == 'Literal' and argument.get('value') == 0:
                return True
            if argument and argument.get('type') == 'ArrayExpression':
                return False  # ![] = false, but !![] = true
            if argument and argument.get('type') == 'UnaryExpression' and argument.get('operator') == '!':
                # !!something
                inner = argument.get('argument')
                if inner and inner.get('type') == 'ArrayExpression':
                    return True
        return False
