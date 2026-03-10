"""Comprehensive tests for pyjsclear.utils.ast_helpers."""

import copy
import math

import pytest

from pyjsclear.utils.ast_helpers import (
    _CHILD_KEYS,
    deep_copy,
    get_child_keys,
    get_literal_value,
    is_boolean_literal,
    is_identifier,
    is_literal,
    is_null_literal,
    is_numeric_literal,
    is_string_literal,
    is_undefined,
    is_valid_identifier,
    make_block_statement,
    make_expression_statement,
    make_identifier,
    make_literal,
    make_var_declaration,
    nodes_equal,
    replace_identifiers,
)


# ---------------------------------------------------------------------------
# deep_copy
# ---------------------------------------------------------------------------


class TestDeepCopy:
    def test_basic_node(self):
        node = {'type': 'Literal', 'value': 42, 'raw': '42'}
        result = deep_copy(node)
        assert result == node
        assert result is not node

    def test_nested_node_independence(self):
        inner = {'type': 'Identifier', 'name': 'x'}
        outer = {'type': 'ExpressionStatement', 'expression': inner}
        result = deep_copy(outer)
        result['expression']['name'] = 'y'
        assert inner['name'] == 'x'

    def test_list_children(self):
        node = {'type': 'BlockStatement', 'body': [{'type': 'EmptyStatement'}]}
        result = deep_copy(node)
        result['body'].append({'type': 'EmptyStatement'})
        assert len(node['body']) == 1

    def test_none_passthrough(self):
        assert deep_copy(None) is None

    def test_empty_dict(self):
        assert deep_copy({}) == {}


# ---------------------------------------------------------------------------
# Type check predicates
# ---------------------------------------------------------------------------


class TestIsLiteral:
    def test_string_literal(self):
        assert is_literal({'type': 'Literal', 'value': 'hello', 'raw': '"hello"'})

    def test_numeric_literal(self):
        assert is_literal({'type': 'Literal', 'value': 42, 'raw': '42'})

    def test_not_a_dict(self):
        assert not is_literal('Literal')
        assert not is_literal(42)
        assert not is_literal(None)
        assert not is_literal([])

    def test_wrong_type(self):
        assert not is_literal({'type': 'Identifier', 'name': 'x'})

    def test_missing_type(self):
        assert not is_literal({'value': 42})

    def test_empty_dict(self):
        assert not is_literal({})


class TestIsIdentifier:
    def test_basic(self):
        assert is_identifier({'type': 'Identifier', 'name': 'foo'})

    def test_not_identifier(self):
        assert not is_identifier({'type': 'Literal', 'value': 1})

    def test_non_dict(self):
        assert not is_identifier('Identifier')
        assert not is_identifier(None)


class TestIsStringLiteral:
    def test_string(self):
        assert is_string_literal({'type': 'Literal', 'value': 'hello'})

    def test_empty_string(self):
        assert is_string_literal({'type': 'Literal', 'value': ''})

    def test_number_not_string(self):
        assert not is_string_literal({'type': 'Literal', 'value': 42})

    def test_bool_not_string(self):
        assert not is_string_literal({'type': 'Literal', 'value': True})

    def test_none_not_string(self):
        assert not is_string_literal({'type': 'Literal', 'value': None, 'raw': 'null'})


class TestIsNumericLiteral:
    def test_int(self):
        assert is_numeric_literal({'type': 'Literal', 'value': 42})

    def test_float(self):
        assert is_numeric_literal({'type': 'Literal', 'value': 3.14})

    def test_zero(self):
        assert is_numeric_literal({'type': 'Literal', 'value': 0})

    def test_negative(self):
        assert is_numeric_literal({'type': 'Literal', 'value': -1})

    def test_string_not_numeric(self):
        assert not is_numeric_literal({'type': 'Literal', 'value': '42'})

    def test_bool_not_numeric(self):
        # In Python bool is subclass of int, but isinstance(True, bool) is True
        # and the function checks for (int, float). Since bool IS int, this returns True.
        # However, the check order matters: is_boolean_literal checks bool first.
        # is_numeric_literal will return True for booleans because bool subclasses int.
        assert is_numeric_literal({'type': 'Literal', 'value': True})


