"""Multi-pass deobfuscation orchestrator."""

from .parser import parse
from .generator import generate
from .transforms.hex_escapes import decode_hex_escapes_source, HexEscapes
from .transforms.unused_vars import UnusedVariableRemover
from .transforms.constant_prop import ConstantProp
from .transforms.reassignment import ReassignmentRemover
from .transforms.dead_branch import DeadBranchRemover
from .transforms.object_packer import ObjectPacker
from .transforms.proxy_functions import ProxyFunctionInliner
from .transforms.expression_simplifier import ExpressionSimplifier
from .transforms.sequence_splitter import SequenceSplitter
from .transforms.logical_to_if import LogicalToIf
from .transforms.control_flow import ControlFlowRecoverer
from .transforms.property_simplifier import PropertySimplifier
from .transforms.anti_tamper import AntiTamperRemover
from .transforms.object_simplifier import ObjectSimplifier
from .transforms.string_revealer import StringRevealer


# StringRevealer runs first to handle string arrays before other transforms
# modify the wrapper function structure.
# Remaining transforms follow obfuscator-io-deobfuscator order.
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
    StringRevealer,
]


class Deobfuscator:
    """Multi-pass JavaScript deobfuscator."""

    def __init__(self, code, max_iterations=50):
        self.original_code = code
        self.max_iterations = max_iterations

    def execute(self):
        """Run all transforms and return cleaned source."""
        # Skip source-level hex decoding — AST-level HexEscapes handles it
        # with proper double-quote normalization like Babel.
        code = self.original_code
        hex_changed = False

        # Parse (fall back to original source if hex decoding broke parsing)
        try:
            ast = parse(code)
        except SyntaxError:
            try:
                ast = parse(self.original_code)
                # Original parses but decoded doesn't — discard hex decode
                code = self.original_code
                hex_changed = False
            except SyntaxError:
                # Neither parses. Return hex-decoded version if it changed
                # (still a useful deobfuscation even without AST transforms).
                if hex_changed:
                    return code
                return self.original_code

        # Multi-pass transform loop
        any_transform_changed = False
        for i in range(self.max_iterations):
            modified = False
            for cls in TRANSFORM_CLASSES:
                try:
                    transform = cls(ast)
                    result = transform.execute()
                except Exception:
                    continue
                if result:
                    modified = True
                    any_transform_changed = True

            if not modified:
                break

        # If nothing changed, return original code to avoid reformatting
        if not any_transform_changed and not hex_changed:
            return self.original_code

        # Generate output
        try:
            output = generate(ast)
        except Exception:
            # If only hex decoding changed the source, return the decoded
            # version directly rather than falling back to the original.
            if hex_changed:
                return code
            return self.original_code

        return output
