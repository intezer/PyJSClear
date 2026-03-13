"""Shared test helpers for pyjsclear unit tests."""

from typing import Any

from pyjsclear.generator import generate
from pyjsclear.parser import parse


def roundtrip(js_code: str, transform_class: type) -> tuple[str, bool]:
    """Parse JS, apply a transform, return (generated_code, changed)."""
    ast = parse(js_code)
    t = transform_class(ast)
    changed = t.execute()
    return generate(ast), changed


def parse_expr(js_expr: str) -> dict[str, Any]:
    """Parse a JS expression and return the expression AST node."""
    ast = parse(js_expr + ';')
    return ast['body'][0]['expression']


def normalize(js_code: str) -> str:
    """Collapse all whitespace to single spaces for comparison."""
    return ' '.join(js_code.split())
