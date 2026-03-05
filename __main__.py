"""CLI entry point: python -m pyjsclear input.js [-o output.js]"""
import argparse
import sys
from . import deobfuscate


def main():
    parser = argparse.ArgumentParser(
        description='Deobfuscate JavaScript files.')
    parser.add_argument('input', help='Input JS file (use - for stdin)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--max-iterations', type=int, default=50,
                        help='Maximum transform passes (default: 50)')
    args = parser.parse_args()

    if args.input == '-':
        code = sys.stdin.read()
    else:
        with open(args.input, 'r', errors='replace') as f:
            code = f.read()

    result = deobfuscate(code, max_iterations=args.max_iterations)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
    else:
        sys.stdout.write(result)


if __name__ == '__main__':
    main()