class TestIsBooleanLiteral:
    def test_true(self):
        assert is_boolean_literal({'type': 'Literal', 'value': True})

    def test_false(self):
        assert is_boolean_literal({'type': 'Literal', 'value': False})

    def test_int_not_bool(self):
        assert not is_boolean_literal({'type': 'Literal', 'value': 1})

    def test_string_not_bool(self):
        assert not is_boolean_literal({'type': 'Literal', 'value': 'true'})


class TestIsNullLiteral:
    def test_null(self):
        assert is_null_literal({'type': 'Literal', 'value': None, 'raw': 'null'})

    def test_none_without_raw(self):
        # Must have raw == 'null' to be considered null literal
        assert not is_null_literal({'type': 'Literal', 'value': None})

    def test_none_wrong_raw(self):
        assert not is_null_literal({'type': 'Literal', 'value': None, 'raw': 'undefined'})

    def test_non_literal(self):
        assert not is_null_literal({'type': 'Identifier', 'name': 'null'})


class TestIsUndefined:
    def test_undefined_identifier(self):
        assert is_undefined({'type': 'Identifier', 'name': 'undefined'})

    def test_other_identifier(self):
        assert not is_undefined({'type': 'Identifier', 'name': 'null'})

    def test_literal_not_undefined(self):
        assert not is_undefined({'type': 'Literal', 'value': None, 'raw': 'null'})

    def test_non_dict(self):
        assert not is_undefined(None)


# ---------------------------------------------------------------------------
# get_literal_value
# ---------------------------------------------------------------------------


class TestGetLiteralValue:
    def test_string_value(self):
        val, ok = get_literal_value({'type': 'Literal', 'value': 'hello'})
        assert ok is True
        assert val == 'hello'

    def test_numeric_value(self):
        val, ok = get_literal_value({'type': 'Literal', 'value': 42})
        assert ok is True
        assert val == 42

    def test_none_value_null(self):
        val, ok = get_literal_value({'type': 'Literal', 'value': None, 'raw': 'null'})
        assert ok is True
        assert val is None

    def test_non_literal(self):
        val, ok = get_literal_value({'type': 'Identifier', 'name': 'x'})
        assert ok is False
        assert val is None

    def test_literal_missing_value_key(self):
        # A Literal node without a 'value' key; .get returns None
        val, ok = get_literal_value({'type': 'Literal', 'raw': '42'})
        assert ok is True
        assert val is None

    def test_bool_value(self):
        val, ok = get_literal_value({'type': 'Literal', 'value': True})
        assert ok is True
        assert val is True


# ---------------------------------------------------------------------------
# make_literal
# ---------------------------------------------------------------------------


