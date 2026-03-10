# PyJSClear

Pure Python JavaScript deobfuscator. No Node.js dependency. Single dependency: `esprima2`.

## Quick Start

```bash
# Run
python -m pyjsclear input.js -o output.js
# or via API
from pyjsclear import deobfuscate
result = deobfuscate(js_code)
```

## Architecture

**Pipeline**: parse → multi-pass transforms → generate. Transforms loop until convergence (max 50 iterations).

### Core Modules

| Module | Purpose |
|--------|---------|
| `parser.py` | Wraps esprima2, outputs plain-dict ESTree AST |
| `generator.py` | AST → JavaScript source with operator precedence |
| `traverser.py` | Visitor pattern: `traverse(node, {enter, exit})` with REMOVE/SKIP sentinels |
| `scope.py` | Two-pass scope analysis: `build_scope_tree(ast)` → `(root_scope, node_scope_map)` |
| `deobfuscator.py` | Orchestrator: runs 16 transforms in a loop |

### Transforms (in execution order)

1. `StringRevealer` – Decode obfuscator.io string arrays (basic/base64/RC4)
2. `HexEscapes` – Normalize `\xHH`/`\uHHHH` escapes
3. `UnusedVariableRemover` – Remove zero-reference variables
4. `ConstantProp` – Replace constant variable refs with literal values
5. `ReassignmentRemover` – Eliminate `var x = y` alias chains
6. `DeadBranchRemover` – Remove unreachable `if(true/false)` branches
7. `ObjectPacker` – Consolidate sequential property assignments into object literals
8. `ProxyFunctionInliner` – Inline single-return proxy functions
9. `SequenceSplitter` – Split comma sequences into statements
10. `ExpressionSimplifier` – Constant folding (`3+5` → `8`)
11. `LogicalToIf` – Convert `a && b()` to `if(a) { b(); }`
12. `ControlFlowRecoverer` – Recover linear code from switch-based flattening
13. `PropertySimplifier` – `obj["prop"]` → `obj.prop`
14. `AntiTamperRemover` – Remove self-defending/debug-protection IIFEs
15. `ObjectSimplifier` – Inline proxy object property accesses
16. `StringRevealer` – Second pass for newly exposed arrays

All transforms inherit from `transforms/base.py:Transform`. Set `rebuild_scope = True` if the transform needs fresh scope data.

### Utilities

- `utils/ast_helpers.py` – Node creation (`make_literal`, `make_identifier`), type checks (`is_literal`, `is_identifier`), `deep_copy`, `get_child_keys`
- `utils/string_decoders.py` – Base64/RC4 decoders for obfuscator.io

## Key Conventions

- AST nodes are **plain dicts** with a `type` key
- `traverse()` visitors receive `(node, parent, key, index)` — return REMOVE/SKIP/replacement-dict
- `set_changed()` must only be called when an actual mutation occurs (controls the convergence loop)
- Scope rebuilding is expensive; only transforms that need it set `rebuild_scope = True`

## Code Style

- **Black**: line-length 120, target py311, skip-string-normalization, exclude `tests/resources/`
- **isort**: black profile, force-single-line imports, 2 blank lines after imports
- Run `black` and `isort` on any edited Python file (available as CLI commands, not pip packages in venv)

## Testing

```bash
pytest tests/                           # all tests
pytest tests/transforms/                # transform tests only
pytest tests/test_regression.py         # end-to-end regression (47k files)
```

Test helpers in `conftest.py`: `roundtrip(code, TransformClass)`, `parse_expr(expr)`, `normalize(code)`.

### Fuzz Testing

8 fuzz targets in `tests/fuzz/` covering the full pipeline, parser, generator, transforms, expression simplifier, string decoders, scope analysis, and AST traversal. OSS-Fuzz compatible (atheris/libFuzzer).

```bash
# Run all targets for 10s each (standalone, no extra deps)
tests/fuzz/run_local.sh all 10

# Run a single target for 60s
tests/fuzz/run_local.sh fuzz_deobfuscate 60

# With atheris (requires clang + libFuzzer):
CLANG_BIN=$(which clang) pip install atheris
tests/fuzz/run_local.sh fuzz_deobfuscate 300
```

Fuzz helpers in `tests/fuzz/conftest_fuzz.py`: `bytes_to_js(data)`, `bytes_to_ast_dict(data)`, `run_fuzzer(target_fn)`. Targets use atheris when available, otherwise a standalone random-based fuzzer.

## CI/CD

- **Tests**: `.github/workflows/tests.yml` — pytest on push/PR to `main` (Python 3.11–3.13)
- **Fuzz**: `.github/workflows/fuzz.yml` — 8 fuzz targets on push/PR to `develop` (60s each, standalone fuzzer)
- **Publish**: `.github/workflows/publish.yml` — build + publish to PyPI on GitHub Release (requires `PYPI_TOKEN` secret)

## Safety Guarantees

- Never crashes on valid JS (parse failure → fallback hex decode → return original)
- Never expands output (output > input → return original)
- Per-transform exception isolation
- No external calls (pure computation)
