"""Shared helpers for fuzz targets."""

import os
import random
import struct
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

MAX_INPUT_SIZE = 102_400  # 100KB cap

SAFE_EXCEPTIONS = (RecursionError,)

# ESTree node types for synthetic AST generation
_STATEMENT_TYPES = [
    "ExpressionStatement",
    "VariableDeclaration",
    "ReturnStatement",
    "IfStatement",
    "WhileStatement",
    "ForStatement",
    "BlockStatement",
    "EmptyStatement",
    "BreakStatement",
    "ContinueStatement",
    "ThrowStatement",
]

_EXPRESSION_TYPES = [
    "Literal",
    "Identifier",
    "BinaryExpression",
    "UnaryExpression",
    "CallExpression",
    "MemberExpression",
    "AssignmentExpression",
    "ConditionalExpression",
    "ArrayExpression",
    "ObjectExpression",
    "FunctionExpression",
    "ThisExpression",
]

_BINARY_OPS = [
    "+",
    "-",
    "*",
    "/",
    "%",
    "==",
    "!=",
    "===",
    "!==",
    "<",
    ">",
    "<=",
    ">=",
    "&&",
    "||",
    "&",
    "|",
    "^",
    "<<",
    ">>",
    ">>>",
]
_UNARY_OPS = ["-", "+", "!", "~", "typeof", "void"]


def bytes_to_js(data):
    """Decode bytes to a JS string with size limit."""
    text = data[:MAX_INPUT_SIZE].decode("utf-8", errors="replace")
    return text


def bytes_to_ast_dict(data, max_depth=5, max_children=4):
    """Build a synthetic ESTree AST dict from bytes for testing generator/traverser."""
    rng = random.Random(int.from_bytes(data[:8].ljust(8, b"\x00"), "little"))
    pos = 8

    def consume_byte():
        nonlocal pos
        if pos < len(data):
            val = data[pos]
            pos += 1
            return val
        return rng.randint(0, 255)

    def make_literal():
        kind = consume_byte() % 4
        if kind == 0:
            return {"type": "Literal", "value": consume_byte(), "raw": str(consume_byte())}
        elif kind == 1:
            return {"type": "Literal", "value": True, "raw": "true"}
        elif kind == 2:
            return {"type": "Literal", "value": None, "raw": "null"}
        else:
            return {"type": "Literal", "value": "fuzz", "raw": '"fuzz"'}

    def make_identifier():
        names = ["a", "b", "c", "x", "y", "foo", "bar", "_", "$"]
        return {"type": "Identifier", "name": names[consume_byte() % len(names)]}

    def make_node(depth=0):
        if depth >= max_depth:
            return make_literal() if consume_byte() % 2 == 0 else make_identifier()

        type_idx = consume_byte()
        if type_idx % 3 == 0:
            # Expression
            expr_type = _EXPRESSION_TYPES[consume_byte() % len(_EXPRESSION_TYPES)]
            if expr_type == "Literal":
                return make_literal()
            elif expr_type == "Identifier":
                return make_identifier()
            elif expr_type == "BinaryExpression":
                return {
                    "type": "BinaryExpression",
                    "operator": _BINARY_OPS[consume_byte() % len(_BINARY_OPS)],
                    "left": make_node(depth + 1),
                    "right": make_node(depth + 1),
                }
            elif expr_type == "UnaryExpression":
                return {
                    "type": "UnaryExpression",
                    "operator": _UNARY_OPS[consume_byte() % len(_UNARY_OPS)],
                    "argument": make_node(depth + 1),
                    "prefix": True,
                }
            elif expr_type == "CallExpression":
                num_args = consume_byte() % max_children
                return {
                    "type": "CallExpression",
                    "callee": make_node(depth + 1),
                    "arguments": [make_node(depth + 1) for _ in range(num_args)],
                }
            elif expr_type == "MemberExpression":
                computed = consume_byte() % 2 == 0
                return {
                    "type": "MemberExpression",
                    "object": make_node(depth + 1),
                    "property": make_node(depth + 1),
                    "computed": computed,
                }
            elif expr_type == "AssignmentExpression":
                return {
                    "type": "AssignmentExpression",
                    "operator": "=",
                    "left": make_identifier(),
                    "right": make_node(depth + 1),
                }
            elif expr_type == "ConditionalExpression":
                return {
                    "type": "ConditionalExpression",
                    "test": make_node(depth + 1),
                    "consequent": make_node(depth + 1),
                    "alternate": make_node(depth + 1),
                }
            elif expr_type == "ArrayExpression":
                num = consume_byte() % max_children
                return {
                    "type": "ArrayExpression",
                    "elements": [make_node(depth + 1) for _ in range(num)],
                }
            elif expr_type == "ObjectExpression":
                num = consume_byte() % max_children
                return {
                    "type": "ObjectExpression",
                    "properties": [
                        {
                            "type": "Property",
                            "key": make_identifier(),
                            "value": make_node(depth + 1),
                            "kind": "init",
                            "computed": False,
                            "method": False,
                            "shorthand": False,
                        }
                        for _ in range(num)
                    ],
                }
            elif expr_type == "FunctionExpression":
                return {
                    "type": "FunctionExpression",
                    "id": None,
                    "params": [],
                    "body": {
                        "type": "BlockStatement",
                        "body": [make_statement(depth + 1) for _ in range(consume_byte() % 3)],
                    },
                    "generator": False,
                    "async": False,
                }
            else:
                return {"type": "ThisExpression"}
        else:
            return make_statement(depth)

    def make_statement(depth=0):
        if depth >= max_depth:
            return {
                "type": "ExpressionStatement",
                "expression": make_literal(),
            }

        stmt_type = _STATEMENT_TYPES[consume_byte() % len(_STATEMENT_TYPES)]
        if stmt_type == "ExpressionStatement":
            return {"type": "ExpressionStatement", "expression": make_node(depth + 1)}
        elif stmt_type == "VariableDeclaration":
            return {
                "type": "VariableDeclaration",
                "declarations": [
                    {
                        "type": "VariableDeclarator",
                        "id": make_identifier(),
                        "init": make_node(depth + 1) if consume_byte() % 2 == 0 else None,
                    }
                ],
                "kind": ["var", "let", "const"][consume_byte() % 3],
            }
        elif stmt_type == "ReturnStatement":
            return {"type": "ReturnStatement", "argument": make_node(depth + 1) if consume_byte() % 2 == 0 else None}
        elif stmt_type == "IfStatement":
            return {
                "type": "IfStatement",
                "test": make_node(depth + 1),
                "consequent": {"type": "BlockStatement", "body": [make_statement(depth + 1)]},
                "alternate": (
                    {"type": "BlockStatement", "body": [make_statement(depth + 1)]} if consume_byte() % 2 == 0 else None
                ),
            }
        elif stmt_type == "WhileStatement":
            return {
                "type": "WhileStatement",
                "test": make_node(depth + 1),
                "body": {"type": "BlockStatement", "body": [make_statement(depth + 1)]},
            }
        elif stmt_type == "ForStatement":
            return {
                "type": "ForStatement",
                "init": None,
                "test": make_node(depth + 1),
                "update": None,
                "body": {"type": "BlockStatement", "body": [make_statement(depth + 1)]},
            }
        elif stmt_type == "BlockStatement":
            num = consume_byte() % max_children
            return {"type": "BlockStatement", "body": [make_statement(depth + 1) for _ in range(num)]}
        elif stmt_type == "EmptyStatement":
            return {"type": "EmptyStatement"}
        elif stmt_type == "BreakStatement":
            return {"type": "BreakStatement", "label": None}
        elif stmt_type == "ContinueStatement":
            return {"type": "ContinueStatement", "label": None}
        elif stmt_type == "ThrowStatement":
            return {"type": "ThrowStatement", "argument": make_node(depth + 1)}
        return {"type": "EmptyStatement"}

    num_stmts = max(1, consume_byte() % 6)
    return {
        "type": "Program",
        "body": [make_statement(0) for _ in range(num_stmts)],
        "sourceType": "script",
    }


