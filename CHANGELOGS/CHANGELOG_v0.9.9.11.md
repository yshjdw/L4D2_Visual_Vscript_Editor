# v0.9.9.11

- Clicking .nut files or their sections in the project tree selects the corresponding document. Double-click also opens it; renaming remains available through the context menu.
- Drag a .nut file onto a project folder to relocate it. Updates document paths and the includes dependency metadata, and prevents duplicate names. The original drag-to-IncludeScript text-slot functionality remains supported.
- Event `env` field hover uses event-specific English source documentation, plus Chinese interpretations where the source makes the meaning clear; unsupported details are not invented. Dragged member tokens retain these tooltips.
- No project schema change; old .l4vp projects remain supported.

Note: Handwritten raw Squirrel `IncludeScript(...)` statements are not programmatically rewritten when a file is moved. Update those references manually.
