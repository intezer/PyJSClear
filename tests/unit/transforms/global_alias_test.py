"""Tests for the GlobalAliasInliner transform."""

from pyjsclear.transforms.global_alias import GlobalAliasInliner
from tests.unit.conftest import roundtrip


class TestBasicAliases:
    """Tests for var X = GLOBAL → inline X as GLOBAL."""

    def test_json_alias(self):
        code, changed = roundtrip('var _0x1 = JSON; _0x1.parse("{}");', GlobalAliasInliner)
        assert changed is True
        assert 'JSON.parse' in code

    def test_console_alias(self):
        code, changed = roundtrip('var _0x1 = console; _0x1.log("hi");', GlobalAliasInliner)
        assert changed is True
        assert 'console.log' in code

    def test_math_alias(self):
        code, changed = roundtrip('var _0x1 = Math; var y = _0x1.floor(x);', GlobalAliasInliner)
        assert changed is True
        assert 'Math.floor' in code

    def test_buffer_alias(self):
        code, changed = roundtrip('var _0x1 = Buffer; _0x1.from(x);', GlobalAliasInliner)
        assert changed is True
        assert 'Buffer.from' in code

    def test_require_alias(self):
        code, changed = roundtrip('var _0x1 = require; _0x1("fs");', GlobalAliasInliner)
        assert changed is True
        assert 'require("fs")' in code


class TestSkipNonGlobals:
    """Tests that non-global aliases are not inlined."""

    def test_non_global_alias_unchanged(self):
        code, changed = roundtrip('var _0x1 = myVar; _0x1.foo();', GlobalAliasInliner)
        assert changed is False

    def test_no_aliases_returns_false(self):
        code, changed = roundtrip('var x = 1;', GlobalAliasInliner)
        assert changed is False


class TestSkipContexts:
    """Tests that replacement skips property names, declarations, etc."""

    def test_skip_property_name(self):
        """Don't replace identifier when it's a non-computed property name."""
        code, changed = roundtrip('var _0x1 = JSON; obj._0x1 = 5;', GlobalAliasInliner)
        assert changed is False or 'obj._0x1' in code or 'obj.JSON' not in code

    def test_skip_declaration_id(self):
        """Don't replace the LHS of the alias declaration itself."""
        code, changed = roundtrip('var _0x1 = JSON; _0x1.parse("{}");', GlobalAliasInliner)
        assert 'var _0x1' in code or 'var JSON' not in code


class TestAssignmentAliases:
    """Tests for X = GLOBAL assignment (not just var X = GLOBAL)."""

    def test_assignment_alias_found_alongside_var_alias(self):
        """Assignment aliases are only scanned when at least one var alias exists."""
        code, changed = roundtrip(
            'var _0x1 = JSON; var _0x2; _0x2 = Object; _0x2.keys({});',
            GlobalAliasInliner,
        )
        assert changed is True
        assert 'Object.keys' in code

    def test_assignment_only_no_var_alias_returns_false(self):
        """Without a var alias, the assignment alias scan doesn't run."""
        code, changed = roundtrip('var _0x1; _0x1 = Object; _0x1.keys({});', GlobalAliasInliner)
        assert changed is False
