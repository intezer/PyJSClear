#!/usr/bin/env python3
"""Fuzz target for AST traversal.

Tests traverse() and simple_traverse() with synthetic ASTs and
visitors that return REMOVE/SKIP/replacement.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import FuzzedDataProvider
from conftest_fuzz import bytes_to_ast_dict
from conftest_fuzz import run_fuzzer

from pyjsclear.traverser import REMOVE
from pyjsclear.traverser import SKIP
from pyjsclear.traverser import simple_traverse
from pyjsclear.traverser import traverse


MAX_VISITED = 10_000


def TestOneInput(data: bytes) -> None:
    if len(data) < 8:
        return

    fdp = FuzzedDataProvider(data)
    mode = fdp.ConsumeIntInRange(0, 2)
    remaining = fdp.ConsumeBytes(fdp.remaining_bytes())
    ast = bytes_to_ast_dict(remaining)

    visited = 0

    match mode:
        case 0:
            action_byte = remaining[0] if remaining else 0

            def enter(node, parent, key, index):
                nonlocal visited
                visited += 1
                if visited > MAX_VISITED:
                    return SKIP
                if isinstance(node, dict) and node.get('type') == 'Literal' and action_byte % 3 == 0:
                    return SKIP
                return None

            try:
                traverse(ast, {'enter': enter})
            except SAFE_EXCEPTIONS:
                return

        case 1:
            action_byte = remaining[1] if len(remaining) > 1 else 0

            def enter(node, parent, key, index):
                nonlocal visited
                visited += 1
                if visited > MAX_VISITED:
                    return SKIP
                if isinstance(node, dict) and node.get('type') == 'EmptyStatement' and action_byte % 2 == 0:
                    return REMOVE
                return None

            try:
                traverse(ast, {'enter': enter})
            except SAFE_EXCEPTIONS:
                return

        case 2:
            def callback(node, parent):
                nonlocal visited
                visited += 1
                if visited > MAX_VISITED:
                    raise StopIteration('too many nodes')

            try:
                simple_traverse(ast, callback)
            except (StopIteration, SAFE_EXCEPTIONS[0]):
                return


if __name__ == '__main__':
    run_fuzzer(TestOneInput)
