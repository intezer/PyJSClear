"""Make esprima2's string/template scanning linear instead of quadratic.

esprima2 builds string and template literal values with ``value += ch`` in a
``while`` loop (``Scanner.scanStringLiteral`` / ``scanTemplate``). In CPython
that misses the in-place string-concat optimization, so scanning a single large
literal is O(n^2) — one multi-megabyte string literal takes tens of seconds.

The fix (proposed upstream, s0md3v/esprima2#10) is to accumulate into a list and
join once at the end. Rather than copy the method bodies, we take the installed
method source and apply that two-line transform: ``value += ch`` becomes a list
extend (``list += "chars"`` extends by character), and the accumulator is joined
at the return. Deriving from the live source keeps the patch faithful to
whatever esprima2 version is installed. It is gated to versions verified to
carry the expected source; any other version, or an unreadable source, leaves
esprima untouched.
"""

import inspect
import textwrap

import esprima
from esprima import scanner


_SUPPORTED_ESPRIMA_VERSIONS = frozenset({(5, 0, 1), (5, 0, 2), (6, 0, 0)})

# method -> (old, new) source edits turning the char-by-char accumulator into a
# list joined once at the end.
_SUBSTITUTIONS = {
    'scanStringLiteral': [("str = ''", 'str = []'), ('value=str,', "value=''.join(str),")],
    'scanTemplate': [("cooked = ''", 'cooked = []'), ('cooked=cooked,', "cooked=''.join(cooked),")],
}


def apply_patch() -> bool:
    """Rebind esprima's scanner methods to linear versions. Returns True if applied."""
    if getattr(esprima, '__version__', None) not in _SUPPORTED_ESPRIMA_VERSIONS:
        return False

    for method, edits in _SUBSTITUTIONS.items():
        func = getattr(scanner.Scanner, method)
        if getattr(func, '_linearized', False):
            continue
        try:
            source = textwrap.dedent(inspect.getsource(func))
        except OSError:
            return False
        for old, new in edits:
            if source.count(old) != 1:
                return False  # source drifted from what we verified; leave esprima untouched
            source = source.replace(old, new)
        namespace: dict = {}
        exec(source, vars(scanner), namespace)  # noqa: S102 - transform of the installed esprima source
        patched = namespace[method]
        patched._linearized = True
        setattr(scanner.Scanner, method, patched)
    return True


apply_patch()
