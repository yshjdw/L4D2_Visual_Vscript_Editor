# v26.3

- Fixed the hit-testing area of overly wide canvas sections: the `QGraphicsProxyWidget` now expands to include the real rightmost nested child control, even when Qt layout size hints are stale.
- Updated the scene bounds after synchronization to keep rightmost sockets, drop targets, context menus, and mouse interaction reachable.
- Added right-edge geometry regression tests; no project format or Squirrel codegen changes.
- Updated editor window title to 26.3.

UI behaviour still requires verification with PySide6 on Windows.
