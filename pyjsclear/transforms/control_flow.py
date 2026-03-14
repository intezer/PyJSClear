"""Control flow flattening recovery.

Detects patterns like:
  var _array = "1|0|3|2|4".split("|"), _index = 0;
  while(true) { switch(_array[_index++]) { case "0": ...; continue; ... } break; }

And reconstructs the linear statement sequence.
"""

from __future__ import annotations

from ..utils.ast_helpers import get_child_keys
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_literal
from ..utils.ast_helpers import is_string_literal
from .base import Transform


class ControlFlowRecoverer(Transform):
    """Recover control flow from flattened switch/loop dispatchers.

    Handles two patterns:
    1. VariableDeclaration with split() initializer followed by a dispatcher loop.
    2. ExpressionStatement assignment with split() followed by a dispatcher loop.
    """

    rebuild_scope = True

    def execute(self) -> bool:
        """Run the transform and return whether any changes were made."""
        self._recover_in_bodies(self.ast)
        return self.has_changed()

    def _recover_in_bodies(self, root: dict) -> None:
        """Iteratively walk the AST looking for bodies containing CFF patterns."""
        stack: list[dict] = [root]
        visited: set[int] = set()
        while stack:
            node = stack.pop()
            if not isinstance(node, dict) or 'type' not in node:
                continue

            node_id = id(node)
            if node_id in visited:
                continue
            visited.add(node_id)

            node_type = node.get('type', '')

            if node_type in ('Program', 'BlockStatement'):
                self._try_recover_body(node.get('body', []))

            self._queue_children(node, stack)

    @staticmethod
    def _queue_children(node: dict, stack: list[dict]) -> None:
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

    def _try_recover_body(self, body: list[dict]) -> None:
        """Scan a body array for CFF patterns and recover them in place."""
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

    def _try_recover_variable_pattern(self, body: list[dict], index: int, statement: dict) -> bool:
        """Attempt recovery of Pattern 1: VariableDeclaration with split + loop."""
        if statement.get('type') != 'VariableDeclaration':
            return False
        state_info = self._find_state_array_in_declaration(statement)
        if not state_info:
            return False
        states, state_variable, counter_variable = state_info
        next_index = index + 1
        if next_index >= len(body):
            return False
        recovered = self._try_recover_from_loop(
            body[next_index],
            states,
            state_variable,
            counter_variable,
        )
        if recovered is None:
            return False
        body[index : next_index + 1] = recovered
        self.set_changed()
        return True

    def _try_recover_expression_pattern(self, body: list[dict], index: int, statement: dict) -> bool:
        """Attempt recovery of Pattern 2: ExpressionStatement with split assignment + loop."""
        if statement.get('type') != 'ExpressionStatement':
            return False
        expression = statement.get('expression')
        if not expression or expression.get('type') != 'AssignmentExpression':
            return False
        state_info = self._find_state_from_assignment(expression)
        if not state_info:
            return False
        states, state_variable = state_info
        next_index = index + 1
        counter_variable = None
        if next_index < len(body):
            found_counter = self._find_counter_init(body[next_index])
            if found_counter is not None:
                counter_variable = found_counter
                next_index += 1
        if next_index >= len(body):
            return False
        recovered = self._try_recover_from_loop(
            body[next_index],
            states,
            state_variable,
            counter_variable or '_index',
        )
        if recovered is None:
            return False
        body[index : next_index + 1] = recovered
        self.set_changed()
        return True

    def _find_state_array_in_declaration(self, declaration: dict) -> tuple[list[str], str, str | None] | None:
        """Find a 'X'.split('|') pattern in a VariableDeclaration."""
        for declarator in declaration.get('declarations', []):
            initializer = declarator.get('init')
            if not initializer or not self._is_split_call(initializer):
                continue
            states = self._extract_split_states(initializer)
            if not states:
                continue
            if declarator.get('id', {}).get('type') != 'Identifier':
                continue
            state_variable = declarator['id']['name']
            counter_variable = self._find_counter_in_declaration(declaration, exclude=declarator)
            return states, state_variable, counter_variable
        return None

    def _find_counter_in_declaration(self, declaration: dict, exclude: dict) -> str | None:
        """Find a numeric-initialized counter variable, skipping the excluded declarator."""
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

    def _find_state_from_assignment(self, expression: dict) -> tuple[list[str], str] | None:
        """Extract state array from an assignment expression with split()."""
        if expression.get('type') != 'AssignmentExpression':
            return None
        if not is_identifier(expression.get('left')):
            return None
        right = expression.get('right')
        if not self._is_split_call(right):
            return None
        states = self._extract_split_states(right)
        if not states:
            return None
        return states, expression['left']['name']

    def _find_counter_init(self, statement: dict) -> str | None:
        """Find a counter variable initialization in a statement."""
        if not isinstance(statement, dict):
            return None
        match statement.get('type'):
            case 'VariableDeclaration':
                return self._find_counter_in_variable_declaration(statement)
            case 'ExpressionStatement':
                return self._find_counter_in_expression_statement(statement)
        return None

    @staticmethod
    def _find_counter_in_variable_declaration(statement: dict) -> str | None:
        """Extract counter name from a VariableDeclaration with numeric init."""
        for declarator in statement.get('declarations', []):
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

    @staticmethod
    def _find_counter_in_expression_statement(statement: dict) -> str | None:
        """Extract counter name from an ExpressionStatement with numeric assignment."""
        expression = statement.get('expression')
        if not expression:
            return None
        if expression.get('type') != 'AssignmentExpression':
            return None
        if not is_identifier(expression.get('left')):
            return None
        if not is_literal(expression.get('right')):
            return None
        if not isinstance(expression['right'].get('value'), (int, float)):
            return None
        return expression['left']['name']

    @staticmethod
    def _is_split_call(node: dict | None) -> bool:
        """Check if node is a 'X'.split('|') call expression."""
        if not isinstance(node, dict):
            return False
        if node.get('type') != 'CallExpression':
            return False
        callee = node.get('callee')
        if not callee or callee.get('type') != 'MemberExpression':
            return False
        if not is_string_literal(callee.get('object')):
            return False
        property_node = callee.get('property')
        is_split_identifier = is_identifier(property_node) and property_node.get('name') == 'split'
        is_split_string = is_string_literal(property_node) and property_node.get('value') == 'split'
        if not is_split_identifier and not is_split_string:
            return False
        arguments = node.get('arguments', [])
        return len(arguments) == 1 and is_string_literal(arguments[0])

    @staticmethod
    def _extract_split_states(node: dict) -> list[str]:
        """Extract the ordered state list from a 'X'.split('|') call."""
        callee = node['callee']
        string_value = callee['object']['value']
        separator = node['arguments'][0]['value']
        return string_value.split(separator)

    def _try_recover_from_loop(
        self,
        loop: dict,
        states: list[str],
        state_variable: str,
        counter_variable: str | None,
    ) -> list[dict] | None:
        """Try to recover the linear statement sequence from a dispatcher loop."""
        if not isinstance(loop, dict):
            return None

        initial_value = 0
        switch_body: dict | None = None

        match loop.get('type', ''):
            case 'ForStatement':
                initial_value = self._extract_for_init_value(loop.get('init'))
                switch_body = self._extract_switch_from_loop_body(loop.get('body'))
            case 'WhileStatement':
                if self._is_truthy(loop.get('test')):
                    switch_body = self._extract_switch_from_loop_body(loop.get('body'))

        if switch_body is None:
            return None

        case_map = self._build_case_map(switch_body.get('cases', []))
        return self._reconstruct_statements(case_map, states, initial_value)

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
    def _build_case_map(cases: list[dict]) -> dict[str, tuple[list[dict], list[dict]]]:
        """Build a map from case test value to (filtered statements, original statements)."""
        case_map: dict[str, tuple[list[dict], list[dict]]] = {}
        for case in cases:
            test = case.get('test')
            if not test or test.get('type') != 'Literal':
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
            case_map[key] = (statements, case.get('consequent', []))
        return case_map

    @staticmethod
    def _reconstruct_statements(
        case_map: dict[str, tuple[list[dict], list[dict]]],
        states: list[str],
        initial_value: int,
    ) -> list[dict] | None:
        """Reconstruct the linear statement sequence from a case map and state order."""
        recovered: list[dict] = []
        for index in range(initial_value, len(states)):
            state = states[index]
            if state not in case_map:
                break
            statements, original = case_map[state]
            recovered.extend(statements)
            if original and original[-1].get('type') == 'ReturnStatement':
                recovered.append(original[-1])
                break
        return recovered or None

    @staticmethod
    def _extract_switch_from_loop_body(body: dict | None) -> dict | None:
        """Extract SwitchStatement from a loop body block."""
        if not isinstance(body, dict):
            return None
        if body.get('type') == 'SwitchStatement':
            return body
        if body.get('type') != 'BlockStatement':
            return None
        for statement in body.get('body', []):
            if statement.get('type') == 'SwitchStatement':
                return statement
        return None

    @staticmethod
    def _is_truthy(node: dict | None) -> bool:
        """Check if a test expression is always truthy (e.g., true, !0, !![])."""
        if not isinstance(node, dict):
            return False
        node_type = node.get('type')
        if node_type == 'Literal':
            return bool(node.get('value'))
        if node_type != 'UnaryExpression' or node.get('operator') != '!':
            return False
        argument = node.get('argument')
        if not argument:
            return False
        # !0 => true
        if argument.get('type') == 'Literal' and argument.get('value') == 0:
            return True
        # !![] => true
        if (
            argument.get('type') == 'UnaryExpression'
            and argument.get('operator') == '!'
            and argument.get('argument', {}).get('type') == 'ArrayExpression'
        ):
            return True
        return False
