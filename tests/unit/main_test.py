"""Unit tests for pyjsclear.__main__."""

import sys
from io import StringIO
from unittest.mock import patch, mock_open

import pytest

from pyjsclear.__main__ import main


class TestReadFromFileOutputToStdout:
    """Test 1: Read from file, output to stdout."""

    def test_reads_file_and_writes_to_stdout(self, tmp_path, monkeypatch):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')

        monkeypatch.setattr(sys, 'argv', ['pyjsclear', str(input_file)])

        stdout = StringIO()
        monkeypatch.setattr(sys, 'stdout', stdout)

        with patch('pyjsclear.__main__.deobfuscate', return_value='var x = 1;') as mock_deobf:
            main()

        mock_deobf.assert_called_once_with('var x = 1;', max_iterations=50)
        assert stdout.getvalue() == 'var x = 1;'


class TestReadFromFileWriteToOutput:
    """Test 2: Read from file, write to output file (-o)."""

    def test_writes_result_to_output_file(self, tmp_path, monkeypatch):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')
        output_file = tmp_path / 'output.js'

        monkeypatch.setattr(sys, 'argv', ['pyjsclear', str(input_file), '-o', str(output_file)])

        with patch('pyjsclear.__main__.deobfuscate', return_value='let x = 1;'):
            main()

        assert output_file.read_text() == 'let x = 1;'

    def test_output_long_form_flag(self, tmp_path, monkeypatch):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')
        output_file = tmp_path / 'output.js'

        monkeypatch.setattr(sys, 'argv', ['pyjsclear', str(input_file), '--output', str(output_file)])

        with patch('pyjsclear.__main__.deobfuscate', return_value='let x = 1;'):
            main()

        assert output_file.read_text() == 'let x = 1;'


class TestReadFromStdin:
    """Test 3: Read from stdin (input == '-')."""

    def test_reads_from_stdin_when_dash(self, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['pyjsclear', '-'])
        monkeypatch.setattr(sys, 'stdin', StringIO('obfuscated();'))

        stdout = StringIO()
        monkeypatch.setattr(sys, 'stdout', stdout)

        with patch('pyjsclear.__main__.deobfuscate', return_value='clean();') as mock_deobf:
            main()

        mock_deobf.assert_called_once_with('obfuscated();', max_iterations=50)
        assert stdout.getvalue() == 'clean();'


class TestMaxIterationsFlag:
    """Test 4: --max-iterations flag passed through."""

    def test_custom_max_iterations(self, tmp_path, monkeypatch):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')

        monkeypatch.setattr(sys, 'argv', ['pyjsclear', str(input_file), '--max-iterations', '10'])

        stdout = StringIO()
        monkeypatch.setattr(sys, 'stdout', stdout)

        with patch('pyjsclear.__main__.deobfuscate', return_value='var x = 1;') as mock_deobf:
            main()

        mock_deobf.assert_called_once_with('var x = 1;', max_iterations=10)

    def test_default_max_iterations(self, tmp_path, monkeypatch):
        input_file = tmp_path / 'input.js'
        input_file.write_text('var x = 1;')

        monkeypatch.setattr(sys, 'argv', ['pyjsclear', str(input_file)])

        stdout = StringIO()
        monkeypatch.setattr(sys, 'stdout', stdout)

        with patch('pyjsclear.__main__.deobfuscate', return_value='var x = 1;') as mock_deobf:
            main()

        mock_deobf.assert_called_once_with('var x = 1;', max_iterations=50)


class TestMissingInputArgument:
    """Test 5: Missing input argument raises SystemExit."""

    def test_missing_input_raises_system_exit(self, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['pyjsclear'])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2
