"""Tests for the HexNumerics transform."""

from pyjsclear.transforms.hex_numerics import HexNumerics
from tests.unit.conftest import roundtrip


class TestHexToDecimal:
    """Tests for converting hex numeric literals to decimal."""

    def test_simple_hex(self):
        code, changed = roundtrip('var x = 0xff;', HexNumerics)
        assert changed is True
        assert '255' in code
        assert '0xff' not in code

    def test_zero(self):
        code, changed = roundtrip('var x = 0x0;', HexNumerics)
        assert changed is True
        assert '= 0' in code

    def test_uppercase_hex(self):
        code, changed = roundtrip('var x = 0XFF;', HexNumerics)
        assert changed is True
        assert '255' in code

    def test_multiple_hex_values(self):
        code, changed = roundtrip('var x = 0x10; var y = 0x20;', HexNumerics)
        assert changed is True
        assert '16' in code
        assert '32' in code


class TestNoTransform:
    """Tests where hex conversion should not occur."""

    def test_decimal_unchanged(self):
        code, changed = roundtrip('var x = 42;', HexNumerics)
        assert changed is False

    def test_string_unchanged(self):
        code, changed = roundtrip('var x = "0xff";', HexNumerics)
        assert changed is False

    def test_float_unchanged(self):
        code, changed = roundtrip('var x = 3.14;', HexNumerics)
        assert changed is False

    def test_no_raw_field_unchanged(self):
        """Numeric literal without a raw field should not be transformed."""
        from pyjsclear.generator import generate
        from pyjsclear.parser import parse

        ast = parse('var x = 1;')
        # Manually remove raw to simulate a synthetic node
        for stmt in ast['body']:
            for decl in stmt.get('declarations', []):
                init = decl.get('init')
                if init and 'raw' in init:
                    del init['raw']
        changed = HexNumerics(ast).execute()
        assert changed is False

    def test_negative_hex_value(self):
        """Hex literal with negative value uses plain str() path (line 26)."""
        from pyjsclear.generator import generate
        from pyjsclear.parser import parse

        ast = parse('var x = 0x1;')
        # Manually set the value to a negative to test the else branch
        decl = ast['body'][0]['declarations'][0]
        decl['init']['value'] = -5
        decl['init']['raw'] = '0x1'  # keep as hex to trigger the transform
        changed = HexNumerics(ast).execute()
        assert changed is True
        result = generate(ast)
        assert '-5' in result
