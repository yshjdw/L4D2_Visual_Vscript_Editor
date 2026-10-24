# v0.8.4

- Fixed saved `env` / Table / Set references becoming passive labels when nested inside expression slots.
- Right-click or double-click an embedded variable reference to reopen member selection.
- Resolve the original declaration via `symbol_id`, including event blocks nested under Events and blocks in branches.
- The member window's root action restores an `env.xxx` reference to `env`; selection updates only this reference, not the source variable declaration.
- Missing/deleted symbol source now produces an explanatory message instead of an exception.
- Added regression coverage for nested event variables, ordinary Table declarations, and missing references.

GUI event propagation still requires Windows PySide6 testing.
