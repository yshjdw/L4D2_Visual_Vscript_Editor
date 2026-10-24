# v0.7.8 — 2026-10-21

## Changes

- New Summon block uses L4D2 `SpawnEntityFromTable(classname, keyvalues)`.
- Summon has a detached, scrollable config window (right-click the block -> Summon 配置工作区). Each key is off unless explicitly checked. When all off, emitted keyvalues are `{}`. Disabled keys are omitted (not empty strings).
- Entity picker includes documented L4D2 weapon/item spawn point classnames and a smaller group of generic entity examples. The catalogue is **not** an exhaustive guarantee of VScript runtime spawnability: entity-specific keyvalues and engine restrictions still apply.
- Project tree now shows `scripts/vscripts/` explicitly; newly generated project entry can be `director_base_addon.nut`, `scriptedmode_addon.nut`, or `mapspawn_addon.nut` depending on selected load context. The file name `direct_addon_xxx.nut` is not treated as the universal native entry.
- Project `.nut` file items can be dragged into an expression/text socket. This inserts an `IncludeScript("filename")` expression in that socket; `.nut` suffix is removed. Avoid dragging a file onto a position that would cause the same script to load itself.
- External-library methods are shown as draggable blocks; their receiver now defaults to the external owner (e.g. `ArmorSystem.LoadArmor(...)`) rather than the placeholder `entity`. The external API description dialogue and palette refresh remain accessible via Tools.
- Method hover info preserves per-method signature/parameters/source link; event hover info preserves known field metadata and source. **Not all methods/events have individually verified official prose descriptions in the offline database.** Missing text is explicitly identified rather than guessed.
- Existing .l4vp serialization is unchanged.

## Limitations

- PySide6 GUI could not be launched in this execution environment. Mouse/touch/drag operations require an interactive Windows smoke test.
- Actual `.nut` script behavior and specific entity keyvalues have not been run in L4D2.
- No automatic import of existing `.nut` source.

## References

- https://wiki.alliedmods.net/Left_4_Dead_2_Events
- https://developer.valvesoftware.com/wiki/L4D2_Level_Design/Weapon_and_Item_Spawning
- https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions
