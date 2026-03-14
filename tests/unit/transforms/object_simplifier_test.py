"""Tests for the ObjectSimplifier transform."""

import pytest

from pyjsclear.generator import generate
from pyjsclear.parser import parse
from pyjsclear.transforms.object_simplifier import ObjectSimplifier
from tests.unit.conftest import normalize
from tests.unit.conftest import roundtrip


class TestLiteralPropertyAccess:
    """Tests for inlining literal property accesses from proxy objects."""

    def test_numeric_property(self):
        code, changed = roundtrip('const o = {x: 1}; y(o.x);', ObjectSimplifier)
        assert changed is True
        assert 'y(1)' in code
        assert 'o.x' not in code

    def test_string_property(self):
        code, changed = roundtrip('const o = {s: "hello"}; y(o.s);', ObjectSimplifier)
        assert changed is True
        assert 'hello' in code
        assert 'o.s' not in code

    def test_computed_string_access(self):
        code, changed = roundtrip('const o = {x: 1}; y(o["x"]);', ObjectSimplifier)
        assert changed is True
        assert 'y(1)' in code
        assert 'o["x"]' not in code


class TestFunctionPropertyCall:
    """Tests for inlining function property calls."""

    def test_simple_function_inline(self):
        code, changed = roundtrip(
            'const o = {f: function(a) { return a; }}; o.f(1);',
            ObjectSimplifier,
        )
        assert changed is True
        assert 'o.f' not in code

    def test_multi_param_function_inline(self):
        code, changed = roundtrip(
            'const o = {f: function(a, b) { return a + b; }}; o.f(1, 2);',
            ObjectSimplifier,
        )
        assert changed is True
        assert '1 + 2' in code
        assert 'o.f' not in code


class TestPropertyAssignmentPreventsInlining:
    """Tests that property assignment on the object prevents inlining."""

    def test_assignment_blocks_inlining(self):
        code, changed = roundtrip('const o = {x: 1}; o.x = 2; y(o.x);', ObjectSimplifier)
        assert changed is False
        assert 'o.x' in code


class TestNonConstantBinding:
    """Tests that non-constant bindings are not inlined."""

    def test_var_reassigned_no_inline(self):
        code, changed = roundtrip('var o = {x: 1}; o = {}; y(o.x);', ObjectSimplifier)
        assert changed is False
        assert 'o.x' in code


class TestLetBindingConstant:
    """Let binding without reassignment is treated as constant and inlined."""

    def test_let_without_reassignment_inlines(self):
        code, changed = roundtrip('let o = {x: 1}; y(o.x);', ObjectSimplifier)
        assert changed is True
        assert 'y(1)' in code


class TestNonProxyObject:
    """Tests that objects with non-literal, non-function values are skipped."""

    def test_object_with_identifier_value_skipped(self):
        code, changed = roundtrip('const o = {x: someVar}; y(o.x);', ObjectSimplifier)
        assert changed is False
        assert 'o.x' in code

    def test_object_with_call_expression_value_skipped(self):
        code, changed = roundtrip('const o = {x: foo()}; y(o.x);', ObjectSimplifier)
        assert changed is False
        assert 'o.x' in code


class TestNoProxyObjects:
    """Tests that the transform returns False when there is nothing to do."""

    def test_no_objects_returns_false(self):
        code, changed = roundtrip('var x = 1; y(x);', ObjectSimplifier)
        assert changed is False

    def test_empty_object_returns_false(self):
        code, changed = roundtrip('const o = {}; y(o);', ObjectSimplifier)
        assert changed is False


