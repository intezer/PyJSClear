"""Regression tests for PyJSClear deobfuscation quality.

Tests cover:
- Var-based string array pattern (Strategy 2b)
- Obfuscator.io function-declaration pattern (Strategy 2)
- Source-level hex escape decoding for unparseable files
- Dead code removal after string decode
- Residual _0x parameter names (not decoder calls)
- 2-element array negative test (below threshold)
- No-obfuscation passthrough
- Cross-cutting quality invariants
"""

import os
import re
from pathlib import Path

import pyjsclear

SAMPLES_DIR = Path(__file__).parent / 'resources' / 'regression_samples'

RE_0X = re.compile(r'\b_0x[0-9a-fA-F]{2,}\b')
RE_HEX = re.compile(r'\\x[0-9a-fA-F]{2}')


def _deobfuscate(filename):
    code = (SAMPLES_DIR / filename).read_text()
    result = pyjsclear.deobfuscate(code)
    return code, result


def _count_0x(text):
    return len(RE_0X.findall(text))


def _count_hex(text):
    return len(RE_HEX.findall(text))


# ================================================================
# Strategy 2b: Var-based string array + rotation + decoder
# ================================================================


class TestVarArrayPattern:
    """Tests for var _0x... = [...] + IIFE rotation + var decoder pattern."""

    def test_animatedweb_full_decode(self):
        """AnimatedWeb: small file, 5-element array, should fully decode all _0x."""
        code, result = _deobfuscate('AnimatedWeb-obfuscated.js')
        assert result != code, 'Output should differ from input'
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        assert 'createAnimatedComponent' in result

    def test_alias_decode(self):
        """alias: 31 _0x identifiers, should decode most strings."""
        code, result = _deobfuscate('alias-obfuscated.js')
        assert result != code
        assert _count_0x(result) <= 5, f'Expected <= 5 _0x remaining, got {_count_0x(result)}'
        assert 'require' in result
        assert 'path' in result

    def test_2100bytes_decode(self):
        """2100bytes: array with hex escapes, tests both array decode and hex removal."""
        code, result = _deobfuscate('2100bytes-obfuscated.js')
        assert result != code
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        assert _count_hex(result) == 0, f'All hex escapes should be removed, got {_count_hex(result)}'

    def test_ngeventdirs_improvement(self):
        """ngEventDirs: was a Node.js win, should now show improvement."""
        code, result = _deobfuscate('ngEventDirs-obfuscated.js')
        assert result != code
        in_0x = _count_0x(code)
        out_0x = _count_0x(result)
        assert out_0x < in_0x, f'Should reduce _0x: {in_0x} -> {out_0x}'
        assert 'ngEventDirectives' in result


# ================================================================
# Obfuscator.io function-declaration pattern (large file)
# ================================================================


class TestObfuscatorIoFunctionPattern:
    """Tests for function-declaration based obfuscator.io pattern."""

    def test_large_obfuscatorio_decodes(self):
        """Large obfuscator.io sample: should decode strings and reduce _0x."""
        code, result = _deobfuscate('large-obfuscatorio-obfuscated.js')
        assert result != code
        in_0x = _count_0x(code)
        out_0x = _count_0x(result)
        # Should reduce _0x by at least 30%
        assert out_0x < in_0x * 0.7, (
            f'Expected >= 30% _0x reduction, got {in_0x} -> {out_0x} ' f'({100*(in_0x-out_0x)/in_0x:.0f}%)'
        )

    def test_large_obfuscatorio_hex_removed(self):
        """Large obfuscator.io sample: all hex escapes should be removed."""
        code, result = _deobfuscate('large-obfuscatorio-obfuscated.js')
        assert _count_hex(result) == 0, f'Hex escapes remain: {_count_hex(result)}'

    def test_large_obfuscatorio_has_readable_strings(self):
        """Large obfuscator.io sample: output should contain readable strings."""
        code, result = _deobfuscate('large-obfuscatorio-obfuscated.js')
        assert 'require' in result
        assert 'undefined' in result


