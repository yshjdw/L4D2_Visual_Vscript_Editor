# v0.9.9.37

- Palette: long English and Chinese titles wrap into additional lines and increase card height, instead of widening the entire left dock. Cap the palette dock width at 420px.
- Utilities: fix English tooltip fallback for `weapon_classname`; regenerate utility/operator/boolean/event tooltips on language switch.
- Defaults for new installations: English + General. Existing saved presentation settings remain unchanged.
- Move every prior `CHANGELOG_v*.md` file into `CHANGELOGS/`; update README and START_HERE paths.
- No changes to saved projects or Squirrel code generation.
- Move KMP substring matching into a Qt-independent module for direct testing.
- Translate embedded database provenance strings in English API and event hover tips; verified against full offline catalog.
