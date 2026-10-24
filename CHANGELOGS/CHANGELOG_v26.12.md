# v26.12

- Add **Entity from entity index / 根据实体索引获取实体句柄** under **General utilities → Entity lookup & checks**.
- Generates `EntIndexToHScript(env.weaponentid)` by default; edit the input to `env.entityid`, `env.propid`, `env.attackerentid`, or any other *entity index*.
- Clearly distinguish entity indices, player userIDs, and weapon-type IDs in both languages.
- Support English/中文, General/Professional captions, bilingual tooltips and existing nested drag/drop expression sockets.
- Retain existing project format and all utility operation IDs.
- Add v26.12 regression tests for Squirrel code generation, type, expression embedding and metadata.
