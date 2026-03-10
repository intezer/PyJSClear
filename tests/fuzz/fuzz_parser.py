#!/usr/bin/env python3
"""Fuzz target for the pyjsclear parser."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import bytes_to_js
from conftest_fuzz import run_fuzzer

from pyjsclear.parser import parse


def TestOneInput(data):
    if len(data) < 1:
        return

    code = bytes_to_js(data)

    try:
        result = parse(code)
    except SyntaxError:
        # Expected for invalid JS
        return
    except SAFE_EXCEPTIONS:
        return

    # Successful parse must return a Program or Module dict
    assert isinstance(result, dict), f"parse() returned {type(result)}, expected dict"
    assert result.get("type") in ("Program", "Module"), f"Unexpected root type: {result.get('type')}"


if __name__ == "__main__":
    run_fuzzer(TestOneInput)
