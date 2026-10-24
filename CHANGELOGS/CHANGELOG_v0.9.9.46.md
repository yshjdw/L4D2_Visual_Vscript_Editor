# v0.9.9.46

- New sections appear in front of existing canvas sections immediately after creation, regardless of earlier click-to-front z-order. Preserves project section order and code generation semantics.
- Added two directly draggable, two-parameter Math expression blocks: `max(a,b)` and `min(a,b)`. They can also be selected in the existing Math function dropdown and embedded expression menu.
- Math helpers compile to `::L4VP_Utils.Max(a,b)` / `::L4VP_Utils.Min(a,b)` and generate the named helper definitions only when used, once per script. No anonymous functions or assumptions about engine Math globals.
- Added Chinese/English, General/Professional captions and localized hover explanations for both blocks.
- Original `.l4vp` file structure and previously saved Math blocks remain compatible.
