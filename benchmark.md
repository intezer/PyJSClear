# Benchmark: PyJSClear vs Node.js Deobfuscation Pipeline

## Test Input

- File: `b3ef2e11c855f4812e64230632f125db5e7da1df3e9e34fdb2f088ebe5e16603`
- Size: 190 KB obfuscated JavaScript

## Tools Compared

1. **PyJSClear** — single command
2. **Node.js pipeline** — `obfuscator-io-deobfuscator` followed by `javascript-deobfuscator --he --su --tp`

## Results

| Approach | Time | Output Size |
|---|---|---|
| PyJSClear | 1.3s | 204 KB |
| obfuscator-io-deobfuscator | 2.1s | 200 KB |
| + javascript-deobfuscator | +0.5s (2.6s total) | 201 KB |

## Commands

```bash
# PyJSClear
python -m pyjsclear <input> -o deobf.js

# Node.js pipeline
obfuscator-io-deobfuscator -o step1.js <input>
npx javascript-deobfuscator --he --su --tp -i step1.js -o step2.js
```

## Notes

- PyJSClear is ~2x faster than the Node.js pipeline
- Output sizes are comparable; PyJSClear produces slightly more output due to minor formatting differences
- PyJSClear replaces two separate Node.js tools with a single Python command
- Test performed on 2026-03-06, Linux (aarch64), Python 3.12
