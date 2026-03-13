#!/usr/bin/env python3
"""Fuzz target for the pyjsclear code generator.

Two modes:
1. Roundtrip: parse valid JS -> generate -> assert string output
2. Synthetic AST: random AST dict -> generate -> handle expected errors
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import FuzzedDataProvider
from conftest_fuzz import bytes_to_ast_dict
from conftest_fuzz import bytes_to_js
from conftest_fuzz import run_fuzzer

from pyjsclear.generator import generate
from pyjsclear.parser import parse


def TestOneInput(data: bytes) -> None:
    if len(data) < 4:
        return

    fdp = FuzzedDataProvider(data)
    mode = fdp.ConsumeIntInRange(0, 1)

    if mode == 0:
        # Roundtrip: parse then generate
        code = bytes_to_js(fdp.ConsumeBytes(fdp.remaining_bytes()))
        try:
            ast = parse(code)
        except (SyntaxError, RecursionError):
            return

        try:
            result = generate(ast)
        except SAFE_EXCEPTIONS:
            return

        assert isinstance(result, str), f'generate() returned {type(result)}, expected str'
    else:
        # Synthetic AST: test with malformed input
        remaining = fdp.ConsumeBytes(fdp.remaining_bytes())
        ast = bytes_to_ast_dict(remaining)

        try:
            result = generate(ast)
        except (KeyError, TypeError, AttributeError, ValueError):
            return
        except SAFE_EXCEPTIONS:
            return

        assert isinstance(result, str), f'generate() returned {type(result)}, expected str'


if __name__ == '__main__':
    run_fuzzer(TestOneInput)
