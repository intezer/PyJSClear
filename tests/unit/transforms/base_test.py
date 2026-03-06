import pytest

from pyjsclear.transforms.base import Transform


class TestTransformInit:
    def test_stores_ast(self):
        ast = {"type": "Program"}
        t = Transform(ast)
        assert t.ast is ast

    def test_stores_scope_tree(self):
        scope_tree = {"root": True}
        t = Transform("ast", scope_tree=scope_tree)
        assert t.scope_tree is scope_tree

    def test_stores_node_scope(self):
        node_scope = {"node": "scope"}
        t = Transform("ast", node_scope=node_scope)
        assert t.node_scope is node_scope

    def test_scope_tree_defaults_to_none(self):
        t = Transform("ast")
        assert t.scope_tree is None

    def test_node_scope_defaults_to_none(self):
        t = Transform("ast")
        assert t.node_scope is None

    def test_changed_defaults_to_false(self):
        t = Transform("ast")
        assert t._changed is False


class TestTransformExecute:
    def test_raises_not_implemented(self):
        t = Transform("ast")
        with pytest.raises(NotImplementedError):
            t.execute()


class TestTransformChangedTracking:
    def test_has_changed_initially_false(self):
        t = Transform("ast")
        assert t.has_changed() is False

    def test_set_changed_makes_has_changed_true(self):
        t = Transform("ast")
        t.set_changed()
        assert t.has_changed() is True

    def test_set_changed_is_idempotent(self):
        t = Transform("ast")
        t.set_changed()
        t.set_changed()
        assert t.has_changed() is True


class TestTransformRebuildScope:
    def test_class_default_is_false(self):
        assert Transform.rebuild_scope is False

    def test_instance_inherits_default(self):
        t = Transform("ast")
        assert t.rebuild_scope is False

    def test_subclass_can_override(self):
        class MyTransform(Transform):
            rebuild_scope = True

            def execute(self):
                pass

        assert MyTransform.rebuild_scope is True
        t = MyTransform("ast")
        assert t.rebuild_scope is True
