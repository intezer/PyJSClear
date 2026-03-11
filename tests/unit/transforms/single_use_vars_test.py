"""Tests for the SingleUseVarInliner transform."""

from pyjsclear.transforms.single_use_vars import SingleUseVarInliner
from pyjsclear.transforms.single_use_vars import _is_require_call
from tests.unit.conftest import roundtrip


class TestBasicInlining:
    """Tests for basic single-use require() inlining."""

    def test_simple_require_inlined(self):
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

    def test_require_member_access(self):
        code = '''
        function f() {
            const proc = require("process");
            return proc.env.HOME;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'require("process").env.HOME' in result

    def test_var_require_inlined(self):
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


class TestNoInlining:
    """Tests where inlining should NOT occur."""

    def test_multi_use_not_inlined(self):
        code = '''
        function f() {
            const fs = require("fs");
            fs.readFileSync("a");
            fs.writeFileSync("b", "c");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_non_require_call_not_inlined(self):
        code = '''
        function f() {
            const x = getData("foo");
            return x.bar;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_reassigned_var_not_inlined(self):
        code = '''
        function f() {
            let x = require("fs");
            x = require("path");
            return x.join("a");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_no_require_returns_false(self):
        result, changed = roundtrip('var x = 1;', SingleUseVarInliner)
        assert changed is False

    def test_require_no_args_not_inlined(self):
        code = '''
        function f() {
            const x = require();
            return x.foo;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False

    def test_require_numeric_arg_not_inlined(self):
        code = '''
        function f() {
            const x = require(42);
            return x.foo;
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is False


class TestNestedContexts:
    """Tests for inlining in nested scopes (classes, closures)."""

    def test_class_method_inlined(self):
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

    def test_nested_function_inlined(self):
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

    def test_multiple_scopes_inlined(self):
        code = '''
        function a() {
            const x = require("fs");
            x.readFileSync("a");
        }
        function b() {
            const y = require("path");
            y.join("a", "b");
        }
        '''
        result, changed = roundtrip(code, SingleUseVarInliner)
        assert changed is True
        assert 'const x' not in result
        assert 'const y' not in result


class TestIsRequireCall:
    """Tests for the _is_require_call helper."""

    def test_valid_require(self):
        node = {
            'type': 'CallExpression',
            'callee': {'type': 'Identifier', 'name': 'require'},
            'arguments': [{'type': 'Literal', 'value': 'fs'}],
        }
        assert _is_require_call(node) is True

    def test_non_require_callee(self):
        node = {
            'type': 'CallExpression',
            'callee': {'type': 'Identifier', 'name': 'import'},
            'arguments': [{'type': 'Literal', 'value': 'fs'}],
        }
        assert _is_require_call(node) is False

    def test_not_call_expression(self):
        assert _is_require_call({'type': 'Literal', 'value': 1}) is False
        assert _is_require_call(None) is False

    def test_numeric_arg(self):
        node = {
            'type': 'CallExpression',
            'callee': {'type': 'Identifier', 'name': 'require'},
            'arguments': [{'type': 'Literal', 'value': 42}],
        }
        assert _is_require_call(node) is False

    def test_multiple_args(self):
        node = {
            'type': 'CallExpression',
            'callee': {'type': 'Identifier', 'name': 'require'},
            'arguments': [
                {'type': 'Literal', 'value': 'fs'},
                {'type': 'Literal', 'value': 'extra'},
            ],
        }
        assert _is_require_call(node) is False

    def test_member_callee(self):
        node = {
            'type': 'CallExpression',
            'callee': {
                'type': 'MemberExpression',
                'object': {'type': 'Identifier', 'name': 'module'},
                'property': {'type': 'Identifier', 'name': 'require'},
            },
            'arguments': [{'type': 'Literal', 'value': 'fs'}],
        }
        assert _is_require_call(node) is False
