# v0.9.9.6 — 可换行参数布局

- 将积木主参数行由固定的 QHBoxLayout 改为 WrappingFields。参数槽宽度不足时，将完整参数控件换至下一行，避免 NetProps、嵌套表达式和包含长名称的字段被压缩成窄条。
- WrappingFields 支持 Qt 的 heightForWidth、sizeHint 与 minimumSize，使积木随行数增加高度。
- ExpressionSlot 根据内部控件调整最小宽度，防止多层嵌入时子槽位被布局压缩。
- 保持已有 Block、Section 与 .l4vp 数据结构不变；仅修改渲染布局。
- 添加布局代码回归检查；实际 Windows GUI 视觉效果仍需 PySide6 实机验证。
