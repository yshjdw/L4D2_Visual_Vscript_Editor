# v0.9.9.42 — Nestable Utility Wrappers / 通用工具可嵌套及扩充

## English

- Fixed the real cause of Utilities refusing parameter-slot drops: `utility` was omitted from `can_embed`. The block library already emitted `MIME_BLOCK` and the canvas already handled it; it now accepts the type.
- Expanded from 5 to 25 built-in utility expressions, organized into four collapsible groups: Players & weapons, Inventory & slots, Entity lookup & checks, and ScriptScope data.
- Added safe inventory-slot access `GetInvTable(player, inv)` for slot0–slot5, plus dedicated slot4, slot existence, slot classname, complete inventory table and inventory classname queries. Empty slots return null/false rather than dereferencing missing keys.
- Added entity validity, safe active weapon/classname, player name/UserID/health, button-mask detection, clip size, classname lookup and ScriptScope member access.
- Utility blocks support expression nesting, multi-argument sockets, right-click deletion, language/style-aware captions, and independent bilingual hover help.
- No hidden global declarations are generated: compound expressions are inline Squirrel function expressions. Original five utility operations and saved block data remain compatible.
- Search expansion now also remembers utility group expansion and restores it after clearing the search.

## 中文

- 修复通用工具无法拖入表达式槽的根因：`can_embed` 未接受 `utility`，而非拖动数据本身缺失。
- 通用工具从原来的 5 种扩充为 25 种，分四组折叠：玩家与武器、背包与槽位、实体查找与检查、ScriptScope 数据。
- 新增 GetInvTable 安全读取 slot0–slot5、slot4 快捷版、槽位存在检测、物品 Classname、完整背包 Table、按 Classname 检查背包。
- 新增实体有效性、安全获取当前武器、玩家名称、UserID、实际生命值、按键检测、弹匣容量、实体查找以及 ScriptScope 成员读取等。
- 允许嵌套表达式和多参数槽，支持中英文、General / Professional、悬停提示、删除与拖拽。
- 复合表达式以内联 Squirrel 函数方式输出，不产生额外全局命名空间或强制依赖；兼容原有五个快捷工具的保存格式。
- 搜索过程会保留新增四个折叠组的展开状态。

## Testing / 测试

- `python -m unittest discover -s tests -q`
- Python `compileall` and archive CRC test.
- Real PySide6 drag and GUI visual testing unavailable in this runtime.
