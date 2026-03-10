"""Unit tests for ProxyFunctionInliner transform."""

import pytest

from pyjsclear.transforms.proxy_functions import ProxyFunctionInliner
from tests.unit.conftest import normalize, roundtrip


class TestProxyFunctionInlinerBasic:
    def test_binary_proxy_inlined(self):
        code, changed = roundtrip(
            'function p(a, b) { return a + b; } p(1, 2);',
            ProxyFunctionInliner,
        )
        assert changed is True
        norm = normalize(code)
        # The call p(1, 2) is replaced with 1 + 2; function declaration remains
        assert '1 + 2;' in norm
        assert 'p(1, 2)' not in norm

    def test_call_proxy_inlined(self):
        code, changed = roundtrip(
            'function p(a, b) { return a(b); } p(foo, 1);',
            ProxyFunctionInliner,
        )
        assert changed is True
        norm = normalize(code)
        assert 'foo(1);' in norm
        assert 'p(foo, 1)' not in norm

    def test_arrow_proxy_inlined(self):
        code, changed = roundtrip(
            'var p = (a) => a * 2; p(3);',
            ProxyFunctionInliner,
        )
        assert changed is True
        norm = normalize(code)
        assert '3 * 2;' in norm
        assert 'p(3)' not in norm


class TestProxyFunctionInlinerSkips:
    def test_multi_statement_body_not_inlined(self):
        code, changed = roundtrip(
            'function p(a) { var x = 1; return a + x; } p(5);',
            ProxyFunctionInliner,
        )
        assert changed is False
        assert 'p(5)' in normalize(code)

    def test_non_constant_binding_not_inlined(self):
        code, changed = roundtrip(
            'var p = (a) => a * 2; p = something; p(3);',
            ProxyFunctionInliner,
        )
        assert changed is False
        assert 'p(3)' in normalize(code)

    def test_no_proxy_functions_returns_false(self):
        code, changed = roundtrip(
            'var x = 1 + 2;',
            ProxyFunctionInliner,
        )
        assert changed is False


class TestProxyFunctionInlinerEdgeCases:
    def test_missing_args_substitutes_undefined(self):
        code, changed = roundtrip(
            'function p(a, b) { return a + b; } p(1);',
            ProxyFunctionInliner,
        )
        assert changed is True
        norm = normalize(code)
        assert '1 + undefined' in norm

    def test_function_with_no_return_value_gives_undefined(self):
        code, changed = roundtrip(
            'function p() { return; } var x = p();',
            ProxyFunctionInliner,
        )
        assert changed is True
        assert 'undefined' in code

    def test_nested_calls_processed_innermost_first(self):
        code, changed = roundtrip(
            'function p(a, b) { return a + b; } p(p(1, 2), 3);',
            ProxyFunctionInliner,
        )
        assert changed is True
        norm = normalize(code)
        # Both inner and outer calls should be inlined
        assert '1 + 2 + 3' in norm
        # No call-site references to p remain (function decl still present)
        assert 'p(1, 2)' not in norm
        assert 'p(p(' not in norm


class TestProxyFunctionInlinerDisallowed:
    def test_function_expression_in_return_not_inlined(self):
        code, changed = roundtrip(
            'function p() { return function() {}; } p();',
            ProxyFunctionInliner,
        )
        assert changed is False

    def test_assignment_expression_in_return_not_inlined(self):
        code, changed = roundtrip(
            'function p(a) { return a = 1; } p(x);',
            ProxyFunctionInliner,
        )
        assert changed is False

    def test_sequence_expression_in_return_not_inlined(self):
        code, changed = roundtrip(
            'function p(a) { return (1, a); } p(x);',
            ProxyFunctionInliner,
        )
        assert changed is False


