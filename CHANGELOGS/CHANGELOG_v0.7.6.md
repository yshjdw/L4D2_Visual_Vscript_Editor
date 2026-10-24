# v0.7.6

- 将变量引用拖入 `value` 槽后保留 `variable_ref` AST 节点，并显示金色圆形变量引用控件；删除引用后恢复原文本输入框。不是把路径直接改写到 QLineEdit。
- 修复 `ability_use` 无成员候选：已核对字段 `userid`、`ability`、`context`，并补充少量可核对事件。
- 修正 `weapon_reload` 字段为 `userid`、`manual`。
- 下拉框及其弹出列表文字统一黑色。
- 未经逐项核对的事件字段不自动猜测，仍保留手工填写入口。
- 这是第一轮结构化引用：已写入 `symbol_id` 与路径；跨重命名的全量符号自动重绑定尚未实现。

资料依据：
- https://wiki.alliedmods.net/Left_4_Dead_2_Events
- https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions
