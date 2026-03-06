"""JJEncode decoder.

JJEncode encodes JavaScript using $ and _ variable manipulations.
This decoder uses Node.js subprocess since JJEncode requires
JavaScript execution to fully resolve the symbol table.
"""

import os
import re
import shutil
import subprocess
import tempfile


# Detection patterns for JJEncode
_JJENCODE_PATTERNS = [
    re.compile(r'\$=~\[\];'),
    re.compile(r'\$\$=\{___:\+\+\$'),
    re.compile(r'\$\$\$=\(\$\[\$\]\+""\)\[\$\]'),
    re.compile(r'[\$_]{3,}.*[\[\]]{2,}.*[\+!]{2,}'),
]


def is_jj_encoded(code):
    """Check if code is JJEncoded."""
    first_line = code.split('\n', 1)[0]
    return any(p.search(first_line) for p in _JJENCODE_PATTERNS)


def jj_decode(code):
    """Decode JJEncoded JavaScript using Node.js with Function interception."""
    if not is_jj_encoded(code):
        return None
    return _run_with_function_intercept(code)


def jj_decode_via_eval(code):
    """Simpler fallback: just run the JJEncode in Node with Function intercepted."""
    return _run_with_function_intercept(code)


def _run_with_function_intercept(code):
    """Run JS code with Function constructor intercepted via Proxy."""
    node = shutil.which('node')
    if not node:
        return None

    js_wrapper = (
        'var _captured = [];\n'
        'var _origFunction = Function;\n'
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
        'Object.getPrototypeOf(function(){}).constructor = _proxyFn;\n'
        'try {\n' + code + '\n' + '} catch(e) {}\n'
        'Function = _origFunction;\n'
        'Function.prototype.constructor = _origFunction;\n'
        'if (_captured.length > 0) {\n'
        '  console.log(_captured[_captured.length - 1]);\n'
        '}\n'
    )

    try:
        fd, tmp_path = tempfile.mkstemp(suffix='.js')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(js_wrapper)
            result = subprocess.run(
                [node, tmp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout.strip()
            return output if output else None
        finally:
            os.unlink(tmp_path)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return None
