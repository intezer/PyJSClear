"""Pure Python JavaScript deobfuscation library.

Combines functionality from obfuscator-io-deobfuscator (13 AST transforms)
and javascript-deobfuscator (3 surface-cleanup modules) into a single
Python package.
"""

from .deobfuscator import Deobfuscator


__version__ = '0.1.4'


def deobfuscate(code: str, max_iterations: int = 50) -> str:
    """Deobfuscate JavaScript code. Returns cleaned source.

    Args:
        code: JavaScript source code string.
        max_iterations: Maximum transform passes (default 50).

    Returns:
        Deobfuscated JavaScript source code.
    """
    return Deobfuscator(code, max_iterations=max_iterations).execute()


def deobfuscate_file(input_path: str, output_path: str | None = None, max_iterations: int = 50) -> str | bool:
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

    if output_path:
        with open(output_path, 'w') as output_file:
            output_file.write(result)
        return result != code
    return result
