"""Tests for the TypeScript enum resolver transform."""

from pyjsclear.transforms.enum_resolver import EnumResolver
from tests.unit.conftest import roundtrip


class TestEnumResolver:
    """Tests for inlining TypeScript enum member accesses."""

    def test_basic_enum(self):
        code = '''
        var E;
        (function (x) {
            x[x.FOO = 0] = "FOO";
            x[x.BAR = 1] = "BAR";
        })(E || (E = {}));
        console.log(E.FOO, E.BAR);
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert 'E.FOO' not in result
        assert 'E.BAR' not in result
        assert '0' in result
        assert '1' in result

    def test_non_sequential_values(self):
        code = '''
        var E;
        (function (x) {
            x[x.A = 0] = "A";
            x[x.B = 4] = "B";
            x[x.C = 10] = "C";
        })(E || (E = {}));
        var v = E.B;
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert '4' in result

    def test_enum_in_expression(self):
        code = '''
        var Level;
        (function (x) {
            x[x.INFO = 0] = "INFO";
            x[x.WARN = 1] = "WARN";
        })(Level || (Level = {}));
        if (level === Level.WARN) { alert(); }
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert 'Level.WARN' not in result
        assert '=== 1' in result

    def test_assignment_target_not_replaced(self):
        """Enum IIFE internals should not be replaced."""
        code = '''
        var E;
        (function (x) {
            x[x.FOO = 0] = "FOO";
        })(E || (E = {}));
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is False

    def test_no_enums_returns_false(self):
        result, changed = roundtrip('var x = 1;', EnumResolver)
        assert changed is False

    def test_enum_as_function_arg(self):
        code = '''
        var Mode;
        (function (m) {
            m[m.READ = 0] = "READ";
            m[m.WRITE = 1] = "WRITE";
        })(Mode || (Mode = {}));
        open(file, Mode.READ);
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert 'Mode.READ' not in result

    def test_multiple_enums(self):
        code = '''
        var A;
        (function (x) { x[x.X = 0] = "X"; })(A || (A = {}));
        var B;
        (function (y) { y[y.Y = 5] = "Y"; })(B || (B = {}));
        console.log(A.X, B.Y);
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert 'A.X' not in result
        assert 'B.Y' not in result

    def test_negative_enum_value(self):
        code = '''
        var E;
        (function (x) {
            x[x.NONE = -1] = "NONE";
            x[x.OK = 0] = "OK";
        })(E || (E = {}));
        console.log(E.NONE, E.OK);
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert 'E.NONE' not in result
        assert 'E.OK' not in result
        assert '-1' in result
        assert ', 0' in result or '(0' in result

    def test_export_assigned_enum(self):
        """Enum assigned via u = r.exports || (r.exports = {}) pattern."""
        code = '''
        var u;
        (function (x) {
            x[x.B639G7B = 0] = "B639G7B";
            x[x.V4E6B4O = 1] = "V4E6B4O";
        })(u = r.a689XV5 || (r.a689XV5 = {}));
        console.log(u.B639G7B);
        '''
        result, changed = roundtrip(code, EnumResolver)
        assert changed is True
        assert 'u.B639G7B' not in result
        assert '0' in result