class TestCoverageGaps:
    """Tests targeting uncovered lines in proxy_functions.py."""

    def test_callee_not_identifier(self):
        """Line 42: CallExpression with non-identifier callee (e.g., member expression)."""
        code, changed = roundtrip(
            'function p(a) { return a; } obj.p(1);',
            ProxyFunctionInliner,
        )
        # obj.p(1) callee is MemberExpression, not Identifier — should not inline
        assert 'obj.p(1)' in normalize(code)

    def test_destructuring_params_not_proxy(self):
        """Line 109: Function with non-identifier params (destructuring) is not a proxy."""
        code, changed = roundtrip(
            'function f({a, b}) { return a + b; } f({a: 1, b: 2});',
            ProxyFunctionInliner,
        )
        assert changed is False

    def test_body_is_none(self):
        """Line 113: Function body is None — not a proxy."""
        from pyjsclear.parser import parse
        from pyjsclear.generator import generate

        ast = parse('function f() { return 1; } f();')
        # Manually remove the body
        func = ast['body'][0]
        func['body'] = None
        t = ProxyFunctionInliner(ast)
        changed = t.execute()
        assert changed is False

    def test_block_body_non_return_statement(self):
        """Line 126: Block body with a non-return statement (e.g., expression)."""
        code, changed = roundtrip(
            'function f() { console.log(1); } f();',
            ProxyFunctionInliner,
        )
        assert changed is False

    def test_arrow_in_return_not_proxy(self):
        """Lines 158-159: _is_proxy_value rejects ArrowFunctionExpression."""
        code, changed = roundtrip(
            'function f() { return () => 1; } f();',
            ProxyFunctionInliner,
        )
        assert changed is False

    def test_list_child_with_disallowed_type(self):
        """Line 157: _is_proxy_value rejects disallowed type in list child."""
        # Array with a function expression as element
        code, changed = roundtrip(
            'function f() { return [function() {}]; } f();',
            ProxyFunctionInliner,
        )
        assert changed is False

    def test_get_replacement_body_none(self):
        """Line 166: _get_replacement when body is None returns undefined."""
        from pyjsclear.parser import parse

        ast = parse('function f() { return 1; } f();')
        t = ProxyFunctionInliner(ast)
        # Manually create a func_node with no body
        func_node = {'type': 'FunctionDeclaration', 'params': [], 'body': None}
        result = t._get_replacement(func_node, [])
        assert result is not None
        assert result.get('name') == 'undefined'

    def test_get_replacement_block_empty(self):
        """Line 174: _get_replacement with empty block body returns None."""
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        t = ProxyFunctionInliner(ast)
        func_node = {
            'type': 'FunctionDeclaration',
            'params': [],
            'body': {'type': 'BlockStatement', 'body': []},
        }
        result = t._get_replacement(func_node, [])
        assert result is None

    def test_get_replacement_block_non_return(self):
        """Line 174: _get_replacement with block body that starts with non-return."""
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        t = ProxyFunctionInliner(ast)
        func_node = {
            'type': 'FunctionDeclaration',
            'params': [],
            'body': {
                'type': 'BlockStatement',
                'body': [{'type': 'ExpressionStatement', 'expression': {'type': 'Literal', 'value': 1}}],
            },
        }
        result = t._get_replacement(func_node, [])
        assert result is None

    def test_get_replacement_not_block_not_arrow(self):
        """Line 180: _get_replacement with non-block, non-arrow body returns None."""
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        t = ProxyFunctionInliner(ast)
        func_node = {
            'type': 'FunctionDeclaration',
            'params': [],
            'body': {'type': 'Literal', 'value': 1},
        }
        result = t._get_replacement(func_node, [])
        assert result is None

    def test_get_replacement_return_no_argument(self):
        """Line 177: _get_replacement with return but no argument gives undefined."""
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        t = ProxyFunctionInliner(ast)
        func_node = {
            'type': 'FunctionDeclaration',
            'params': [],
            'body': {
                'type': 'BlockStatement',
                'body': [{'type': 'ReturnStatement', 'argument': None}],
            },
        }
        result = t._get_replacement(func_node, [])
        assert result is not None
        assert result.get('name') == 'undefined'

    def test_is_proxy_value_non_dict(self):
        """Line 148: _is_proxy_value with non-dict returns False."""
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        t = ProxyFunctionInliner(ast)
        assert t._is_proxy_value('not_a_dict') is False
        assert t._is_proxy_value(None) is False
        assert t._is_proxy_value(42) is False

    def test_function_non_block_body_not_arrow(self):
        """Line 132: body not BlockStatement and func is not ArrowFunction."""
        from pyjsclear.parser import parse

        ast = parse('function f(a) { return a; } f(1);')
        func = ast['body'][0]
        # Replace body with a non-block to trigger line 132
        func['body'] = {'type': 'ExpressionStatement', 'expression': {'type': 'Identifier', 'name': 'a'}}
        t = ProxyFunctionInliner(ast)
        changed = t.execute()
        # Should not crash; function is not a proxy since body is not block or arrow expr
        assert not changed

    def test_is_proxy_value_child_dict_disallowed(self):
        """Line 158-159: _is_proxy_value child dict with disallowed type."""
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        t = ProxyFunctionInliner(ast)
        # A node containing a child dict with a disallowed type
        node = {
            'type': 'BinaryExpression',
            'operator': '+',
            'left': {'type': 'Identifier', 'name': 'a'},
            'right': {'type': 'AssignmentExpression', 'operator': '=', 'left': {'type': 'Identifier', 'name': 'b'}, 'right': {'type': 'Literal', 'value': 1}},
        }
        assert t._is_proxy_value(node) is False
