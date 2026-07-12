"""Performance regression test for incremental parent-map maintenance (TKT-16478).

Transforms replace nodes in place; before the fix, every replacement dropped the
cached parent map, forcing a full O(N) rebuild on the next lookup — quadratic
overall when thousands of proxy-object references are inlined.
"""

import signal
import time

import pyjsclear


_PROXY_OBJECT_OBFUSCATION = (
    "var _0xmap = {"
    + ",".join(f"'k{i}': {i}" for i in range(4000))
    + "};\n"
    + ";".join(f"console.log(_0xmap.k{i})" for i in range(4000))
    + ";\n"
)


class _TestTimeout(BaseException):
    """Raised by the alarm handler.

    Derives from BaseException so it sails past the deobfuscator pipeline's
    broad `except Exception` (deobfuscator.py) and actually kills the test at
    the deadline instead of being swallowed and stalling CI for the full
    quadratic runtime.
    """


class TestIncrementalParentMap:
    def test_object_simplifier_is_not_quadratic_on_many_references(self):
        def _timeout(signum, frame):
            raise _TestTimeout()

        old_handler = signal.signal(signal.SIGALRM, _timeout)
        signal.setitimer(signal.ITIMER_REAL, 20)
        try:
            start = time.monotonic()
            result = pyjsclear.deobfuscate(_PROXY_OBJECT_OBFUSCATION)
            elapsed = time.monotonic() - start
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)

        # Inlining happened (proxy map references replaced by their literal values).
        assert '_0xmap.k0' not in result
        # And it did not take quadratic time (pre-fix this is minutes).
        assert elapsed < 15
