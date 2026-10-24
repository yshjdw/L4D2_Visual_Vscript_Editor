# v0.9.9.4

- Import all documented SendTable array declarations and indexed array ranges from user-provided 2024 L4D2 netprop transcription, including nested/ranged groups; 114 distinct array records in offline catalog. Array ranges are documentation metadata and not all proven to work with GetProp*Array at runtime.
- Netprop picker shows array element type and length and warns on unverified SendTable ranges. Type inference uses documented element type for Float/Vector/String/Int when provided.
- Newly created If has a single condition/body and no mandatory Else. Button '+' creates Else on the first press and inserts Else If before the final Else thereafter. Each Else If contains an editable expression slot and a '-' button deleting its entire branch. Old If projects with legacy branches remain supported.
- Confirm raw Squirrel editor uses QPlainTextEdit, accepts Space and Enter; canvas drag shortcut does not consume text input while the editor is focused.
- 180 non-GUI unit tests passing. GUI/runtime testing not performed in this environment.
