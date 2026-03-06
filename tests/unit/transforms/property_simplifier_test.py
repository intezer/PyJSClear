import pytest

from pyjsclear.transforms.property_simplifier import PropertySimplifier
from tests.unit.conftest import roundtrip


class TestBracketToDot:
    """Tests for converting obj["prop"] to obj.prop."""

    def test_simple_bracket_to_dot(self):
        code, changed = roundtrip('obj["foo"];', PropertySimplifier)
        assert changed is True
        assert code == 'obj.foo;'

    def test_invalid_identifier_unchanged(self):
        code, changed = roundtrip('obj["0abc"];', PropertySimplifier)
        assert changed is False
        assert '"0abc"' in code or "'0abc'" in code

    def test_reserved_word_is_valid_identifier(self):
        code, changed = roundtrip('obj["class"];', PropertySimplifier)
        assert changed is True
        assert code == 'obj.class;'

    def test_non_string_computed_unchanged(self):
        code, changed = roundtrip('obj[x];', PropertySimplifier)
        assert changed is False
        assert 'obj[x]' in code

    def test_already_dot_notation_unchanged(self):
        code, changed = roundtrip('obj.foo;', PropertySimplifier)
        assert changed is False
        assert 'obj.foo' in code


class TestObjectLiteralKeys:
    """Tests for simplifying string literal keys in object literals."""

    def test_string_key_to_identifier(self):
        """String key becomes Identifier."""
        code, changed = roundtrip('var x = {"foo": 1};', PropertySimplifier)
        assert changed is True
        assert 'foo: 1' in code or 'foo:' in code

    def test_invalid_identifier_key_unchanged(self):
        code, changed = roundtrip('var x = {"0abc": 1};', PropertySimplifier)
        assert changed is False
        assert '0abc' in code

    def test_already_identifier_key_no_change(self):
        code, changed = roundtrip('var x = {foo: 1};', PropertySimplifier)
        assert changed is False
        assert 'foo' in code


class TestMultipleProperties:
    """Tests for mixed property access patterns."""

    def test_mixed_bracket_and_dot(self):
        code, changed = roundtrip('obj["foo"]; obj.bar; obj["0bad"];', PropertySimplifier)
        assert changed is True
        assert 'obj.foo' in code
        assert 'obj.bar' in code
        assert '0bad' in code

    def test_multiple_object_literal_keys(self):
        code, changed = roundtrip('var x = {"good": 1, "0bad": 2, ok: 3};', PropertySimplifier)
        assert changed is True
        # "good" converted to identifier key
        assert 'good: 1' in code or 'good:' in code
        # "0bad" stays as string literal
        assert '0bad' in code
        # ok was already an identifier
        assert 'ok' in code
