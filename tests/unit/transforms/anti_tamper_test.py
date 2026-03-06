"""Unit tests for AntiTamperRemover transform."""

import pytest

from pyjsclear.transforms.anti_tamper import AntiTamperRemover
from tests.unit.conftest import normalize, roundtrip


class TestAntiTamperRemover:
    """Tests for removing anti-tamper IIFE patterns."""

    def test_self_defending_pattern_removed(self):
        code = '(function() {  var x = function() {    return this.constructor().constructor("return this")();  };})();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_iife_with_toString_search_removed(self):
        code = '(function() { var x = toString().search("test"); })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_console_disable_bracket_removed(self):
        code = '(function() { console["log"] = function(){}; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_console_disable_dot_removed(self):
        code = '(function() { console.log = function(){}; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_console_warn_bracket_removed(self):
        code = '(function() { console["warn"] = function(){}; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_normal_iife_preserved(self):
        code = '(function() { var x = 1; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is False
        assert 'var x = 1' in normalize(result)

    def test_non_iife_expression_preserved(self):
        code = 'foo();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is False
        assert 'foo()' in normalize(result)

    def test_unary_expression_iife_with_self_defending_removed(self):
        code = '!(function() { var x = this.constructor().constructor("return this")(); })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_no_anti_tamper_returns_false(self):
        code = 'var a = 1; var b = 2;'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is False

    def test_prototype_toString_pattern_removed(self):
        code = '(function() { var x = prototype.toString; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_proto_pattern_removed(self):
        code = '(function() { var x = obj.__proto__; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_arrow_function_iife_with_pattern_removed(self):
        code = '(() => { console["warn"] = function(){}; })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        assert normalize(result).strip() == ''

    def test_debugger_loop_not_detected_by_generator(self):
        """The generator emits DebuggerStatement as a comment, so the
        debugger regex does not match in generated code. This means
        debug-protection IIFEs are not removed by this transform alone."""
        code = '(function() { while(true) { debugger; } })();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is False

    def test_regular_function_call_not_iife(self):
        """A regular call expression (not an IIFE) should be left alone even
        if it contains suspicious-looking identifiers."""
        code = 'constructor();'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is False
        assert 'constructor()' in normalize(result)

    def test_multiple_statements_only_anti_tamper_removed(self):
        code = 'var a = 1;(function() { console["log"] = function(){}; })();var b = 2;'
        result, changed = roundtrip(code, AntiTamperRemover)
        assert changed is True
        norm = normalize(result)
        assert 'var a = 1' in norm
        assert 'var b = 2' in norm
        assert 'console' not in norm
