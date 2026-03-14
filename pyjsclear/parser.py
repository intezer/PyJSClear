"""JavaScript parser wrapper around esprima2."""

import re

import esprima


_ASYNC_KEY_MAP: dict[str, str] = {'isAsync': 'async', 'allowAwait': 'await'}

_SCALAR_TYPES = (str, int, float, bool, type(None))


def _fast_to_dict(obj: object) -> object:
    """Convert esprima AST objects to plain dicts, ~2x faster than toDict().

    Uses an explicit work stack to avoid recursion overhead on large ASTs.
    """
    _scalars = _SCALAR_TYPES
    _async_map = _ASYNC_KEY_MAP
    _Pattern = re.Pattern

    # Fast path for scalars (common case for leaf values)
    if isinstance(obj, _scalars):
        return obj

    # Work stack: (source_value, target_container, target_key_or_index)
    # We build the result top-down, pushing child values onto the stack.
    root: object = None
    stack: list[tuple[object, object, object]] = []

    def _enqueue(value: object, container: object, key: object) -> None:
        if isinstance(value, _scalars):
            container[key] = value
        elif isinstance(value, _Pattern):
            container[key] = {}
        else:
            stack.append((value, container, key))

    # Bootstrap: create a wrapper so we can store the root result
    wrapper: list[object] = [None]
    stack.append((obj, wrapper, 0))

    while stack:
        src, target, tkey = stack.pop()

        if isinstance(src, list):
            result_list: list[object] = [None] * len(src)
            target[tkey] = result_list
            for i in range(len(src) - 1, -1, -1):
                _enqueue(src[i], result_list, i)
        elif isinstance(src, _scalars):
            target[tkey] = src
        elif isinstance(src, _Pattern):
            target[tkey] = {}
        else:
            # Object with __dict__ (esprima node) or plain dict
            raw = src if isinstance(src, dict) else src.__dict__
            output: dict[str, object] = {}
            target[tkey] = output
            for k, v in raw.items():
                if k[0] == '_':  # faster than k.startswith('_')
                    continue
                if k == 'optional' and v is False:
                    continue
                k = _async_map.get(k, k)
                _enqueue(v, output, k)

    return wrapper[0]


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
