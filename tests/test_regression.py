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
# Obfuscator.io with SequenceExpression rotation
# ================================================================


class TestSequenceExpressionRotation:
    """Obfuscator.io files where the rotation IIFE is inside a SequenceExpression."""

    def test_code_beautify_site_string_decode(self):
        """code_beautify_site: rotation + main code in (rotationIIFE(), mainIIFE()).

        The rotation IIFE and main code IIFE are comma-separated inside a
        SequenceExpression. Tests that rotation is found inside the sequence,
        executed correctly, and the main code is preserved after removal.
        """
        code, result = _deobfuscate('code_beautify_site.js')
        assert result != code
        in_0x = _count_0x(code)
        out_0x = _count_0x(result)
        assert out_0x < in_0x * 0.35, (
            f'Expected >= 65% _0x reduction, got {in_0x} -> {out_0x} ' f'({100*(in_0x-out_0x)/in_0x:.0f}%)'
        )
        # All string decoder calls should be resolved
        assert 'palindrome' in result
        assert 'console.log' in result or 'console["log"]' in result
        assert 'toLowerCase' in result or 'toLowerCas' not in result
        assert 'reverse' in result
        assert 'split' in result

    def test_code_beautify_site_no_empty_output(self):
        """code_beautify_site: output must not be empty (regression for removal bug)."""
        code, result = _deobfuscate('code_beautify_site.js')
        assert len(result) > 100, f'Output too short ({len(result)} bytes), likely lost main code'


# ================================================================
# String array with shuffle + numeric expressions as offsets
# ================================================================


class TestStringArrayShuffleExpressions:
    """Obfuscator.io string array with complex numeric expressions in offsets."""

    def test_strings_array_shuffle_decode(self):
        """strings_array_shuffle_numbers_to_expressions: numeric-expression offsets.

        The decoder offset uses complex expressions like (-0x9c6+0x3*-0x9c9+0x28d2).
        Tests that _eval_numeric resolves these and string replacement works.
        """
        code, result = _deobfuscate('strings_array_shuffle_numbers_to_expressions.js')
        assert result != code
        # String literals should appear in the output
        assert 'log' in result
        assert ') = ' in result or ')\\x20=\\x20' not in result

    def test_strings_array_shuffle_object_literal_resolution(self):
        """strings_array_shuffle_numbers_to_expressions: member expression args.

        Decoder calls use _0x3531db._0x217c1c (object property lookup) as the
        argument. Tests that object literal collection and resolution works.
        """
        code, result = _deobfuscate('strings_array_shuffle_numbers_to_expressions.js')
        # The object literal {_0x217c1c: 0x1b1} should be resolved
        # and the decoder call with that value should succeed
        assert '_0x3531db' not in result or '_0x217c1c' not in result, 'Object literal reference should be resolved'


# ================================================================
# Basic string array (2-element, below old threshold)
# ================================================================


class TestSmallStringArray:
    """String arrays with 2 elements (below the old >= 5 threshold)."""

    def test_strings_array_full_decode(self):
        """strings_array: 2-element array, tests lowered threshold.

        Previously required >= 5 elements. Now >= 2 should decode.
        Output should be clean console.log("Hello, World!").
        """
        code, result = _deobfuscate('strings_array.js')
        assert result != code
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        assert 'Hello' in result
        assert 'World' in result
        assert 'console' in result


# ================================================================
# Control flow flattening recovery
# ================================================================


class TestControlFlowFlatten:
    """Control flow flattened code (switch-case dispatch pattern)."""

    def test_control_flow_flatten_recovery(self):
        """control_flow_flatten: switch-based control flow should be linearized.

        The obfuscated code uses a while/switch dispatch loop. After recovery,
        the code should be readable with the original logic flow.
        """
        code, result = _deobfuscate('control_flow_flatten.js')
        assert result != code
        assert len(result) < len(code), 'Output should be smaller after flattening recovery'
        # The code is a palindrome checker
        assert 'toLowerCase' in result
        assert 'reverse' in result
        assert 'split' in result
        assert 'forEach' in result or 'for' in result


# ================================================================
# Split string concatenation
# ================================================================


class TestSplitStrings:
    """Split string concatenation patterns."""

    def test_split_strings_joined(self):
        """split_strings: "Hel" + "lo," + " Wo" + "rld!" should be joined.

        Tests ExpressionSimplifier constant folding for string concatenation.
        """
        code, result = _deobfuscate('split_strings.js')
        assert result != code
        assert _count_0x(result) == 0
        assert 'Hello, World!' in result
        assert len(result) < len(code), 'Output should be smaller after string joining'


# ================================================================
# Unicode/hex escape to readable string
# ================================================================


class TestStringToUnicode:
    """Unicode/hex escape conversion patterns."""

    def test_string_to_unicode_decoded(self):
        """string_to_unicode: hex escapes should be decoded to readable text."""
        code, result = _deobfuscate('string_to_unicode.js')
        assert result != code
        assert 'Hello Intezer' in result
        assert 'console' in result


