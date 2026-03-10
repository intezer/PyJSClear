#!/usr/bin/env python3
"""Fuzz target for string decoders (base64, RC4).

Tests base64_transform(), BasicStringDecoder, Base64StringDecoder, Rc4StringDecoder
with random arrays, keys, and indices.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import FuzzedDataProvider
from conftest_fuzz import run_fuzzer

from pyjsclear.utils.string_decoders import Base64StringDecoder
from pyjsclear.utils.string_decoders import BasicStringDecoder
from pyjsclear.utils.string_decoders import Rc4StringDecoder
from pyjsclear.utils.string_decoders import base64_transform


def TestOneInput(data):
    if len(data) < 8:
        return

    fdp = FuzzedDataProvider(data)
    decoder_choice = fdp.ConsumeIntInRange(0, 3)

    if decoder_choice == 0:
        # Test base64_transform with random strings
        encoded = fdp.ConsumeUnicode(1024)
        try:
            result = base64_transform(encoded)
        except SAFE_EXCEPTIONS:
            return
        assert isinstance(result, str), f"base64_transform returned {type(result)}"

    elif decoder_choice == 1:
        # Test BasicStringDecoder
        num_strings = fdp.ConsumeIntInRange(0, 20)
        string_array = [fdp.ConsumeUnicode(64) for _ in range(num_strings)]
        offset = fdp.ConsumeIntInRange(-5, 5)
        decoder = BasicStringDecoder(string_array, offset)
        if num_strings > 0:
            idx = fdp.ConsumeIntInRange(-2, num_strings * 2)
            try:
                result = decoder.get_string(idx)
            except SAFE_EXCEPTIONS:
                return
            # None is valid for out-of-range indices
            if result is not None:
                assert isinstance(result, str), f"BasicStringDecoder returned {type(result)}"

    elif decoder_choice == 2:
        # Test Base64StringDecoder
        num_strings = fdp.ConsumeIntInRange(0, 20)
        string_array = [fdp.ConsumeUnicode(64) for _ in range(num_strings)]
        offset = fdp.ConsumeIntInRange(-5, 5)
        decoder = Base64StringDecoder(string_array, offset)
        if num_strings > 0:
            idx = fdp.ConsumeIntInRange(-2, num_strings * 2)
            try:
                result = decoder.get_string(idx)
            except SAFE_EXCEPTIONS:
                return
            # None is valid for out-of-range indices
            if result is not None:
                assert isinstance(result, str), f"Base64StringDecoder returned {type(result)}"

    elif decoder_choice == 3:
        # Test Rc4StringDecoder - potential ZeroDivisionError with empty key
        num_strings = fdp.ConsumeIntInRange(0, 20)
        string_array = [fdp.ConsumeUnicode(64) for _ in range(num_strings)]
        offset = fdp.ConsumeIntInRange(-5, 5)
        decoder = Rc4StringDecoder(string_array, offset)
        if num_strings > 0:
            idx = fdp.ConsumeIntInRange(-2, num_strings * 2)
            key = fdp.ConsumeUnicode(32)  # May be empty - tests empty key guard
            try:
                result = decoder.get_string(idx, key=key)
            except SAFE_EXCEPTIONS:
                return
            # None is valid for out-of-range or None key
            if result is not None:
                assert isinstance(result, str), f"Rc4StringDecoder returned {type(result)}"


if __name__ == "__main__":
    run_fuzzer(TestOneInput)