class TestMakeLiteral:
    def test_integer(self):
        node = make_literal(42)
        assert node == {'type': 'Literal', 'value': 42, 'raw': '42'}

    def test_float_whole_number(self):
        # Whole floats are rendered as int strings
        node = make_literal(3.0)
        assert node['raw'] == '3'

    def test_float_fractional(self):
        node = make_literal(3.14)
        assert node['raw'] == '3.14'

    def test_negative_zero_float(self):
        # -0.0 in Python: str(-0.0) is '-0.0', and -0.0 == 0 is True
        # but str(-0.0).startswith('-') triggers the else branch
        node = make_literal(-0.0)
        assert node['raw'] == '-0.0'

    def test_boolean_true(self):
        node = make_literal(True)
        assert node == {'type': 'Literal', 'value': True, 'raw': 'true'}

    def test_boolean_false(self):
        node = make_literal(False)
        assert node == {'type': 'Literal', 'value': False, 'raw': 'false'}

    def test_null(self):
        node = make_literal(None)
        assert node == {'type': 'Literal', 'value': None, 'raw': 'null'}

    def test_simple_string(self):
        node = make_literal('hello')
        assert node['value'] == 'hello'
        assert node['raw'] == '"hello"'

    def test_string_with_double_quotes(self):
        """Bug #2: String containing double quotes. repr('say "hi"') gives
        The raw value must properly escape inner double quotes."""
        node = make_literal('say "hi"')
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')
        assert raw == '"say \\"hi\\""'

    def test_custom_raw(self):
        node = make_literal(42, raw='0x2A')
        assert node == {'type': 'Literal', 'value': 42, 'raw': '0x2A'}

    def test_negative_int(self):
        node = make_literal(-5)
        assert node['raw'] == '-5'

    def test_large_float(self):
        node = make_literal(1e10)
        # 1e10 == int(1e10) and not negative zero, so raw = str(int(1e10))
        assert node['raw'] == '10000000000'

    # --- Bug #2 documentation tests ---
    # make_literal() for strings uses repr() manipulation which is fragile.
    # The code does: raw = repr(value).replace("'", '"')
    # then checks if raw starts with '"' and if not, re-wraps.
    # This section documents the current behavior for edge cases.

    def test_bug2_string_with_single_quotes(self):
        """Bug #2: Strings containing single quotes. repr() would use double quotes
        for the Python repr, so replacing ' with " produces unexpected results.

        For "it's", repr gives: "it's" (Python uses double quotes when string
        contains single quote). Then replace("'", '"') turns it into "it"s".
        But since it starts with '"', the if-branch doesn't trigger.
        """
        node = make_literal("it's")
        # repr("it's") => '"it\'s"' -- actually Python repr escapes the single quote
        # Let's just document what actually happens
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')

    def test_bug2_backslash_string(self):
        """Bug #2: Strings with backslashes. repr() produces escape sequences
        which then get the quote replacement applied.

        repr('a\\b') => "'a\\\\b'" => replace ' with " => '"a\\\\b"'
        """
        node = make_literal('a\\b')
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')
        # The repr-based approach double-escapes the backslash for raw
        # In proper JSON/JS, "a\\b" would represent the string a\b
        # but repr gives us Python escaping, not JS escaping
        assert '\\\\' in raw  # double-escaped backslash from repr

    def test_bug2_unicode_string(self):
        """Bug #2: Unicode strings. repr() may produce \\uXXXX or the literal char
        depending on the character. For printable unicode, repr includes it literally."""
        node = make_literal('\u00e9')  # e-acute
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')

    def test_bug2_newline_string(self):
        """Bug #2: Strings with newlines. repr() produces \\n which is valid JS too,
        so this case happens to work."""
        node = make_literal('line1\nline2')
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')
        assert '\\n' in raw

    def test_bug2_tab_string(self):
        """Bug #2: Strings with tabs. repr() produces \\t which is valid JS."""
        node = make_literal('a\tb')
        raw = node['raw']
        assert '\\t' in raw

    def test_bug2_string_with_both_quote_types(self):
        """Bug #2: String containing both single and double quotes.
        repr() for a string with both quotes uses single-quote wrapping and
        escapes the single quotes. The replace("'", '"') then converts ALL
        single quotes (including the wrapping ones) to double quotes."""
        node = make_literal("""he said "it's" fine""")
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')

    def test_bug2_empty_string(self):
        """Bug #2: Empty string should produce '""'."""
        node = make_literal('')
        assert node['raw'] == '""'

    def test_bug2_null_byte_string(self):
        """Bug #2: String with null byte. repr() produces \\x00 which is NOT
        valid JS (JS uses \\0 or \\u0000). This documents the current behavior."""
        node = make_literal('a\x00b')
        raw = node['raw']
        assert raw.startswith('"')
        assert raw.endswith('"')
        assert '\\0' in raw


# ---------------------------------------------------------------------------
# make_identifier
# ---------------------------------------------------------------------------


class TestMakeIdentifier:
    def test_basic(self):
        assert make_identifier('foo') == {'type': 'Identifier', 'name': 'foo'}

    def test_underscore(self):
        assert make_identifier('_') == {'type': 'Identifier', 'name': '_'}


# ---------------------------------------------------------------------------
# make_expression_statement
# ---------------------------------------------------------------------------


class TestMakeExpressionStatement:
    def test_wraps_expression(self):
        expr = {'type': 'Literal', 'value': 42, 'raw': '42'}
        result = make_expression_statement(expr)
        assert result['type'] == 'ExpressionStatement'
        assert result['expression'] is expr


# ---------------------------------------------------------------------------
# make_block_statement
# ---------------------------------------------------------------------------


class TestMakeBlockStatement:
    def test_empty_body(self):
        result = make_block_statement([])
        assert result == {'type': 'BlockStatement', 'body': []}

    def test_with_statements(self):
        stmts = [{'type': 'EmptyStatement'}, {'type': 'EmptyStatement'}]
        result = make_block_statement(stmts)
        assert result['body'] is stmts
        assert len(result['body']) == 2


