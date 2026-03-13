"""Tests for the SingleUseVarInliner transform."""

from pyjsclear.transforms.single_use_vars import SingleUseVarInliner
from tests.unit.conftest import roundtrip


class TestRequireInlining:
    """Tests for single-use require() inlining."""

    def test_simple_require_inlined(self) -> None:
        code = '''
        function f() {
            const x = require("fs");
            x.readFileSync("a");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'require("fs").readFileSync' in result
        assert 'const x' not in result

    def test_require_member_access(self) -> None:
        code = '''
        function f() {
            const proc = require("process");
            return proc.env.HOME;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'require("process").env.HOME' in result

    def test_var_require_inlined(self) -> None:
        code = '''
        function f() {
            var x = require("path");
            return x.join("a", "b");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'require("path")' in result
        assert 'var x' not in result


class TestExpressionInlining:
    """Tests for single-use non-require expression inlining."""

    def test_property_access_inlined(self) -> None:
        code = '''
        function f() {
            const x = obj.prop;
            return x.foo;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'obj.prop.foo' in result
        assert 'const x' not in result

    def test_method_call_inlined(self) -> None:
        code = '''
        function f(arr) {
            const x = Buffer.from(arr);
            return x.toString();
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'Buffer.from(arr).toString()' in result

    def test_new_expression_inlined(self) -> None:
        code = '''
        function f() {
            const d = new Date();
            return d.getTime();
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'new Date().getTime()' in result

    def test_string_literal_inlined(self) -> None:
        code = '''
        function f() {
            const url = "https://example.com";
            fetch(url);
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'fetch("https://example.com")' in result
        assert 'const url' not in result

    def test_simple_call_inlined(self) -> None:
        code = '''
        function f(x) {
            const n = parseInt(x);
            return n + 1;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'parseInt(x) + 1' in result


class TestNoInlining:
    """Tests where inlining should NOT occur."""

    def test_multi_use_not_inlined(self) -> None:
        code = '''
        function f() {
            const fs = require("fs");
            fs.readFileSync("a");
            fs.writeFileSync("b", "c");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_reassigned_var_not_inlined(self) -> None:
        code = '''
        function f() {
            let x = require("fs");
            x = require("path");
            return x.join("a");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_no_init_returns_false(self) -> None:
        result, changed = roundtrip('var x;', SingleUseVarInliner)
        assert changed is False

    def test_large_init_not_inlined(self) -> None:
        """Init expressions with too many AST nodes should not be inlined."""
        # Build a deeply nested expression that exceeds the node limit
        code = '''
        function f() {
            const x = a.b.c.d(e.f.g(h.i.j(k, l, m), n), o, p);
            return x;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_assignment_target_not_inlined(self) -> None:
        code = '''
        function f() {
            const x = obj.prop;
            x = 42;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_mutated_member_not_inlined(self) -> None:
        """var x = {}; x[key] = val; should NOT inline to {}[key] = val."""
        code = '''
        function f() {
            var x = {};
            x["foo"] = 42;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False
        assert 'var x' in result

    def test_mutated_dot_member_not_inlined(self) -> None:
        """var x = {}; x.foo = val; should NOT inline."""
        code = '''
        function f() {
            var x = {};
            x.foo = 42;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False


class TestNestedContexts:
    """Tests for inlining in nested scopes (classes, closures)."""

    def test_class_method_inlined(self) -> None:
        code = '''
        var Cls = class {
            static method() {
                const x = require("process");
                return x.env.HOME;
            }
        };
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'require("process").env.HOME' in result

    def test_nested_function_inlined(self) -> None:
        code = '''
        function outer() {
            function inner() {
                const x = require("fs");
                return x.existsSync("a");
            }
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'require("fs").existsSync' in result

    def test_multiple_scopes_inlined(self) -> None:
        code = '''
        function a() {
            const x = obj.foo;
            use(x);
        }
        function b() {
            const y = obj.bar;
            use(y);
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'const x' not in result
        assert 'const y' not in result
