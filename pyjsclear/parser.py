"""JavaScript parser wrapper around esprima2."""

import re

import esprima


_ASYNC_KEY_MAP: dict[str, str] = {'isAsync': 'async', 'allowAwait': 'await'}


def _fast_to_dict(node: object) -> object:
    """Convert esprima AST objects to plain dicts, ~2x faster than toDict()."""
    if isinstance(node, (str, int, float, bool, type(None))):
        return node
    if isinstance(node, list):
        return [_fast_to_dict(item) for item in node]
    if isinstance(node, re.Pattern):
        return {}
    # Object with __dict__ (esprima node)
    attributes = node if isinstance(node, dict) else node.__dict__
    converted_node: dict[str, object] = {}
    for attribute_key, attribute_value in attributes.items():
        if attribute_key.startswith('_'):
            continue
        if attribute_key == 'optional' and attribute_value is False:
            continue
        normalized_key = _ASYNC_KEY_MAP.get(attribute_key, attribute_key)
        converted_node[normalized_key] = _fast_to_dict(attribute_value)
    return converted_node


def parse(source_code: str) -> dict:
    """Parse JavaScript source into an ESTree-compatible AST dict.

    Tries parseScript first, falls back to parseModule.
    Raises SyntaxError on parse failure.
    """
    try:
        return _fast_to_dict(esprima.parseScript(source_code))
    except esprima.Error:
        pass
    except Exception as parse_error:
        raise SyntaxError(f'Failed to parse JavaScript: {parse_error}') from parse_error

    try:
        return _fast_to_dict(esprima.parseModule(source_code))
    except Exception as parse_error:
        raise SyntaxError(f'Failed to parse JavaScript: {parse_error}') from parse_error
