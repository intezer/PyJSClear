"""Tests for the MemberChainResolver transform."""

from pyjsclear.transforms.member_chain_resolver import MemberChainResolver
from tests.unit.conftest import normalize
from tests.unit.conftest import roundtrip


class TestBasicResolution:
    """Tests for resolving A.B.C chains to string literals."""

    def test_simple_chain(self):
        code = '''
        ClassA.method1 = "hello";
        Exports.prop1 = ClassA;
        var x = obj.prop1.method1;
        '''
        result, changed = roundtrip(code, MemberChainResolver)
        assert changed is True
        assert '"hello"' in result

    def test_multiple_props(self):
        code = '''
        ClassA.m1 = "foo";
        ClassA.m2 = "bar";
        Exports.p = ClassA;
        var x = obj.p.m1;
        var y = obj.p.m2;
        '''
        result, changed = roundtrip(code, MemberChainResolver)
        assert changed is True
        assert '"foo"' in result
        assert '"bar"' in result


class TestNoResolution:
    """Tests where the chain should NOT be resolved."""

    def test_no_class_constants(self):
        """No string literal assignments → nothing to resolve."""
        result, changed = roundtrip('var x = obj.a.b;', MemberChainResolver)
        assert changed is False

    def test_assignment_target_not_replaced(self):
        """LHS of assignment should not be replaced."""
        code = '''
        ClassA.m1 = "foo";
        Exports.p = ClassA;
        obj.p.m1 = "new_value";
        '''
        result, changed = roundtrip(code, MemberChainResolver)
        # The assignment target should not be replaced
        assert 'obj.p.m1' in result

    def test_two_level_not_three(self):
        """Two-level chain (obj.prop) doesn't match — needs three levels."""
        code = '''
        ClassA.m1 = "foo";
        var x = ClassA.m1;
        '''
        result, changed = roundtrip(code, MemberChainResolver)
        assert changed is False


class TestComputedAccess:
    """Tests for computed property access in chains."""

    def test_computed_string_prop_collected(self):
        """String literal computed props should be collected."""
        code = '''
        ClassA["m1"] = "hello";
        Exports["p"] = ClassA;
        var x = obj["p"]["m1"];
        '''
        result, changed = roundtrip(code, MemberChainResolver)
        assert changed is True
        assert '"hello"' in result

    def test_computed_non_string_not_resolved(self):
        """Non-string computed props should not be collected."""
        code = '''
        ClassA[0] = "hello";
        Exports.p = ClassA;
        var x = obj.p[0];
        '''
        result, changed = roundtrip(code, MemberChainResolver)
        assert changed is False


class TestHelperFunctions:
    """Direct tests for _get_member_names helper."""

    def test_get_member_names_none(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        assert _get_member_names(None) == (None, None)

    def test_get_member_names_no_prop(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'x'},
            'property': None,
            'computed': False,
        }
        assert _get_member_names(node) == (None, None)

    def test_get_member_names_computed_non_string(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'x'},
            'property': {'type': 'Literal', 'value': 42},
            'computed': True,
        }
        assert _get_member_names(node) == (None, None)

    def test_get_member_names_non_identifier_obj(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Literal', 'value': 1},
            'property': {'type': 'Identifier', 'name': 'x'},
            'computed': False,
        }
        assert _get_member_names(node) == (None, None)
