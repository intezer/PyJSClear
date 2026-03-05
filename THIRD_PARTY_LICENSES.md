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
