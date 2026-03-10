"""Unit tests for pyjsclear.traverser module."""

import pytest

from pyjsclear.parser import parse
from pyjsclear.traverser import REMOVE
from pyjsclear.traverser import SKIP
from pyjsclear.traverser import collect_nodes
from pyjsclear.traverser import find_parent
from pyjsclear.traverser import remove_from_parent
from pyjsclear.traverser import replace_in_parent
from pyjsclear.traverser import simple_traverse
from pyjsclear.traverser import traverse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_program(*statements):
    """Build a minimal Program AST with given body statements."""
    return {'type': 'Program', 'sourceType': 'script', 'body': list(statements)}


def _var_decl(name, value):
    """Build a VariableDeclaration: var <name> = <value>;"""
    return {
        'type': 'VariableDeclaration',
        'declarations': [
            {
                'type': 'VariableDeclarator',
                'id': {'type': 'Identifier', 'name': name},
                'init': {'type': 'Literal', 'value': value, 'raw': str(value)},
            }
        ],
        'kind': 'var',
    }


def _expr_stmt(expression):
    return {'type': 'ExpressionStatement', 'expression': expression}


def _literal(value):
    return {'type': 'Literal', 'value': value, 'raw': str(value)}


def _identifier(name):
    return {'type': 'Identifier', 'name': name}


# ===========================================================================
# 1. traverse enter/exit ordering
# ===========================================================================


class TestTraverseEnterExit:
    def test_enter_before_children_exit_after(self):
        """Enter is called on parent before children; exit after children."""
        ast = parse('var x = 1;')
        log = []

        def enter(node, parent, key, index):
            log.append(('enter', node['type']))

        def exit_(node, parent, key, index):
            log.append(('exit', node['type']))

        traverse(ast, {'enter': enter, 'exit': exit_})

        # Program entered first
        assert log[0] == ('enter', 'Program')
        # Program exited last
        assert log[-1] == ('exit', 'Program')

        # VariableDeclaration entered before its children
        enter_vd = log.index(('enter', 'VariableDeclaration'))
        enter_vdtor = log.index(('enter', 'VariableDeclarator'))
        exit_vdtor = log.index(('exit', 'VariableDeclarator'))
        exit_vd = log.index(('exit', 'VariableDeclaration'))
        assert enter_vd < enter_vdtor < exit_vdtor < exit_vd

    def test_multiple_statements_order(self):
        """Statements are visited in body order."""
        ast = parse('var a = 1; var b = 2;')
        entered = []

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration':
                # grab the declared name
                name = node['declarations'][0]['id']['name']
                entered.append(name)

        traverse(ast, {'enter': enter})
        assert entered == ['a', 'b']


# ===========================================================================
# 2. REMOVE sentinel
# ===========================================================================


class TestRemove:
    def test_remove_from_body_array(self):
        """Returning REMOVE from enter removes a node from parent array."""
        ast = parse('var a = 1; var b = 2; var c = 3;')

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration' and node['declarations'][0]['id']['name'] == 'b':
                return REMOVE

        traverse(ast, {'enter': enter})
        names = [s['declarations'][0]['id']['name'] for s in ast['body']]
        assert names == ['a', 'c']

    def test_remove_single_child_sets_none(self):
        """Returning REMOVE for a single-child slot sets it to None."""
        # var x = 1;  ->  init is a single child of VariableDeclarator
        ast = parse('var x = 1;')

        def enter(node, parent, key, index):
            if node['type'] == 'Literal':
                return REMOVE

        traverse(ast, {'enter': enter})
        init_val = ast['body'][0]['declarations'][0]['init']
        assert init_val is None

    def test_remove_from_exit(self):
        """REMOVE returned from exit also removes the node."""
        ast = parse('var a = 1; var b = 2;')

        def exit_(node, parent, key, index):
            if node['type'] == 'VariableDeclaration' and node['declarations'][0]['id']['name'] == 'a':
                return REMOVE

        traverse(ast, {'exit': exit_})
        names = [s['declarations'][0]['id']['name'] for s in ast['body']]
        assert names == ['b']


# ===========================================================================
# 3. SKIP sentinel
# ===========================================================================


class TestSkip:
    def test_skip_prevents_child_traversal(self):
        """Returning SKIP from enter skips children."""
        ast = parse('var x = 1;')
        entered_types = []

        def enter(node, parent, key, index):
            entered_types.append(node['type'])
            if node['type'] == 'VariableDeclaration':
                return SKIP

        traverse(ast, {'enter': enter})
        # VariableDeclarator should NOT have been entered
        assert 'VariableDeclarator' not in entered_types
        assert 'Literal' not in entered_types

    def test_skip_still_calls_exit(self):
        """SKIP from enter still triggers exit for that node."""
        ast = parse('var x = 1;')
        exit_types = []

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration':
                return SKIP

        def exit_(node, parent, key, index):
            exit_types.append(node['type'])

        traverse(ast, {'enter': enter, 'exit': exit_})
        assert 'VariableDeclaration' in exit_types
        # Children should not appear in exit either
        assert 'VariableDeclarator' not in exit_types


