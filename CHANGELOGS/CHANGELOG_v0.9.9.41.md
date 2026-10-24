# v0.9.9.41 — Two-level Classname and Item catalogs / 双层分类

## English

- Reorganized the draggable **Entity classnames** and **Items** libraries into two-level collapsible groups. Each top-level group contains named child groups (weapons, medical supplies, spawners, logic, map effects, melee, mission items, etc.).
- Each value appears only once in the palette, while the old `classname`, `item`, `item_melee`, `item_world` and `classname_*` data IDs remain valid for existing projects.
- All new group captions and descriptions support Chinese and English, as well as General and Professional styles for the individual string-literal blocks.
- Search (Enter to apply) expands matching groups, preserving the complete two-level open/closed state from before searching. Clearing the search box restores everything immediately, without Enter.
- No change to literal values or generated Squirrel code. No change to the `.l4vp` format.

## 中文

- 将 **Entity Classnames** 和 **Items** 两个长列表改为二级折叠目录（例如枪械、补给、刷新点、逻辑实体、环境特效、近战、任务物品）。
- 去掉工具库重复展示的条目，旧版项目引用的 literal group ID 仍可使用。
- 子分类标题与悬浮说明均提供中文和英文，积木仍支持 General / Professional 显示。
- 回车触发搜索时展开匹配子分类；搜索之前的两层展开状态会被保存。清空搜索框立即恢复原始展开状态。
- 不改变 `.l4vp` 工程格式和生成的 Squirrel 字符串。

## Testing / 验证

- `python -m unittest discover -s tests -q`
- Python source compile and ZIP integrity check.
- No PySide6 GUI test in this environment; real Qt mouse/drag interaction requires Windows verification.
