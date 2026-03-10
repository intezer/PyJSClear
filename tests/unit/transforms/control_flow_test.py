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
    return {'type': 'Literal', 'value': value, 'raw': repr(value)}


def _identifier(name):
    return {'type': 'Identifier', 'name': name}


def _call_expr(callee, arguments):
    return {'type': 'CallExpression', 'callee': callee, 'arguments': arguments}


def _member_expr(obj, prop, computed=False):
    return {'type': 'MemberExpression', 'object': obj, 'property': prop, 'computed': computed}


def _expr_stmt(expression):
    return {'type': 'ExpressionStatement', 'expression': expression}


def _split_call(string_val, separator='|'):
    """Build a "string".split("|") CallExpression node."""
    return _call_expr(
        callee=_member_expr(_literal(string_val), _identifier('split')),
        arguments=[_literal(separator)],
    )


def _assignment(left_name, right):
    return {
        'type': 'AssignmentExpression',
        'operator': '=',
        'left': _identifier(left_name),
        'right': right,
    }


def _var_declaration(declarations):
    return {'type': 'VariableDeclaration', 'declarations': declarations, 'kind': 'var'}


def _var_declarator(name, init=None):
    return {'type': 'VariableDeclarator', 'id': _identifier(name), 'init': init}


def _switch_case(test_value, consequent):
    return {'type': 'SwitchCase', 'test': _literal(test_value), 'consequent': consequent}


def _switch_stmt(discriminant, cases):
    return {'type': 'SwitchStatement', 'discriminant': discriminant, 'cases': cases}


def _while_true(body_stmts):
    return {
        'type': 'WhileStatement',
        'test': _literal(True),
        'body': {'type': 'BlockStatement', 'body': body_stmts},
    }


def _continue_stmt():
    return {'type': 'ContinueStatement', 'label': None}


def _break_stmt():
    return {'type': 'BreakStatement', 'label': None}


def _return_stmt(argument=None):
    return {'type': 'ReturnStatement', 'argument': argument}


def _program(body):
    return {'type': 'Program', 'body': body, 'sourceType': 'script'}


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
            'type': 'UpdateExpression',
            'operator': '++',
            'argument': _identifier(counter_var),
            'prefix': False,
        },
        computed=True,
    )

    loop = _while_true([_switch_stmt(discriminant, switch_cases), _break_stmt()])

    decl = _var_declaration(
        [
            _var_declarator(state_var, _split_call(state_string)),
            _var_declarator(counter_var, _literal(0)),
        ]
    )

    return _program([decl, loop])


