# v0.9.9.9 — General-mode wording and section deletion

## General block style

- Reworked Chinese general-mode captions against the user-supplied Valve L4D2 Script Functions and Events exports.
- General mode no longer falls back to mechanical captions such as `调用 xxx`, `xxx 事件发生时`, `之后脚本执行`, or direct word-by-word translations for the audited symbols.
- Added natural descriptions for navigation areas, call chainers, QAngle/Vector conversions, HUD/update helpers, audio functions, file helpers and several interaction APIs.
- `explain_*` events are presented as in-game teaching/instructor prompts rather than generic events.
- Professional mode still displays the canonical API/event name and code generation remains unchanged.
- Tooltips retain the canonical name/signature/source description for verification.

## Section deletion

- Fixed section deletion so removing a normal section updates both the document model and live scene.
- Deletion is queued until the context menu closes, preventing a QGraphicsProxyWidget from destroying itself inside its own menu callback.
- Added the `...` section-title button as a second entry point for edit/delete.
- `init` remains non-deletable and cannot be recreated manually; internal `data` sections remain managed by their variables.

## Tests

- 207 non-GUI unit tests pass.
- Added regression checks for natural-language captions, professional-mode canonical names, presentation/code-generation separation, and actual scene rebuild logic used by section deletion.
