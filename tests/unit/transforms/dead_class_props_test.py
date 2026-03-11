"""Tests for the dead class property remover transform."""

from pyjsclear.transforms.dead_class_props import DeadClassPropRemover
from tests.unit.conftest import roundtrip


class TestDeadClassPropRemover:
    """Tests for removing dead class property assignments."""

    def test_dead_prop_written_but_never_read(self):
        code = '''
        var C = class {};
        C.x = 1;
        C.y = 2;
        console.log(C.x);
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'C.x' in result
        assert 'C.y' not in result

    def test_fully_dead_class_all_props_removed(self):
        code = '''
        var C = class {};
        C.x = 1;
        C.y = 2;
        C.z = 3;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'C.x' not in result
        assert 'C.y' not in result
        assert 'C.z' not in result

    def test_inner_name_standalone_escapes_class(self):
        """If the inner class name is used standalone, the class has escaped."""
        code = '''
        var Outer = class Inner {};
        Outer.x = 1;
        foo(Inner);
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        # Inner is used standalone, so Outer has escaped — props not removed
        assert changed is False

    def test_inner_name_member_only_still_dead(self):
        """Inner name used only as member access doesn't escape the class."""
        code = '''
        var Outer = class Inner {};
        Outer.x = 1;
        Inner.y = 2;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        # Neither Outer nor Inner have standalone refs — class is fully dead
        assert changed is True
        assert 'Outer.x' not in result
        assert 'Inner.y' not in result

    def test_escaped_class_props_preserved(self):
        """Class assigned to module.exports escapes — props should be kept."""
        code = '''
        var C = class {};
        C.x = 1;
        C.y = 2;
        module.exports = C;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is False
        assert 'C.x' in result
        assert 'C.y' in result

    def test_this_prop_reads_prevent_full_dead(self):
        """this.prop reads inside class body count as reads."""
        code = '''
        var C = class {
            static foo() { return this.x; }
        };
        C.x = 1;
        C.y = 2;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        # x is read via this.x, y is dead; but class itself only has member refs
        # so C is fully dead EXCEPT for this.x reads — y should be removed
        assert changed is True
        assert 'C.x' in result
        assert 'C.y' not in result

    def test_non_class_var_untouched(self):
        code = '''
        var x = {};
        x.a = 1;
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is False

    def test_assignment_class_expression(self):
        """Class assigned via assignment expression (not var declarator)."""
        code = '''
        var C;
        C = class {};
        C.x = 1;
        C.y = 2;
        console.log(C.x);
        '''
        result, changed = roundtrip(code, DeadClassPropRemover)
        assert changed is True
        assert 'C.x' in result
        assert 'C.y' not in result

    def test_no_classes_returns_false(self):
        result, changed = roundtrip('var x = 1;', DeadClassPropRemover)
        assert changed is False
