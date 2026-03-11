"""Regression tests for the main sample.js deobfuscation.

This file tests the full pipeline against the large esbuild-bundled sample.
It checks both structural properties (output parses, size reasonable, no hex
escapes) and semantic properties (decoded strings appear, modern JS features
used where appropriate).

These tests are designed to catch regressions from transform interactions —
e.g., if a new transform causes proxy function inlining to blow up, or if
an optimization prevents another transform from firing.
"""

import re
from pathlib import Path

import pytest

import pyjsclear
from pyjsclear.parser import parse


SAMPLE_PATH = Path(__file__).parent / 'resources' / 'sample.js'

RE_0X = re.compile(r'\b_0x[0-9a-fA-F]{2,}\b')
RE_HEX_ESCAPE = re.compile(r'\\x[0-9a-fA-F]{2}')
RE_HEX_NUMERIC = re.compile(r'\b0x[0-9a-fA-F]+\b')


@pytest.fixture(scope='module')
def sample_result():
    """Deobfuscate sample.js once for the entire module."""
    code = SAMPLE_PATH.read_text()
    result = pyjsclear.deobfuscate(code)
    return code, result


# ================================================================
# Output validity
# ================================================================


class TestOutputValidity:
    """The output must be valid, parseable JavaScript."""

    def test_output_parses(self, sample_result):
        """Output must be parseable by esprima2."""
        _, result = sample_result
        ast = parse(result)
        assert ast is not None
        assert ast.get('type') == 'Program'

    def test_output_not_empty(self, sample_result):
        _, result = sample_result
        assert len(result.strip()) > 1000

    def test_output_is_multiline(self, sample_result):
        """Output should be pretty-printed, not a single line."""
        _, result = sample_result
        assert len(result.splitlines()) > 100


# ================================================================
# Size and structure invariants
# ================================================================


class TestSizeInvariants:
    """Output size should be reasonable — not bloated, not empty."""

    def test_output_smaller_than_input(self, sample_result):
        code, result = sample_result
        assert len(result) < len(code), f'Output ({len(result)}) should be smaller than input ({len(code)})'

    def test_output_not_too_small(self, sample_result):
        """Output shouldn't lose most of the code — sanity floor."""
        code, result = sample_result
        assert len(result) > len(code) * 0.3, f'Output suspiciously small: {len(result)} < 30% of {len(code)}'

    def test_output_ratio_within_bounds(self, sample_result):
        """Output should be 50–85% of input for this sample."""
        code, result = sample_result
        ratio = len(result) / len(code)
        assert 0.50 < ratio < 0.85, f'Output/input ratio {ratio:.2f} outside expected range 0.50–0.85'

    def test_no_extremely_long_lines(self, sample_result):
        """No line should exceed 2000 chars (proxy inliner blowup guard)."""
        _, result = sample_result
        for i, line in enumerate(result.splitlines(), 1):
            assert len(line) <= 2000, f'Line {i} is {len(line)} chars (max 2000). ' f'Preview: {line[:100]}...'

    def test_few_long_lines(self, sample_result):
        """At most 5 lines over 500 chars."""
        _, result = sample_result
        long_lines = sum(1 for l in result.splitlines() if len(l) > 500)
        assert long_lines <= 5, f'{long_lines} lines > 500 chars'


# ================================================================
# Hex and encoding cleanup
# ================================================================


class TestEncodingCleanup:
    """All hex/encoding artifacts should be cleaned up."""

    def test_no_hex_escapes(self, sample_result):
        _, result = sample_result
        count = len(RE_HEX_ESCAPE.findall(result))
        assert count == 0, f'{count} hex escapes remain'

    def test_no_hex_numeric_literals(self, sample_result):
        _, result = sample_result
        count = len(RE_HEX_NUMERIC.findall(result))
        assert count == 0, f'{count} hex numeric literals remain (0x...)'


# ================================================================
# Decoded string content (semantic correctness)
# ================================================================


