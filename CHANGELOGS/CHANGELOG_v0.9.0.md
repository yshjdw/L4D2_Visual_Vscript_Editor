# v0.9.0 — ScriptScope / Table / 赋值运算

- 变量类型下拉框新增 `ScriptScope`。该类型在可视化编辑中按 Table 处理，Value 槽填写实体表达式（例如 `ent`）；生成代码先执行 `ent.ValidateScriptScope()`，随后 `local scope = ent.GetScriptScope()`。
- 普通变量 Value 为 `ent.GetScriptScope()`、或嵌入官方 `GetScriptScope` 表达式时，自动识别为实体作用域 Table。不覆盖原始函数调用；支持直接打开已有 Table 嵌套工作区并添加成员。
- ScriptScope Table 工作区内新增变量将生成 `scope.member <- expression`；在子 Table/Array 工作区新增数据将生成嵌套 `{...}` / `[...]`。不会把 GetScriptScope 的运行时值替换为 `{}`。
- 新增赋值积木下拉框：`auto`, `=`, `<-`, `+=`, `-=`, `*=`, `/=`, `%=`。auto 对简单目标使用 =，对成员目标选择 <-；动态目标建议用户显式选择 = 或 <-。新槽位 `<-` 不支持裸 local 名称。
- 支持 v1 `.l4vp` 结构，旧项目读取不需要迁移。
- 新增 `examples/ScriptScope_Demo.l4vp` 和 `examples/scriptscope_demo_generated.nut`。
- 102 项非 GUI 测试通过。未完成 Windows PySide6 实际交互及 L4D2 游戏内验证。

## 用法

1. Function 内创建实体变量 `ent`（由参数或查找积木取得）。
2. 新建变量 `scope`，类型选择 `ScriptScope`，Value 填 `ent`。
3. 点击“打开数据定义分区”，直接往 Table 根容器中添加 `hp`、`inventory` 等成员，复杂成员继续打开自己的嵌套窗口。
4. 在赋值积木中用 `=` 修改已有成员，`<-` 创建/覆盖 Table 槽位。Source 标识符不是 Table 时不能使用 `<-`。
5. 也可以将 `ent.GetScriptScope()` 直接放入普通变量 Value，编辑器自动把它识别为 Table。

**注意**：实体变量必须有效；`ValidateScriptScope()` 不负责校验实体句柄。`ScriptScope` 下拉类型 Value 需要填实体本身，不应再填 `ent.GetScriptScope()`。如把成员赋值放进顶层 Namespace，目标实体必须在运行到该语句时已经存在。自动模式只能使用保守的表达式形态判断，不能保证动态 Table 成员是否存在。
