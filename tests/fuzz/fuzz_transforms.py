#!/usr/bin/env python3
"""Fuzz target for individual transforms.

Tests each transform in isolation, bypassing the orchestrator's exception masking.
Any unhandled exception (except RecursionError) is a finding.
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from conftest_fuzz import SAFE_EXCEPTIONS
from conftest_fuzz import FuzzedDataProvider
from conftest_fuzz import bytes_to_js
from conftest_fuzz import run_fuzzer

from pyjsclear.parser import parse
from pyjsclear.scope import build_scope_tree
from pyjsclear.transforms.anti_tamper import AntiTamperRemover
from pyjsclear.transforms.constant_prop import ConstantProp
from pyjsclear.transforms.control_flow import ControlFlowRecoverer
from pyjsclear.transforms.dead_branch import DeadBranchRemover
from pyjsclear.transforms.expression_simplifier import ExpressionSimplifier
from pyjsclear.transforms.hex_escapes import HexEscapes
from pyjsclear.transforms.logical_to_if import LogicalToIf
from pyjsclear.transforms.object_packer import ObjectPacker
from pyjsclear.transforms.object_simplifier import ObjectSimplifier
from pyjsclear.transforms.property_simplifier import PropertySimplifier
from pyjsclear.transforms.proxy_functions import ProxyFunctionInliner
from pyjsclear.transforms.reassignment import ReassignmentRemover
from pyjsclear.transforms.sequence_splitter import SequenceSplitter
from pyjsclear.transforms.string_revealer import StringRevealer
from pyjsclear.transforms.unused_vars import UnusedVariableRemover


TRANSFORM_CLASSES = [
    StringRevealer,
    HexEscapes,
    UnusedVariableRemover,
    ConstantProp,
    ReassignmentRemover,
    DeadBranchRemover,
    ObjectPacker,
    ProxyFunctionInliner,
    SequenceSplitter,
    ExpressionSimplifier,
    LogicalToIf,
    ControlFlowRecoverer,
    PropertySimplifier,
    AntiTamperRemover,
    ObjectSimplifier,
]


def TestOneInput(data):
    if len(data) < 4:
        return

    fdp = FuzzedDataProvider(data)
    transform_idx = fdp.ConsumeIntInRange(0, len(TRANSFORM_CLASSES) - 1)
    transform_class = TRANSFORM_CLASSES[transform_idx]

    js_code = bytes_to_js(fdp.ConsumeBytes(fdp.remaining_bytes()))

    try:
        ast = parse(js_code)
    except (SyntaxError, RecursionError):
        return

    scope_tree = None
    node_scope = None
    if transform_class.rebuild_scope:
        try:
            scope_tree, node_scope = build_scope_tree(ast)
        except SAFE_EXCEPTIONS:
            return

    try:
        transform = transform_class(ast, scope_tree=scope_tree, node_scope=node_scope)
        transform.execute()
    except SAFE_EXCEPTIONS:
        return


if __name__ == "__main__":
    run_fuzzer(TestOneInput)