# ===========================================================================
# 4. Node replacement
# ===========================================================================


class TestNodeReplacement:
    def test_replace_node_from_enter(self):
        """Returning a new dict with 'type' from enter replaces the node."""
        ast = parse('var x = 1;')

        replacement = {'type': 'Literal', 'value': 42, 'raw': '42'}

        def enter(node, parent, key, index):
            if node['type'] == 'Literal' and node.get('value') == 1:
                return replacement

        traverse(ast, {'enter': enter})
        init = ast['body'][0]['declarations'][0]['init']
        assert init['value'] == 42

    def test_replace_node_in_array_from_enter(self):
        """Replacement works for nodes within an array (body)."""
        ast = parse('var a = 1; var b = 2;')

        empty_stmt = {'type': 'EmptyStatement'}

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration' and node['declarations'][0]['id']['name'] == 'a':
                return empty_stmt

        traverse(ast, {'enter': enter})
        assert ast['body'][0]['type'] == 'EmptyStatement'
        # Second statement is untouched
        assert ast['body'][1]['type'] == 'VariableDeclaration'

    def test_replace_node_from_exit(self):
        """Returning a new node from exit replaces the node."""
        ast = parse('var x = 1;')

        replacement = {'type': 'Literal', 'value': 99, 'raw': '99'}

        def exit_(node, parent, key, index):
            if node['type'] == 'Literal' and node.get('value') == 1:
                return replacement

        traverse(ast, {'exit': exit_})
        init = ast['body'][0]['declarations'][0]['init']
        assert init['value'] == 99

    def test_skip_then_replace_in_exit(self):
        """SKIP + exit replacement: exit can replace the skipped node."""
        ast = parse('var x = 1;')

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration':
                return SKIP

        empty_stmt = {'type': 'EmptyStatement'}

        def exit_(node, parent, key, index):
            if node['type'] == 'VariableDeclaration':
                return empty_stmt

        traverse(ast, {'enter': enter, 'exit': exit_})
        assert ast['body'][0]['type'] == 'EmptyStatement'

    def test_skip_then_remove_in_exit(self):
        """SKIP + REMOVE from exit removes the node."""
        ast = parse('var a = 1; var b = 2;')

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration' and node['declarations'][0]['id']['name'] == 'a':
                return SKIP

        def exit_(node, parent, key, index):
            if node['type'] == 'VariableDeclaration' and node['declarations'][0]['id']['name'] == 'a':
                return REMOVE

        traverse(ast, {'enter': enter, 'exit': exit_})
        assert len(ast['body']) == 1
        assert ast['body'][0]['declarations'][0]['id']['name'] == 'b'


# ===========================================================================
# 5. Visitor as dict or object
# ===========================================================================


class TestVisitorForms:
    def test_visitor_as_dict(self):
        ast = parse('var x = 1;')
        called = []

        traverse(ast, {'enter': lambda n, p, k, i: called.append(n['type'])})
        assert 'Program' in called

    def test_visitor_as_object(self):
        ast = parse('var x = 1;')
        called = []

        class Visitor:
            def enter(self, node, parent, key, index):
                called.append(node['type'])

        traverse(ast, Visitor())
        assert 'Program' in called

    def test_visitor_object_with_exit_only(self):
        ast = parse('var x = 1;')
        exited = []

        class Visitor:
            def exit(self, node, parent, key, index):
                exited.append(node['type'])

        traverse(ast, Visitor())
        assert 'Program' in exited

    def test_visitor_dict_with_no_enter(self):
        """Dict visitor with only exit still works."""
        ast = parse('var x = 1;')
        exited = []

        traverse(ast, {'exit': lambda n, p, k, i: exited.append(n['type'])})
        assert 'Program' in exited


# ===========================================================================
# 6. simple_traverse
# ===========================================================================


class TestSimpleTraverse:
    def test_visits_all_nodes(self):
        ast = parse('var x = 1;')
        types = []

        simple_traverse(ast, lambda node, parent: types.append(node['type']))
        assert 'Program' in types
        assert 'VariableDeclaration' in types
        assert 'VariableDeclarator' in types
        assert 'Identifier' in types
        assert 'Literal' in types

    def test_callback_receives_parent(self):
        ast = parse('var x = 1;')
        parent_map = {}

        def cb(node, parent):
            parent_map[node['type']] = parent

        simple_traverse(ast, cb)
        # Program has no parent
        assert parent_map['Program'] is None
        # VariableDeclaration's parent is Program
        assert parent_map['VariableDeclaration'] is ast

    def test_visits_nested_structure(self):
        """Traverses through function bodies and nested expressions."""
        ast = parse('function foo() { return 1 + 2; }')
        types = []
        simple_traverse(ast, lambda n, p: types.append(n['type']))
        assert 'FunctionDeclaration' in types
        assert 'ReturnStatement' in types
        assert 'BinaryExpression' in types

    def test_skips_non_node_children(self):
        """Nodes without 'type' or non-dict children are skipped gracefully."""
        # A hand-crafted node with a non-dict child value
        ast = {
            'type': 'Program',
            'sourceType': 'script',
            'body': [],
        }
        visited = []
        simple_traverse(ast, lambda n, p: visited.append(n['type']))
        assert visited == ['Program']


