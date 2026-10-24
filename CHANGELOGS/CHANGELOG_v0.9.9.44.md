# v0.9.9.44 — Complete string-call statement separation / 完整修复字符串调用语句分隔

- Rebuild the inline Squirrel string argument quoting function with explicit line separators around **all** `if`, `for`, and `return` statements.
- v0.9.9.43 inserted separators for some adjacent `if` statements, but still left `} o+=c` on one line; this patch addresses the whole expression.
- Add regression coverage for the actual long `DoEntFire("worldspawn", "RunScriptCode", ...)` case.
- Keep saved `.l4vp` format and other API blocks unchanged.
- Also release Pills Staged Diagnostic v5 with the fixed code and retained stage markers.
