# Third-Party Licenses

This project is a derivative work that re-implements deobfuscation algorithms
from the following Node.js packages in pure Python. No source code was directly
copied; the implementations were written from scratch following the same
algorithmic approaches.

---

## obfuscator-io-deobfuscator

- **Version:** 1.0.6
- **Author:** Ben (ben-sb)
- **Repository:** https://github.com/ben-sb/obfuscator-io-deobfuscator
- **License:** Apache License 2.0

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

**Transforms derived from this project:** StringRevealer, ControlFlowRecoverer,
ProxyFunctionInliner, ConstantProp, ExpressionSimplifier, DeadBranchRemover,
ObjectSimplifier, ObjectPacker, UnusedVariableRemover, ReassignmentRemover,
SequenceSplitter, AntiTamperRemover, PropertySimplifier.

---

## javascript-deobfuscator

- **Author:** Ben (ben-sb)
- **Repository:** https://github.com/ben-sb/javascript-deobfuscator
- **License:** Apache License 2.0

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

**Features derived from this project:** hex escape decoding (`--he`),
static array unpacking (`--su`), property access transformation (`--tp`).

---

## esprima2

- **Version:** 5.0.1
- **Author:** Somdev Sangwan (s0md3v)
- **Repository:** https://github.com/s0md3v/esprima2
- **License:** BSD 2-Clause License

```
Copyright JS Foundation and other contributors, https://js.foundation/

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

**Usage:** Runtime dependency — JavaScript parser providing ESTree-compatible AST with ES2024 support.