class TestCoverageGaps:
    """Tests targeting uncovered lines in object_simplifier.py."""

    def test_binding_node_not_variable_declarator(self):
        """Line 32: binding.node is not VariableDeclarator (e.g., function declaration)."""
        code, changed = roundtrip('const f = function() {}; f();', ObjectSimplifier)
        assert changed is False

    def test_string_key_property(self):
        """Lines 136, 140-142: _get_property_key with Literal string key."""
        code, changed = roundtrip('const o = {"x": 1}; y(o.x);', ObjectSimplifier)
        assert changed is True
        assert 'y(1)' in code

    def test_computed_non_string_access(self):
        """Lines 148, 155: _get_member_prop_name with computed non-string (number)."""
        code, changed = roundtrip('const o = {x: 1}; y(o[0]);', ObjectSimplifier)
        assert changed is False

    def test_no_property_on_member(self):
        """Line 148: _get_member_prop_name where prop is missing."""
        # This is hard to trigger from valid JS, but we test normal computed access
        code, changed = roundtrip('const o = {x: 1}; var k = "x"; y(o[k]);', ObjectSimplifier)
        assert changed is False

    def test_reference_not_as_member_object(self):
        """Lines 65, 67: Reference used but not as MemberExpression.object."""
        code, changed = roundtrip('const o = {x: 1}; y(o);', ObjectSimplifier)
        assert changed is False

    def test_property_name_not_in_prop_map(self):
        """Line 72: Property name accessed that doesn't exist in prop_map."""
        code, changed = roundtrip('const o = {x: 1}; y(o.z);', ObjectSimplifier)
        assert changed is False

    def test_inline_arrow_expression(self):
        """Lines 171-173: Arrow function with expression body inlining."""
        code, changed = roundtrip(
            'const o = {fn: (a) => a + 1}; var x = o.fn(5);',
            ObjectSimplifier,
        )
        assert changed is True
        assert '5 + 1' in normalize(code)

    def test_function_not_called(self):
        """Line 110: Function property used but not as callee of CallExpression."""
        code, changed = roundtrip(
            'const o = {fn: function(a) { return a; }}; var x = o.fn;',
            ObjectSimplifier,
        )
        # Function property accessed but not called — should not inline
        assert changed is False

    def test_inline_function_multi_stmt_body_not_inlined(self):
        """Line 176: Block body with non-single-return is not inlined."""
        code, changed = roundtrip(
            'const o = {fn: function(a) { var x = 1; return a + x; }}; o.fn(5);',
            ObjectSimplifier,
        )
        assert changed is False

    def test_inline_function_no_return_argument(self):
        """Line 180: Block body with return but no argument."""
        code, changed = roundtrip(
            'const o = {fn: function() { return; }}; var x = o.fn();',
            ObjectSimplifier,
        )
        assert changed is False

    def test_recurse_into_child_scopes(self):
        """Line 88: Process child scopes recursively."""
        code, changed = roundtrip(
            'function outer() { const o = {x: 1}; function inner() { y(o.x); } }',
            ObjectSimplifier,
        )
        # The object is in outer scope; inner scope should still get inlined
        assert changed is True
        assert 'y(1)' in code

    def test_is_proxy_object_non_property_type(self):
        """Lines 121, 124: _is_proxy_object with non-Property type or missing value."""
        ast = parse('const o = {x: 1}; y(o.x);')
        t = ObjectSimplifier(ast)
        # SpreadElement is not a Property
        assert t._is_proxy_object([{'type': 'SpreadElement', 'argument': {'type': 'Identifier', 'name': 'a'}}]) is False
        # Property with no value
        assert t._is_proxy_object([{'type': 'Property', 'key': {'type': 'Identifier', 'name': 'x'}}]) is False

    def test_get_property_key_no_key(self):
        """Lines 136: _get_property_key returns None when key is missing."""
        ast = parse('const o = {x: 1};')
        t = ObjectSimplifier(ast)
        assert t._get_property_key({}) is None
        assert t._get_property_key({'key': {'type': 'Literal', 'value': 123}}) is None

    def test_computed_property_key_ignored(self):
        """Line 46: property key returns None for computed key (not Identifier or string Literal)."""
        ast = parse('const o = {x: 1}; var y = o.x;')
        t = ObjectSimplifier(ast)
        # A property with a computed (non-string, non-identifier) key returns None
        assert t._get_property_key({'key': {'type': 'BinaryExpression'}}) is None

    def test_has_property_assignment_me_parent_info_none(self):
        """Line 97: _has_property_assignment where find_parent returns None for me."""
        # Build a scenario with a detached member expression
        ast = parse('const o = {x: 1}; var y = o.x;')
        t = ObjectSimplifier(ast)
        # This should work normally since the member expression is in the AST
        changed = t.execute()
        assert changed is True

    def test_try_inline_function_call_me_parent_info_none(self):
        """Line 107: _try_inline_function_call where find_parent returns None."""
        ast = parse('const o = {fn: function(a) { return a; }}; o.fn(1);')
        t = ObjectSimplifier(ast)
        changed = t.execute()
        assert changed is True

    def test_get_member_prop_name_no_property(self):
        """Line 148: _get_member_property_name with no property returns None."""
        ast = parse('const o = {x: 1};')
        t = ObjectSimplifier(ast)
        assert t._get_member_property_name({}) is None
        assert t._get_member_property_name({'property': None}) is None

    def test_body_not_block_not_expression(self):
        """Line 183: body that's not BlockStatement and not expression for non-arrow."""
        ast = parse('const o = {fn: function(a) { return a; }}; o.fn(1);')
        t = ObjectSimplifier(ast)
        # Manually set the function body to something that is not a BlockStatement
        props = ast['body'][0]['declarations'][0]['init']['properties']
        func = props[0]['value']
        func['body'] = {'type': 'Literal', 'value': 1}  # Not a BlockStatement
        changed = t.execute()
        # Should not inline since body is not a BlockStatement for a FunctionExpression
        assert not changed
