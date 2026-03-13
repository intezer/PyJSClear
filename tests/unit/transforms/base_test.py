import pytest

from pyjsclear.transforms.base import Transform


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
