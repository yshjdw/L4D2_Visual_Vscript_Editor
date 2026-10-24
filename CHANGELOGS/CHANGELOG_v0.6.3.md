# v0.6.3 — Context menu and viewport fix

- Variable token right click shows a real detached context menu: Rename, Copy Reference, and Open Independent Complex Variable Workspace (Table/Set).
- Block context menus detached from embedded QGraphicsProxyWidget. Fixes graphics-scene popup covering most of the viewport.
- Complex-variable definition windows are top-level Qt.Window windows, not child popups embedded into the canvas. Windows retain their own movable / zoomable visual workspace and palette.
- Creating a section now uses the visible canvas center as the insertion point, adds only the new QGraphicsProxyWidget, and preserves all other section coordinates, camera position, and zoom.
- Section double-click editing detached from QGraphicsProxyWidget for the same reason.
- Kept the original AST, `.l4vp` project format, codegen and restrictions for complex data sections.

Note: Automated model-level tests and Python compilation pass. Windows PySide6 GUI and touch testing must still be performed on the target PC.
