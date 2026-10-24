# v26.9

- Fix the context menu of embedded variable references opening offset from the mouse.
- Make variable-reference menus top-level (not parented to a proxy-hosted QLabel).
- Use physical cursor coordinates for Qt-proxy native context events, and map viewport context clicks directly to screen coordinates.
- Preserve variable reference copy, member picker and deletion actions.
- No changes to .l4vp serialization, script generation or section geometry.
