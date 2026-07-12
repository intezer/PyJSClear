import pytest

from pyjsclear.parser import parse
from pyjsclear.transforms.base import Transform
from pyjsclear.traverser import build_parent_map


class TestTransformInit:
    def test_stores_ast(self):
        ast = {'type': 'Program'}
        transform = Transform(ast)
        assert transform.ast is ast

    def test_stores_scope_tree(self):
        scope_tree = {'root': True}
        transform = Transform('ast', scope_tree=scope_tree)
        assert transform.scope_tree is scope_tree

    def test_stores_node_scope(self):
        node_scope = {'node': 'scope'}
        transform = Transform('ast', node_scope=node_scope)
        assert transform.node_scope is node_scope

    def test_scope_tree_defaults_to_none(self):
        transform = Transform('ast')
        assert transform.scope_tree is None

    def test_node_scope_defaults_to_none(self):
        transform = Transform('ast')
        assert transform.node_scope is None


class TestTransformExecute:
    def test_raises_not_implemented(self):
        transform = Transform('ast')
        with pytest.raises(NotImplementedError):
            transform.execute()


class TestTransformChangedTracking:
    def test_has_changed_initially_false(self):
        transform = Transform('ast')
        assert transform.has_changed() is False

    def test_set_changed_makes_has_changed_true(self):
        transform = Transform('ast')
        transform.set_changed()
        assert transform.has_changed() is True

    def test_set_changed_is_idempotent(self):
        transform = Transform('ast')
        transform.set_changed()
        transform.set_changed()
        assert transform.has_changed() is True


class TestRecordReplacement:
    def test_find_parent_returns_recorded_entry_without_rebuild(self):
        ast = parse('f(1);')
        transform = Transform(ast)
        cached_map = transform.get_parent_map()

        call = ast['body'][0]['expression']
        replacement = {'type': 'Literal', 'value': 2, 'raw': '2'}
        call['arguments'][0] = replacement
        transform.record_replacement(replacement, call, 'arguments', 0)

        parent, key, index = transform.find_parent(replacement)
        assert parent is call
        assert key == 'arguments'
        assert index == 0
        # The lookup was served by the patched cache, not a full rebuild.
        assert transform._parent_map is cached_map

    def test_noop_when_map_not_built(self):
        ast = parse('f(1);')
        transform = Transform(ast)

        call = ast['body'][0]['expression']
        replacement = {'type': 'Literal', 'value': 2, 'raw': '2'}
        call['arguments'][0] = replacement
        transform.record_replacement(replacement, call, 'arguments', 0)

        assert transform._parent_map is None

    def test_recorded_entry_matches_rebuild_for_list_child(self):
        ast = parse('f(1);')
        transform = Transform(ast)
        transform.get_parent_map()

        call = ast['body'][0]['expression']
        replacement = {'type': 'Literal', 'value': 2, 'raw': '2'}
        call['arguments'][0] = replacement
        transform.record_replacement(replacement, call, 'arguments', 0)

        assert transform.find_parent(replacement) == build_parent_map(ast)[id(replacement)]

    def test_recorded_entry_matches_rebuild_for_dict_child(self):
        ast = parse('x + 1;')
        transform = Transform(ast)
        transform.get_parent_map()

        statement = ast['body'][0]
        replacement = {'type': 'Literal', 'value': 2, 'raw': '2'}
        statement['expression'] = replacement
        transform.record_replacement(replacement, statement, 'expression', None)

        assert transform.find_parent(replacement) == build_parent_map(ast)[id(replacement)]


class TestTransformRebuildScope:
    def test_class_default_is_false(self):
        assert Transform.rebuild_scope is False

    def test_instance_inherits_default(self):
        transform = Transform('ast')
        assert transform.rebuild_scope is False

    def test_subclass_can_override(self):
        class MyTransform(Transform):
            rebuild_scope = True

            def execute(self):
                pass

        assert MyTransform.rebuild_scope is True
        transform = MyTransform('ast')
        assert transform.rebuild_scope is True
