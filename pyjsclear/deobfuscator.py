"""Multi-pass deobfuscation orchestrator."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from .generator import generate
from .parser import parse
from .scope import build_scope_tree
from .transforms.aa_decode import aa_decode
from .transforms.aa_decode import is_aa_encoded
from .transforms.anti_tamper import AntiTamperRemover
from .transforms.class_static_resolver import ClassStaticResolver
from .transforms.class_string_decoder import ClassStringDecoder
from .transforms.cleanup import EmptyIfRemover
from .transforms.cleanup import LetToConst
from .transforms.cleanup import OptionalCatchBinding
from .transforms.cleanup import ReturnUndefinedCleanup
from .transforms.cleanup import TrailingReturnRemover
from .transforms.cleanup import VarToConst
from .transforms.constant_prop import ConstantProp
from .transforms.control_flow import ControlFlowRecoverer
from .transforms.dead_branch import DeadBranchRemover
from .transforms.dead_class_props import DeadClassPropRemover
from .transforms.dead_expressions import DeadExpressionRemover
from .transforms.dead_object_props import DeadObjectPropRemover
from .transforms.else_if_flatten import ElseIfFlattener
from .transforms.enum_resolver import EnumResolver
from .transforms.eval_unpack import eval_unpack
from .transforms.eval_unpack import is_eval_packed
from .transforms.expression_simplifier import ExpressionSimplifier
from .transforms.global_alias import GlobalAliasInliner
from .transforms.hex_escapes import HexEscapes
from .transforms.hex_escapes import decode_hex_escapes_source
from .transforms.hex_numerics import HexNumerics
from .transforms.jj_decode import is_jj_encoded
from .transforms.jj_decode import jj_decode
from .transforms.jsfuck_decode import is_jsfuck
from .transforms.jsfuck_decode import jsfuck_decode
from .transforms.logical_to_if import LogicalToIf
from .transforms.member_chain_resolver import MemberChainResolver
from .transforms.noop_calls import NoopCallRemover
from .transforms.nullish_coalescing import NullishCoalescing
from .transforms.object_packer import ObjectPacker
from .transforms.object_simplifier import ObjectSimplifier
from .transforms.optional_chaining import OptionalChaining
from .transforms.property_simplifier import PropertySimplifier
from .transforms.proxy_functions import ProxyFunctionInliner
from .transforms.reassignment import ReassignmentRemover
from .transforms.require_inliner import RequireInliner
from .transforms.sequence_splitter import SequenceSplitter
from .transforms.single_use_vars import SingleUseVarInliner
from .transforms.string_revealer import StringRevealer
from .transforms.unreachable_code import UnreachableCodeRemover
from .transforms.unused_vars import UnusedVariableRemover
from .transforms.variable_renamer import VariableRenamer
from .transforms.xor_string_decode import XorStringDecoder
from .traverser import simple_traverse


if TYPE_CHECKING:
    from collections.abc import Callable

    # Type alias for detector/decoder pairs used in pre-passes
    type PrePassEntry = tuple[Callable[[str], bool], Callable[[str], str | None]]

_SCOPE_TRANSFORMS: frozenset[type] = frozenset(
    {
        ConstantProp,
        SingleUseVarInliner,
        ReassignmentRemover,
        ProxyFunctionInliner,
        UnusedVariableRemover,
        ObjectSimplifier,
        StringRevealer,
        VariableRenamer,
        VarToConst,
        LetToConst,
    }
)

# StringRevealer runs first to decode string arrays before other transforms
# modify wrapper function structure. Remaining order follows obfuscator-io-deobfuscator.
TRANSFORM_CLASSES: list[type] = [
    StringRevealer,
    HexEscapes,
    HexNumerics,
    ClassStringDecoder,
    XorStringDecoder,
    MemberChainResolver,
    DeadClassPropRemover,
    ClassStaticResolver,
    EnumResolver,
    RequireInliner,
    GlobalAliasInliner,
    UnusedVariableRemover,
    ConstantProp,
    ReassignmentRemover,
    SingleUseVarInliner,
    DeadBranchRemover,
    UnreachableCodeRemover,
    NoopCallRemover,
    EmptyIfRemover,
    DeadObjectPropRemover,
    ObjectPacker,
    ProxyFunctionInliner,
    SequenceSplitter,
    DeadExpressionRemover,
    ExpressionSimplifier,
    NullishCoalescing,
    OptionalChaining,
    LogicalToIf,
    ElseIfFlattener,
    OptionalCatchBinding,
    ReturnUndefinedCleanup,
    TrailingReturnRemover,
    ControlFlowRecoverer,
    PropertySimplifier,
    AntiTamperRemover,
    ObjectSimplifier,
    StringRevealer,
]

_EXPENSIVE_TRANSFORMS: frozenset[type] = frozenset({ControlFlowRecoverer, ProxyFunctionInliner, ObjectPacker})

_POST_PASS_TRANSFORMS: list[type] = [VariableRenamer, VarToConst, LetToConst]

# File-size thresholds
_LARGE_FILE_SIZE: int = 500_000  # 500 KB — reduce iterations
_MAX_CODE_SIZE: int = 2_000_000  # 2 MB — use lite mode
_LITE_MAX_ITERATIONS: int = 10
_NODE_COUNT_LIMIT: int = 50_000  # skip ControlFlowRecoverer above this
_VERY_LARGE_NODE_COUNT: int = 100_000  # cap iterations to 3

# Ordered detector/decoder pairs for the pre-pass stage.
_PRE_PASS_ENTRIES: list[PrePassEntry] = [
    (is_jsfuck, jsfuck_decode),
    (is_aa_encoded, aa_decode),
    (is_jj_encoded, jj_decode),
    (is_eval_packed, eval_unpack),
]


def _count_nodes(syntax_tree: dict) -> int:
    """Return the total number of nodes in *syntax_tree*."""
    count: int = 0

    def _increment(node: dict, parent: dict | None) -> None:
        nonlocal count
        count += 1

    simple_traverse(syntax_tree, _increment)
    return count


class Deobfuscator:
    """Multi-pass JavaScript deobfuscator.

    Applies a configurable sequence of AST transforms in a loop until the code
    stabilises or *max_iterations* is reached, then runs cosmetic post-passes.
    """

    _MAX_OUTER_CYCLES: int = 5

    def __init__(self, code: str, max_iterations: int = 50) -> None:
        self.original_code: str = code
        self.max_iterations: int = max_iterations

    def _run_pre_passes(self, code: str) -> str | None:
        """Detect whole-file encodings (JSFuck, AAEncode, etc.) and decode them.

        Returns the decoded source when a known encoding is found, or ``None``
        to continue with the normal AST pipeline.
        """
        # Look up via module globals so unittest.mock.patch can intercept.
        module = sys.modules[__name__]
        for detector, decoder in _PRE_PASS_ENTRIES:
            if not getattr(module, detector.__name__)(code):
                continue
            decoded = getattr(module, decoder.__name__)(code)
            if decoded:
                return decoded
        return None

    def execute(self) -> str:
        """Run all deobfuscation passes and return cleaned JavaScript source."""
        code = self.original_code

        decoded = self._run_pre_passes(code)
        if decoded:
            recursive_deobfuscator = Deobfuscator(decoded, max_iterations=self.max_iterations)
            return recursive_deobfuscator.execute()

        syntax_tree = self._try_parse_or_fallback(code)
        if isinstance(syntax_tree, str):
            return syntax_tree

        return self._transform_loop(syntax_tree, code)

    def _try_parse_or_fallback(self, code: str) -> dict | str:
        """Parse *code* into an AST, falling back to hex-decode on failure.

        Returns the parsed AST dict on success, or a decoded/original source
        string when parsing fails.
        """
        try:
            return parse(code)
        except SyntaxError:
            decoded = decode_hex_escapes_source(code)
            if decoded != code:
                return decoded
            return self.original_code

    def _transform_loop(self, syntax_tree: dict, code: str) -> str:
        """Run the outer generate-reparse convergence loop and post-passes.

        Returns the best deobfuscated source produced.
        """
        previous_code = code
        last_changed_tree: dict | None = None

        try:
            for _cycle in range(self._MAX_OUTER_CYCLES):
                changed = self._run_ast_transforms(
                    syntax_tree,
                    code_size=len(previous_code),
                )

                if not changed:
                    break

                last_changed_tree = syntax_tree
                generated = self._try_generate(syntax_tree)
                if generated is None or generated == previous_code:
                    break

                previous_code = generated
                try:
                    syntax_tree = parse(generated)
                except SyntaxError:
                    break

            any_post_changed = self._run_post_passes(syntax_tree)

            if last_changed_tree is None and not any_post_changed:
                return self.original_code

            return self._try_generate(syntax_tree) or previous_code
        except RecursionError:
            # Deeply nested JS can exceed Python's recursion limit during
            # parsing or AST walking. Return best result so far.
            return previous_code

    @staticmethod
    def _try_generate(syntax_tree: dict) -> str | None:
        """Generate source from *syntax_tree*, returning ``None`` on failure."""
        try:
            return generate(syntax_tree)
        except Exception:
            return None

    @staticmethod
    def _run_post_passes(syntax_tree: dict) -> bool:
        """Run cosmetic post-passes (renaming, var-to-const).

        Returns ``True`` if any post-pass modified the AST.
        """
        any_changed = False
        for post_transform_class in _POST_PASS_TRANSFORMS:
            try:
                if post_transform_class(syntax_tree).execute():
                    any_changed = True
            except Exception:
                pass
        return any_changed

    def _run_ast_transforms(self, syntax_tree: dict, code_size: int = 0) -> bool:
        """Run all AST transform passes.

        Returns ``True`` if any transform modified the AST.
        """
        node_count = _count_nodes(syntax_tree) if code_size > _LARGE_FILE_SIZE else 0
        iteration_limit = self._compute_iteration_limit(code_size, node_count)
        active_transforms = self._select_transforms(code_size, node_count)

        skipped_transforms: set[type] = set()

        scope_tree: dict | None = None
        node_scope: dict | None = None
        scope_dirty: bool = True

        any_transform_changed = False
        for iteration in range(iteration_limit):
            modified = False
            for transform_class in active_transforms:
                if transform_class in skipped_transforms:
                    continue

                result, scope_tree, node_scope, scope_dirty = self._execute_single_transform(
                    syntax_tree,
                    transform_class,
                    scope_tree,
                    node_scope,
                    scope_dirty,
                )

                if result is None:
                    continue
                if result:
                    modified = True
                    any_transform_changed = True
                elif iteration > 0:
                    skipped_transforms.add(transform_class)

            if not modified:
                break

        return any_transform_changed

    def _compute_iteration_limit(self, code_size: int, node_count: int) -> int:
        """Determine the maximum iteration count based on file/AST size."""
        limit = self.max_iterations
        if code_size > _LARGE_FILE_SIZE:
            limit = min(limit, _LITE_MAX_ITERATIONS)
        if node_count > _VERY_LARGE_NODE_COUNT:
            limit = min(limit, 3)
        return limit

    @staticmethod
    def _select_transforms(code_size: int, node_count: int) -> list[type]:
        """Return the transform list, excluding expensive ones for large inputs."""
        if code_size > _MAX_CODE_SIZE or node_count > _NODE_COUNT_LIMIT:
            return [transform for transform in TRANSFORM_CLASSES if transform not in _EXPENSIVE_TRANSFORMS]
        return TRANSFORM_CLASSES

    @staticmethod
    def _execute_single_transform(
        syntax_tree: dict,
        transform_class: type,
        scope_tree: dict | None,
        node_scope: dict | None,
        scope_dirty: bool,
    ) -> tuple[bool | None, dict | None, dict | None, bool]:
        """Run a single transform, rebuilding scope lazily as needed.

        Returns ``(result, scope_tree, node_scope, scope_dirty)`` where
        *result* is ``True``/``False`` for success/no-change, or ``None``
        if the transform raised an exception.
        """
        try:
            if transform_class in _SCOPE_TRANSFORMS and scope_dirty:
                scope_tree, node_scope = build_scope_tree(syntax_tree)
                scope_dirty = False

            if transform_class in _SCOPE_TRANSFORMS:
                transform = transform_class(
                    syntax_tree,
                    scope_tree=scope_tree,
                    node_scope=node_scope,
                )
            else:
                transform = transform_class(syntax_tree)

            result = transform.execute()
        except Exception:
            return None, scope_tree, node_scope, scope_dirty

        if result:
            scope_dirty = True
        return result, scope_tree, node_scope, scope_dirty
