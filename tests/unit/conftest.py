"""Shared test helpers for pyjsclear unit tests."""

from pyjsclear.parser import parse
from pyjsclear.generator import generate


def roundtrip(js_code, transform_class):
    """Parse JS, apply a transform, return (generated_code, changed)."""
    ast = parse(js_code)
    t = transform_class(ast)
    changed = t.execute()
    return generate(ast), changed


def parse_expr(js_expr):
    """Parse a JS expression and return the expression AST node."""
    ast = parse(js_expr + ';')
    return ast['body'][0]['expression']


def normalize(js_code):
    """Collapse all whitespace to single spaces for comparison."""
    return ' '.join(js_code.split())
