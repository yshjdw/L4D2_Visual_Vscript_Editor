# v26.18 — Safe orphan Data cleanup / 安全清理孤立数据工作区

- Automatically removes empty orphaned Data workspaces as before.
- Also detects **strictly identical** nonempty orphan Data/Namespace pairs and removes only the obsolete Data section.
- Archives the original removed nonempty workspace inside the `.l4vp` project (`recovered_workspaces`) so it can be exported from Tools.
- Keeps nonempty orphaned Data workspaces that contain unique, ambiguous or nested content, and continues showing validation errors until repaired manually.
- Does not modify generated Squirrel code or change the `.l4vp` schema version.

中文：空孤立分区继续自动清理；对已经与 Namespace 定义完全一致的孤立非空 Data 工作区自动去重，原始内容归档在工程恢复记录中。内容不一致、嵌套或无法确认的数据不会自动删除。可以通过“工具 → 导出已恢复的 Data 分区”导出恢复记录。
