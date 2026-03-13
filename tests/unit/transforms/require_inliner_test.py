"""Tests for the RequireInliner transform."""

from pyjsclear.transforms.require_inliner import RequireInliner
from tests.unit.conftest import roundtrip


class TestRequirePolyfillDetection:
    """Tests for detecting and inlining require polyfill wrappers."""

    def test_typeof_require_polyfill(self) -> None:
        code = '''
        var _0x544bfe = (function() { return typeof require !== "undefined" ? require : null; })();
        _0x544bfe("fs");
        _0x544bfe("path");
        '''
        result, changed = roundtrip(code, RequireInliner)
        assert changed is True
        assert 'require("fs")' in result
        assert 'require("path")' in result

    def test_preserves_non_polyfill_calls(self) -> None:
        """Regular function calls should not be changed."""
        result, changed = roundtrip('myFunc("fs");', RequireInliner)
        assert changed is False
        assert 'require' not in result

    def test_no_polyfills_returns_false(self) -> None:
        result, changed = roundtrip('var x = 1;', RequireInliner)
        assert changed is False

    def test_multi_arg_call_unchanged(self) -> None:
        """Polyfill calls with != 1 arg should not be replaced."""
        code = '''
        var _0x544bfe = (function() { return typeof require !== "undefined" ? require : null; })();
        _0x544bfe("fs", "extra");
        '''
        result, changed = roundtrip(code, RequireInliner)
        assert changed is False
