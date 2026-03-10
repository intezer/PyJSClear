<p align="center">
  <img src="https://raw.githubusercontent.com/intezer/PyJSClear/main/PyJSClear.png" alt="PyJSClear" width="200">
</p>

# PyJSClear

Pure Python JavaScript deobfuscator. Combines the functionality of
[obfuscator-io-deobfuscator](https://github.com/ben-sb/obfuscator-io-deobfuscator)
(13 AST transforms for obfuscator.io output) and
[javascript-deobfuscator](https://github.com/ben-sb/javascript-deobfuscator)
(hex escape decoding, static array unpacking, property access cleanup)
into a single Python library with no Node.js dependency.

## Installation

```bash
pip install pyjsclear
```

For development:

```bash
git clone https://github.com/intezer/PyJSClear.git
cd PyJSClear
pip install -e .
pip install pytest
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
pyjsclear input.js

# File to file
pyjsclear input.js -o output.js

# Stdin to stdout
cat input.js | pyjsclear -

# With custom iteration limit
pyjsclear input.js --max-iterations 20
```

## What it does

PyJSClear applies 16 transforms in a multi-pass loop until no further changes
are made (up to 50 iterations by default):

| # | Transform | Description |
|---|-----------|-------------|
| 1 | **StringRevealer** | Decode obfuscator.io string arrays (basic, base64, RC4), including rotation IIFEs, wrapper functions, multiple decoders per file, and SequenceExpression-wrapped rotation patterns |
| 2 | **HexEscapes** | Normalize `\xHH`/`\uHHHH` escape sequences in string literal AST nodes |
| 3 | **UnusedVariableRemover** | Remove variables with zero references |
| 4 | **ConstantProp** | Propagate constant literals to all reference sites |
| 5 | **ReassignmentRemover** | Eliminate redundant `x = y` reassignment chains |
| 6 | **DeadBranchRemover** | Remove unreachable `if(true)/if(false)` and ternary branches |
| 7 | **ObjectPacker** | Consolidate sequential `obj.x = ...` assignments into object literals |
| 8 | **ProxyFunctionInliner** | Inline single-return proxy functions at all call sites |
| 9 | **SequenceSplitter** | Split comma expressions `(a(), b(), c())` into separate statements; extract `(0, fn)(args)` indirect call prefixes; normalize loop/if bodies to block statements |
| 10 | **ExpressionSimplifier** | Evaluate static expressions: `3 + 5` -> `8`, `![]` -> `false`, `typeof undefined` -> `"undefined"`, `test ? false : true` -> `!test` |
| 11 | **LogicalToIf** | Convert `a && b()` / `a \|\| b()` in statement position to if-statements |
| 12 | **ControlFlowRecoverer** | Recover linear code from `"1\|0\|3".split("\|")` + `while/switch` dispatch patterns |
| 13 | **PropertySimplifier** | Convert `obj["prop"]` to `obj.prop` where valid |
| 14 | **AntiTamperRemover** | Remove self-defending and anti-debug IIFEs |
| 15 | **ObjectSimplifier** | Inline proxy object property accesses |
| 16 | **StringRevealer** | Second pass to catch strings exposed by earlier transforms |

### Safety guarantees

- **Never expands output**: if the deobfuscated result is larger than the input,
  the original code is returned unchanged.
- **Never crashes on valid JS**: parse errors fall back to returning the original
  source. Transform exceptions are caught per-transform and skipped.

## Testing

```bash
pytest tests/                           # all tests
pytest tests/test_regression.py         # regression suite (35 tests across 25 samples)
pytest tests/ -n auto                   # parallel execution (requires pytest-xdist)
```

Validated against six datasets totalling 47,836 files (full datasets, no sampling):

| Dataset | Files | Crashes | Expanded | Reduced | Source |
|---------|-------|---------|----------|---------|--------|
| E1 technique samples | 20 | 0 | 0 | 13 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |
| Kaggle Obfuscated | 1,477 | 0 | 0 | 1,199 | [Kaggle](https://www.kaggle.com/datasets/fanbyprinciple/obfuscated-javascript-dataset) |
| Kaggle NotObfuscated | 1,898 | 0 | 0 | 217 | [Kaggle](https://www.kaggle.com/datasets/fanbyprinciple/obfuscated-javascript-dataset) |
| MalJS (malware) | 23,212 | 0 | 0 | 3,193 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |
| BenignJS | 21,209 | 0 | 0 | 4,354 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |
| E1 original (clean) | 20 | 0 | 0 | 15 | [JSIMPLIFIER](https://zenodo.org/records/17531662) |

Files >200KB or exceeding a 15-second wall-clock timeout are skipped and counted as unchanged (14,529 of MalJS, 940 of BenignJS). BenignJS reductions are genuine deobfuscation of obfuscated JS scraped from benign websites. A handful of Kaggle NotObfuscated files are mislabeled (genuinely obfuscated Angular test specs). E1 original reductions come from minor whitespace/formatting cleanup by the code generator.

**Head-to-head vs Node.js tools** (obfuscator-io-deobfuscator + javascript-deobfuscator pipeline):

On the Kaggle Obfuscated dataset (1,477 files), PyJSClear reduces 1,199 files while the Node.js pipeline changes zero — the dataset's lightweight obfuscation (hex escapes, basic string arrays without `parseInt` checksums) falls outside obfuscator-io-deobfuscator's detection heuristics. On the E1 and MalJS datasets (heavily obfuscated), PyJSClear produces smaller output on 93.8% of files where at least one tool changed output, driven by dead-code removal, proxy-function inlining, bracket-to-dot conversion, and control-flow recovery.

**Parse coverage**: PyJSClear uses [esprima2](https://github.com/s0md3v/esprima2) which supports ES2024 syntax, including arrow functions, optional chaining, nullish coalescing, and more.

## Architecture

Built on [esprima2](https://github.com/s0md3v/esprima2) (ESTree-compatible JS parser with ES2024 support) with a custom code generator, AST traverser (enter/exit/replace/remove), and scope analysis. Transforms run in a fixed order within a convergence loop; StringRevealer runs both first and last to handle string arrays before and after other transforms modify wrapper function structure.

## Limitations

- Large files (>100KB) with deep obfuscation can be slow due to the
  multi-pass architecture. Consider using `max_iterations` to limit passes.
- Not all obfuscator.io configurations are handled — some advanced string
  encoding patterns may not be fully decoded. Supported encodings: basic
  (index lookup), base64, RC4, and multi-decoder (multiple encoding types
  sharing one string array).

## License

Apache License 2.0 — see [LICENSE](LICENSE).

This project is a derivative work based on
[obfuscator-io-deobfuscator](https://github.com/ben-sb/obfuscator-io-deobfuscator)
(Apache 2.0) and
[javascript-deobfuscator](https://github.com/ben-sb/javascript-deobfuscator)
(Apache 2.0). See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) and
[NOTICE](NOTICE) for full attribution.
