"""Remove anti-tamper, self-defending, and debug protection patterns.

Detects common obfuscator.io patterns:
- Self-defending functions (check if code was modified)
- Debug protection (infinite debugger loops)
- Console output disabling
"""

from __future__ import annotations

import re
from typing import Any

from ..generator import generate
from ..traverser import REMOVE
from ..traverser import traverse
from .base import Transform


_DEBUGGER_PATTERN: re.Pattern[str] = re.compile(r'\bdebugger\b')
_LOOP_OR_INTERVAL_PATTERN: re.Pattern[str] = re.compile(r'\bwhile\b|\bfor\b|\bsetInterval\b')


class AntiTamperRemover(Transform):
    """Remove self-defending, debug protection, and console-disabling code."""

    rebuild_scope = True

    _SELF_DEFENDING_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r'constructor\s*\(\s*\)\s*\.\s*constructor\s*\('),
        re.compile(r'toString\s*\(\s*\)\s*\.\s*search'),
        re.compile(r'prototype\s*\.\s*toString'),
        re.compile(r'__proto__'),
    ]

    _DEBUG_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r'\bdebugger\b'),
        re.compile(r'setInterval\s*\('),
    ]

    _CONSOLE_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r'console\s*\[\s*[\'"](?:log|warn|error|info|debug|trace|exception|table)'),
        re.compile(r'console\s*\.\s*(?:log|warn|error|info|debug|trace|exception|table)\s*='),
    ]

    @staticmethod
    def _extract_iife_call(expression: dict[str, Any]) -> dict[str, Any] | None:
        """Return the CallExpression node from an IIFE wrapper, or None."""
        if expression.get('type') == 'CallExpression':
            return expression
        if (
            expression.get('type') == 'UnaryExpression'
            and expression.get('argument', {}).get('type') == 'CallExpression'
        ):
            return expression.get('argument')
        return None

    def _matches_anti_tamper_pattern(self, source: str) -> bool:
        """Return True if source contains self-defending, debug, or console-disabling code."""
        if any(pattern.search(source) for pattern in self._SELF_DEFENDING_PATTERNS):
            return True
        if _DEBUGGER_PATTERN.search(source) and _LOOP_OR_INTERVAL_PATTERN.search(source):
            return True
        return any(pattern.search(source) for pattern in self._CONSOLE_PATTERNS)

    def _find_anti_tamper_nodes(self) -> list[dict[str, Any]]:
        """Traverse the AST and collect expression statements that match anti-tamper patterns."""
        flagged_nodes: list[dict[str, Any]] = []

        def enter(node: dict[str, Any], parent: dict[str, Any], key: str, index: int | None) -> None:
            """Flag IIFE expression statements that contain anti-tamper code."""
            if node.get('type') != 'ExpressionStatement':
                return

            expression = node.get('expression')
            if not expression:
                return

            call_node = self._extract_iife_call(expression)
            if not call_node:
                return

            callee = call_node.get('callee')
            if not callee:
                return
            if callee.get('type') not in (
                'FunctionExpression',
                'ArrowFunctionExpression',
            ):
                return

            try:
                generated_source = generate(callee)
            except Exception:
                return

            if self._matches_anti_tamper_pattern(generated_source):
                flagged_nodes.append(node)

        traverse(self.ast, {'enter': enter})
        return flagged_nodes

    def _remove_nodes(self, nodes: list[dict[str, Any]]) -> None:
        """Remove the given nodes from the AST and mark the transform as changed."""
        removal_ids: set[int] = {id(node) for node in nodes}

        def enter(node: dict[str, Any], parent: dict[str, Any], key: str, index: int | None) -> object | None:
            """Return REMOVE sentinel for flagged nodes."""
            if id(node) in removal_ids:
                self.set_changed()
                return REMOVE
            return None

        traverse(self.ast, {'enter': enter})

    def execute(self) -> bool:
        """Scan for and remove anti-tamper IIFEs. Return True if AST was modified."""
        flagged_nodes = self._find_anti_tamper_nodes()
        if flagged_nodes:
            self._remove_nodes(flagged_nodes)
        return self.has_changed()