# ===========================================================================
# 7. collect_nodes
# ===========================================================================


class TestCollectNodes:
    def test_collect_identifiers(self):
        ast = parse('var x = y;')
        ids = collect_nodes(ast, 'Identifier')
        names = {n['name'] for n in ids}
        assert 'x' in names
        assert 'y' in names

    def test_collect_literals(self):
        ast = parse('var a = 1; var b = 2;')
        lits = collect_nodes(ast, 'Literal')
        values = {n['value'] for n in lits}
        assert values == {1, 2}

    def test_collect_nonexistent_type(self):
        ast = parse('var x = 1;')
        result = collect_nodes(ast, 'WhileStatement')
        assert result == []

    def test_collect_deeply_nested(self):
        ast = parse('function f() { if (true) { return 42; } }')
        lits = collect_nodes(ast, 'Literal')
        values = [n['value'] for n in lits]
        assert True in values
        assert 42 in values


# ===========================================================================
# 8. find_parent
# ===========================================================================


class TestFindParent:
    def test_find_parent_in_array(self):
        """Node in an array slot returns the correct parent, key, and index."""
        ast = parse('var a = 1; var b = 2;')
        target = ast['body'][1]  # second VariableDeclaration
        result = find_parent(ast, target)
        assert result is not None
        parent, key, index = result
        assert parent is ast
        assert key == 'body'
        assert index == 1

    def test_find_parent_single_child(self):
        """Node in a single-child slot returns None for index."""
        ast = parse('var x = 1;')
        init_node = ast['body'][0]['declarations'][0]['init']
        result = find_parent(ast, init_node)
        assert result is not None
        parent, key, index = result
        assert parent is ast['body'][0]['declarations'][0]
        assert key == 'init'
        assert index is None

    def test_find_parent_returns_none_if_not_found(self):
        ast = parse('var x = 1;')
        stranger = {'type': 'Literal', 'value': 999, 'raw': '999'}
        result = find_parent(ast, stranger)
        assert result is None

    def test_find_parent_root_node(self):
        """The root node itself has no parent."""
        ast = parse('var x = 1;')
        result = find_parent(ast, ast)
        assert result is None

    def test_find_parent_identifier_in_declarator(self):
        ast = parse('var x = 1;')
        id_node = ast['body'][0]['declarations'][0]['id']
        result = find_parent(ast, id_node)
        parent, key, index = result
        assert parent is ast['body'][0]['declarations'][0]
        assert key == 'id'
        assert index is None


# ===========================================================================
# 9. replace_in_parent
# ===========================================================================


class TestReplaceInParent:
    def test_replace_in_array(self):
        ast = parse('var a = 1; var b = 2;')
        parent = ast
        new_node = {'type': 'EmptyStatement'}
        replace_in_parent(parent, 'body', 0, new_node)
        assert ast['body'][0] is new_node
        assert ast['body'][1]['type'] == 'VariableDeclaration'

    def test_replace_single_child(self):
        ast = parse('var x = 1;')
        declarator = ast['body'][0]['declarations'][0]
        new_init = {'type': 'Literal', 'value': 42, 'raw': '42'}
        replace_in_parent(declarator, 'init', None, new_init)
        assert declarator['init'] is new_init
        assert declarator['init']['value'] == 42


# ===========================================================================
# 10. remove_from_parent
# ===========================================================================


