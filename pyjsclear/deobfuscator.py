"""Multi-pass deobfuscation orchestrator."""

from .generator import generate
from .parser import parse
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
from .transforms.aa_decode import aa_decode
from .transforms.aa_decode import is_aa_encoded
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


# StringRevealer runs first to handle string arrays before other transforms
# modify the wrapper function structure.
# Remaining transforms follow obfuscator-io-deobfuscator order.
TRANSFORM_CLASSES = [
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

# Expensive transforms to skip in lite mode (large files)
_EXPENSIVE_TRANSFORMS = {ControlFlowRecoverer, ProxyFunctionInliner, ObjectPacker}

# Large file thresholds
_LARGE_FILE_SIZE = 500_000  # 500KB - reduce iterations
_MAX_CODE_SIZE = 2_000_000  # 2MB - use lite mode
_LITE_MAX_ITERATIONS = 10
_NODE_COUNT_LIMIT = 50_000  # Skip ControlFlowRecoverer above this


def _count_nodes(ast: dict) -> int:
    """Count total AST nodes."""
    count = 0

    def increment_count(node: dict, parent: dict | None) -> None:
        nonlocal count
        count += 1

    simple_traverse(ast, increment_count)
    return count


class Deobfuscator:
    """Multi-pass JavaScript deobfuscator."""

    def __init__(self, code: str, max_iterations: int = 50) -> None:
        self.original_code = code
        self.max_iterations = max_iterations

    def _run_pre_passes(self, code: str) -> str | None:
        """Run encoding detection and eval unpacking pre-passes.

        Returns decoded code if an encoding/packing was detected and decoded,
        or None to continue with the normal AST pipeline.
        """
        # JSFuck check (must be first — these are whole-file encodings)
        if is_jsfuck(code):
            decoded = jsfuck_decode(code)
            if decoded:
                return decoded

        # AAEncode check
        if is_aa_encoded(code):
            decoded = aa_decode(code)
            if decoded:
                return decoded

        # JJEncode check
        if is_jj_encoded(code):
            decoded = jj_decode(code)
            if decoded:
                return decoded

        # Eval packer check
        if is_eval_packed(code):
            decoded = eval_unpack(code)
            if decoded:
                return decoded

        return None

    # Maximum number of outer re-parse cycles (generate → re-parse → re-transform)
    _MAX_OUTER_CYCLES = 5

    def execute(self) -> str:
        """Run all transforms and return cleaned source."""
        code = self.original_code

        # Pre-pass: encoding detection and eval unpacking
        decoded = self._run_pre_passes(code)
        if decoded:
            # Feed decoded result back through the full pipeline for further cleanup
            sub = Deobfuscator(decoded, max_iterations=self.max_iterations)
            return sub.execute()

        # Try to parse; if it fails, apply source-level hex decoding as fallback
        try:
            ast = parse(code)
        except SyntaxError:
            # Source-level hex decode for unparseable files (e.g. ES modules)
            decoded = decode_hex_escapes_source(code)
            if decoded != code:
                return decoded
            return self.original_code

        # Outer loop: run AST transforms until generate→re-parse converges.
        # Post-passes (VariableRenamer, VarToConst, LetToConst) only run on
        # the final cycle to avoid interfering with subsequent transform rounds.
        previous_code = code
        last_changed_ast = None
        try:
            for _cycle in range(self._MAX_OUTER_CYCLES):
                changed = self._run_ast_transforms(
                    ast,
                    code_size=len(previous_code),
                )

                if not changed:
                    break

                last_changed_ast = ast

                try:
                    generated = generate(ast)
                except Exception:
                    break

                if generated == previous_code:
                    break

                previous_code = generated

                # Re-parse for the next cycle
                try:
                    ast = parse(generated)
                except SyntaxError:
                    break

            # Run post-passes on the final AST (always — they're cheap and handle
            # cosmetic transforms like var→const even when no main transforms fired)
            any_post_changed = False
            for post_transform in [VariableRenamer, VarToConst, LetToConst]:
                try:
                    if post_transform(ast).execute():
                        any_post_changed = True
                except Exception:
                    pass

            if last_changed_ast is None and not any_post_changed:
                return self.original_code

            try:
                return generate(ast)
            except Exception:
                return previous_code
        except RecursionError:
            # Safety net: esprima's parser is purely recursive with no depth
            # limit, so deeply nested JS hits Python's recursion limit during
            # parsing or re-parsing.  Our AST walkers are cheaper per level
            # but also recursive.  Return best result so far.
            return previous_code

    def _run_ast_transforms(self, ast: dict, code_size: int = 0) -> bool:
        """Run all AST transform passes. Returns True if any transform changed the AST."""
        node_count = _count_nodes(ast) if code_size > _LARGE_FILE_SIZE else 0

        lite_mode = code_size > _MAX_CODE_SIZE
        max_iterations = self.max_iterations
        if code_size > _LARGE_FILE_SIZE:
            max_iterations = min(max_iterations, _LITE_MAX_ITERATIONS)

        # For very large ASTs, further reduce iterations
        if node_count > 100_000:
            max_iterations = min(max_iterations, 3)

        # Build transform list based on mode
        transform_classes = TRANSFORM_CLASSES
        if lite_mode or node_count > _NODE_COUNT_LIMIT:
            transform_classes = [t for t in TRANSFORM_CLASSES if t not in _EXPENSIVE_TRANSFORMS]

        # Track which transforms are no longer productive
        skip_transforms = set()

        # Multi-pass transform loop
        any_transform_changed = False
        for iteration in range(max_iterations):
            modified = False
            for transform_class in transform_classes:
                if transform_class in skip_transforms:
                    continue
                try:
                    transform = transform_class(ast)
                    result = transform.execute()
                except Exception:
                    continue
                if result:
                    modified = True
                    any_transform_changed = True
                elif iteration > 0:
                    # Skip transforms that haven't changed anything after the first pass
                    skip_transforms.add(transform_class)

            if not modified:
                break

        return any_transform_changed
