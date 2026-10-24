# v0.8.0

- Fixed nested operator / math / function expression slots throwing `AttributeError: 'EmbeddedOwner' object has no attribute 'section'` when dragging local variables. The drop handler now resolves an embedded owner chain to the enclosing real statement before lexical visibility checks.
- Preserve local-variable scope restrictions across unrelated sections and prior-statement checks.
- Explicit black `×` text and high-contrast light background for variable-reference and embedded-expression removal buttons.
- Added non-GUI regression tests for recursive owner resolution, cross-section scope protection, and deletion button styling.
- 86 unittest cases pass. No Windows/PySide6 interactive runtime test performed in the build environment.
