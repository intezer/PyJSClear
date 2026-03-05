<p align="center">
  <img src="PyJSClear.png" alt="PyJSClear" width="200">
</p>

# PyJSClear

Pure Python JavaScript deobfuscator. Combines the functionality of
[obfuscator-io-deobfuscator](https://github.com/ben-sb/obfuscator-io-deobfuscator)
(13 AST transforms for obfuscator.io output) and
[javascript-deobfuscator](https://github.com/saucesteals/javascript-deobfuscator)
(hex escape decoding, static array unpacking, property access cleanup)
into a single Python library with no Node.js dependency.

## Installation

```bash
pip install pyjsparser   # only runtime dependency
pip install -e .          # install PyJSClear
```

## Usage

### Python API

```python
from pyjsclear import deobfuscate, deobfuscate_file

# From a string
cleaned = deobfuscate(obfuscated_code)

# From a file
deobfuscate_file("input.js", "output.js")

# Or get the result as a string
cleaned = deobfuscate_file("input.js")
```

### Command line

```bash
# File to stdout
python -m pyjsclear input.js

# File to file
python -m pyjsclear input.js -o output.js

# Stdin to stdout
cat input.js | python -m pyjsclear -

# With custom iteration limit
python -m pyjsclear input.js --max-iterations 20
```

## What it does

PyJSClear applies 14 transforms in a multi-pass loop until no further changes
are made (up to 50 iterations by default):

| # | Transform | Description |
|---|-----------|-------------|
| 1 | **StringRevealer** | Decode obfuscator.io string arrays (basic, base64, RC4), including rotation IIFEs and wrapper functions |
| 2 | **UnusedVariableRemover** | Remove variables with zero references |
| 3 | **ConstantProp** | Propagate constant literals to all reference sites |
| 4 | **ReassignmentRemover** | Eliminate redundant `x = y` reassignment chains |
| 5 | **DeadBranchRemover** | Remove unreachable `if(true)/if(false)` and ternary branches |
| 6 | **ObjectPacker** | Consolidate sequential `obj.x = ...` assignments into object literals |
| 7 | **ProxyFunctionInliner** | Inline single-return proxy functions at all call sites |
| 8 | **ExpressionSimplifier** | Evaluate static expressions: `3 + 5` -> `8`, `![]` -> `false`, `typeof undefined` -> `"undefined"` |
| 9 | **SequenceSplitter** | Split comma expressions `(a(), b(), c())` into separate statements |
| 10 | **ControlFlowRecoverer** | Recover linear code from `"1\|0\|3".split("\|")` + `while/switch` dispatch patterns |
| 11 | **PropertySimplifier** | Convert `obj["prop"]` to `obj.prop` where valid |
| 12 | **AntiTamperRemover** | Remove self-defending and anti-debug IIFEs |
| 13 | **ObjectSimplifier** | Inline proxy object property accesses |
| 14 | **StringRevealer** | Second pass to catch strings exposed by earlier transforms |

A pre-AST pass also decodes `\xHH` hex escape sequences in source text.

### Safety guarantees

- **Never expands output**: if the deobfuscated result is larger than the input,
  the original code is returned unchanged.
- **Never crashes on valid JS**: parse errors fall back to returning the original
  source. Transform exceptions are caught per-transform and skipped.

## How it was built

This library was developed as a pure Python re-implementation of two established
Node.js deobfuscation tools. The goal was to eliminate the Node.js/Babel
dependency while matching or exceeding their deobfuscation quality.

### Approach

1. **Algorithm analysis**: The transform logic in
   [obfuscator-io-deobfuscator](https://github.com/ben-sb/obfuscator-io-deobfuscator)
   (13 Babel transforms) and
   [javascript-deobfuscator](https://github.com/saucesteals/javascript-deobfuscator)
   (3 modules: `--he`, `--su`, `--tp`) was studied to understand the
   deobfuscation algorithms — pattern detection, AST rewriting strategies,
   and transform ordering.

2. **Python infrastructure**: A lightweight AST toolchain was built on
   [pyjsparser](https://github.com/nickoala/pyjsparser) (ESTree-compatible
   JS parser), with a custom code generator, AST traverser with
   enter/exit/replace/remove support, and scope analysis for variable binding.

3. **Transform re-implementation**: Each transform was written from scratch
   in Python following the same algorithmic approach as the originals, adapted
   to work with pyjsparser's ESTree AST (vs. Babel's AST). Key differences
   include the string revealer's obfuscator.io pattern handling (rotation IIFE
   evaluation, two-level wrapper indirection) and the control flow recoverer.

4. **Multi-pass orchestrator**: Transforms run in a fixed order within a
   convergence loop, matching the obfuscator-io-deobfuscator architecture.
   StringRevealer runs both first and last to handle string arrays before
   other transforms modify wrapper function structure.

### Testing methodology

The library was validated against five datasets:

| Dataset | Files | Crashes | Expanded | Reduced | Source |
|---------|-------|---------|----------|---------|--------|
| E1 technique samples | 20 | 0 | 0 | 13 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |
| Obfuscated JS dataset | 500 | 0 | 0 | 39 | [Kaggle](https://www.kaggle.com/datasets/fanbyprinciple/obfuscated-javascript-dataset) |
| MalJS (malware) | 200 | 0 | 0 | 79 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |
| BenignJS | 500 | 0 | 0 | 112 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |
| NotObfuscated | 1,885 | 0 | 0 | 191 | [Kaggle](https://www.kaggle.com/datasets/fanbyprinciple/obfuscated-javascript-dataset) |

**Head-to-head vs Node.js tools** (obfuscator-io-deobfuscator v1.0.6):

- E1 samples: PyJSClear wins 17, ob-io wins 0 (out of 17 changed files)
- MalJS sample: PyJSClear wins 20, ob-io wins 0 (out of 20 compared)
- Zero regressions detected across all tested datasets

The Node.js tools expand most files due to Babel's verbose code generator,
while PyJSClear's compact generator and "never expand" safety guarantee avoid this.

**"Do no harm" validation**: Tested against 500 BenignJS files and 1,885
NotObfuscated files. Zero files were expanded or corrupted — transforms only
fire when genuine obfuscation patterns are detected.

## Architecture

```
pyjsclear/
├── __init__.py              # Public API: deobfuscate(), deobfuscate_file()
├── __main__.py              # CLI entry point
├── parser.py                # pyjsparser wrapper
├── generator.py             # ESTree AST -> JavaScript source
├── traverser.py             # AST visitor (enter/exit, replace, remove)
├── scope.py                 # Scope tree & variable binding analysis
├── deobfuscator.py          # Multi-pass transform orchestrator
├── transforms/
│   ├── base.py              # Transform base class with change tracking
│   ├── string_revealer.py   # String array decode (basic/base64/RC4/obfuscator.io)
│   ├── control_flow.py      # Control flow flattening recovery
│   ├── proxy_functions.py   # Proxy function inlining
│   ├── constant_prop.py     # Constant propagation
│   ├── expression_simplifier.py
│   ├── property_simplifier.py
│   ├── dead_branch.py
│   ├── object_simplifier.py
│   ├── object_packer.py
│   ├── unused_vars.py
│   ├── reassignment.py
│   ├── sequence_splitter.py
│   ├── anti_tamper.py
│   └── hex_escapes.py
└── utils/
    ├── string_decoders.py   # Base64, RC4 decoders
    └── ast_helpers.py        # AST node construction & inspection
```

## Limitations

- **pyjsparser** does not support all ES2020+ syntax (optional chaining,
  nullish coalescing, etc.). Files using these features will be returned
  unchanged.
- Large files (>100KB) with deep obfuscation can be slow due to the
  multi-pass architecture. Consider using `max_iterations` to limit passes.
- Not all obfuscator.io configurations are handled — some advanced string
  encoding patterns may not be fully decoded.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

This project is a derivative work based on
[obfuscator-io-deobfuscator](https://github.com/ben-sb/obfuscator-io-deobfuscator)
(Apache 2.0) and
[javascript-deobfuscator](https://github.com/saucesteals/javascript-deobfuscator)
(MIT). See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) and
[NOTICE](NOTICE) for full attribution.