class SimpleFuzzedDataProvider:
    """Minimal FuzzedDataProvider for when atheris is not available."""

    def __init__(self, data):
        self._data = data
        self._pos = 0

    def ConsumeUnicode(self, max_length):
        end = min(self._pos + max_length, len(self._data))
        chunk = self._data[self._pos : end]
        self._pos = end
        return chunk.decode("utf-8", errors="replace")

    def ConsumeBytes(self, max_length):
        end = min(self._pos + max_length, len(self._data))
        chunk = self._data[self._pos : end]
        self._pos = end
        return chunk

    def ConsumeIntInRange(self, min_val, max_val):
        if self._pos < len(self._data):
            val = self._data[self._pos]
            self._pos += 1
            return min_val + (val % (max_val - min_val + 1))
        return min_val

    def ConsumeBool(self):
        return self.ConsumeIntInRange(0, 1) == 1

    def remaining_bytes(self):
        return len(self._data) - self._pos


try:
    import atheris

    FuzzedDataProvider = atheris.FuzzedDataProvider
except ImportError:
    atheris = None
    FuzzedDataProvider = SimpleFuzzedDataProvider


def run_fuzzer(target_fn, argv=None, custom_setup=None):
    """Run a fuzz target with atheris if available, otherwise with random inputs."""
    if atheris is not None:
        if custom_setup:
            atheris.instrument_func(target_fn)
            custom_setup()
        atheris.Setup(argv or sys.argv, target_fn)
        atheris.Fuzz()
    else:
        # Standalone random-based fuzzing
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("corpus_dirs", nargs="*", default=[])
        parser.add_argument("-max_total_time", type=int, default=10)
        parser.add_argument("-max_len", type=int, default=MAX_INPUT_SIZE)
        parser.add_argument("-timeout", type=int, default=30)
        parser.add_argument("-rss_limit_mb", type=int, default=2048)
        parser.add_argument("-runs", type=int, default=0)
        args = parser.parse_args(argv[1:] if argv else sys.argv[1:])

        # First, run seed corpus files
        seeds_run = 0
        for corpus_dir in args.corpus_dirs:
            if os.path.isdir(corpus_dir):
                for fname in sorted(os.listdir(corpus_dir)):
                    fpath = os.path.join(corpus_dir, fname)
                    if os.path.isfile(fpath):
                        with open(fpath, "rb") as f:
                            data = f.read()
                        try:
                            target_fn(data)
                        except Exception as e:
                            if not isinstance(e, SAFE_EXCEPTIONS):
                                print(f"FINDING in seed {fname}: {type(e).__name__}: {e}")
                        seeds_run += 1

        # Then random inputs
        import time

        rng = random.Random(42)
        start = time.time()
        runs = 0
        max_runs = args.runs if args.runs > 0 else float("inf")
        while time.time() - start < args.max_total_time and runs < max_runs:
            length = rng.randint(0, min(args.max_len, 4096))
            data = bytes(rng.randint(0, 255) for _ in range(length))
            try:
                target_fn(data)
            except Exception as e:
                if not isinstance(e, SAFE_EXCEPTIONS):
                    print(f"FINDING at run {runs}: {type(e).__name__}: {e}")
            runs += 1

        print(f"Fuzzing complete: {seeds_run} seeds + {runs} random inputs in {time.time() - start:.1f}s")
