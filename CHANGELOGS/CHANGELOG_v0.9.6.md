# v0.9.6

- Fixed C-shaped branch first-slot insertion when dropping onto the branch header.
- Stop auto-pan when a drop is intercepted by the viewport event filter, and reject unrecognized drag MIME types.
- Added dedicated draggable ScriptScope member list to Data workspace.
- Added `reference` mode for ScriptScope members: no runtime assignment or creation code is emitted.
- Cross-window member copy automatically creates a reference-only data member when source and destination have identical entity bindings.
- Cross-event reference resolution now uses the destination's own bound ScriptScope alias instead of leaking a local name from the source event.
- Added non-GUI regression tests for ScriptScope member copying, modes, mismatch rejection.
