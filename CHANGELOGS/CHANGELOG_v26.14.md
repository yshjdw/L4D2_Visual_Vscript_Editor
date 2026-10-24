# v26.14 — Spawn catalogue and ZSpawn / 生成实体目录与感染者生成

- Summon classname library expanded from 36 to 86 entries across eight nested, searchable, independently collapsible categories. Weapon items, carryables, equipment, spawn points and infected guidance are separate.
- 生成实体的 Classname 库新增二级分类及常见枪械、药品、投掷物、近战、刷新点等，中文/英文及 General/Professional 模式正常取标签、提示。
- Summon right-click configuration now has a two-level category selector as well as a manual classname field. Editing other settings without touching the classname preserves already embedded classname expressions.
- Added a distinct **Spawn infected (ZSpawn)** source-block statement for 0–8 common/special infected types and a Vector position. Native code generation uses ZSpawn(table), not SpawnEntityFromTable for special infected.
- Expanded optional spawn keyvalues (`melee_weapon`, `ammo`, `skin`, `body`), which remain disabled unless explicitly checked.
- Existing .l4vp projects and literal payload IDs are unchanged. No named user variables or existing Summon blocks are rewritten.
- Regression tests exercise category completeness, codegen, bilingual tooltip and infected types. Does not claim full L4D2 runtime verification.
