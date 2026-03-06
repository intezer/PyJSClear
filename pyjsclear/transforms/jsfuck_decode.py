"""JSFUCK decoder.

JSFUCK encodes JavaScript using only []()!+ characters.
Decoding requires JavaScript execution, so we use Node.js subprocess.
If Node.js is unavailable, returns None (graceful degradation).
"""

import os
import re
import shutil
import subprocess
import tempfile


# JSFUCK uses only these characters (plus optional whitespace/semicolons)
_JSFUCK_RE = re.compile(r'^[\s\[\]\(\)!+;]+$')


def is_jsfuck(code):
    """Check if code is JSFUCK-encoded.

    JSFUCK code consists only of []()!+ characters (with optional whitespace/semicolons).
    We also require minimum length to avoid false positives.
    """
    stripped = code.strip()
    if len(stripped) < 100:
        return False
    # Check if code starts with JSFUCK-style patterns
    # Some JSFUCK variants have a preamble (like $ = String.fromCharCode(...))
    # so we check if the majority of the code is JSFUCK chars
    jsfuck_chars = set('[]()!+ \t\n\r;')
    jsfuck_count = sum(1 for c in stripped if c in jsfuck_chars)
    return jsfuck_count / len(stripped) > 0.9


def jsfuck_decode(code):
    """Decode JSFUCK-encoded JavaScript using Node.js. Returns decoded string or None."""
    node = shutil.which('node')
    if not node:
        return None

    stripped = code.strip()

    # Strategy: JSFUCK gets Function via []['flat']['constructor'] or similar
    # prototype chain access. We intercept by patching Function.prototype.constructor
    # and wrapping the code to capture what gets passed to Function().
    js_wrapper = (
        'var _captured = [];\n'
        'var _origFunction = Function;\n'
        # Patch the prototype chain so JSFUCK's []['constructor']['constructor'] is intercepted
        'var _handler = {\n'
        '  apply: function(target, thisArg, args) {\n'
        '    var body = args[args.length - 1];\n'
        '    if (typeof body === "string" && body.length > 0) _captured.push(body);\n'
        '    return target.apply(thisArg, args);\n'
        '  },\n'
        '  construct: function(target, args) {\n'
        '    var body = args[args.length - 1];\n'
        '    if (typeof body === "string" && body.length > 0) _captured.push(body);\n'
        '    return new target(...args);\n'
        '  }\n'
        '};\n'
        'var _proxyFn = new Proxy(_origFunction, _handler);\n'
        'Function = _proxyFn;\n'
        'Function.prototype.constructor = _proxyFn;\n'
        # Patch common prototype chains JSFUCK uses
        'Object.getPrototypeOf(function(){}).constructor = _proxyFn;\n'
        'try {\n' + stripped + '\n' + '} catch(e) {}\n'
        'Function = _origFunction;\n'
        'Function.prototype.constructor = _origFunction;\n'
        'if (_captured.length > 0) {\n'
        '  console.log(_captured[_captured.length - 1]);\n'
        '}\n'
    )

    try:
        # Write to temp file to avoid shell arg length limits
        fd, tmp_path = tempfile.mkstemp(suffix='.js')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(js_wrapper)
            result = subprocess.run(
                [node, tmp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout.strip()
            return output if output else None
        finally:
            os.unlink(tmp_path)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return None