# ================================================================
# Hex escape decoding for unparseable files (ES modules)
# ================================================================


class TestHexEscapeFallback:
    """Tests for source-level hex decode when AST parsing fails."""

    def test_app_test_hex_removal(self):
        """App.test: ES module with import, 2 hex escapes should be decoded."""
        code, result = _deobfuscate('App-obfuscated.test.js')
        assert result != code, 'Output should differ (hex decoded)'
        assert _count_hex(result) == 0, f'All hex escapes should be removed, got {_count_hex(result)}'
        assert 'creates instance without' in result

    def test_authentication_hex_removal(self):
        """authentication: ES module, 12 hex escapes should be decoded."""
        code, result = _deobfuscate('authentication-obfuscated.js')
        assert result != code
        assert _count_hex(result) == 0, f'All hex escapes should be removed, got {_count_hex(result)}'

    def test_chrome_partial_hex_decode(self):
        r"""chrome: parse-fail with \x0a (newline) that must stay escaped.

        Printable hex escapes are decoded but control chars like \x0a are
        correctly preserved to avoid breaking string literal syntax.
        """
        code, result = _deobfuscate('chrome-obfuscated.js')
        assert result != code, 'Output should differ (some hex decoded)'
        in_hex = _count_hex(code)
        out_hex = _count_hex(result)
        assert out_hex < in_hex, f'Should reduce hex: {in_hex} -> {out_hex}'
        # Only non-printable escapes (\x0a etc.) should remain
        remaining = RE_HEX.findall(result)
        for esc in remaining:
            val = int(esc[2:], 16)
            assert (
                val < 0x20 or val > 0x7E or val in (0x22, 0x27, 0x5C)
            ), f'Printable hex escape {esc} (chr {val}) should have been decoded'


# ================================================================
# Non-string-array transforms (PropertySimplifier, etc.)
# ================================================================


class TestOtherTransforms:
    """Files where string array decode doesn't fire but other transforms do."""

    def test_animatedflatlist_property_simplifier(self):
        """AnimatedFlatList: 1-element array (below Strategy 2b threshold).

        Strategy 2b should NOT fire (array too small). PropertySimplifier
        converts bracket notation to dot notation, reducing output size.
        """
        code, result = _deobfuscate('AnimatedFlatList-obfuscated.js')
        assert result != code, 'PropertySimplifier should transform the code'
        assert len(result) < len(code), 'Output should be smaller (bracket -> dot)'
        # _0x count should be unchanged (no string decode happened)
        assert _count_0x(result) == _count_0x(
            code
        ), f'_0x count should be unchanged: {_count_0x(code)} -> {_count_0x(result)}'

    def test_animatedimage_2element_array_no_decode(self):
        """AnimatedImage: 2-element array — below Strategy 2b threshold.

        Must NOT trigger string array decoding. Only PropertySimplifier
        should fire (bracket -> dot). This is a negative test.
        """
        code, result = _deobfuscate('AnimatedImage-obfuscated.js')
        assert result != code, 'PropertySimplifier should still fire'
        assert _count_0x(result) == _count_0x(code), (
            f'_0x count should be unchanged (array too small for decode): ' f'{_count_0x(code)} -> {_count_0x(result)}'
        )


# ================================================================
# Dead code removal after string decode
# ================================================================