def _make_cff_ast_expr_pattern(state_string, state_var, counter_var, cases_map):
    """Build a full CFF AST with ExpressionStatement pattern."""
    switch_cases = []
    for key, stmts in cases_map.items():
        switch_cases.append(_switch_case(key, stmts + [_continue_stmt()]))

    discriminant = _member_expr(
        _identifier(state_var),
        {
            'type': 'UpdateExpression',
            'operator': '++',
            'argument': _identifier(counter_var),
            'prefix': False,
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
        node = _split_call('1|0|3|2')
        assert self.t._is_split_call(node) is True

    def test_non_dict_returns_false(self):
        assert self.t._is_split_call(None) is False
        assert self.t._is_split_call('string') is False

    def test_non_call_expression(self):
        assert self.t._is_split_call({'type': 'Identifier', 'name': 'x'}) is False

    def test_callee_not_member_expression(self):
        node = _call_expr(_identifier('split'), [_literal('|')])
        assert self.t._is_split_call(node) is False

    def test_object_not_string_literal(self):
        node = _call_expr(
            callee=_member_expr(_identifier('arr'), _identifier('split')),
            arguments=[_literal('|')],
        )
        assert self.t._is_split_call(node) is False

    def test_property_not_split(self):
        node = _call_expr(
            callee=_member_expr(_literal('1|2'), _identifier('join')),
            arguments=[_literal('|')],
        )
        assert self.t._is_split_call(node) is False

    def test_no_arguments(self):
        node = _call_expr(
            callee=_member_expr(_literal('1|2'), _identifier('split')),
            arguments=[],
        )
        assert self.t._is_split_call(node) is False

    def test_argument_not_string(self):
        node = _call_expr(
            callee=_member_expr(_literal('1|2'), _identifier('split')),
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
        node = _split_call('1|0|3|2')
        assert self.t._extract_split_states(node) == ['1', '0', '3', '2']

    def test_single_state(self):
        node = _split_call('0')
        assert self.t._extract_split_states(node) == ['0']

    def test_five_states(self):
        node = _split_call('4|2|0|1|3')
        assert self.t._extract_split_states(node) == ['4', '2', '0', '1', '3']

    def test_custom_separator(self):
        node = _split_call('a-b-c', separator='-')
        assert self.t._extract_split_states(node) == ['a', 'b', 'c']


# ---------------------------------------------------------------------------
# Tests: basic CFF recovery (variable declaration pattern)
# ---------------------------------------------------------------------------


class TestBasicCFFRecovery:
    """Test full CFF recovery using manually built ASTs."""

    def test_two_states_reordered(self):
        """var _a = "1|0".split("|"), _i = 0; while(true) { switch(...) { case "0": b(); case "1": a(); } break; }"""
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('b'), []))],
            '1': [_expr_stmt(_call_expr(_identifier('a'), []))],
        }
        ast = _make_cff_ast_var_pattern('1|0', '_a', '_i', cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast['body']
        # State order is "1", "0" => a(), then b()
        assert len(body) == 2
        assert body[0]['type'] == 'ExpressionStatement'
        assert body[0]['expression']['callee']['name'] == 'a'
        assert body[1]['type'] == 'ExpressionStatement'
        assert body[1]['expression']['callee']['name'] == 'b'

    def test_three_states(self):
        """Three states: "2|0|1" => c(), a(), b()"""
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('a'), []))],
            '1': [_expr_stmt(_call_expr(_identifier('b'), []))],
            '2': [_expr_stmt(_call_expr(_identifier('c'), []))],
        }
        ast = _make_cff_ast_var_pattern('2|0|1', '_a', '_i', cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast['body']
        assert len(body) == 3
        assert body[0]['expression']['callee']['name'] == 'c'
        assert body[1]['expression']['callee']['name'] == 'a'
        assert body[2]['expression']['callee']['name'] == 'b'

    def test_sequential_order(self):
        """States "0|1|2" => a(), b(), c() (no reorder needed)."""
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('a'), []))],
            '1': [_expr_stmt(_call_expr(_identifier('b'), []))],
            '2': [_expr_stmt(_call_expr(_identifier('c'), []))],
        }
        ast = _make_cff_ast_var_pattern('0|1|2', '_a', '_i', cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast['body']
        assert len(body) == 3
        assert body[0]['expression']['callee']['name'] == 'a'
        assert body[1]['expression']['callee']['name'] == 'b'
        assert body[2]['expression']['callee']['name'] == 'c'

    def test_continue_statements_filtered(self):
        """ContinueStatement nodes should not appear in recovered output."""
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('a'), []))],
        }
        ast = _make_cff_ast_var_pattern('0', '_a', '_i', cases)
        t = ControlFlowRecoverer(ast)
        t.execute()

        body = ast['body']
        for stmt in body:
            assert stmt['type'] != 'ContinueStatement'

    def test_return_statement_preserved(self):
        """Return statements should be preserved in the recovered output."""
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('a'), []))],
            '1': [_return_stmt(_literal(42))],
        }
        ast = _make_cff_ast_var_pattern('0|1', '_a', '_i', cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast['body']
        assert len(body) == 2
        assert body[0]['expression']['callee']['name'] == 'a'
        assert body[1]['type'] == 'ReturnStatement'
        assert body[1]['argument']['value'] == 42


# ---------------------------------------------------------------------------
# Tests: expression statement pattern
# ---------------------------------------------------------------------------


class TestExpressionPattern:
    """Test CFF recovery with ExpressionStatement pattern."""

    def test_expression_pattern_two_states(self):
        """_a = "1|0".split("|"); _i = 0; while(true) { ... }"""
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('b'), []))],
            '1': [_expr_stmt(_call_expr(_identifier('a'), []))],
        }
        ast = _make_cff_ast_expr_pattern('1|0', '_a', '_i', cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast['body']
        assert len(body) == 2
        assert body[0]['expression']['callee']['name'] == 'a'
        assert body[1]['expression']['callee']['name'] == 'b'

    def test_expression_pattern_three_states(self):
        cases = {
            '0': [_expr_stmt(_call_expr(_identifier('x'), []))],
            '1': [_expr_stmt(_call_expr(_identifier('y'), []))],
            '2': [_expr_stmt(_call_expr(_identifier('z'), []))],
        }
        ast = _make_cff_ast_expr_pattern('2|1|0', '_arr', '_idx', cases)
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is True
        body = ast['body']
        assert len(body) == 3
        assert body[0]['expression']['callee']['name'] == 'z'
        assert body[1]['expression']['callee']['name'] == 'y'
        assert body[2]['expression']['callee']['name'] == 'x'


# ---------------------------------------------------------------------------
# Tests: no CFF pattern present
# ---------------------------------------------------------------------------


class TestNoCFFPattern:
    """Test that non-CFF code is left unchanged."""

    def test_plain_statements_unchanged(self):
        ast = _program(
            [
                _expr_stmt(_call_expr(_identifier('foo'), [])),
                _expr_stmt(_call_expr(_identifier('bar'), [])),
            ]
        )
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is False
        assert len(ast['body']) == 2

    def test_while_without_switch_unchanged(self):
        loop = _while_true([_expr_stmt(_call_expr(_identifier('doStuff'), []))])
        ast = _program([loop])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()

        assert changed is False

    def test_var_decl_without_split_unchanged(self):
        decl = _var_declaration([_var_declarator('x', _literal(10))])
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
            ' while (true) {'
            ' switch (_a[_i++]) { case "0": b(); continue; case "1": a(); continue; }'
            ' break; }'
        )
        code, changed = rt(js)
        assert changed is True
        assert 'a();' in code
        assert 'b();' in code
        # a (case "1") should come before b (case "0") because order is "1|0"
        assert code.index('a()') < code.index('b()')

    def test_three_state_roundtrip(self):
        js = (
            'var _s = "2|0|1".split("|"), _c = 0;'
            ' while (true) {'
            ' switch (_s[_c++]) { case "0": first(); continue; case "1": second(); continue; case "2": third(); continue; }'
            ' break; }'
        )
        code, changed = rt(js)
        assert changed is True
        # Order: "2|0|1" => third, first, second
        assert code.index('third()') < code.index('first()')
        assert code.index('first()') < code.index('second()')


