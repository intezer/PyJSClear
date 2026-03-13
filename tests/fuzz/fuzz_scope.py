#!/usr/bin/env python3
"""Fuzz target for scope analysis."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import bytes_to_js
from conftest_fuzz import run_fuzzer

from pyjsclear.parser import parse
from pyjsclear.scope import build_scope_tree


def TestOneInput(data: bytes) -> None:
    if len(data) < 2:
        return

    js_code = bytes_to_js(data)

    try:
        ast = parse(js_code)
    except (SyntaxError, RecursionError):
        return

    try:
        root_scope, node_scope_map = build_scope_tree(ast)
    except SAFE_EXCEPTIONS:
        return

    assert root_scope is not None, 'build_scope_tree returned None root_scope'
    assert isinstance(node_scope_map, dict), f'node_scope_map is {type(node_scope_map)}, expected dict'


if __name__ == '__main__':
    run_fuzzer(TestOneInput)
