# v26.7 — Long expression text input and variable hit fixes

- Route mouse press, move, release and double-click into deeply nested text fields even when outdated parent widget bounds prevent QGraphicsProxyWidget from forwarding.
- Restore focus to the QGraphicsProxyWidget and selected QLineEdit / QTextEdit; preserve editing and text selection.
- Rebuild text context menus for rightmost input fields.
- Resolve interactive leaf controls independently of noninteractive nested label hit tests, fixing variable pills covered by stale sibling geometry.
- Preserve precise block and variable copy-drag behavior, section sizing and Squirrel code generation.
- Windows/PySide6 integration testing remains required; the container does not include the Qt runtime.
