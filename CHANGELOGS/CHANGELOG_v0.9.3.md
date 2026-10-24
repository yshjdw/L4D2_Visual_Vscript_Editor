# v0.9.3 — Data workspace isolation

- 修复工程文件中 `kind=data` 的辅助数据分区错误地加载到主工作区。
- 主画布默认跳过辅助 Data 分区，只渲染 Namespace/Function/Events/Init 等顶层工作区。
- Table/Array/ScriptScope 的独立编辑窗口显式允许显示 Data 分区及不可删除根容器。
- 工程栏的脚本节点不再将内部 Data 分区暴露为常规顶层编辑分区。
- 不更改 `.l4vp` 文件存储格式，完整保留成员定义以及引用。
- 该问题由用户提供的 `keep_ammo_on_relaod.l4vp` 验证，其中 `data value` 包含 `ammo` 成员。

注意：当前环境未安装 PySide6，尚未进行 Windows UI 实测。