class TestRemoveFromParent:
    def test_remove_from_array_pops(self):
        ast = parse('var a = 1; var b = 2; var c = 3;')
        assert len(ast['body']) == 3
        remove_from_parent(ast, 'body', 1)
        assert len(ast['body']) == 2
        names = [s['declarations'][0]['id']['name'] for s in ast['body']]
        assert names == ['a', 'c']

    def test_remove_single_child_sets_none(self):
        ast = parse('var x = 1;')
        declarator = ast['body'][0]['declarations'][0]
        assert declarator['init'] is not None
        remove_from_parent(declarator, 'init', None)
        assert declarator['init'] is None


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    def test_traverse_node_without_type_is_skipped(self):
        """A node missing 'type' is returned as-is and not traversed."""
        ast = {'no_type': True}
        called = []
        traverse(ast, {'enter': lambda n, p, k, i: called.append(True)})
        assert called == []

    def test_traverse_empty_body(self):
        """Traversing a program with empty body does not crash."""
        ast = {'type': 'Program', 'sourceType': 'script', 'body': []}
        entered = []
        traverse(ast, {'enter': lambda n, p, k, i: entered.append(n['type'])})
        assert entered == ['Program']

    def test_remove_adjusts_iteration_index(self):
        """Removing nodes during traversal does not skip siblings."""
        ast = parse('var a = 1; var b = 2; var c = 3;')
        removed = []

        def enter(node, parent, key, index):
            if node['type'] == 'VariableDeclaration':
                removed.append(node['declarations'][0]['id']['name'])
                return REMOVE

        traverse(ast, {'enter': enter})
        # All three should be visited and removed
        assert set(removed) == {'a', 'b', 'c'}
        assert ast['body'] == []

    def test_replacement_continues_traversal_into_new_node(self):
        """After replacement, traversal descends into the new node's children.

        When enter returns a replacement, the current node is swapped but enter
        is NOT re-invoked on the replacement itself.  However, the replacement's
        children ARE traversed, so they should appear in the log.
        """
        ast = parse('var x = 1;')
        entered_types = []

        def enter(node, parent, key, index):
            entered_types.append(node['type'])
            # Replace the VariableDeclaration with a new ExpressionStatement
            if node['type'] == 'VariableDeclaration':
                return _expr_stmt(_literal(99))

        traverse(ast, {'enter': enter})
        # The replacement's child Literal(99) should be entered
        assert 'Literal' in entered_types
        # The replacement node's body is stored in the AST
        assert ast['body'][0]['type'] == 'ExpressionStatement'
        assert ast['body'][0]['expression']['value'] == 99


# ===========================================================================
# Coverage gap tests
# ===========================================================================


class TestSimpleTraverseNoneType:
    """Line 115: simple_traverse with node where type is None."""

    def test_node_with_none_type(self):
        node = {'type': None, 'body': []}
        visited = []
        simple_traverse(node, lambda n, p: visited.append(n.get('type')))
        # Should not visit the node since type is None
        assert visited == []


class TestSimpleTraverseFallbackChildKeys:
    """Line 119: simple_traverse fallback child_keys for unknown node type."""

    def test_unknown_node_type_fallback(self):
        # A node with an unknown type should trigger the fallback get_child_keys
        # Note: the fallback skips 'expression' for non-ExpressionStatement, so use 'argument'
        node = {
            'type': 'Program',
            'sourceType': 'script',
            'body': [
                {
                    'type': 'CustomUnknownStatement',
                    'argument': {'type': 'Identifier', 'name': 'x'},
                }
            ],
        }
        visited = []
        simple_traverse(node, lambda n, p: visited.append(n.get('type')))
        assert 'Program' in visited
        assert 'CustomUnknownStatement' in visited
        # The fallback child_keys should find the 'argument' child
        assert 'Identifier' in visited


class TestFindParentNonDictNode:
    """Line 160: find_parent with non-dict node in tree."""

    def test_find_parent_skips_non_dict_children(self):
        # Build an AST where some child values are not dicts
        ast = {
            'type': 'Program',
            'sourceType': 'script',
            'body': [
                'not a dict',
                42,
                None,
                {'type': 'ExpressionStatement', 'expression': {'type': 'Identifier', 'name': 'x'}},
            ],
        }
        target = ast['body'][3]['expression']
        result = find_parent(ast, target)
        assert result is not None
        parent, key, index = result
        assert parent is ast['body'][3]
        assert key == 'expression'
        assert index is None

    def test_find_parent_with_string_in_list(self):
        # Ensure find_parent handles non-dict items in lists gracefully
        target = {'type': 'Literal', 'value': 1}
        ast = {
            'type': 'Program',
            'sourceType': 'script',
            'body': [
                {
                    'type': 'ExpressionStatement',
                    'expression': target,
                    'extra': 'string_value',
                }
            ],
        }
        result = find_parent(ast, target)
        assert result is not None
        parent, key, index = result
        assert parent is ast['body'][0]
        assert key == 'expression'


class TestTraverseFallbackChildKeys:
    """Line 68-69: traverse with unknown node type triggers fallback child_keys."""

    def test_traverse_unknown_node_type(self):
        ast = {
            'type': 'Program',
            'sourceType': 'script',
            'body': [
                {
                    'type': 'UnknownCustomNode',
                    'argument': {'type': 'Identifier', 'name': 'x'},
                }
            ],
        }
        visited = []
        traverse(ast, {'enter': lambda n, p, k, i: visited.append(n['type'])})
        assert 'Program' in visited
        assert 'UnknownCustomNode' in visited
        assert 'Identifier' in visited
