"""Tests for incremental parent-map maintenance across transform call sites (TKT-16478).

Transforms replace nodes in place while iterating; each replacement calls
record_replacement() to patch the cached parent map in O(1) instead of
invalidate_parent_map(), which would force a full O(N) rebuild on the next
find_parent lookup -- quadratic overall when many nodes are replaced in one
pass. These tests assert the observable effect: build_parent_map() is called
at most once per transform execution, no matter how many nodes it replaces.
"""

from unittest.mock import patch

from pyjsclear.parser import parse
from pyjsclear.transforms.class_static_resolver import ClassStaticResolver
from pyjsclear.transforms.object_simplifier import ObjectSimplifier
from pyjsclear.transforms.string_revealer import StringRevealer
from pyjsclear.traverser import build_parent_map


_REFERENCE_COUNT = 200


class TestObjectSimplifierIncrementalParentMap:
    def test_build_parent_map_called_once_when_many_properties_are_inlined(self):
        # Arrange
        properties = ', '.join(f'k{i}: {i}' for i in range(_REFERENCE_COUNT))
        accesses = '; '.join(f'console.log(o.k{i})' for i in range(_REFERENCE_COUNT))
        ast = parse(f'const o = {{{properties}}}; {accesses};')
        transform = ObjectSimplifier(ast)

        # Act
        with patch('pyjsclear.transforms.base.build_parent_map', wraps=build_parent_map) as mock_build_parent_map:
            changed = transform.execute()

        # Assert
        assert changed is True
        assert mock_build_parent_map.call_count == 1


class TestStringRevealerIncrementalParentMap:
    def test_build_parent_map_called_once_when_many_array_accesses_are_replaced(self):
        # Arrange
        elements = ', '.join(f'"s{i}"' for i in range(_REFERENCE_COUNT))
        accesses = '; '.join(f'f(arr[{i}])' for i in range(_REFERENCE_COUNT))
        ast = parse(f'var arr = [{elements}]; {accesses};')
        transform = StringRevealer(ast)

        # Act
        with patch('pyjsclear.transforms.base.build_parent_map', wraps=build_parent_map) as mock_build_parent_map:
            changed = transform.execute()

        # Assert
        assert changed is True
        assert mock_build_parent_map.call_count <= 1


class TestClassStaticResolverIncrementalParentMap:
    def test_build_parent_map_called_once_when_many_static_properties_are_inlined(self):
        # Arrange
        accesses = '; '.join(f'console.log(C.X + {i})' for i in range(_REFERENCE_COUNT))
        ast = parse(f'var C = class {{}}; C.X = 100; {accesses};')
        transform = ClassStaticResolver(ast)

        # Act
        with patch('pyjsclear.transforms.base.build_parent_map', wraps=build_parent_map) as mock_build_parent_map:
            changed = transform.execute()

        # Assert
        assert changed is True
        assert mock_build_parent_map.call_count == 1
        # The transform invalidates the cache once the traversal completes,
        # so the next lookup rebuilds fresh rather than reusing stale entries.
        assert transform._parent_map is None
