# v0.9.9.33 — English UI translation audit

- Extended the English UI catalog with editor/toolbox/utility block labels, field captions, string-call argument types, tooltips, Qt dialogs, context menus, and status messages.
- Translated event-browser categories and refreshed API table headings on language changes.
- Localized dynamic labels in Chain Editor, member picker, NetProp picker and external-API method tooltips, preserving their API identifiers and user-authored strings.
- Localized dock-widget Close / Undock tooltips (avoiding Qt OS-language fallbacks), and improved translation handling for checkboxes and radio buttons.
- Corrected the app title's stale version text and fixed Help's inaccurate claim that variables default to root (actual default is auto).
- Preserved persistent variable/scope values and generated .nut output; presentation-only changes must not modify script semantics.
- Added five targeted English UI tests and verified identical source generation with the provided pills-can-be-used-many-times .l4vp sample.

Qt/PySide6 graphical interaction is not available in the test environment; visual inspection on Windows has not been performed.
