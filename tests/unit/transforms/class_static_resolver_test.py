"""Tests for the class static resolver transform."""

from pyjsclear.transforms.class_static_resolver import ClassStaticResolver
from tests.unit.conftest import roundtrip


class TestClassStaticResolver:
    """Tests for inlining class static properties and identity methods."""

    def test_constant_prop_basic(self):
        code = '''
        var C = class {};
        C.X = 100;
        console.log(C.X + 1);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert '100 + 1' in result
        assert 'C.X + 1' not in result

    def test_constant_prop_string(self):
        code = '''
        var C = class {};
        C.NAME = "hello";
        foo(C.NAME);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert '"hello"' in result
        assert 'C.NAME' not in result or result.count('C.NAME') == 1  # only definition

    def test_constant_prop_preserves_assignment(self):
        """The assignment C.X = 100 itself should not be replaced."""
        code = '''
        var C = class {};
        C.X = 100;
        var y = C.X;
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert 'C.X = 100' in result

    def test_constant_prop_skips_reassigned(self):
        code = '''
        var C = class {};
        C.X = 100;
        C.X = 200;
        console.log(C.X);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is False

    def test_identity_method_inline(self):
        code = '''
        var C = class {
            static id(x) { return x; }
        };
        var a = C.id("hello");
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert '"hello"' in result
        assert 'C.id(' not in result

    def test_identity_method_with_expression(self):
        code = '''
        var C = class {
            static wrap(v) { return v; }
        };
        var a = [C.wrap(42), C.wrap("test")];
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert 'C.wrap(' not in result

    def test_non_identity_method_not_inlined(self):
        code = '''
        var C = class {
            static double(x) { return x + x; }
        };
        var a = C.double(5);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is False

    def test_multi_param_not_inlined(self):
        code = '''
        var C = class {
            static pick(a, b) { return a; }
        };
        var x = C.pick(1, 2);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is False

    def test_no_class_returns_false(self):
        result, changed = roundtrip('var x = 1;', ClassStaticResolver)
        assert changed is False

    def test_non_literal_prop_not_inlined(self):
        code = '''
        var C = class {};
        C.X = foo();
        console.log(C.X);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is False

    def test_combined_constant_and_identity(self):
        """Both constant prop and identity method in the same class."""
        code = '''
        var C = class {
            static id(x) { return x; }
        };
        C.BASE = 100;
        var a = [C.BASE + 0, C.id('')];
        var b = [C.BASE + 1, C.id('')];
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert 'C.BASE' not in result or 'C.BASE = 100' in result
        assert 'C.id(' not in result

    def test_computed_property_access(self):
        code = '''
        var C = class {};
        C.X = 42;
        console.log(C["X"]);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is True
        assert '42' in result

    def test_not_a_class(self):
        """Non-class variable should not be processed."""
        code = '''
        var C = {};
        C.X = 100;
        console.log(C.X);
        '''
        result, changed = roundtrip(code, ClassStaticResolver)
        assert changed is False
