"""Tests for the ClassStringDecoder transform."""

from pyjsclear.transforms.class_string_decoder import ClassStringDecoder
from tests.unit.conftest import roundtrip


class TestBasicDecode:
    """Tests for basic class-based string decoder resolution."""

    def test_no_class_patterns_returns_false(self):
        result, changed = roundtrip('var x = 1;', ClassStringDecoder)
        assert changed is False

    def test_no_decoder_methods_returns_false(self):
        """Class with props but no decoder method should not fire."""
        code = '''
        var Cls = class {};
        Cls.p1 = "hello";
        '''
        result, changed = roundtrip(code, ClassStringDecoder)
        assert changed is False


class TestClassPropCollection:
    """Tests for collecting string properties on classes."""

    def test_string_prop_collected(self):
        """String assignments on class vars should be tracked internally."""
        # This is an indirect test — if props aren't collected, resolution won't work
        code = '''
        var Cls = class {};
        Cls.p1 = "foo";
        Cls.p2 = "bar";
        '''
        result, changed = roundtrip(code, ClassStringDecoder)
        # No decoder method, so no changes expected
        assert changed is False


class TestDeadClassPropRemover:
    """Tests for the DeadClassPropRemover transform."""

    def test_no_classes_returns_false(self):
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        result, changed = roundtrip('var x = 1;', DeadClassPropRemover)
        assert changed is False

    def test_dead_prop_removed(self):
        """Property written but never read should be removed."""
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        code = '''
        var Cls = class {};
        Cls.deadProp = "never_used";
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'deadProp' not in result

    def test_read_prop_preserved(self):
        """Property that is read should NOT be removed."""
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        code = '''
        var Cls = class {};
        Cls.liveProp = "used";
        var x = Cls.liveProp;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        # liveProp is read, so it should be preserved
        assert 'liveProp' in result

    def test_fully_dead_class(self):
        """Class that is only used via property assignments — all props dead."""
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        code = '''
        var Cls = class {};
        Cls.a = "x";
        Cls.b = "y";
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'Cls.a' not in result
        assert 'Cls.b' not in result

    def test_assignment_class_detected(self):
        """Class assigned via `X = class {}` (not var) should be detected."""
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        code = '''
        var Cls;
        Cls = class {};
        Cls.deadProp = "never_used";
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'deadProp' not in result

    def test_sequence_expression_dead_props(self):
        """Dead props inside SequenceExpression should be stripped."""
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        code = '''
        var Cls = class {};
        Cls.dead1 = "a", Cls.dead2 = "b";
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'dead1' not in result
        assert 'dead2' not in result

    def test_sequence_expression_partial_removal(self):
        """Only dead props removed from a sequence; live ones kept."""
        from pyjsclear.transforms.dead_class_props import DeadClassPropRemover

        code = '''
        var Cls = class {};
        Cls.dead = "a", Cls.live = "b";
        var x = Cls.live;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'dead' not in result or 'Cls.dead' not in result
        assert 'Cls.live' in result


class TestClassStringDecoderHelpers:
    """Tests for ClassStringDecoder helper functions."""

    def test_get_member_names_computed_string(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Literal', 'value': 'prop'},
            'computed': True,
        }
        assert _get_member_names(node) == ('obj', 'prop')

    def test_get_member_names_non_identifier_prop(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Literal', 'value': 42},
            'computed': True,
        }
        assert _get_member_names(node) == (None, None)

    def test_get_member_names_dot_notation(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'prop'},
            'computed': False,
        }
        assert _get_member_names(node) == ('obj', 'prop')

    def test_get_member_names_no_prop(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        assert _get_member_names(None) == (None, None)
        assert _get_member_names({'type': 'Literal'}) == (None, None)

    def test_get_member_names_non_identifier_object(self):
        from pyjsclear.utils.ast_helpers import get_member_names as _get_member_names

        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Literal', 'value': 1},
            'property': {'type': 'Identifier', 'name': 'prop'},
            'computed': False,
        }
        assert _get_member_names(node) == (None, None)
