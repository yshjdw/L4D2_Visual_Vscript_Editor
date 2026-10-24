# v0.6 — interaction fixes

- Fixed mouse-drag event conflicts by disabling QGraphicsProxyWidget ItemIsMovable. Sections now move exclusively via title grips.
- Deferred re-creating widgets after existing-block DnD, preventing the source widget from being deleted inside its own drag event loop.
- Added viewport touch-event tracking: one-finger canvas panning, two-finger pinch zoom and panning. Not yet tested on a physical touchscreen.
- Canvas pan: middle mouse, space+left mouse, left mouse on empty background, optional hand mode.
- Added zoom +/- and reset 100% controls, visible new-section button, explicit hand-mode control.
- Added context menu on block background (not only ellipsis button).
- Complex Table/Set variables now open a separate modal workspace window with their own canvas and restricted block palette. Uses the same underlying Section object and ID as the project; nested definitions use the owning document.
- New complex-data workspace is only created from a Table/Set variable. It is not an ordinary independently inserted section.
- Block palette is the initially visible left dock tab.
- No expression-block nesting was added.

## Remaining limitations

- Cannot execute PySide6 GUI tests in this runtime; verify gesture delivery on the target touchscreen.
- This is still a prototype: drag preview/ghost and magnetic insertion are not at Scratch's animation-quality level.
- Data-definition nested windows are modal and each opens a focused editing canvas, not a main-canvas overlay.
