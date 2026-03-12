import pytest

import pyjsclear
from pyjsclear import Deobfuscator
from pyjsclear import deobfuscate
from pyjsclear import deobfuscate_file


class TestVersion:
    def test_version_is_semver(self):
        parts = pyjsclear.__version__.split('.')
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


class TestDeobfuscate:
    def test_returns_string(self):
        result = deobfuscate('var x = 1;')
        assert isinstance(result, str)


class TestDeobfuscateFile:
    def test_reads_file_returns_string_no_output(self, tmp_path):
        input_file = tmp_path / 'input.js'
        input_file.write_text('const x = 1;')

        result = deobfuscate_file(str(input_file))
        assert isinstance(result, str)
        assert result == 'const x = 1;'

    def test_writes_output_file_returns_false_when_unchanged(self, tmp_path):
        code = 'const x = 1;'
        input_file = tmp_path / 'input.js'
        input_file.write_text(code)
        output_file = tmp_path / 'output.js'

        result = deobfuscate_file(str(input_file), output_path=str(output_file))
        assert result is False
        assert output_file.read_text() == code

    def test_writes_output_file_returns_true_when_changed(self, tmp_path):
        # Use code that the deobfuscator will actually transform
        code = 'var x = 1 + 2;'
        input_file = tmp_path / 'input.js'
        input_file.write_text(code)
        output_file = tmp_path / 'output.js'

        result = deobfuscate_file(str(input_file), output_path=str(output_file))
        output_content = output_file.read_text()

        if output_content != code:
            assert result is True
        else:
            # If deobfuscator doesn't change this code, result should be False
            assert result is False

    def test_with_max_iterations(self, tmp_path):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')

        result = deobfuscate_file(str(input_file), max_iterations=3)
        assert isinstance(result, str)


class TestDeobfuscatorImport:
    def test_deobfuscator_importable(self):
        assert Deobfuscator is not None
        assert callable(Deobfuscator)
