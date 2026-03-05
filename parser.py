"""JavaScript parser wrapper around pyjsparser."""

import pyjsparser


def parse(code):
    """Parse JavaScript code into an ESTree-compatible AST.

    Returns a Program node (dict).
    Raises SyntaxError on parse failure.
    """
    try:
        return pyjsparser.parse(code)
    except Exception as e:
        raise SyntaxError(f"Failed to parse JavaScript: {e}") from e