# ---------------------------------------------------------------------------
# Tests: _build_case_map
# ---------------------------------------------------------------------------


class TestBuildCaseMap:
    """Test the static _build_case_map method."""

    def test_basic_map(self):
        stmt_a = _expr_stmt(_call_expr(_identifier('a'), []))
        stmt_b = _expr_stmt(_call_expr(_identifier('b'), []))
        cases = [
            _switch_case('0', [stmt_a, _continue_stmt()]),
            _switch_case('1', [stmt_b, _continue_stmt()]),
        ]
        result = ControlFlowRecoverer._build_case_map(cases)
        assert '0' in result
        assert '1' in result
        # Filtered statements should not include ContinueStatement
        filtered_0, _ = result['0']
        assert len(filtered_0) == 1
        assert filtered_0[0]['expression']['callee']['name'] == 'a'

    def test_skips_default_case(self):
        """Default case (test=None) should be skipped."""
        default_case = {'type': 'SwitchCase', 'test': None, 'consequent': [_break_stmt()]}
        cases = [
            _switch_case('0', [_expr_stmt(_call_expr(_identifier('a'), [])), _continue_stmt()]),
            default_case,
        ]
        result = ControlFlowRecoverer._build_case_map(cases)
        assert len(result) == 1
        assert '0' in result

    def test_numeric_float_key_normalized(self):
        """Float values like 1.0 should be normalized to '1'."""
        cases = [_switch_case(1.0, [_expr_stmt(_call_expr(_identifier('a'), [])), _continue_stmt()])]
        result = ControlFlowRecoverer._build_case_map(cases)
        assert '1' in result


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
        node = {'type': 'UnaryExpression', 'operator': '!', 'argument': _literal(0), 'prefix': True}
        assert self.t._is_truthy(node) is True

    def test_not_dict(self):
        assert self.t._is_truthy(None) is False
        assert self.t._is_truthy('string') is False

    def test_double_not_array_is_truthy(self):
        """!![] should be truthy."""
        inner = {'type': 'ArrayExpression', 'elements': []}
        not_inner = {'type': 'UnaryExpression', 'operator': '!', 'argument': inner, 'prefix': True}
        double_not = {'type': 'UnaryExpression', 'operator': '!', 'argument': not_inner, 'prefix': True}
        assert self.t._is_truthy(double_not) is True


