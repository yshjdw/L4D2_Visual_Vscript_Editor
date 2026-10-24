# v0.9.9.45 — Remove anonymous immediately-invoked functions / 移除匿名立即调用函数

- `string_call` typed `string` parameters now concatenate source-code double quotes directly: `"\\\"" + pills.GetClassname() + "\\\""`; stop generating a multi-line string-escaping IIFE. Static quoted literal parameters are escaped at generation time.
- All `utility` expressions avoid `(function(...){...})(...)`. Simple wrappers emit direct calls; multi-step or once-only wrappers emit `::L4VP_Utils.<Function>(...)` with short named helper definitions automatically included only when referenced.
- Preserve `.l4vp` format, embedded drag support, and existing utility operation IDs.
- Update bilingual `string_call` parameter tooltip so it no longer claims arbitrary runtime string escaping. Limitation: dynamically produced strings containing quotes, backslashes, or newlines must be explicitly escaped before insertion into `RunScriptCode`; classnames are safe for simple concatenation.
- Add regression tests for generated source, named helper dependencies and absence of immediately-invoked functions.
- Game-side Squirrel execution still requires actual L4D2 validation.
