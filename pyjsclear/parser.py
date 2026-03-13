"""JavaScript parser wrapper around esprima2."""

import re

import esprima


_ASYNC_MAP = {'isAsync': 'async', 'allowAwait': 'await'}


def _fast_to_dict(obj: object) -> object:
    """Convert esprima AST objects to plain dicts, ~2x faster than toDict()."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, list):
        return [_fast_to_dict(item) for item in obj]
    if isinstance(obj, re.Pattern):
        return {}
    # Object with __dict__ (esprima node)
    result_dict = obj if isinstance(obj, dict) else obj.__dict__
    output = {}
    for key, value in result_dict.items():
        if key.startswith('_'):
            continue
        if key == 'optional' and value is False:
            continue
        key = _ASYNC_MAP.get(key, key)
        output[key] = _fast_to_dict(value)
    return output


def parse(code: str) -> dict:
    """Parse JavaScript code into an ESTree-compatible AST.

    Returns a Program node (dict).
    Raises SyntaxError on parse failure.
    """
    try:
        return _fast_to_dict(esprima.parseScript(code))
    except esprima.Error:
        try:
            return _fast_to_dict(esprima.parseModule(code))
        except Exception as e:
            raise SyntaxError(f'Failed to parse JavaScript: {e}') from e
    except Exception as e:
        raise SyntaxError(f'Failed to parse JavaScript: {e}') from e
