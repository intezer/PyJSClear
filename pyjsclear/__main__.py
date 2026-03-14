"""CLI entry point: python -m pyjsclear input.js [-o output.js]"""

import argparse
import sys

from . import deobfuscate


def _read_input(source_path: str) -> str:
    """Read JavaScript source from stdin or a file path."""
    if source_path == '-':
        return sys.stdin.read()
    with open(source_path, 'r', errors='replace') as input_file:
        return input_file.read()


def _write_output(destination_path: str, content: str) -> None:
    """Write deobfuscated content to the given file path."""
    with open(destination_path, 'w') as output_file:
        output_file.write(content)


def main() -> None:
    """Parse CLI arguments and run the deobfuscator."""
    argument_parser = argparse.ArgumentParser(description='Deobfuscate JavaScript files.')
    argument_parser.add_argument('input', help='Input JS file (use - for stdin)')
    argument_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    argument_parser.add_argument(
        '--max-iterations',
        type=int,
        default=50,
        help='Maximum transform passes (default: 50)',
    )
    args = argument_parser.parse_args()

    code = _read_input(args.input)
    result = deobfuscate(code, max_iterations=args.max_iterations)

    if args.output:
        _write_output(args.output, result)
        return

    sys.stdout.write(result)


if __name__ == '__main__':
    main()
