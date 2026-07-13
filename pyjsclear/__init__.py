"""Pure Python JavaScript deobfuscation library.

Combines functionality from obfuscator-io-deobfuscator (13 AST transforms)
and javascript-deobfuscator (3 surface-cleanup modules) into a single
Python package.
"""

from pathlib import Path

from .deobfuscator import Deobfuscator


__all__ = ['Deobfuscator', 'deobfuscate', 'deobfuscate_file']

__version__ = '0.1.6'


def deobfuscate(
    code: str,
    max_iterations: int = 50,
    time_budget_seconds: float | None = None,
) -> str:
    """Deobfuscate JavaScript code and return cleaned source.

    Args:
        code: JavaScript source code string.
        max_iterations: Maximum transform passes (default 50).
        time_budget_seconds: Optional coarse wall-clock budget, checked between
            transform cycles (a stuck transform is not interrupted — enforce a
            hard bound externally). Restarts at each nested decode layer, so it
            is not a global deadline; on expiry the best result so far is
            returned. ``None`` (default) disables it.

    Returns:
        Deobfuscated JavaScript source code.
    """
    return Deobfuscator(
        code,
        max_iterations=max_iterations,
        time_budget_seconds=time_budget_seconds,
    ).execute()


def deobfuscate_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    max_iterations: int = 50,
    time_budget_seconds: float | None = None,
) -> str | bool:
    """Deobfuscate a JavaScript file.

    Args:
        input_path: Path to input JS file.
        output_path: Path to write output (if None, returns string).
        max_iterations: Maximum transform passes.
        time_budget_seconds: Optional coarse wall-clock budget, checked between
            transform cycles (a stuck transform is not interrupted — enforce a
            hard bound externally). Restarts at each nested decode layer, so it
            is not a global deadline; on expiry the best result so far is
            returned. ``None`` (default) disables it.

    Returns:
        True if content changed (when output_path given), or the deobfuscated string.
    """
    with open(input_path, 'r', errors='replace') as input_file:
        code = input_file.read()

    result = deobfuscate(code, max_iterations=max_iterations, time_budget_seconds=time_budget_seconds)

    if not output_path:
        return result

    with open(output_path, 'w') as output_file:
        output_file.write(result)
    return result != code
