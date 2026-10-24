# v0.7.3 - Data variable docking and Array operations

- Data variable round tokens can be dragged into expression/value sockets.
- Drop resolves the variable declaration by stable ID and emits full namespace/table/array paths, e.g. `::MyScript.data.items[0]`.
- Complex variable windows retain an independent canvas and display one non-deletable C-style definition root. All definition children reside inside this root.
- Added Array (UI: Set `[]`) operation blocks: append, push, extend, insert, remove, pop, top, resize, clear, len, reverse, sort, slice.
- Parameter slots change when operation changes; non-void Array operations may be embedded in value sockets.
- In a Set data definition, operations generate statements **after** the initial Array/Table declaration. They are not inserted into the literal `[]` initializer.
- Array operations are rejected inside Table (`{}`) definition roots.
- Existing `.l4vp` v1 format unchanged.
- 50 automated non-GUI tests passed. GUI/touch behavior still requires testing with PySide6 on Windows.

## Limitations

- A dropped variable reference is resolved to a Squirrel expression when dropped. If a parent variable is later renamed, the already-inserted expression is not yet automatically rewritten; an ID-backed reference node and project-wide refactoring are planned.
- Only direct root members and recursively linked Data members are type-aware in this version. Dynamically typed runtime fields remain manually editable.
- Data operations have initial post-initialization support; script-dependent ordering should be reviewed for projects whose operation arguments call functions declared later.
