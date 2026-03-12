"""Pure Python JavaScript deobfuscation library.

Combines functionality from obfuscator-io-deobfuscator (13 AST transforms)
and javascript-deobfuscator (3 surface-cleanup modules) into a single
Python package.
"""

from .deobfuscator import Deobfuscator


__version__ = '0.1.3'


def deobfuscate(code, max_iterations=50):
    """Deobfuscate JavaScript code. Returns cleaned source.

    Args:
        code: JavaScript source code string.
        max_iterations: Maximum transform passes (default 50).

    Returns:
        Deobfuscated JavaScript source code.
    """
    return Deobfuscator(code, max_iterations=max_iterations).execute()


def deobfuscate_file(input_path, output_path=None, max_iterations=50):
    """Deobfuscate a JavaScript file.

    Args:
        input_path: Path to input JS file.
        output_path: Path to write output (if None, returns string).
        max_iterations: Maximum transform passes.

    Returns:
        True if content changed (when output_path given), or the deobfuscated string.
    """
    with open(input_path, 'r', errors='replace') as f:
        code = f.read()

    result = deobfuscate(code, max_iterations=max_iterations)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(result)
        return result != code
    return result