class TestDeadCodeRemoval:
    """Files where string decode enables massive dead code elimination."""

    def test_hello_world_full_recovery(self):
        """hello_world: 1.5KB obfuscated -> 64b clean 'console.log("hello world")'.

        Tests end-to-end: string decode -> dead branch removal ->
        unused variable removal -> clean readable output.
        """
        code, result = _deobfuscate('hello_world-obfuscated.js')
        assert result != code
        assert _count_0x(result) == 0
        assert len(result) < 100, f'Expected tiny output, got {len(result)}b'
        assert 'console.log("hello world")' in result

    def test_ngcontroller_infrastructure_stripped(self):
        """ngController: 9KB -> ~162b, entire obfuscation infrastructure removed.

        After string array decode, the rotation IIFE, decoder function,
        and array declaration are removed, leaving only the small directive.
        """
        code, result = _deobfuscate('ngController-obfuscated.js')
        assert result != code
        assert _count_0x(result) == 0
        assert len(result) < len(code) * 0.05, (
            f'Expected >95% size reduction, got {len(code)}b -> {len(result)}b ' f'({100*len(result)/len(code):.0f}%)'
        )
        assert 'ngControllerDirective' in result
        assert 'restrict' in result


# ================================================================
# Residual _0x names (renamed variables, NOT decoder calls)
# ================================================================


class TestResidualIdentifiers:
    """Files where strings are fully decoded but _0x variable names remain."""

    def test_stream_passthrough_residual_params(self):
        """_stream_passthrough: all strings decoded, _0x params remain.

        Remaining _0x identifiers are function parameters and local
        variables, NOT unreplaced decoder calls. This tests that we
        decode what we should and leave what we can't rename.
        """
        code, result = _deobfuscate('_stream_passthrough-obfuscated.js')
        assert result != code
        in_0x = _count_0x(code)
        out_0x = _count_0x(result)
        assert out_0x < in_0x, f'Should reduce _0x: {in_0x} -> {out_0x}'
        # Verify decoded strings appear
        assert 'module.exports' in result
        assert 'PassThrough' in result
        assert '_stream_transform' in result
        # Verify NO remaining decoder calls (string hex args)
        assert not re.search(r"_0x[0-9a-fA-F]+\s*\(\s*'0x", result), 'Should have no unreplaced decoder calls'

    def test_dns_partial_decode_with_structure(self):
        """dns: 465 _0x -> ~323, has switch/case and real code structure.

        Medium-complexity file with control flow. Tests that string
        decode works alongside non-trivial code patterns.
        """
        code, result = _deobfuscate('dns-obfuscated.js')
        assert result != code
        in_0x = _count_0x(code)
        out_0x = _count_0x(result)
        assert out_0x < in_0x * 0.75, f'Expected >= 25% _0x reduction, got {in_0x} -> {out_0x}'
        # Should have real code structures preserved
        assert 'switch' in result
        assert 'assert' in result


# ================================================================
# No-obfuscation passthrough
# ================================================================


class TestPassthrough:
    """Files with no obfuscation markers should still produce valid output."""

    def test_interactionmanager_no_regression(self):
        """InteractionManager: no _0x, no hex — output should be valid JS."""
        code, result = _deobfuscate('InteractionManager-obfuscated.js')
        assert _count_0x(result) == 0
        assert _count_hex(result) == 0
        assert 'module.exports' in result or 'module' in result


# ================================================================
# Cross-cutting quality assertions
# ================================================================


class TestQualityInvariants:
    """Invariants that should hold for all samples."""

    def test_no_empty_output(self):
        """No sample should produce empty output."""
        for f in SAMPLES_DIR.glob('*.js'):
            code = f.read_text()
            result = pyjsclear.deobfuscate(code)
            assert len(result.strip()) > 0, f'{f.name} produced empty output'

    def test_no_hex_increase(self):
        """Deobfuscation should never introduce new hex escapes."""
        for f in SAMPLES_DIR.glob('*.js'):
            code = f.read_text()
            result = pyjsclear.deobfuscate(code)
            assert _count_hex(result) <= _count_hex(
                code
            ), f'{f.name}: hex escapes increased from {_count_hex(code)} to {_count_hex(result)}'

    def test_output_not_larger_than_3x(self):
        """Output should not be excessively larger than input."""
        for f in SAMPLES_DIR.glob('*.js'):
            code = f.read_text()
            result = pyjsclear.deobfuscate(code)
            assert len(result) <= len(code) * 3, f'{f.name}: output {len(result)} > 3x input {len(code)}'
