"""Shared helpers for fuzz targets."""

import argparse
import os
import random
import sys
import time
from typing import Any
from typing import Callable


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

MAX_INPUT_SIZE = 102_400  # 100KB cap

SAFE_EXCEPTIONS = (RecursionError,)

# ESTree node types for synthetic AST generation
_STATEMENT_TYPES = [
    'ExpressionStatement',
    'VariableDeclaration',
    'ReturnStatement',
    'IfStatement',
    'WhileStatement',
    'ForStatement',
    'BlockStatement',
    'EmptyStatement',
    'BreakStatement',
    'ContinueStatement',
    'ThrowStatement',
]

_EXPRESSION_TYPES = [
    'Literal',
    'Identifier',
    'BinaryExpression',
    'UnaryExpression',
    'CallExpression',
    'MemberExpression',
    'AssignmentExpression',
    'ConditionalExpression',
    'ArrayExpression',
    'ObjectExpression',
    'FunctionExpression',
    'ThisExpression',
]

_BINARY_OPS = [
    '+',
    '-',
    '*',
    '/',
    '%',
    '==',
    '!=',
    '===',
    '!==',
    '<',
    '>',
    '<=',
    '>=',
    '&&',
    '||',
    '&',
    '|',
    '^',
    '<<',
    '>>',
    '>>>',
]
_UNARY_OPS = ['-', '+', '!', '~', 'typeof', 'void']


def bytes_to_js(data: bytes) -> str:
    """Decode bytes to a JS string with size limit."""
    return data[:MAX_INPUT_SIZE].decode('utf-8', errors='replace')


