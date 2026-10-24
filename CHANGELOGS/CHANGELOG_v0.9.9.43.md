# v0.9.9.43 — String-call Squirrel syntax repair / 延迟函数字符串语法修复

- Fix `string_call` typed string serialization: emit explicit newline statement separators between consecutive `if` blocks inside the generated Squirrel anonymous quoting function.
- Fix the missing line separator between the enclosing `for` block and `return`.
- Prevents Squirrel 3.0.4 `end of statement expected (; or lf)` at `if(c==format(...))` when nesting typed string calls in DoEntFire/RunScriptCode.
- No changes to the `.l4vp` project format or V/W model and classname data.
- Regression tests cover generated separators and original call arguments.
