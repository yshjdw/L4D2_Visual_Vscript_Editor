# v0.9.4

- Restore copy-drag for embedded oval variable references. Dragging creates a fresh reference in the destination slot without removing the source.
- Add a grip to embedded oval/hexagonal expression nodes to copy their full nested expression AST to another compatible socket.
- Enable QGraphicsView edge auto-panning during supported drags using a 35-ms timer and a 65-pixel viewport margin. Timer stops on drag leave/drop.
- Preserve lexical scope checks when copying local variable references between sockets.
- Tests: static drag protocol checks and existing non-GUI tests. Windows GUI still requires manual testing.