def bytes_to_ast_dict(data: bytes, max_depth: int = 5, max_children: int = 4) -> dict:
    """Build a synthetic ESTree AST dict from bytes for testing generator/traverser."""
    rng = random.Random(int.from_bytes(data[:8].ljust(8, b'\x00'), 'little'))
    pos = 8

    def consume_byte() -> int:
        nonlocal pos
        if pos < len(data):
            val = data[pos]
            pos += 1
            return val
        return rng.randint(0, 255)

    def make_literal() -> dict:
        match consume_byte() % 4:
            case 0:
                return {'type': 'Literal', 'value': consume_byte(), 'raw': str(consume_byte())}
            case 1:
                return {'type': 'Literal', 'value': True, 'raw': 'true'}
            case 2:
                return {'type': 'Literal', 'value': None, 'raw': 'null'}
            case _:
                return {'type': 'Literal', 'value': 'fuzz', 'raw': '"fuzz"'}

    def make_identifier() -> dict:
        names = ['a', 'b', 'c', 'x', 'y', 'foo', 'bar', '_', '$']
        return {'type': 'Identifier', 'name': names[consume_byte() % len(names)]}

    def make_node(depth: int = 0) -> dict:
        if depth >= max_depth:
            return make_literal() if consume_byte() % 2 == 0 else make_identifier()

        type_idx = consume_byte()
        if type_idx % 3 != 0:
            return make_statement(depth)

        expr_type = _EXPRESSION_TYPES[consume_byte() % len(_EXPRESSION_TYPES)]
        match expr_type:
            case 'Literal':
                return make_literal()
            case 'Identifier':
                return make_identifier()
            case 'BinaryExpression':
                return {
                    'type': 'BinaryExpression',
                    'operator': _BINARY_OPS[consume_byte() % len(_BINARY_OPS)],
                    'left': make_node(depth + 1),
                    'right': make_node(depth + 1),
                }
            case 'UnaryExpression':
                return {
                    'type': 'UnaryExpression',
                    'operator': _UNARY_OPS[consume_byte() % len(_UNARY_OPS)],
                    'argument': make_node(depth + 1),
                    'prefix': True,
                }
            case 'CallExpression':
                num_args = consume_byte() % max_children
                return {
                    'type': 'CallExpression',
                    'callee': make_node(depth + 1),
                    'arguments': [make_node(depth + 1) for _ in range(num_args)],
                }
            case 'MemberExpression':
                computed = consume_byte() % 2 == 0
                return {
                    'type': 'MemberExpression',
                    'object': make_node(depth + 1),
                    'property': make_node(depth + 1),
                    'computed': computed,
                }
            case 'AssignmentExpression':
                return {
                    'type': 'AssignmentExpression',
                    'operator': '=',
                    'left': make_identifier(),
                    'right': make_node(depth + 1),
                }
            case 'ConditionalExpression':
                return {
                    'type': 'ConditionalExpression',
                    'test': make_node(depth + 1),
                    'consequent': make_node(depth + 1),
                    'alternate': make_node(depth + 1),
                }
            case 'ArrayExpression':
                num = consume_byte() % max_children
                return {
                    'type': 'ArrayExpression',
                    'elements': [make_node(depth + 1) for _ in range(num)],
                }
            case 'ObjectExpression':
                num = consume_byte() % max_children
                return {
                    'type': 'ObjectExpression',
                    'properties': [
                        {
                            'type': 'Property',
                            'key': make_identifier(),
                            'value': make_node(depth + 1),
                            'kind': 'init',
                            'computed': False,
                            'method': False,
                            'shorthand': False,
                        }
                        for _ in range(num)
                    ],
                }
            case 'FunctionExpression':
                return {
                    'type': 'FunctionExpression',
                    'id': None,
                    'params': [],
                    'body': {
                        'type': 'BlockStatement',
                        'body': [make_statement(depth + 1) for _ in range(consume_byte() % 3)],
                    },
                    'generator': False,
                    'async': False,
                }
            case _:
                return {'type': 'ThisExpression'}

    def make_statement(depth: int = 0) -> dict:
        if depth >= max_depth:
            return {'type': 'ExpressionStatement', 'expression': make_literal()}

        stmt_type = _STATEMENT_TYPES[consume_byte() % len(_STATEMENT_TYPES)]
        match stmt_type:
            case 'ExpressionStatement':
                return {'type': 'ExpressionStatement', 'expression': make_node(depth + 1)}
            case 'VariableDeclaration':
                return {
                    'type': 'VariableDeclaration',
                    'declarations': [
                        {
                            'type': 'VariableDeclarator',
                            'id': make_identifier(),
                            'init': make_node(depth + 1) if consume_byte() % 2 == 0 else None,
                        }
                    ],
                    'kind': ['var', 'let', 'const'][consume_byte() % 3],
                }
            case 'ReturnStatement':
                return {
                    'type': 'ReturnStatement',
                    'argument': make_node(depth + 1) if consume_byte() % 2 == 0 else None,
                }
            case 'IfStatement':
                return {
                    'type': 'IfStatement',
                    'test': make_node(depth + 1),
                    'consequent': {'type': 'BlockStatement', 'body': [make_statement(depth + 1)]},
                    'alternate': (
                        {'type': 'BlockStatement', 'body': [make_statement(depth + 1)]}
                        if consume_byte() % 2 == 0
                        else None
                    ),
                }
            case 'WhileStatement':
                return {
                    'type': 'WhileStatement',
                    'test': make_node(depth + 1),
                    'body': {'type': 'BlockStatement', 'body': [make_statement(depth + 1)]},
                }
            case 'ForStatement':
                return {
                    'type': 'ForStatement',
                    'init': None,
                    'test': make_node(depth + 1),
                    'update': None,
                    'body': {'type': 'BlockStatement', 'body': [make_statement(depth + 1)]},
                }
            case 'BlockStatement':
                num = consume_byte() % max_children
                return {'type': 'BlockStatement', 'body': [make_statement(depth + 1) for _ in range(num)]}
            case 'EmptyStatement':
                return {'type': 'EmptyStatement'}
            case 'BreakStatement':
                return {'type': 'BreakStatement', 'label': None}
            case 'ContinueStatement':
                return {'type': 'ContinueStatement', 'label': None}
            case 'ThrowStatement':
                return {'type': 'ThrowStatement', 'argument': make_node(depth + 1)}
            case _:
                return {'type': 'EmptyStatement'}

    num_stmts = max(1, consume_byte() % 6)
    return {
        'type': 'Program',
        'body': [make_statement(0) for _ in range(num_stmts)],
        'sourceType': 'script',
    }


