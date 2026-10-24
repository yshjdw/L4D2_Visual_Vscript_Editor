# v0.7.5 — Function 调用拖出 + 拖动异常修复

- 修复 `l4visual/ui/canvas.py` 中 DragTitle.mouseReleaseEvent 使用未定义的 `scene` 导致释放标题时 `NameError`，并触发多层 Qt 事件回调异常的问题。
- Function 分区标题右侧增加 `⠿ 调用` 拖动把手。拖入允许语句的分区或 C 形分支可创建自定义函数调用积木，原函数分区不发生移动。
- 由 Function 的所属 Namespace、名称、参数列表自动生成调用代码；参数槽初始使用 `null` 占位，需编辑为合适参数。
- 有有效返回值的自定义函数调用积木也可放入兼容表达式槽。
- Function 定义的 ID 保存在调用积木元数据内，为后续重命名同步预留关联。
- 不改变现有 `.l4vp` 存储协议和已有函数分区的 AST。

## 验证限制

通过 Python 编译检查及非 GUI 自动化测试；当前环境没有 PySide6，未做实际 Windows 界面拖放测试。