# ---------------------------------------------------------------------------
# Coverage gap tests
# ---------------------------------------------------------------------------


class TestNonDictInBody:
    """Lines 69-70: Non-dict statement in body list."""

    def test_non_dict_in_body_skipped(self):
        """Non-dict items in body should be skipped without crashing."""
        ast = _program([None, 'not_a_dict', _expr_stmt(_call_expr(_identifier('a'), []))])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()
        assert changed is False


class TestExpressionPatternCounterInit:
    """Lines 106, 116, 119: expression pattern where assignment doesn't have split or counter init fails."""

    def test_expression_pattern_no_split(self):
        """Assignment that is not a split call should not match."""
        ast = _program([
            _expr_stmt(_assignment('x', _literal(42))),
            _while_true([_break_stmt()]),
        ])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()
        assert changed is False

    def test_expression_pattern_missing_loop(self):
        """Expression pattern where there is no loop after the counter init."""
        assign_stmt = _expr_stmt(_assignment('_a', _split_call('1|0')))
        counter_stmt = _expr_stmt(_assignment('_i', _literal(0)))
        # No loop after counter, just ends
        ast = _program([assign_stmt, counter_stmt])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()
        assert changed is False


class TestFindCounterInit:
    """Lines 175-183, 194: _find_counter_init with VariableDeclaration and ExpressionStatement."""

    def setup_method(self):
        self.t = ControlFlowRecoverer(_program([]))

    def test_variable_declaration_counter(self):
        stmt = _var_declaration([_var_declarator('_i', _literal(0))])
        result = self.t._find_counter_init(stmt)
        assert result == '_i'

    def test_expression_statement_counter(self):
        stmt = _expr_stmt(_assignment('_i', _literal(0)))
        result = self.t._find_counter_init(stmt)
        assert result == '_i'

    def test_non_numeric_init_ignored(self):
        stmt = _var_declaration([_var_declarator('_i', _literal('hello'))])
        result = self.t._find_counter_init(stmt)
        assert result is None

    def test_non_dict_returns_none(self):
        result = self.t._find_counter_init(None)
        assert result is None

        result = self.t._find_counter_init('not a dict')
        assert result is None


class TestForStatementPattern:
    """Lines 236-237: ForStatement with init value extraction."""

    def test_for_statement_recovery(self):
        """For loop with switch dispatcher should be recovered."""
        js = (
            'var _a = "1|0".split("|");'
            ' for (var _j = 0; ; ) {'
            ' switch (_a[_j++]) { case "0": b(); continue; case "1": a(); continue; }'
            ' break; }'
        )
        code, changed = rt(js)
        assert changed is True
        assert 'a()' in code
        assert 'b()' in code
        assert code.index('a()') < code.index('b()')


class TestExtractForInitValue:
    """Lines 253-261: _extract_for_init_value with AssignmentExpression init."""

    def test_assignment_expression_init(self):
        init = {
            'type': 'AssignmentExpression',
            'operator': '=',
            'left': _identifier('_i'),
            'right': _literal(0),
        }
        result = ControlFlowRecoverer._extract_for_init_value(init)
        assert result == 0

    def test_variable_declaration_init(self):
        init = _var_declaration([_var_declarator('_i', _literal(2))])
        result = ControlFlowRecoverer._extract_for_init_value(init)
        assert result == 2

    def test_no_init(self):
        result = ControlFlowRecoverer._extract_for_init_value(None)
        assert result == 0


