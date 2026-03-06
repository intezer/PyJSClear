"""Control flow flattening recovery.

Detects patterns like:
  var _array = "1|0|3|2|4".split("|"), _index = 0;
  while(true) { switch(_array[_index++]) { case "0": ...; continue; ... } break; }

And reconstructs the linear statement sequence.
"""

from ..traverser import REMOVE, traverse
from ..utils.ast_helpers import is_identifier, is_literal, is_string_literal
from .base import Transform


class ControlFlowRecoverer(Transform):
    """Recover control flow from flattened switch/loop dispatchers."""

    rebuild_scope = True

    def execute(self):
        self._recover_in_bodies(self.ast)
        return self.has_changed()

    def _recover_in_bodies(self, root):
        """Walk through the AST looking for bodies containing CFF patterns."""
        from ..utils.ast_helpers import get_child_keys

        stack = [root]
        visited = set()
        while stack:
            node = stack.pop()
            if not isinstance(node, dict) or "type" not in node:
                continue

            node_id = id(node)
            if node_id in visited:
                continue
            visited.add(node_id)

            ntype = node.get("type", "")

            # Check in body arrays
            if ntype in ("Program", "BlockStatement"):
                self._try_recover_body(node, "body", node.get("body", []))

            # Queue children for processing
            for key in get_child_keys(node):
                child = node.get(key)
                if child is None:
                    continue
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, dict) and "type" in item:
                            stack.append(item)
                elif isinstance(child, dict) and "type" in child:
                    stack.append(child)

    def _try_recover_body(self, parent_node, body_key, body):
        """Try to find and recover CFF patterns in a body array."""
        i = 0
        while i < len(body):
            stmt = body[i]
            if not isinstance(stmt, dict):
                i += 1
                continue

            # Pattern 1: VariableDeclaration containing split + for/while loop
            if stmt.get("type") == "VariableDeclaration":
                state_info = self._find_state_array_in_decl(stmt)
                if state_info:
                    states, state_var, counter_var = state_info
                    # Look for the loop in the same declaration or next statement
                    next_idx = i + 1
                    if next_idx < len(body):
                        loop = body[next_idx]
                        recovered = self._try_recover_from_loop(
                            loop, states, state_var, counter_var
                        )
                        if recovered is not None:
                            # Replace both statements with recovered statements
                            body[i : next_idx + 1] = recovered
                            self.set_changed()
                            continue

            # Pattern 2: ExpressionStatement with split assignment
            if stmt.get("type") == "ExpressionStatement":
                expr = stmt.get("expression")
                if expr and expr.get("type") == "AssignmentExpression":
                    state_info = self._find_state_from_assignment(expr)
                    if state_info:
                        states, state_var = state_info
                        # Look for counter init + loop
                        next_idx = i + 1
                        counter_var = None
                        if next_idx < len(body):
                            nxt = body[next_idx]
                            cvar = self._find_counter_init(nxt)
                            if cvar is not None:
                                counter_var = cvar
                                next_idx += 1

                        if next_idx < len(body):
                            loop = body[next_idx]
                            recovered = self._try_recover_from_loop(
                                loop, states, state_var, counter_var or "_index"
                            )
                            if recovered is not None:
                                body[i : next_idx + 1] = recovered
                                self.set_changed()
                                continue

            i += 1

    def _find_state_array_in_decl(self, decl):
        """Find "X".split("|") pattern in a VariableDeclaration."""
        for d in decl.get("declarations", []):
            init = d.get("init")
            if not init:
                continue
            if self._is_split_call(init):
                states = self._extract_split_states(init)
                state_var = (
                    d["id"]["name"]
                    if d.get("id", {}).get("type") == "Identifier"
                    else None
                )
                if states and state_var:
                    # Look for counter variable in the same declaration
                    counter_var = None
                    for d2 in decl.get("declarations", []):
                        if d2 is d:
                            continue
                        if d2.get("id", {}).get("type") == "Identifier":
                            init2 = d2.get("init")
                            if (
                                init2
                                and init2.get("type") == "Literal"
                                and isinstance(init2.get("value"), (int, float))
                            ):
                                counter_var = d2["id"]["name"]
                    return states, state_var, counter_var
        return None

    def _find_state_from_assignment(self, expr):
        """Find state array from assignment expression."""
        if expr.get("type") != "AssignmentExpression":
            return None
        if not is_identifier(expr.get("left")):
            return None
        right = expr.get("right")
        if self._is_split_call(right):
            states = self._extract_split_states(right)
            if states:
                return states, expr["left"]["name"]
        return None

    def _find_counter_init(self, stmt):
        """Find counter variable initialization."""
        if not isinstance(stmt, dict):
            return None
        if stmt.get("type") == "VariableDeclaration":
            for d in stmt.get("declarations", []):
                if d.get("id", {}).get("type") == "Identifier":
                    init = d.get("init")
                    if (
                        init
                        and init.get("type") == "Literal"
                        and isinstance(init.get("value"), (int, float))
                    ):
                        return d["id"]["name"]
        if stmt.get("type") == "ExpressionStatement":
            expr = stmt.get("expression")
            if (
                expr
                and expr.get("type") == "AssignmentExpression"
                and is_identifier(expr.get("left"))
                and is_literal(expr.get("right"))
                and isinstance(expr["right"].get("value"), (int, float))
            ):
                return expr["left"]["name"]
        return None

    def _is_split_call(self, node):
        """Check if node is "X".split("|")."""
        if not isinstance(node, dict):
            return False
        if node.get("type") != "CallExpression":
            return False
        callee = node.get("callee")
        if not callee or callee.get("type") != "MemberExpression":
            return False
        obj = callee.get("object")
        prop = callee.get("property")
        if not is_string_literal(obj):
            return False
        if not (is_identifier(prop) and prop.get("name") == "split") and not (
            is_string_literal(prop) and prop.get("value") == "split"
        ):
            return False
        args = node.get("arguments", [])
        if len(args) != 1 or not is_string_literal(args[0]):
            return False
        return True

    def _extract_split_states(self, node):
        """Extract states from "1|0|3|2|4".split("|")."""
        callee = node["callee"]
        string = callee["object"]["value"]
        separator = node["arguments"][0]["value"]
        return string.split(separator)

    def _try_recover_from_loop(self, loop, states, state_var, counter_var):
        """Try to recover statements from a for/while loop with switch dispatcher."""
        if not isinstance(loop, dict):
            return None

        ltype = loop.get("type", "")
        switch_body = None
        initial_value = 0

        if ltype == "ForStatement":
            # for(var _i = 0; ...) { switch(_array[_i++]) { ... } break; }
            init = loop.get("init")
            if init:
                if init.get("type") == "VariableDeclaration":
                    for d in init.get("declarations", []):
                        if d.get("init") and d["init"].get("type") == "Literal":
                            initial_value = int(d["init"].get("value", 0))
                elif init.get("type") == "AssignmentExpression" and is_literal(
                    init.get("right")
                ):
                    initial_value = int(init["right"].get("value", 0))
            switch_body = self._extract_switch_from_loop_body(loop.get("body"))

        elif ltype == "WhileStatement":
            test = loop.get("test")
            if self._is_truthy(test):
                switch_body = self._extract_switch_from_loop_body(loop.get("body"))

        if switch_body is None:
            return None

        cases = switch_body.get("cases", [])
        # Build map from case test value to consequent statements
        cases_map = {}
        for case in cases:
            test = case.get("test")
            if test and test.get("type") == "Literal":
                val = test["value"]
                # Normalize key: float 1.0 -> "1", string "1" -> "1"
                if isinstance(val, float) and val == int(val):
                    key = str(int(val))
                else:
                    key = str(val)
                # Filter out continue and break statements
                stmts = [
                    s
                    for s in case.get("consequent", [])
                    if s.get("type") not in ("ContinueStatement", "BreakStatement")
                ]
                cases_map[key] = (stmts, case.get("consequent", []))

        # Reconstruct statement sequence
        recovered = []
        for idx in range(initial_value, len(states)):
            state = states[idx]
            if state not in cases_map:
                break
            stmts, original = cases_map[state]
            recovered.extend(stmts)
            # Stop if there's a return statement
            if original and original[-1].get("type") == "ReturnStatement":
                recovered.append(original[-1])
                break

        if not recovered:
            return None
        return recovered

    def _extract_switch_from_loop_body(self, body):
        """Extract SwitchStatement from loop body."""
        if not isinstance(body, dict):
            return None
        if body.get("type") == "BlockStatement":
            stmts = body.get("body", [])
            for stmt in stmts:
                if stmt.get("type") == "SwitchStatement":
                    return stmt
        elif body.get("type") == "SwitchStatement":
            return body
        return None

    def _is_truthy(self, node):
        """Check if a test expression is always truthy."""
        if not isinstance(node, dict):
            return False
        if node.get("type") == "Literal":
            return bool(node.get("value"))
        # !0 = true, !![] = true
        if node.get("type") == "UnaryExpression" and node.get("operator") == "!":
            arg = node.get("argument")
            if arg and arg.get("type") == "Literal" and arg.get("value") == 0:
                return True
            if arg and arg.get("type") == "ArrayExpression":
                return False  # ![] = false, but !![] = true
            if (
                arg
                and arg.get("type") == "UnaryExpression"
                and arg.get("operator") == "!"
            ):
                # !!something
                inner = arg.get("argument")
                if inner and inner.get("type") == "ArrayExpression":
                    return True
        return False