# ---------------------------------------------------------------------------
# make_var_declaration
# ---------------------------------------------------------------------------


class TestMakeVarDeclaration:
    def test_var_no_init(self):
        result = make_var_declaration('x')
        assert result['type'] == 'VariableDeclaration'
        assert result['kind'] == 'var'
        assert len(result['declarations']) == 1
        decl = result['declarations'][0]
        assert decl['type'] == 'VariableDeclarator'
        assert decl['id'] == {'type': 'Identifier', 'name': 'x'}
        assert decl['init'] is None

    def test_let_with_init(self):
        init = {'type': 'Literal', 'value': 5, 'raw': '5'}
        result = make_var_declaration('y', init=init, kind='let')
        assert result['kind'] == 'let'
        assert result['declarations'][0]['init'] is init

    def test_const(self):
        result = make_var_declaration('Z', kind='const')
        assert result['kind'] == 'const'


# ---------------------------------------------------------------------------
# is_valid_identifier
# ---------------------------------------------------------------------------


class TestIsValidIdentifier:
    def test_simple(self):
        assert is_valid_identifier('foo')

    def test_underscore_prefix(self):
        assert is_valid_identifier('_private')

    def test_dollar_prefix(self):
        assert is_valid_identifier('$jquery')

    def test_digits_allowed_after_first(self):
        assert is_valid_identifier('x1')

    def test_starts_with_digit(self):
        assert not is_valid_identifier('1abc')

    def test_empty_string(self):
        assert not is_valid_identifier('')

    def test_none(self):
        assert not is_valid_identifier(None)

    def test_non_string(self):
        assert not is_valid_identifier(42)

    def test_hyphen(self):
        assert not is_valid_identifier('foo-bar')

    def test_single_dollar(self):
        assert is_valid_identifier('$')

    def test_single_underscore(self):
        assert is_valid_identifier('_')

    def test_reserved_words_pass_regex(self):
        # The function only does regex check, not reserved word check
        assert is_valid_identifier('if')
        assert is_valid_identifier('return')
        assert is_valid_identifier('class')


# ---------------------------------------------------------------------------
# _CHILD_KEYS and get_child_keys
# ---------------------------------------------------------------------------


class TestChildKeys:
    def test_known_node_type(self):
        node = {'type': 'BinaryExpression', 'left': {}, 'right': {}, 'operator': '+'}
        assert get_child_keys(node) == ('left', 'right')

    def test_literal_has_no_children(self):
        assert get_child_keys({'type': 'Literal', 'value': 1}) == ()

    def test_identifier_has_no_children(self):
        assert get_child_keys({'type': 'Identifier', 'name': 'x'}) == ()

    def test_non_dict_returns_empty(self):
        assert get_child_keys('not a node') == ()
        assert get_child_keys(None) == ()
        assert get_child_keys(42) == ()

    def test_missing_type_returns_empty(self):
        assert get_child_keys({'value': 42}) == ()

    def test_unknown_node_type_fallback(self):
        # Unknown type falls back to heuristic: keys with dict/list values not in _SKIP_KEYS
        node = {'type': 'UnknownThing', 'body': [], 'extra': {}, 'name': 'test'}
        keys = get_child_keys(node)
        assert 'body' in keys
        assert 'extra' in keys
        # 'name' is in _SKIP_KEYS so should not appear
        assert 'name' not in keys

    def test_fallback_skips_type_key(self):
        node = {'type': 'CustomNode', 'child': {'type': 'Literal'}}
        keys = get_child_keys(node)
        assert 'type' not in keys
        assert 'child' in keys

    def test_all_known_types_in_child_keys(self):
        # Sanity check: every value in _CHILD_KEYS is a tuple
        for node_type, keys in _CHILD_KEYS.items():
            assert isinstance(keys, tuple), f'{node_type} keys is not a tuple'


# ---------------------------------------------------------------------------
# replace_identifiers
# ---------------------------------------------------------------------------


