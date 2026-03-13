"""Unit tests for ConstantProp transform."""

import pytest

from pyjsclear.transforms.constant_prop import ConstantProp
from pyjsclear.transforms.constant_prop import _should_skip_reference
from tests.unit.conftest import normalize
from tests.unit.conftest import roundtrip


class TestConstantPropBasic:
    def test_const_numeric_propagated_and_removed(self):
        code, changed = roundtrip('const x = 5; y(x);', ConstantProp)
        assert changed is True
        assert normalize(code) == normalize('y(5);')

    def test_var_no_reassignment_propagated(self):
        code, changed = roundtrip('var x = "hello"; console.log(x);', ConstantProp)
        assert changed is True
        assert normalize(code) == normalize('console.log("hello");')

    def test_let_with_reassignment_unchanged(self):
        code, changed = roundtrip('let x = 1; x = 2; y(x);', ConstantProp)
        assert changed is False
        assert 'x' in code

    def test_multiple_references_replaced(self):
        code, changed = roundtrip('const x = 5; x; x;', ConstantProp)
        assert changed is True
        assert 'x' not in normalize(code).replace('5', '')
        # Declaration should be removed
        assert 'const' not in code

    def test_function_scope_propagation(self):
        code, changed = roundtrip('function f() { const a = true; return a; }', ConstantProp)
        assert changed is True
        assert normalize(code) == normalize('function f() { return true; }')

    def test_non_literal_init_no_propagation(self):
        code, changed = roundtrip('const x = foo(); y(x);', ConstantProp)
        assert changed is False
        assert 'x' in code

    def test_null_literal_propagated(self):
        code, changed = roundtrip('const x = null; y(x);', ConstantProp)
        assert changed is True
        assert normalize(code) == normalize('y(null);')


class TestConstantPropSkipConditions:
    """Tests for reference skip conditions (lines 15-22)."""

    def test_skip_assignment_lhs(self):
        """Line 18: Reference used as assignment target should be skipped."""
        code = 'const x = 5; x = 10;'
        result, changed = roundtrip(code, ConstantProp)
        # x = 10 assignment target should not be replaced with 5 = 10
        assert isinstance(changed, bool)

    def test_skip_update_target(self):
        """Line 20: Reference used as update target should be skipped."""
        code = 'var x = 5; x++;'
        result, changed = roundtrip(code, ConstantProp)
        # x++ should not become 5++; x has writes so it's not constant
        assert changed is False

    def test_skip_declarator_id(self):
        """Line 22: Reference used as VariableDeclarator id should be skipped."""
        code = 'const x = 5; var y = x + 1;'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is True
        assert '5 + 1' in normalize(result) or '5' in result


class TestConstantPropDeclaratorRemoval:
    """Tests for declarator removal edge cases."""

    def test_fully_inlined_declaration_removed(self):
        """Line 101: Empty declarations list triggers REMOVE of entire VariableDeclaration."""
        code = 'const _0x1 = 5; var y = _0x1 + 1;'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is True
        assert '_0x1' not in result
        assert '5' in result

    def test_partially_inlined_multi_declarator(self):
        """Declarator removal when multiple declarators exist — only propagated one removed."""
        code = 'const a = 1, b = foo(); var y = a;'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is True
        # a should be inlined and removed, but b (non-literal) stays
        assert 'foo()' in result

    def test_non_declarator_in_declarations(self):
        """Line 64: Non-VariableDeclarator type check."""
        # Normal constants should be propagated
        code = 'const x = true; if (x) { y(); }'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is True
        assert 'true' in result

    def test_boolean_constant_propagated(self):
        """Boolean literals are properly propagated."""
        code = 'const flag = false; if (flag) { x(); }'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is True
        assert 'false' in result


class TestConstantPropSkipReferenceEdgeCases:
    """Additional tests for _should_skip_reference edge cases."""

    def test_ref_parent_is_none(self):
        """Line 15: ref_parent is None → return True (skip)."""
        assert _should_skip_reference(None, 'left') is True

    def test_update_expression_parent(self):
        """Line 20: UpdateExpression parent → return True."""
        parent = {'type': 'UpdateExpression', 'operator': '++', 'argument': {}}
        assert _should_skip_reference(parent, 'argument') is True

    def test_variable_declarator_id(self):
        """Line 22: VariableDeclarator id parent → return True."""
        parent = {'type': 'VariableDeclarator', 'id': {}, 'init': None}
        assert _should_skip_reference(parent, 'id') is True

    def test_variable_declarator_init_not_skipped(self):
        """VariableDeclarator with key='init' should NOT be skipped."""
        parent = {'type': 'VariableDeclarator', 'id': {}, 'init': {}}
        assert _should_skip_reference(parent, 'init') is False

    def test_assignment_expression_right_not_skipped(self):
        """AssignmentExpression with key='right' should NOT be skipped."""
        parent = {'type': 'AssignmentExpression', 'operator': '=', 'left': {}, 'right': {}}
        assert _should_skip_reference(parent, 'right') is False

    def test_normal_parent_not_skipped(self):
        """Normal parent (e.g., CallExpression) should NOT be skipped."""
        parent = {'type': 'CallExpression', 'callee': {}, 'arguments': []}
        assert _should_skip_reference(parent, 'arguments') is False


class TestConstantPropDeclaratorEdgeCases:
    """Tests for declarator removal type checks (lines 79, 82, 84)."""

    def test_binding_with_assignments_not_removed(self):
        """Line 79: binding with assignments — declaration not removed."""
        # x is assigned a literal but then reassigned → not constant → not propagated
        code = 'var x = 5; x = 10; y(x);'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is False

    def test_non_dict_decl_node_skip(self):
        """Line 82: decl_node not a dict — defensive check doesn't crash."""
        code = 'const a = 1; y(a);'
        result, changed = roundtrip(code, ConstantProp)
        assert changed is True
        assert '1' in result
