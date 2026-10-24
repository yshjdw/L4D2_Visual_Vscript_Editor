# v0.7.2 (GUI fix)

- 修正分区标题拖动鼠标坐标取样：使用 QCursor 屏幕坐标统一映射到 viewport / scene，避免代理控件叠加坐标变换引起跳动。
- 积木变量右键菜单与普通积木右键菜单改为使用顶层 QMenu + QCursor.pos()，避免代理控件错误定位。
- Function 创建与编辑：所属 Namespace 改为当前 .nut 文件已有 Namespace 的必选下拉；无 Namespace 时阻止确认。
- 在 Namespace 与所属 Function 分区之间绘制浅蓝色虚线，随拖动和分区尺寸更新；连线纯视觉，不改变分区保存坐标。
- Namespace 改名时同步更新其 Function 的 owner 属性。
- 分区属性类型切换时，清除并禁用不适用的控件数据；仅保存适用字段。
- 顶部工具栏增加独立 `－ / ＋ / 100%` 画布缩放操作。

验证：44 个非 GUI 单元测试通过，Python compileall 通过。`tools/gui_smoke.py` 添加了 Namespace 连线、选择和禁用字段测试。此环境无 PySide6，GUI 自检须在 Windows 执行。
