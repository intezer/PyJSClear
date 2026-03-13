"""Tests for the XorStringDecoder transform."""

from pyjsclear.transforms.xor_string_decode import XorStringDecoder
from pyjsclear.transforms.xor_string_decode import _extract_numeric_array
from pyjsclear.transforms.xor_string_decode import _xor_decode
from tests.unit.conftest import roundtrip


class TestXorDecode:
    """Tests for the _xor_decode helper."""

    def test_basic_xor(self) -> None:
        """XOR decode with known prefix and data."""
        # Prefix: [1, 2, 3, 4], data XOR'd with prefix
        prefix = [1, 2, 3, 4]
        message = b'ABCD'
        encoded = prefix + [b ^ prefix[i % 4] for i, b in enumerate(message)]
        result = _xor_decode(encoded)
        assert result == 'ABCD'

    def test_too_short_returns_none(self) -> None:
        assert _xor_decode([1, 2, 3]) is None
        assert _xor_decode([1, 2, 3, 4]) is None

    def test_invalid_utf8_returns_none(self) -> None:
        result = _xor_decode([0, 0, 0, 0, 0xFF, 0xFE])
        assert result is None


class TestExtractNumericArray:
    """Tests for _extract_numeric_array helper."""

    def test_valid_array(self) -> None:
        node = {
            'type': 'ArrayExpression',
            'elements': [
                {'type': 'Literal', 'value': 10, 'raw': '10'},
                {'type': 'Literal', 'value': 20, 'raw': '20'},
            ],
        }
        assert _extract_numeric_array(node) == [10, 20]

    def test_non_array_returns_none(self) -> None:
        assert _extract_numeric_array({'type': 'Literal', 'value': 1}) is None
        assert _extract_numeric_array(None) is None

    def test_out_of_range_returns_none(self) -> None:
        node = {
            'type': 'ArrayExpression',
            'elements': [{'type': 'Literal', 'value': 300, 'raw': '300'}],
        }
        assert _extract_numeric_array(node) is None

    def test_non_numeric_element_returns_none(self) -> None:
        node = {
            'type': 'ArrayExpression',
            'elements': [{'type': 'Literal', 'value': 'str', 'raw': '"str"'}],
        }
        assert _extract_numeric_array(node) is None


class TestXorStringDecoderTransform:
    """Tests for the full XorStringDecoder transform."""

    def test_no_decoder_returns_false(self) -> None:
        result, changed = roundtrip('var x = 1;', XorStringDecoder)
        assert changed is False

    def test_decoder_detected_and_inlined(self) -> None:
        """Integration test: XOR decoder function + call site should be resolved."""
        # Build a XOR-encoded byte array for "test"
        prefix = [0x10, 0x20, 0x30, 0x40]
        message = b'test'
        encoded = prefix + [b ^ prefix[i % 4] for i, b in enumerate(message)]
        arr_str = ', '.join(str(b) for b in encoded)
        code = f'''
        function decoder(arr) {{
            var prefix = arr.slice(0, 4);
            var data = Buffer.from(arr.slice(4));
            for (var i = 0; i < data.length; i++) {{
                data[i] ^= prefix[i % 4];
            }}
            return data.toString();
        }}
        var _0xResult = decoder([{arr_str}]);
        obj[_0xResult];
        '''
        result, changed = roundtrip(code, XorStringDecoder)
        assert changed is True
        assert 'obj.test' in result or 'obj["test"]' in result or '"test"' in result

    def test_standalone_identifier_replaced(self) -> None:
        """Standalone use of decoded var (e.g., require(_0xVar)) gets string literal."""
        prefix = [0x10, 0x20, 0x30, 0x40]
        message = b'fs'
        encoded = prefix + [b ^ prefix[i % 4] for i, b in enumerate(message)]
        arr_str = ', '.join(str(b) for b in encoded)
        code = f'''
        function decoder(arr) {{
            var prefix = arr.slice(0, 4);
            var data = Buffer.from(arr.slice(4));
            for (var i = 0; i < data.length; i++) {{
                data[i] ^= prefix[i % 4];
            }}
            return data.toString();
        }}
        var _0xMod = decoder([{arr_str}]);
        require(_0xMod);
        '''
        result, changed = roundtrip(code, XorStringDecoder)
        assert changed is True
        assert 'require("fs")' in result

    def test_dead_declaration_removed(self) -> None:
        """After inlining, the var _0xResult = decoder(...) should be removed."""
        prefix = [0x10, 0x20, 0x30, 0x40]
        message = b'test'
        encoded = prefix + [b ^ prefix[i % 4] for i, b in enumerate(message)]
        arr_str = ', '.join(str(b) for b in encoded)
        code = f'''
        function decoder(arr) {{
            var prefix = arr.slice(0, 4);
            var data = Buffer.from(arr.slice(4));
            for (var i = 0; i < data.length; i++) {{
                data[i] ^= prefix[i % 4];
            }}
            return data.toString();
        }}
        var _0xResult = decoder([{arr_str}]);
        obj[_0xResult];
        '''
        result, changed = roundtrip(code, XorStringDecoder)
        assert changed is True
        # _0xResult should be removed (no remaining references)
        assert '_0xResult' not in result

    def test_non_valid_identifier_uses_string_literal(self) -> None:
        """Decoded string with non-identifier chars stays as string literal."""
        prefix = [0x10, 0x20, 0x30, 0x40]
        message = b'a-b'
        encoded = prefix + [b ^ prefix[i % 4] for i, b in enumerate(message)]
        arr_str = ', '.join(str(b) for b in encoded)
        code = f'''
        function decoder(arr) {{
            var prefix = arr.slice(0, 4);
            var data = Buffer.from(arr.slice(4));
            for (var i = 0; i < data.length; i++) {{
                data[i] ^= prefix[i % 4];
            }}
            return data.toString();
        }}
        var _0xResult = decoder([{arr_str}]);
        obj[_0xResult];
        '''
        result, changed = roundtrip(code, XorStringDecoder)
        assert changed is True
        assert '"a-b"' in result or "'a-b'" in result
