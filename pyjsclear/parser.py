"""JavaScript parser wrapper around esprima2."""

import re

import esprima

_ASYNC_MAP = {'isAsync': 'async', 'allowAwait': 'await'}


def _fast_to_dict(obj):
    """Convert esprima AST objects to plain dicts, ~2x faster than toDict()."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, list):
        return [_fast_to_dict(item) for item in obj]
    if isinstance(obj, re.Pattern):
        return {}
    # Object with __dict__ (esprima node)
    d = obj if isinstance(obj, dict) else obj.__dict__
    result = {}
    for k, v in d.items():
        if v is None or k.startswith('_'):
            continue
        if k == 'optional' and v is False:
            continue
        k = _ASYNC_MAP.get(k, k)
        result[k] = _fast_to_dict(v)
    return result


def parse(code):
    """Parse JavaScript code into an ESTree-compatible AST.

    Returns a Program node (dict).
    Raises SyntaxError on parse failure.
    """
    try:
        return _fast_to_dict(esprima.parseScript(code))
    except Exception as e:
        raise SyntaxError(f'Failed to parse JavaScript: {e}') from e