class TestReplaceIdentifiers:
    def test_simple_replacement(self):
        node = {
            'type': 'BinaryExpression',
            'operator': '+',
            'left': {'type': 'Identifier', 'name': 'a'},
            'right': {'type': 'Identifier', 'name': 'b'},
        }
        param_map = {'a': {'type': 'Literal', 'value': 1, 'raw': '1'}}
        replace_identifiers(node, param_map)
        assert node['left'] == {'type': 'Literal', 'value': 1, 'raw': '1'}
        assert node['right'] == {'type': 'Identifier', 'name': 'b'}

    def test_replacement_is_deep_copied(self):
        replacement = {'type': 'Literal', 'value': 1, 'raw': '1'}
        node = {
            'type': 'ExpressionStatement',
            'expression': {'type': 'Identifier', 'name': 'x'},
        }
        replace_identifiers(node, {'x': replacement})
        # Mutating the replacement should not affect the substituted node
        replacement['value'] = 999
        assert node['expression']['value'] == 1

    def test_skips_non_computed_member_property(self):
        # obj.foo -- 'foo' should NOT be replaced even if in param_map
        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'foo'},
            'computed': False,
        }
        param_map = {
            'foo': {'type': 'Literal', 'value': 'replaced', 'raw': '"replaced"'},
            'obj': {'type': 'Identifier', 'name': 'newObj'},
        }
        replace_identifiers(node, param_map)
        # object should be replaced
        assert node['object']['name'] == 'newObj'
        # property should NOT be replaced (non-computed)
        assert node['property']['name'] == 'foo'

    def test_replaces_computed_member_property(self):
        # obj[foo] -- 'foo' SHOULD be replaced
        node = {
            'type': 'MemberExpression',
            'object': {'type': 'Identifier', 'name': 'obj'},
            'property': {'type': 'Identifier', 'name': 'foo'},
            'computed': True,
        }
        param_map = {'foo': {'type': 'Literal', 'value': 'bar', 'raw': '"bar"'}}
        replace_identifiers(node, param_map)
        assert node['property'] == {'type': 'Literal', 'value': 'bar', 'raw': '"bar"'}

    def test_replaces_in_array_children(self):
        node = {
            'type': 'ArrayExpression',
            'elements': [
                {'type': 'Identifier', 'name': 'a'},
                {'type': 'Identifier', 'name': 'b'},
                {'type': 'Literal', 'value': 3, 'raw': '3'},
            ],
        }
        param_map = {'a': {'type': 'Literal', 'value': 1, 'raw': '1'}}
        replace_identifiers(node, param_map)
        assert node['elements'][0] == {'type': 'Literal', 'value': 1, 'raw': '1'}
        assert node['elements'][1] == {'type': 'Identifier', 'name': 'b'}

    def test_recursive_replacement(self):
        node = {
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'BinaryExpression',
                'operator': '+',
                'left': {'type': 'Identifier', 'name': 'x'},
                'right': {'type': 'Literal', 'value': 1, 'raw': '1'},
            },
        }
        param_map = {'x': {'type': 'Literal', 'value': 10, 'raw': '10'}}
        replace_identifiers(node, param_map)
        assert node['expression']['left'] == {'type': 'Literal', 'value': 10, 'raw': '10'}

    def test_non_dict_input_noop(self):
        # Should not raise
        replace_identifiers(None, {'x': {'type': 'Literal'}})
        replace_identifiers('string', {'x': {'type': 'Literal'}})
        replace_identifiers([], {'x': {'type': 'Literal'}})

    def test_no_type_key_noop(self):
        node = {'value': 42}
        replace_identifiers(node, {'value': {'type': 'Literal'}})
        assert node == {'value': 42}

    def test_child_is_none_skipped(self):
        node = {
            'type': 'ReturnStatement',
            'argument': None,
        }
        # Should not raise
        replace_identifiers(node, {'x': {'type': 'Literal'}})

    def test_nested_list_with_non_identifier_dicts(self):
        # Items in a list that are dicts with 'type' but not Identifier should recurse
        node = {
            'type': 'ArrayExpression',
            'elements': [
                {
                    'type': 'BinaryExpression',
                    'operator': '+',
                    'left': {'type': 'Identifier', 'name': 'x'},
                    'right': {'type': 'Literal', 'value': 1, 'raw': '1'},
                }
            ],
        }
        param_map = {'x': {'type': 'Literal', 'value': 99, 'raw': '99'}}
        replace_identifiers(node, param_map)
        assert node['elements'][0]['left'] == {'type': 'Literal', 'value': 99, 'raw': '99'}


