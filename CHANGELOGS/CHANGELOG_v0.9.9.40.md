# v0.9.9.40

- Expanded L4D2 draggable classnames: regular weapon entities, weapon/item spawners, logic, environment, props, triggers and infected entities. The list is a vetted common subset, not every Source engine classname.
- Added the remaining stock weapon and ammo/aid names, all stock melee script names and carryable mission item names. Identifiers are categorized by API use; melee names are not distinct entity classnames.
- Added a dedicated first-person V equipment/throwable/cola model group; corresponding world W models including cola are kept separate. Added viewmodel of M60, more melee first-person models, survivor arms and infected first-person claws/arms. Some props correctly remain world-only.
- Known V/W counterpart paths are displayed in both English and Chinese tooltips, without guessing missing counterparts.
- Kept previous literal groups and .l4vp codegen intact, and preserved English/General/Professional captions.
- Cross-checked with Valve L4D2 weapon and item spawner documentation, stock L4D2 weapon asset lists and model filename indexes (links in DATA_SOURCES.md).