class TestDecodedStrings:
    """Known strings that should appear in the deobfuscated output."""

    @pytest.mark.parametrize(
        'expected_string',
        [
            'require',
            'path',
            'crypto',
            'Buffer',
            'toString',
            'exports',
            'function',
            'return',
            'const',
        ],
    )
    def test_known_strings_present(self, sample_result, expected_string):
        _, result = sample_result
        assert expected_string in result, f'Expected string {expected_string!r} not found in output'

    def test_require_calls_present(self, sample_result):
        """require() calls should be readable."""
        _, result = sample_result
        assert re.search(r'require\(\s*["\']', result), 'No require("...") calls found'

    def test_string_decode_effective(self, sample_result):
        """_0x identifiers should be significantly reduced vs input."""
        code, result = sample_result
        input_0x = len(RE_0X.findall(code))
        output_0x = len(RE_0X.findall(result))
        reduction_pct = (input_0x - output_0x) / input_0x * 100
        assert reduction_pct > 20, f'Only {reduction_pct:.0f}% _0x reduction ' f'({input_0x} → {output_0x})'


# ================================================================
# Modern JS features (transform-specific checks)
# ================================================================


class TestModernJSFeatures:
    """Transforms should produce modern JS constructs where applicable."""

    def test_has_nullish_coalescing(self, sample_result):
        """NullishCoalescing transform should produce ?? operators."""
        _, result = sample_result
        count = result.count('??')
        assert count > 0, 'No ?? operators found — NullishCoalescing may not be firing'

    def test_has_optional_chaining(self, sample_result):
        """OptionalChaining transform should produce ?. operators."""
        _, result = sample_result
        count = result.count('?.')
        assert count > 0, 'No ?. operators found — OptionalChaining may not be firing'

    def test_has_else_if(self, sample_result):
        """ElseIfFlattener should produce else-if chains."""
        _, result = sample_result
        assert 'else if' in result, 'No else-if found — ElseIfFlattener may not be firing'

    def test_dot_notation_used(self, sample_result):
        """PropertySimplifier should convert bracket to dot notation."""
        _, result = sample_result
        # The output should have more dot accesses than bracket accesses
        dot_count = len(re.findall(r'\w\.\w', result))
        bracket_count = len(re.findall(r'\w\["', result))
        assert dot_count > bracket_count, (
            f'More bracket ({bracket_count}) than dot ({dot_count}) accesses — ' f'PropertySimplifier may not be firing'
        )


# ================================================================
# Regression guards (specific bugs we've caught)
# ================================================================


class TestRegressionGuards:
    """Guards against specific bugs that have occurred in development."""

    def test_no_proxy_inliner_blowup(self, sample_result):
        """Guard against exponential proxy function inlining.

        Bug: OptionalChaining simplified a helper function body below the node
        count threshold, causing ProxyFunctionInliner to inline it. Nested
        calls then caused exponential ternary expansion.
        """
        _, result = sample_result
        max_line_len = max(len(l) for l in result.splitlines())
        assert max_line_len < 2000, f'Max line length {max_line_len} suggests proxy inliner blowup'

    def test_helper_functions_preserved(self, sample_result):
        """Helper functions with conditional bodies called many times should
        be kept as functions, not inlined."""
        _, result = sample_result
        # If the proxy inliner blows up helper functions, we'd see deeply
        # nested typeof chains
        nested_typeof = len(re.findall(r'typeof.*typeof.*typeof.*typeof', result))
        assert nested_typeof <= 3, f'{nested_typeof} deeply nested typeof chains — helpers may be getting inlined'

    def test_dead_expressions_removed(self, sample_result):
        """Standalone `0;` statements should be cleaned up."""
        _, result = sample_result
        # Count lines that are just a number followed by semicolon
        bare_numbers = len(re.findall(r'^\s*\d+;\s*$', result, re.MULTILINE))
        assert bare_numbers == 0, f'{bare_numbers} bare number statements remain'
