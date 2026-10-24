# v26.5 — Deep nested expression pointer routing

- Resolve Qt nested expression targets by mapping every visible descendant into the section root coordinate system instead of relying exclusively on `childAt()` and stale parent hit rectangles.
- Use the same deep pointer lookup when locating nested drop sockets.
- Route right-click to the innermost nested expression; preserve native editing for text fields and variable references.
- Start nested expression drag from its grip, label, or non-interactive body using the existing copy/move MIME protocol.
- Keep v26.4 intrinsic section geometry unchanged to avoid the recursive expansion regression from v26.3.
- Tested source-level and synthetic nested rectangles. Windows Qt interaction still requires manual validation.
