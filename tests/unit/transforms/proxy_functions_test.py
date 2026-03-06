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