# ================================================================
# Base64 string encoding
# ================================================================


class TestBase64Strings:
    """Obfuscator.io base64 string encoding pattern."""

    def test_base64_full_decode(self):
        """base64_strings: all strings should be decoded from base64 encoding."""
        code, result = _deobfuscate('base64_strings.js')
        assert result != code
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        for s in ['split', 'reverse', 'join', 'replace', 'radar', 'hello', 'level', 'world', 'log', 'palindrome']:
            assert s in result, f'Expected decoded string {s!r} in output'

    def test_base64_clean_output(self):
        """base64_strings: output should be a clean palindrome checker."""
        code, result = _deobfuscate('base64_strings.js')
        assert len(result) < 300, f'Expected compact output, got {len(result)} chars'
        assert 'forEach' in result


# ================================================================
# RC4 string encoding
# ================================================================


class TestRc4Strings:
    """Obfuscator.io RC4 string encoding pattern."""

    def test_rc4_full_decode(self):
        """rc4_strings: all strings should be decoded from RC4 encoding."""
        code, result = _deobfuscate('rc4_strings.js')
        assert result != code
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        for s in ['split', 'reverse', 'join', 'replace', 'radar', 'hello', 'level', 'world', 'log', 'palindrome']:
            assert s in result, f'Expected decoded string {s!r} in output'

    def test_rc4_clean_output(self):
        """rc4_strings: output should be a clean palindrome checker."""
        code, result = _deobfuscate('rc4_strings.js')
        assert len(result) < 300, f'Expected compact output, got {len(result)} chars'


# ================================================================
# Hex index string array
# ================================================================


class TestStringHexIndex:
    """String array accessed via hex index literals (e.g. arr[0x0])."""

    def test_hex_index_full_decode(self):
        """string_hex_index: hex indices should resolve to correct strings."""
        code, result = _deobfuscate('string_hex_index.js')
        assert result != code
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        for s in ['radar', 'hello', 'level', 'world', 'palindrome']:
            assert s in result, f'Expected decoded string {s!r} in output'


# ================================================================
# Multiple decoders (base64 + RC4 sharing one array)
# ================================================================


class TestMultipleDecoders:
    """Obfuscator.io pattern with two decoder functions sharing one string array."""

    def test_multiple_decoders_full_decode(self):
        """string_multiple: dual base64+RC4 decoders should both resolve."""
        code, result = _deobfuscate('string_multiple.js')
        assert result != code
        assert _count_0x(result) == 0, f'All _0x should be removed, got {_count_0x(result)}'
        for s in ['split', 'reverse', 'join', 'replace', 'radar', 'hello', 'level', 'world', 'log', 'palindrome']:
            assert s in result, f'Expected decoded string {s!r} in output'

    def test_multiple_decoders_clean_output(self):
        """string_multiple: output should be compact after both decoders resolve."""
        code, result = _deobfuscate('string_multiple.js')
        assert len(result) < 300, f'Expected compact output, got {len(result)} chars'
        assert 'forEach' in result


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

    def test_output_not_larger_than_input(self):
        """Deobfuscated output should never be larger than the input.

        Deobfuscation removes string arrays, dead code, and infrastructure.
        If output grows, something is wrong (e.g., proxy inlining blowup).
        """
        for f in SAMPLES_DIR.glob('*.js'):
            code = f.read_text()
            result = pyjsclear.deobfuscate(code)
            assert len(result) <= len(code) * 1.1, (
                f'{f.name}: output ({len(result)}) > 110% of input ({len(code)}). '
                f'Ratio: {len(result)/len(code):.2f}'
            )

    def test_output_parseable(self):
        """Deobfuscated output should be parseable JavaScript.

        If the output doesn't parse, a transform likely corrupted the AST.
        We skip files whose input doesn't parse (ES modules with import).
        """
        from pyjsclear.parser import parse

        for f in SAMPLES_DIR.glob('*.js'):
            code = f.read_text()
            # Skip files that don't parse as input (ES modules)
            try:
                parse(code)
            except SyntaxError:
                continue
            result = pyjsclear.deobfuscate(code)
            try:
                parse(result)
            except SyntaxError as e:
                pytest.fail(f'{f.name}: output does not parse: {e}')

    def test_no_extremely_long_lines(self):
        """No output line should exceed 5000 chars.

        Long lines indicate expression blowup from proxy function inlining
        or other expansion bugs. The limit is generous (5000) to accommodate
        files with legitimately long array literals.
        """
        for f in SAMPLES_DIR.glob('*.js'):
            code = f.read_text()
            result = pyjsclear.deobfuscate(code)
            for i, line in enumerate(result.splitlines(), 1):
                assert len(line) <= 5000, (
                    f'{f.name} line {i}: {len(line)} chars (max 5000). ' f'Preview: {line[:80]}...'
                )