class SimpleFuzzedDataProvider:
    """Minimal FuzzedDataProvider for when atheris is not available."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0

    def ConsumeUnicode(self, max_length: int) -> str:
        end = min(self._pos + max_length, len(self._data))
        chunk = self._data[self._pos : end]
        self._pos = end
        return chunk.decode('utf-8', errors='replace')

    def ConsumeBytes(self, max_length: int) -> bytes:
        end = min(self._pos + max_length, len(self._data))
        chunk = self._data[self._pos : end]
        self._pos = end
        return chunk

    def ConsumeIntInRange(self, min_val: int, max_val: int) -> int:
        if self._pos < len(self._data):
            val = self._data[self._pos]
            self._pos += 1
            return min_val + (val % (max_val - min_val + 1))
        return min_val

    def ConsumeBool(self) -> bool:
        return self.ConsumeIntInRange(0, 1) == 1

    def remaining_bytes(self) -> int:
        return len(self._data) - self._pos


try:
    import atheris

    FuzzedDataProvider = atheris.FuzzedDataProvider
except ImportError:
    atheris = None
    FuzzedDataProvider = SimpleFuzzedDataProvider


def run_fuzzer(
    target_fn: Callable[[bytes], None],
    argv: list[str] | None = None,
    custom_setup: Callable | None = None,
) -> None:
    """Run a fuzz target with atheris if available, otherwise with random inputs."""
    if atheris is not None:
        if custom_setup:
            atheris.instrument_func(target_fn)
            custom_setup()
        atheris.Setup(argv or sys.argv, target_fn)
        atheris.Fuzz()
        return

    parser = argparse.ArgumentParser()
    parser.add_argument('corpus_dirs', nargs='*', default=[])
    parser.add_argument('-max_total_time', type=int, default=10)
    parser.add_argument('-max_len', type=int, default=MAX_INPUT_SIZE)
    parser.add_argument('-timeout', type=int, default=30)
    parser.add_argument('-rss_limit_mb', type=int, default=2048)
    parser.add_argument('-runs', type=int, default=0)
    args = parser.parse_args(argv[1:] if argv else sys.argv[1:])

    seeds_run = 0
    for corpus_dir in args.corpus_dirs:
        if not os.path.isdir(corpus_dir):
            continue
        for fname in sorted(os.listdir(corpus_dir)):
            fpath = os.path.join(corpus_dir, fname)
            if not os.path.isfile(fpath):
                continue
            with open(fpath, 'rb') as file_handle:
                seed_data = file_handle.read()
            try:
                target_fn(seed_data)
            except Exception as exc:
                if not isinstance(exc, SAFE_EXCEPTIONS):
                    print(f'FINDING in seed {fname}: {type(exc).__name__}: {exc}')
            seeds_run += 1

    rng = random.Random(42)
    start = time.time()
    runs = 0
    max_runs = args.runs if args.runs > 0 else float('inf')
    while time.time() - start < args.max_total_time and runs < max_runs:
        length = rng.randint(0, min(args.max_len, 4096))
        random_data = bytes(rng.randint(0, 255) for _ in range(length))
        try:
            target_fn(random_data)
        except Exception as exc:
            if not isinstance(exc, SAFE_EXCEPTIONS):
                print(f'FINDING at run {runs}: {type(exc).__name__}: {exc}')
        runs += 1

    print(f'Fuzzing complete: {seeds_run} seeds + {runs} random inputs in {time.time() - start:.1f}s')
