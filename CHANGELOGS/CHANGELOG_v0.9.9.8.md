# v0.9.9.8 — Functions, scopes and ScriptScope membership

- Functions may now be defined without a Namespace; empty owner emits `::FunctionName <- function(...)`.
- Function title displays draggable formal parameters. Right-click an argument to define a nested Table/Array schema and select a member reference. Parameter schema is editor-only and does not emit declarations.
- The section title right-click menu offers edit and delete for ordinary sections. `init` is a fixed singleton managed by the file and cannot be created manually, transformed, or deleted. Linked Data sections remain managed by their source variables.
- New boolean expression block `Table 成员存在？` emits `target.rawin(key)` with variable-compatible target and key sockets.
- Local variable validation now permits a copied reference when the destination callback has its own earlier, lexically visible same-name local; it still rejects missing, later, or wrong-branch declarations. Event env remains callback scoped.
- All existing .l4vp serialization remains compatible.

Validation: 199 non-GUI unit tests; Python source compilation. GUI testing requires Windows/PySide6.
