# v26.10

- Fixed embedded QLineEdit mouse-position conversion: viewport -> scene -> graphics proxy -> text editor. Clicking inside a long expression should place the caret at the clicked character, instead of forcing the end.
- Added 8 TraceLine utility expression blocks for `TraceLine(table)`, safe result-field access, and dedicated numeric collision-mask constants. Helpers are generated only when used, with no anonymous immediately-invoked functions.
- Added a dedicated `Summon / spawn entity classnames` draggable category, sourced from the spawn catalog; the drag payload inserts only the quoted classname, never an extra SpawnEntityFromTable call.
- English/Chinese and General/Professional labels/tooltips for new library entries and input parameter hints.
- Added TRACELINE_GUIDE.md and regression tests for helper generation, safe fields, classname expression and caret coordinate path.
- Preserved `.l4vp` schema and existing blocks.

**Note:** Automated tests do not replace Windows Qt pointer interaction or in-game VScript verification.
