# v26.19 — Automatic orphan Data cleanup / 自动清理孤立 Data 工作区

- Automatically removes **all orphaned Data workspaces** whose owning variable has been deleted, whether empty or nonempty.
- No need for the orphan's contents to match an existing Namespace.
- Archives nonempty and fallback-only orphan workspaces to the project recovery records before removing them; export via **Tools → Export recovered Data**.
- Recursively handles nested Data workspaces whose parent workspaces are removed.
- **Preserves both valid linked Table/Array/ScriptScope workspaces and intentional standalone Data globals (no source_id).**
- Keeps the saved `.l4vp` format and normal Squirrel code generation unchanged.

中文：仅当 Data 原来绑定过变量（有 source_id），且该变量已经不存在时，不论内容是否重复，都会自动清理。非空内容会先存入恢复记录；连带失效的嵌套分区也会清理。真正独立的全局 Data（没有 source_id）和正常绑定变量的 Data 都会保留。若孤立区包含可执行语句，删除后生成的代码可能发生变化。
