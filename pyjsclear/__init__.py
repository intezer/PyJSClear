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
        time_budget_seconds: Optional coarse wall-clock budget. It is checked
            between transform cycles only — a single stuck transform is NOT
            interrupted (callers needing a hard bound must enforce it
            externally). On expiry, the best result so far is returned.
            The budget restarts at each nested decode layer (JSFuck/
            eval-packed recursion); it is not a global deadline for the
            whole call. ``None`` (default) means no budget.

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
        time_budget_seconds: Optional coarse wall-clock budget. It is checked
            between transform cycles only — a single stuck transform is NOT
            interrupted (callers needing a hard bound must enforce it
            externally). On expiry, the best result so far is returned.
            The budget restarts at each nested decode layer (JSFuck/
            eval-packed recursion); it is not a global deadline for the
            whole call. ``None`` (default) means no budget.

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
