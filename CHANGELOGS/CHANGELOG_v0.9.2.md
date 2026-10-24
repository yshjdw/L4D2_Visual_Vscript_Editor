# v0.9.2 — NetProps 方法参数与选择窗口修复

- NetPropPicker 作为独立顶层 Qt.Window 打开，不再作为 QGraphicsProxyWidget 内积木的子窗口被剪裁；允许移动、调整尺寸，应用模态。
- 所有已识别的 CNetPropManager / NetProps `GetProp*`、`SetProp*`、`HasProp*` 方法中的属性名参数改为“选择 NetProp”按钮；支持普通方法积木与嵌套表达式内方法积木。
- 由实体类 → 属性路径选择，选择结果以 `literal` Squirrel 字符串保存，自动引用与转义；保持旧工程的已有字符串可显示、重选。
- NetProps 专用积木属性选择窗口、BlockEditor 属性选择也统一改为独立窗口。
- 新增 5 项回归测试，现有 112 项非 GUI 测试通过。

**限制**：无法在本环境实机运行 Windows PySide6 GUI；嵌套方法的任意复杂参数列表以及游戏实际 NetProp 类型需要进一步验证。老工程里已填的非属性表达式不会被自动删除，用户需重新选择属性。
