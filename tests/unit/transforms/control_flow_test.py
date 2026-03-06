"""Unit tests for ControlFlowRecoverer transform."""

import pytest

from pyjsclear.transforms.control_flow import ControlFlowRecoverer
from tests.unit.conftest import normalize, roundtrip


def rt(js_code):
    """Shorthand roundtrip for ControlFlowRecoverer."""
    code, changed = roundtrip(js_code, ControlFlowRecoverer)
    return normalize(code), changed


# ---------------------------------------------------------------------------
# Helper: build AST nodes manually
# ---------------------------------------------------------------------------

def _literal(value):
    return {"type": "Literal", "value": value, "raw": repr(value)}


def _identifier(name):
    return {"type": "Identifier", "name": name}


def _call_expr(callee, arguments):
    return {"type": "CallExpression", "callee": callee, "arguments": arguments}


def _member_expr(obj, prop, computed=False):
    return {"type": "MemberExpression", "object": obj, "property": prop, "computed": computed}


def _expr_stmt(expression):
    return {"type": "ExpressionStatement", "expression": expression}


def _split_call(string_val, separator="|"):
    """Build a "string".split("|") CallExpression node."""
    return _call_expr(
        callee=_member_expr(_literal(string_val), _identifier("split")),
        arguments=[_literal(separator)],
    )


def _assignment(left_name, right):
    return {
        "type": "AssignmentExpression",
        "operator": "=",
        "left": _identifier(left_name),
        "right": right,
    }


def _var_declaration(declarations):
    return {"type": "VariableDeclaration", "declarations": declarations, "kind": "var"}


def _var_declarator(name, init=None):
    return {"type": "VariableDeclarator", "id": _identifier(name), "init": init}


def _switch_case(test_value, consequent):
    return {"type": "SwitchCase", "test": _literal(test_value), "consequent": consequent}


def _switch_stmt(discriminant, cases):
    return {"type": "SwitchStatement", "discriminant": discriminant, "cases": cases}


def _while_true(body_stmts):
    return {
        "type": "WhileStatement",
        "test": _literal(True),
        "body": {"type": "BlockStatement", "body": body_stmts},
    }


def _continue_stmt():
    return {"type": "ContinueStatement", "label": None}


def _break_stmt():
    return {"type": "BreakStatement", "label": None}


def _return_stmt(argument=None):
    return {"type": "ReturnStatement", "argument": argument}


def _program(body):
    return {"type": "Program", "body": body, "sourceType": "script"}


def _make_cff_ast_var_pattern(state_string, state_var, counter_var, cases_map):
    """Build a full CFF AST with VariableDeclaration pattern.

    cases_map: dict mapping case test value (str) -> list of statement nodes
    """
    switch_cases = []
    for key, stmts in cases_map.items():
        switch_cases.append(_switch_case(key, stmts + [_continue_stmt()]))

    discriminant = _member_expr(
        _identifier(state_var),
        {
            "type": "UpdateExpression",
            "operator": "++",
            "argument": _identifier(counter_var),
            "prefix": False,
        },
        computed=True,
    )

    loop = _while_true([_switch_stmt(discriminant, switch_cases), _break_stmt()])

    decl = _var_declaration([
        _var_declarator(state_var, _split_call(state_string)),
        _var_declarator(counter_var, _literal(0)),
    ])

    return _program([decl, loop])


def _make_cff_ast_expr_pattern(state_string, state_var, counter_var, cases_map):
    """Build a full CFF AST with ExpressionStatement pattern."""
    switch_cases = []
    for key, stmts in cases_map.items():
        switch_cases.append(_switch_case(key, stmts + [_continue_stmt()]))

    discriminant = _member_expr(
        _identifier(state_var),
        {
            "type": "UpdateExpression",
            "operator": "++",
            "argument": _identifier(counter_var),
            "prefix": False,
        },
        computed=True,
    )

    loop = _while_true([_switch_stmt(discriminant, switch_cases), _break_stmt()])

    assign_stmt = _expr_stmt(_assignment(state_var, _split_call(state_string)))
    counter_stmt = _expr_stmt(_assignment(counter_var, _literal(0)))

    return _program([assign_stmt, counter_stmt, loop])


