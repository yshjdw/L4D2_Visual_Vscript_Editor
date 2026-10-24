# v0.9.9.47

- New **Globals.IncludeScript** blocks now initialize `scope` to `getroottable()` instead of `null`, matching project-tree `.nut` file dragging and project dependency generation.
- Corrected the displayed argument metadata in newly inserted blocks from the parsed documentation artifact `null:handle scope =` to `scope:handle/table`; the original official API signature remains unchanged.
- English and Chinese API hover tooltips clarify the difference between the native `scope = null` and the editor's explicit root-scope default.
- Saved `.l4vp` IncludeScript blocks retain any existing user-selected `scope` (`null`, `getroottable()`, ScriptScope, etc.).
- Tests cover default expression output, customization, saved project compatibility, and localized hover tips.
