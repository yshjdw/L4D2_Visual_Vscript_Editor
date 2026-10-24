# v0.9.9.23

- 修复嵌套表达式右键 Delete 菜单因 QGraphicsProxyWidget 坐标映射偏移而出现在画布其他区域的问题。
- 使用 QCursor.pos() 定位菜单，保持已有 Scratch 式精准删除行为。