class TestReconstructStatementsEdgeCases:
    """Lines 291, 295-296: _reconstruct_statements with return statement and missing state."""

    def test_missing_state_stops_reconstruction(self):
        """A missing state key should stop reconstruction."""
        cases_map = {
            '0': ([_expr_stmt(_call_expr(_identifier('a'), []))], []),
        }
        result = ControlFlowRecoverer._reconstruct_statements(cases_map, ['0', '1'], 0)
        # Should only contain statements from case '0'
        assert len(result) == 1


class TestExtractSwitchFromLoopBody:
    """Lines 302, 308-310: _extract_switch_from_loop_body edge cases."""

    def setup_method(self):
        self.t = ControlFlowRecoverer(_program([]))

    def test_non_block_statement(self):
        """Non-BlockStatement body returns None."""
        result = self.t._extract_switch_from_loop_body(_expr_stmt(_call_expr(_identifier('a'), [])))
        assert result is None

    def test_switch_directly_as_body(self):
        """SwitchStatement directly as loop body."""
        switch = _switch_stmt(_identifier('x'), [])
        result = self.t._extract_switch_from_loop_body(switch)
        assert result is not None
        assert result['type'] == 'SwitchStatement'

    def test_non_dict_body(self):
        result = self.t._extract_switch_from_loop_body(None)
        assert result is None

        result = self.t._extract_switch_from_loop_body('not a dict')
        assert result is None


class TestWhileTruthyPatterns:
    """Tests for various truthy patterns in while loop tests."""

    def test_while_not_zero(self):
        """while(!0) pattern - truthy via !0."""
        code = (
            'var _a = "1|0".split("|"), _i = 0;'
            ' while(!0) {'
            ' switch(_a[_i++]) { case "0": b(); continue; case "1": a(); continue; }'
            ' break; }'
        )
        result, changed = rt(code)
        assert changed
        assert 'a()' in result
        assert 'b()' in result

    def test_while_double_not_array(self):
        """while(!![]) pattern - truthy via !![]."""
        code = (
            'var _a = "0|1".split("|"), _i = 0;'
            ' while(!![]) {'
            ' switch(_a[_i++]) { case "0": a(); continue; case "1": b(); continue; }'
            ' break; }'
        )
        result, changed = rt(code)
        assert changed
        assert 'a()' in result
        assert 'b()' in result

    def test_case_with_return_in_roundtrip(self):
        """Case with return statement preserved in roundtrip."""
        code = (
            'function f() {'
            ' var _a = "0|1".split("|"), _i = 0;'
            ' while(true) { switch(_a[_i++]) { case "0": a(); continue; case "1": return b(); } break; }'
            ' }'
        )
        result, changed = rt(code)
        assert changed
        assert 'return' in result

    def test_is_truthy_not_array_is_false(self):
        """![] is falsy (line 324)."""
        t = ControlFlowRecoverer(_program([]))
        node = {'type': 'UnaryExpression', 'operator': '!', 'argument': {'type': 'ArrayExpression', 'elements': []}, 'prefix': True}
        assert t._is_truthy(node) is False

    def test_is_truthy_literal_non_bool(self):
        """Literal with non-bool truthy value (line 317)."""
        t = ControlFlowRecoverer(_program([]))
        assert t._is_truthy(_literal(42)) is True
        assert t._is_truthy(_literal('')) is False
        assert t._is_truthy(_literal('hello')) is True

    def test_visited_set_dedup(self):
        """Lines 36-37: visited set prevents re-processing the same node."""
        # A node that appears in multiple places (shared reference)
        shared = _expr_stmt(_call_expr(_identifier('a'), []))
        block = {'type': 'BlockStatement', 'body': [shared]}
        ast = _program([block])
        t = ControlFlowRecoverer(ast)
        changed = t.execute()
        assert changed is False


class TestForInitAssignmentExpression:
    """Lines 259-260: _extract_for_init_value with AssignmentExpression init."""

    def test_for_assignment_init_nonzero(self):
        init = {
            'type': 'AssignmentExpression',
            'operator': '=',
            'left': _identifier('_i'),
            'right': _literal(3),
        }
        result = ControlFlowRecoverer._extract_for_init_value(init)
        assert result == 3
