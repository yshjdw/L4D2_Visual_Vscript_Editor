# v0.9.5

- ScriptScope 的 Table 嵌套编辑区增加成员初始化策略：仅首次创建（默认）、每次覆盖、仅修改已有成员。
- 仅首次创建：`if (!scope.rawin("name")) scope.name <- value;`；避免事件重复触发时覆盖先前保存的数据。
- 每次覆盖：`scope.name <- value;`；仅修改已有成员：`if (scope.rawin("name")) scope.name = value;`。
- 使用成员的稳定名称进行 rawin 检查；嵌套 Table / Array 以完整字面量作为该成员的初始值。
- 初始化方式记录为各成员 `init_mode`，随 `.l4vp` 保存与恢复。没有该字段的旧工程采用默认仅首次创建。
- 普通 Table / Array 构造器不受 ScriptScope 初始化策略影响。该选择器位于 Data/Table 工作区，只有作为 ScriptScope 定义时才影响输出。
- 添加 5 个回归测试；122 项非 GUI 测试通过。

仍未完成 PySide6 Windows 鼠标实测和 L4D2 游戏内行为验证。若不同事件要共享成员，需指向同一实体，且在读取前完成初始化。
