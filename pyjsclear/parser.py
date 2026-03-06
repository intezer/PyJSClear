"""JavaScript parser wrapper around esprima2."""

import esprima


def parse(code):
    """Parse JavaScript code into an ESTree-compatible AST.

    Returns a Program node (dict).
    Raises SyntaxError on parse failure.
    """
    try:
        return esprima.parseScript(code).toDict()
    except Exception as e:
        raise SyntaxError(f"Failed to parse JavaScript: {e}") from e
