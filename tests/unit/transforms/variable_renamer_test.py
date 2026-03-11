"""Tests for the VariableRenamer transform."""

import re

from pyjsclear.transforms.variable_renamer import VariableRenamer
from pyjsclear.transforms.variable_renamer import _infer_from_init
from pyjsclear.transforms.variable_renamer import _name_generator
from pyjsclear.parser import parse
from tests.unit.conftest import roundtrip


class TestBasicRenaming:
    """Tests for basic _0x identifier renaming."""

    def test_single_var_renamed(self):
        code = 'function f() { var _0x1234 = 1; return _0x1234; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x1234' not in result

    def test_multiple_vars_renamed(self):
        code = 'function f() { var _0x1 = 1; var _0x2 = 2; return _0x1 + _0x2; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x' not in result

    def test_function_name_renamed(self):
        code = 'function _0xabc() { return 1; } _0xabc();'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0xabc' not in result

    def test_param_renamed(self):
        code = 'function f(_0xdef) { return _0xdef; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0xdef' not in result

    def test_const_let_renamed(self):
        code = 'function f() { const _0x1 = 1; let _0x2 = 2; return _0x1 + _0x2; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x' not in result


class TestHeuristicNaming:
    """Tests for heuristic-based name inference."""

    def test_require_fs_named(self):
        code = 'function f() { const _0x1 = require("fs"); _0x1.readFileSync("a"); }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const fs = require("fs")' in result

    def test_require_path_named(self):
        code = 'function f() { const _0x1 = require("path"); _0x1.join("a"); }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const path = require("path")' in result

    def test_require_child_process_named(self):
        code = 'function f() { const _0x1 = require("child_process"); _0x1.spawn("a"); }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const cp = require("child_process")' in result

    def test_require_dedupe(self):
        """Multiple require("fs") in same scope get fs, fs2, fs3."""
        code = '''
        function f() {
            const _0x1 = require("fs");
            const _0x2 = require("fs");
            _0x1.readFileSync("a");
            _0x2.readFileSync("b");
        }
        '''
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const fs =' in result
        assert 'const fs2 =' in result

    def test_array_literal_named(self):
        code = 'function f() { const _0x1 = []; _0x1.push(1); }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const arr = []' in result

    def test_object_literal_named(self):
        code = 'function f() { const _0x1 = {}; _0x1.foo = 1; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const obj = {}' in result or 'const obj =' in result

    def test_buffer_from_named(self):
        code = 'function f() { const _0x1 = Buffer.from("abc"); return _0x1; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const buf = Buffer.from' in result

    def test_json_parse_named(self):
        code = 'function f(s) { const _0x1 = JSON.parse(s); return _0x1; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const data = JSON.parse' in result

    def test_new_date_named(self):
        code = 'function f() { const _0x1 = new Date(); return _0x1; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const date = new Date()' in result

    def test_loop_counter_named_i(self):
        code = 'function f() { for (var _0x1 = 0; _0x1 < 10; _0x1++) { console.log(_0x1); } }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'var i = 0' in result or 'var i2 = 0' in result or 'let i = 0' in result

    def test_usage_based_fs_naming(self):
        """Variable used with .existsSync should be named fs even without require init."""
        code = '''
        function f(_0xabc) {
            _0xabc.existsSync("a");
            _0xabc.readFileSync("b");
        }
        '''
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'function f(fs)' in result

    def test_require_with_path_sanitized(self):
        r"""require(".\lib\Foo.node") should not produce invalid identifiers."""
        code = r'function f() { const _0x1 = require(".\\lib\\Foo.node"); return _0x1; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        # Should produce a valid identifier, not ".\lib\Foo.node"
        ast = parse(result)
        assert ast is not None


class TestPreservation:
    """Tests for names that should NOT be renamed."""

    def test_non_0x_preserved(self):
        code = 'function f() { var foo = 1; return foo; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is False
        assert 'foo' in result

    def test_mixed_names(self):
        code = 'function f() { var foo = 1; var _0x1234 = 2; return foo + _0x1234; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'foo' in result
        assert '_0x1234' not in result

    def test_no_0x_returns_false(self):
        code = 'var x = 1;'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is False


class TestNoConflict:
    """Tests that renaming doesn't create naming conflicts."""

    def test_no_conflict_with_existing_names(self):
        code = 'function f() { var a = 1; var _0x1234 = 2; return a + _0x1234; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x1234' not in result
        assert 'var a = 1' in result

    def test_require_name_conflict_resolved(self):
        """If 'fs' already exists, require("fs") should get 'fs2'."""
        code = '''
        function f() {
            var fs = "taken";
            const _0x1 = require("fs");
            return _0x1.readFileSync(fs);
        }
        '''
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert 'const fs2 = require("fs")' in result


class TestNameGenerator:
    """Tests for the name generator function."""

    def test_generates_single_letters(self):
        gen = _name_generator(set())
        names = [next(gen) for _ in range(26)]
        assert names == list('abcdefghijklmnopqrstuvwxyz')

    def test_generates_two_letter_after_single(self):
        gen = _name_generator(set())
        names = [next(gen) for _ in range(28)]
        assert names[26] == 'aa'
        assert names[27] == 'ab'

    def test_skips_reserved(self):
        gen = _name_generator({'a', 'c'})
        assert next(gen) == 'b'
        assert next(gen) == 'd'


class TestNestedScopes:
    """Tests for renaming across nested scopes."""

    def test_nested_functions(self):
        code = '''
        function _0xabc1() {
            var _0x1 = 1;
            function _0xdef2() {
                var _0x2 = 2;
                return _0x2;
            }
            return _0x1;
        }
        '''
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x' not in result

    def test_arrow_function_params(self):
        code = 'var f = (_0xaaa, _0xbbb) => _0xaaa + _0xbbb;'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x' not in result

    def test_class_expression_name_renamed(self):
        code = 'var C = class _0xabc { static m() { return _0xabc; } };'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0xabc' not in result

    def test_rest_param_renamed(self):
        code = 'function f(_0xaaa, ..._0xbbb) { return _0xbbb; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0x' not in result

    def test_catch_param_renamed(self):
        code = 'function f() { try { x(); } catch (_0xabc) { console.log(_0xabc); } }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        assert '_0xabc' not in result

    def test_destructuring_duplicate_names_fixed(self):
        """Obfuscators can produce const [a, a, a] = x; — fix duplicates."""
        code = 'function f(_0xabc) { const [_0xabc, _0xabc, _0xabc] = _0xabc; }'
        result, changed = roundtrip(code, VariableRenamer)
        assert changed is True
        # Should have three different names in the destructuring
        ast = parse(result)
        assert ast is not None  # Must be valid JS
