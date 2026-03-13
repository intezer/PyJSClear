#!/usr/bin/env python3
"""Fuzz target for ExpressionSimplifier in isolation.

Dedicated target because it implements JS type coercion and arithmetic
with many edge-case branches (0/0, 1/0, "" + [], etc.).
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import bytes_to_js
from conftest_fuzz import run_fuzzer

from pyjsclear.generator import generate
from pyjsclear.parser import parse
from pyjsclear.transforms.expression_simplifier import ExpressionSimplifier


def TestOneInput(data: bytes) -> None:
    if len(data) < 2:
        return

    js_code = bytes_to_js(data)

    try:
        ast = parse(js_code)
    except (SyntaxError, RecursionError):
        return

    try:
        transform = ExpressionSimplifier(ast)
        transform.execute()
    except SAFE_EXCEPTIONS:
        return

    try:
        result = generate(ast)
    except SAFE_EXCEPTIONS:
        return

    assert isinstance(result, str), f'generate() returned {type(result)} after ExpressionSimplifier'


if __name__ == '__main__':
    run_fuzzer(TestOneInput)
