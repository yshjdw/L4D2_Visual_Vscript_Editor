# v26.13 — ScriptScope member catalog across local aliases

- Display every declared ScriptScope member in the current .nut document, regardless of the source/target local alias or entity expression; include current workspace for expression reuse.
- Dragging into another ScriptScope Data workspace adds a **reference-only** member using the destination's own scope variable; it never initializes the member on another entity.
- Dragging into an expression socket resolves using target-local ScriptScope variables, with an explicit selection dialog if more than one exists.
- Preserve original source section and member ID for auditability and avoid using stale member names.
- Provide Chinese/English headings, empty-state guidance, source/binding tooltips, and General/Professional labels.
- No change to existing project file format or exported Squirrel code unless a new member reference is added.