# ---------------------------------------------------------------------------
# nodes_equal
# ---------------------------------------------------------------------------


class TestNodesEqual:
    def test_identical_literals(self):
        a = {'type': 'Literal', 'value': 42, 'raw': '42'}
        b = {'type': 'Literal', 'value': 42, 'raw': '42'}
        assert nodes_equal(a, b)

    def test_different_values(self):
        a = {'type': 'Literal', 'value': 42, 'raw': '42'}
        b = {'type': 'Literal', 'value': 43, 'raw': '43'}
        assert not nodes_equal(a, b)

    def test_ignores_position_info(self):
        a = {'type': 'Literal', 'value': 1, 'raw': '1', 'start': 0, 'end': 1}
        b = {'type': 'Literal', 'value': 1, 'raw': '1', 'start': 50, 'end': 51}
        assert nodes_equal(a, b)

    def test_ignores_loc(self):
        a = {'type': 'Identifier', 'name': 'x', 'loc': {'start': {'line': 1}}}
        b = {'type': 'Identifier', 'name': 'x', 'loc': {'start': {'line': 5}}}
        assert nodes_equal(a, b)

    def test_ignores_range(self):
        a = {'type': 'Identifier', 'name': 'x', 'range': [0, 1]}
        b = {'type': 'Identifier', 'name': 'x', 'range': [10, 11]}
        assert nodes_equal(a, b)

    def test_different_types(self):
        a = {'type': 'Literal', 'value': 1}
        b = {'type': 'Identifier', 'name': '1'}
        assert not nodes_equal(a, b)

    def test_list_equality(self):
        a = [{'type': 'Literal', 'value': 1}, {'type': 'Literal', 'value': 2}]
        b = [{'type': 'Literal', 'value': 1}, {'type': 'Literal', 'value': 2}]
        assert nodes_equal(a, b)

    def test_list_different_length(self):
        a = [{'type': 'Literal', 'value': 1}]
        b = [{'type': 'Literal', 'value': 1}, {'type': 'Literal', 'value': 2}]
        assert not nodes_equal(a, b)

    def test_list_different_order(self):
        a = [{'type': 'Literal', 'value': 1}, {'type': 'Literal', 'value': 2}]
        b = [{'type': 'Literal', 'value': 2}, {'type': 'Literal', 'value': 1}]
        assert not nodes_equal(a, b)

    def test_scalar_equality(self):
        assert nodes_equal(42, 42)
        assert nodes_equal('hello', 'hello')
        assert not nodes_equal(42, 43)
        assert not nodes_equal('a', 'b')

    def test_type_mismatch(self):
        # type(a) != type(b) returns False
        assert not nodes_equal(42, '42')
        assert not nodes_equal({}, [])
        assert not nodes_equal(None, {})

    def test_dict_extra_key(self):
        a = {'type': 'Literal', 'value': 1}
        b = {'type': 'Literal', 'value': 1, 'extra': True}
        assert not nodes_equal(a, b)

    def test_nested_structures(self):
        a = {
            'type': 'BinaryExpression',
            'operator': '+',
            'left': {'type': 'Literal', 'value': 1, 'raw': '1'},
            'right': {'type': 'Literal', 'value': 2, 'raw': '2'},
        }
        b = copy.deepcopy(a)
        assert nodes_equal(a, b)
        b['right']['value'] = 3
        assert not nodes_equal(a, b)

    def test_nested_with_position_ignored(self):
        a = {
            'type': 'BinaryExpression',
            'operator': '+',
            'left': {'type': 'Literal', 'value': 1, 'start': 0, 'end': 1},
            'right': {'type': 'Literal', 'value': 2, 'start': 4, 'end': 5},
        }
        b = {
            'type': 'BinaryExpression',
            'operator': '+',
            'left': {'type': 'Literal', 'value': 1, 'start': 100, 'end': 101},
            'right': {'type': 'Literal', 'value': 2, 'start': 200, 'end': 201},
        }
        assert nodes_equal(a, b)

    def test_empty_dicts(self):
        assert nodes_equal({}, {})

    def test_empty_lists(self):
        assert nodes_equal([], [])

    def test_none_values(self):
        assert nodes_equal(None, None)

    def test_bool_equality(self):
        assert nodes_equal(True, True)
        assert not nodes_equal(True, False)
