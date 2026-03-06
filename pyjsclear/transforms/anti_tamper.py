"""Remove anti-tamper, self-defending, and debug protection patterns.

Detects common obfuscator.io patterns:
- Self-defending functions (check if code was modified)
- Debug protection (infinite debugger loops)
- Console output disabling
"""

import re

from .base import Transform
from ..generator import generate
from ..traverser import REMOVE
from ..traverser import traverse


class AntiTamperRemover(Transform):
    """Remove self-defending, debug protection, and console-disabling code."""

    rebuild_scope = True

    # Patterns to match in generated code for suspicious IIFEs
    _SELF_DEFENDING_PATTERNS = [
        re.compile(r'constructor\s*\(\s*\)\s*\.\s*constructor\s*\('),
        re.compile(r'toString\s*\(\s*\)\s*\.\s*search'),
        re.compile(r'prototype\s*\.\s*toString'),
        re.compile(r'__proto__'),
    ]

    _DEBUG_PATTERNS = [
        re.compile(r'\bdebugger\b'),
        re.compile(r'setInterval\s*\('),
    ]

    _CONSOLE_PATTERNS = [
        re.compile(
            r'console\s*\[\s*[\'"](?:log|warn|error|info|debug|trace|exception|table)'
        ),
        re.compile(
            r'console\s*\.\s*(?:log|warn|error|info|debug|trace|exception|table)\s*='
        ),
    ]

    def execute(self):
        nodes_to_remove = []

        def enter(node, parent, key, index):
            if node.get('type') != 'ExpressionStatement':
                return
            expr = node.get('expression')
            if not expr:
                return

            # Check for IIFE patterns: (function(){...})() or !function(){...}()
            call = None
            if expr.get('type') == 'CallExpression':
                call = expr
            elif (
                expr.get('type') == 'UnaryExpression'
                and expr.get('argument', {}).get('type') == 'CallExpression'
            ):
                call = expr.get('argument')

            if not call:
                return

            callee = call.get('callee')
            if not callee:
                return
            if callee.get('type') not in (
                'FunctionExpression',
                'ArrowFunctionExpression',
            ):
                return

            # Generate code and check against patterns
            try:
                src = generate(callee)
            except Exception:
                return

            # Check self-defending
            for pattern in self._SELF_DEFENDING_PATTERNS:
                if pattern.search(src):
                    nodes_to_remove.append(node)
                    return

            # Check debug protection
            if any(p.search(src) for p in self._DEBUG_PATTERNS):
                # Only remove if it looks like a debug trap (has debugger + loop/interval)
                if re.search(r'\bdebugger\b', src) and (
                    re.search(r'\bwhile\b|\bfor\b|\bsetInterval\b', src)
                ):
                    nodes_to_remove.append(node)
                    return

            # Check console disabling
            for pattern in self._CONSOLE_PATTERNS:
                if pattern.search(src):
                    nodes_to_remove.append(node)
                    return

        traverse(self.ast, {'enter': enter})

        # Remove flagged nodes
        if nodes_to_remove:
            remove_set = set(id(n) for n in nodes_to_remove)

            def remover(node, parent, key, index):
                if id(node) in remove_set:
                    self.set_changed()
                    return REMOVE

            traverse(self.ast, {'enter': remover})

        return self.has_changed()
