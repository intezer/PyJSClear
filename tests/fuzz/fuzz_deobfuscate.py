#!/usr/bin/env python3
"""Fuzz target for the full pyjsclear deobfuscation pipeline.

This is the highest priority target — it tests the core safety guarantee
that the deobfuscator never crashes on any input.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import bytes_to_js
from conftest_fuzz import run_fuzzer

from pyjsclear import deobfuscate


def TestOneInput(data):
    if len(data) < 2:
        return

    js_code = bytes_to_js(data)

    try:
        result = deobfuscate(js_code, max_iterations=5)
    except SAFE_EXCEPTIONS:
        return

    # Core safety guarantee: result must never be None
    assert result is not None, "deobfuscate() returned None"
    # Result must be a string
    assert isinstance(result, str), f"deobfuscate() returned {type(result)}, expected str"


if __name__ == "__main__":
    run_fuzzer(TestOneInput)
