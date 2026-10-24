# v26.4 — Section geometry stabilization

## Fixed

- Reverted the v26.3 runaway section-size measurement that counted stretched child widgets' allocated rectangles as intrinsic content and repeatedly re-added margins.
- Measure section dimensions from the Qt layout's *intrinsic minimum*, after bottom-up expression and block layout reflow, instead of accumulated proxy size or mapped coordinates of stretched descendants.
- Synchronize the section panel and `QGraphicsProxyWidget` to the recalculated width and height, allowing both enlargement for genuinely wide nested blocks and reduction after a deletion/edit.
- Recalculate canvas scene bounds after section resize to avoid excessively large blank work areas and incorrect right-edge hit-testing.
- Added repeatability and shrink-vs-grow regression tests; existing .l4vp projects and Squirrel code generation are unchanged.

## Verification

- Python unit tests: 340 run, 339 passed, 1 skipped.
- The supplied `pills can used many times(2).l4vp` loads successfully, and its `director_base_addon.nut` generates without generator errors.
- UI rendering and live mouse hit-testing still require verification on Windows with PySide6.