# ---------------------------------------------------------------------------
# Tests: _is_split_call
# ---------------------------------------------------------------------------

class TestIsSplitCall:
    """Test the _is_split_call detection method."""

    def setup_method(self):
        self.t = ControlFlowRecoverer(_program([]))

    def test_valid_split_call(self):
        node = _split_call("1|0|3|2")
        assert self.t._is_split_call(node) is True

    def test_non_dict_returns_false(self):
        assert self.t._is_split_call(None) is False
        assert self.t._is_split_call("string") is False

    def test_non_call_expression(self):
        assert self.t._is_split_call({"type": "Identifier", "name": "x"}) is False

    def test_callee_not_member_expression(self):
        node = _call_expr(_identifier("split"), [_literal("|")])
        assert self.t._is_split_call(node) is False

    def test_object_not_string_literal(self):
        node = _call_expr(
            callee=_member_expr(_identifier("arr"), _identifier("split")),
            arguments=[_literal("|")],
        )
        assert self.t._is_split_call(node) is False

    def test_property_not_split(self):
        node = _call_expr(
            callee=_member_expr(_literal("1|2"), _identifier("join")),
            arguments=[_literal("|")],
        )
        assert self.t._is_split_call(node) is False

    def test_no_arguments(self):
        node = _call_expr(
            callee=_member_expr(_literal("1|2"), _identifier("split")),
            arguments=[],
        )
        assert self.t._is_split_call(node) is False

    def test_argument_not_string(self):
        node = _call_expr(
            callee=_member_expr(_literal("1|2"), _identifier("split")),
            arguments=[_literal(1)],
        )
        assert self.t._is_split_call(node) is False


# ---------------------------------------------------------------------------
# Tests: _extract_split_states
# ---------------------------------------------------------------------------

class TestExtractSplitStates:
    """Test the _extract_split_states method."""

    def setup_method(self):
        self.t = ControlFlowRecoverer(_program([]))

    def test_basic_extraction(self):
        node = _split_call("1|0|3|2")
        assert self.t._extract_split_states(node) == ["1", "0", "3", "2"]

    def test_single_state(self):
        node = _split_call("0")
        assert self.t._extract_split_states(node) == ["0"]

    def test_five_states(self):
        node = _split_call("4|2|0|1|3")
        assert self.t._extract_split_states(node) == ["4", "2", "0", "1", "3"]

    def test_custom_separator(self):
        node = _split_call("a-b-c", separator="-")
        assert self.t._extract_split_states(node) == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# Tests: basic CFF recovery (variable declaration pattern)
# ---------------------------------------------------------------------------

