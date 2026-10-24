# v26.6 — Deep nested variable-reference hit testing

- Fix drag for embedded variable-reference tokens such as `origin_value` inside a deeply nested `min(...)` or long calculation.
- Reuse the canvas-wide precise hit test added in 26.5, independently of the containing green expression shell. Outdated intermediate QWidget bounds no longer block drag initiation for variable references.
- Share the same `MIME_EXPR` variable-reference copy payload for native token drag and canvas-routed drag; source reference is never deleted during copy.
- Make context menus available even when a token lies outside an outdated parent hit rectangle; copy, member selection (when applicable), and removal are available in both languages.
- Leave 26.4 section geometry and code generation unchanged.
- Mouse integration in a real Windows Qt session remains to be verified.
