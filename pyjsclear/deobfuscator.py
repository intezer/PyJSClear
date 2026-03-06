"""Multi-pass deobfuscation orchestrator."""

from .generator import generate
from .parser import parse
from .transforms.anti_tamper import AntiTamperRemover
from .transforms.constant_prop import ConstantProp
from .transforms.control_flow import ControlFlowRecoverer
from .transforms.dead_branch import DeadBranchRemover
from .transforms.expression_simplifier import ExpressionSimplifier
from .transforms.hex_escapes import HexEscapes
from .transforms.hex_escapes import decode_hex_escapes_source
from .transforms.logical_to_if import LogicalToIf
from .transforms.object_packer import ObjectPacker
from .transforms.object_simplifier import ObjectSimplifier
from .transforms.property_simplifier import PropertySimplifier
from .transforms.proxy_functions import ProxyFunctionInliner
from .transforms.reassignment import ReassignmentRemover
from .transforms.sequence_splitter import SequenceSplitter
from .transforms.string_revealer import StringRevealer
from .transforms.unused_vars import UnusedVariableRemover


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
        code = self.original_code

        # Try to parse; if it fails, apply source-level hex decoding as fallback
        try:
            ast = parse(code)
        except SyntaxError:
            # Source-level hex decode for unparseable files (e.g. ES modules)
            decoded = decode_hex_escapes_source(code)
            if decoded != code:
                return decoded
            return self.original_code

        # Multi-pass transform loop
        any_transform_changed = False
        for i in range(self.max_iterations):
            modified = False
            for transform_class in TRANSFORM_CLASSES:
                try:
                    transform = transform_class(ast)
                    result = transform.execute()
                except Exception:
                    continue
                if result:
                    modified = True
                    any_transform_changed = True

            if not modified:
                break

        if not any_transform_changed:
            return self.original_code

        try:
            return generate(ast)
        except Exception:
            return self.original_code