class TestBasicCFFRecovery:
    """Test full CFF recovery using manually built ASTs."""

    def test_two_states_reordered(self):
        """var _a = "1|0".split("|"), _i = 0; while(true) { switch(...) { case "0": b(); case "1": a(); } break; }"""
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("b"), []))],
            "1": [_expr_stmt(_call_expr(_identifier("a"), []))],
        }
        ast = _make_cff_ast_var_pattern("1|0", "_a", "_i", cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast["body"]
        # State order is "1", "0" => a(), then b()
        assert len(body) == 2
        assert body[0]["type"] == "ExpressionStatement"
        assert body[0]["expression"]["callee"]["name"] == "a"
        assert body[1]["type"] == "ExpressionStatement"
        assert body[1]["expression"]["callee"]["name"] == "b"

    def test_three_states(self):
        """Three states: "2|0|1" => c(), a(), b()"""
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("a"), []))],
            "1": [_expr_stmt(_call_expr(_identifier("b"), []))],
            "2": [_expr_stmt(_call_expr(_identifier("c"), []))],
        }
        ast = _make_cff_ast_var_pattern("2|0|1", "_a", "_i", cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast["body"]
        assert len(body) == 3
        assert body[0]["expression"]["callee"]["name"] == "c"
        assert body[1]["expression"]["callee"]["name"] == "a"
        assert body[2]["expression"]["callee"]["name"] == "b"

    def test_sequential_order(self):
        """States "0|1|2" => a(), b(), c() (no reorder needed)."""
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("a"), []))],
            "1": [_expr_stmt(_call_expr(_identifier("b"), []))],
            "2": [_expr_stmt(_call_expr(_identifier("c"), []))],
        }
        ast = _make_cff_ast_var_pattern("0|1|2", "_a", "_i", cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast["body"]
        assert len(body) == 3
        assert body[0]["expression"]["callee"]["name"] == "a"
        assert body[1]["expression"]["callee"]["name"] == "b"
        assert body[2]["expression"]["callee"]["name"] == "c"

    def test_continue_statements_filtered(self):
        """ContinueStatement nodes should not appear in recovered output."""
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("a"), []))],
        }
        ast = _make_cff_ast_var_pattern("0", "_a", "_i", cases)
        t = ControlFlowRecoverer(ast)
        t.execute()

        body = ast["body"]
        for stmt in body:
            assert stmt["type"] != "ContinueStatement"

    def test_return_statement_preserved(self):
        """Return statements should be preserved in the recovered output."""
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("a"), []))],
            "1": [_return_stmt(_literal(42))],
        }
        ast = _make_cff_ast_var_pattern("0|1", "_a", "_i", cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast["body"]
        assert len(body) == 2
        assert body[0]["expression"]["callee"]["name"] == "a"
        assert body[1]["type"] == "ReturnStatement"
        assert body[1]["argument"]["value"] == 42


# ---------------------------------------------------------------------------
# Tests: expression statement pattern
# ---------------------------------------------------------------------------

class TestExpressionPattern:
    """Test CFF recovery with ExpressionStatement pattern."""

    def test_expression_pattern_two_states(self):
        """_a = "1|0".split("|"); _i = 0; while(true) { ... }"""
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("b"), []))],
            "1": [_expr_stmt(_call_expr(_identifier("a"), []))],
        }
        ast = _make_cff_ast_expr_pattern("1|0", "_a", "_i", cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast["body"]
        assert len(body) == 2
        assert body[0]["expression"]["callee"]["name"] == "a"
        assert body[1]["expression"]["callee"]["name"] == "b"

    def test_expression_pattern_three_states(self):
        cases = {
            "0": [_expr_stmt(_call_expr(_identifier("x"), []))],
            "1": [_expr_stmt(_call_expr(_identifier("y"), []))],
            "2": [_expr_stmt(_call_expr(_identifier("z"), []))],
        }
        ast = _make_cff_ast_expr_pattern("2|1|0", "_arr", "_idx", cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast["body"]
        assert len(body) == 3
        assert body[0]["expression"]["callee"]["name"] == "z"
        assert body[1]["expression"]["callee"]["name"] == "y"
        assert body[2]["expression"]["callee"]["name"] == "x"


# ---------------------------------------------------------------------------
# Tests: no CFF pattern present
# ---------------------------------------------------------------------------

class TestNoCFFPattern:
    """Test that non-CFF code is left unchanged."""

    def test_plain_statements_unchanged(self):
        ast = _program([
            _expr_stmt(_call_expr(_identifier("foo"), [])),
            _expr_stmt(_call_expr(_identifier("bar"), [])),
        ])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is False
        assert len(ast["body"]) == 2

    def test_while_without_switch_unchanged(self):
        loop = _while_true([_expr_stmt(_call_expr(_identifier("doStuff"), []))])
        ast = _program([loop])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is False

    def test_var_decl_without_split_unchanged(self):
        decl = _var_declaration([_var_declarator("x", _literal(10))])
        ast = _program([decl])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is False


# ---------------------------------------------------------------------------
# Tests: roundtrip (parse -> transform -> generate)
# ---------------------------------------------------------------------------

class TestRoundtrip:
    """Test CFF recovery through the full parse/generate pipeline."""

    def test_basic_cff_roundtrip(self):
        js = (
            'var _a = "1|0".split("|"), _i = 0;'
            " while (true) {"
            ' switch (_a[_i++]) { case "0": b(); continue; case "1": a(); continue; }'
            " break; }"
        )
        code, changed = rt(js)
        assert changed is True
        assert "a();" in code
        assert "b();" in code
        # a (case "1") should come before b (case "0") because order is "1|0"
        assert code.index("a()") < code.index("b()")

    def test_three_state_roundtrip(self):
        js = (
            'var _s = "2|0|1".split("|"), _c = 0;'
            " while (true) {"
            ' switch (_s[_c++]) { case "0": first(); continue; case "1": second(); continue; case "2": third(); continue; }'
            " break; }"
        )
        code, changed = rt(js)
        assert changed is True
        # Order: "2|0|1" => third, first, second
        assert code.index("third()") < code.index("first()")
        assert code.index("first()") < code.index("second()")


# ---------------------------------------------------------------------------
# Tests: _build_case_map
# ---------------------------------------------------------------------------

class TestBuildCaseMap:
    """Test the static _build_case_map method."""

    def test_basic_map(self):
        stmt_a = _expr_stmt(_call_expr(_identifier("a"), []))
        stmt_b = _expr_stmt(_call_expr(_identifier("b"), []))
        cases = [
            _switch_case("0", [stmt_a, _continue_stmt()]),
            _switch_case("1", [stmt_b, _continue_stmt()]),
        ]
        result = ControlFlowRecoverer._build_case_map(cases)
        assert "0" in result
        assert "1" in result
        # Filtered statements should not include ContinueStatement
        filtered_0, _ = result["0"]
        assert len(filtered_0) == 1
        assert filtered_0[0]["expression"]["callee"]["name"] == "a"

    def test_skips_default_case(self):
        """Default case (test=None) should be skipped."""
        default_case = {"type": "SwitchCase", "test": None, "consequent": [_break_stmt()]}
        cases = [
            _switch_case("0", [_expr_stmt(_call_expr(_identifier("a"), [])), _continue_stmt()]),
            default_case,
        ]
        result = ControlFlowRecoverer._build_case_map(cases)
        assert len(result) == 1
        assert "0" in result

    def test_numeric_float_key_normalized(self):
        """Float values like 1.0 should be normalized to '1'."""
        cases = [_switch_case(1.0, [_expr_stmt(_call_expr(_identifier("a"), [])), _continue_stmt()])]
        result = ControlFlowRecoverer._build_case_map(cases)
        assert "1" in result


# ---------------------------------------------------------------------------
# Tests: _is_truthy
# ---------------------------------------------------------------------------

class TestIsTruthy:
    """Test the _is_truthy helper method."""

    def setup_method(self):
        self.t = ControlFlowRecoverer(_program([]))

    def test_literal_true(self):
        assert self.t._is_truthy(_literal(True)) is True

    def test_literal_1(self):
        assert self.t._is_truthy(_literal(1)) is True

    def test_literal_false(self):
        assert self.t._is_truthy(_literal(False)) is False

    def test_literal_0(self):
        assert self.t._is_truthy(_literal(0)) is False

    def test_not_zero_is_truthy(self):
        """!0 should be recognized as truthy."""
        node = {"type": "UnaryExpression", "operator": "!", "argument": _literal(0), "prefix": True}
        assert self.t._is_truthy(node) is True

    def test_not_dict(self):
        assert self.t._is_truthy(None) is False
        assert self.t._is_truthy("string") is False

    def test_double_not_array_is_truthy(self):
        """!![] should be truthy."""
        inner = {"type": "ArrayExpression", "elements": []}
        not_inner = {"type": "UnaryExpression", "operator": "!", "argument": inner, "prefix": True}
        double_not = {"type": "UnaryExpression", "operator": "!", "argument": not_inner, "prefix": True}
        assert self.t._is_truthy(double_not) is True
