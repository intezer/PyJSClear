<p align="center">
  <img src="https://raw.githubusercontent.com/intezer/PyJSClear/main/PyJSClear.png" alt="PyJSClear" width="200">
</p>

# PyJSClear

Pure Python JavaScript deobfuscator.

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

PyJSClear applies transforms in a multi-pass loop until the code
stabilizes (default limit: 50 iterations). A final one-shot pass renames
variables and converts var/let to const.

**Capabilities:**
- Whole-file encoding detection: JSFuck, JJEncode, AAEncode, eval-packing
- String array decoding (obfuscator.io basic/base64/RC4, XOR, class-based)
- Constant propagation & reassignment elimination
- Dead code / dead branch / unreachable code removal
- Control-flow unflattening (switch-dispatch recovery)
- Proxy function & proxy object inlining
- Expression simplification & modern syntax recovery (?., ??)
- Anti-tamper / anti-debug removal
- Variable renaming (_0x… → readable names)

Large files (>500 KB / >50 K AST nodes) automatically use a lite mode
that skips expensive transforms.

## Limitations

- **Best results on obfuscator.io output.** JSFuck, JJEncode, AAEncode, and eval-packed code are fully decoded; other obfuscation tools may only partially deobfuscate.
- **Large files get reduced treatment.** Files >500 KB or ASTs >50 K nodes skip expensive transforms; files >2 MB use a minimal lite mode.
- **Recursive AST traversal** may hit Python's default recursion limit (~1 000 frames) on extremely deep nesting; the deobfuscator catches this and returns the best partial result.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

This project is a derivative work based on
[obfuscator-io-deobfuscator](https://github.com/ben-sb/obfuscator-io-deobfuscator)
(Apache 2.0),
[javascript-deobfuscator](https://github.com/ben-sb/javascript-deobfuscator)
(Apache 2.0), and
[webcrack](https://github.com/j4k0xb/webcrack) (MIT).
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) and
[NOTICE](NOTICE) for full attribution.

Test samples include obfuscated JavaScript from the
[JSIMPLIFIER dataset](https://zenodo.org/records/17531662) (GPL-3.0)
and the [Obfuscated JavaScript Dataset](https://www.kaggle.com/datasets/fanbyprinciple/obfuscated-javascript-dataset),
used solely for evaluation purposes.
