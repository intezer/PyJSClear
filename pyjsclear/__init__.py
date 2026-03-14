"""Pure Python JavaScript deobfuscation library.

Combines functionality from obfuscator-io-deobfuscator (13 AST transforms)
and javascript-deobfuscator (3 surface-cleanup modules) into a single
Python package.
"""

from pathlib import Path

from .deobfuscator import Deobfuscator


__all__ = ['Deobfuscator', 'deobfuscate', 'deobfuscate_file']

__version__ = '0.1.4'


def deobfuscate(code: str, max_iterations: int = 50) -> str:
    """Deobfuscate JavaScript code and return cleaned source.

    Args:
        code: JavaScript source code string.
        max_iterations: Maximum transform passes (default 50).

    Returns:
        Deobfuscated JavaScript source code.
    """
    return Deobfuscator(code, max_iterations=max_iterations).execute()


def _write_output(output_path: str | Path, content: str) -> None:
    """Write deobfuscated content to the given file path."""
    with open(output_path, 'w') as output_file:
        output_file.write(content)


def deobfuscate_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    max_iterations: int = 50,
) -> str | bool:
    """Deobfuscate a JavaScript file.

    Args:
        input_path: Path to input JS file.
        output_path: Path to write output (if None, returns string).
        max_iterations: Maximum transform passes.

    Returns:
        True if content changed (when output_path given), or the deobfuscated string.
    """
    with open(input_path, 'r', errors='replace') as input_file:
        code = input_file.read()

    result = deobfuscate(code, max_iterations=max_iterations)

    if not output_path:
        return result

    _write_output(output_path, result)
    return result != code
