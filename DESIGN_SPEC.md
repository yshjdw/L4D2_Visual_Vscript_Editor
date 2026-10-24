# L4D2 Visual VScript 原型设计规范 / v0.2

## 1. 工程与 AST

- `Project`：项目名、事件回调归属 Table、脚本文件列表、外部函数库。
- `ScriptDocument`：一个 `.nut`，保存 IncludeScript 依赖、若干 Section。
- `Section`：独立可拖动分区：namespace、function、think、events、init、data。
- `Block`：基本单元：`kind/args/branches/id`；`branches` 承载 if/for/while/try/event 的内部块。
- 数据结构以 AST 保存，画布的 x/y 仅是布局信息，**不决定词法作用域**。

## 2. 变量

- 函数内部新增普通变量默认生成 `local`，函数外默认为根作用域 `::Name <- ...`，命名空间成员为 `::Owner.Name <- ...`。
- 变量圆形模块与原定义共享唯一 ID；右键修改名称，左键复制引用并拖到参数槽；禁止拖动导致隐式重新声明。
- 复杂变量分 `Table {}` 与 `Set []`；后者是编辑器术语，实际对应 Squirrel Array（不是真正 Set 集合）。
- 在命名空间/文件初始化/data 定义区对复杂变量右键，可打开独立数据定义分区；分区以变量 ID 绑定，不依赖变量名。
- data 分区仅接收变量声明、赋值/成员赋值、调用、官方方法、NetProps 等数据相关模块。任何 if/for/while/event/try 均不允许直接放入。
- 嵌套数据定义通过 `source_id/parent_section_id` 递归连接，在源码中只生成**一个包含所有层级**的 `{}`/`[]` 初始化表达式，而不是重复声明子对象。
- 子定义区的附加赋值/调用语句放在顶层初始化期执行，不会非法塞入 `{}`/`[]` 的字段位置。
- 变量链组合成 AST 的 `member` 和 `index` 节点，根对象结构已知时逐级提供下拉候选；索引允许数字表达式。

## 3. 函数、API 与 NetProps

- 自定义函数：由独立函数分区的名称/参数列表管理，调用积木从当前工程函数符号中选择并展示参数槽。
- 官方 API：独立工具块，有对象插槽、参数插槽与可选的黄色返回变量圆形端。`void` 方法不可绑定输出变量。
- NetProps：Get 为对象/属性两个基本输入槽和可选结果变量；Set 为对象/属性/值三个槽。数组版本再显示索引输入。
- NetProps 第二槽先根据实体表达式推测 SendTable，然后检索索引及其继承链；推断失败仍可手动选表、输入属性。
- 外部 API：以 JSON 存储在工程的 `library` 字段，预留属性 Schema、函数签名与返回类型扩展。对于无法获得源码的第三方 Mod，可手工注册。

## 4. 流程控制与事件

- `if`（可增加 Else If）/while/Foreach/数值 For/实体 For/try-catch/return/continue/break/throw。
- 数值 For 输入数字 N 表示遍历 `[0,N)`；输入 `range(start,stop,step)` 由生成器翻译成原生 Squirrel for，不导出 `range()` 函数调用。旧项目的 `start/stop/step` 仍兼容。
- 原版事件采用半椭圆块，只能放到事件监听分区；每个事件块带一个可拖出的 `env` 形参变量，注册时自动生成 `__CollectGameEventCallbacks`。
- `Think` 分区可以创建全局 Think 函数，支持自动寻找/生成 info_target 并附加 Think；运行时复杂生命周期由用户手动修改或使用高级积木实现。
- 多行字符串窗口将真实换行转成安全引用的多个 Squirrel 字符串拼接项。

## 5. 代码生成与验证

- 先建立必要 Table，再生成复杂数据和函数定义，最后执行文件初始化操作；`.nut` 文件依赖可通过工程树设置，导出 `IncludeScript()`。
- 语义检查：事件分区限制、数据分区限制、函数/分区命名合法性、NetProps 离线查找、API void 结果误用、循环控制越界、文件依赖循环、绑定的复杂数据分区孤儿/类型不一致。
- 原始表达式块留作逃生舱，当前不尝试解析现有 `.nut` 文件反向生成 AST。
- `.l4vp` 为版本化的压缩自定义容器，含摘要但未加密。导出 `.nut` 为另一个步骤。

## 6. 代码结构

| 模块 | 职责 |
|---|---|
| `l4visual/models.py` | Project/Document/Section/Block 模型 |
| `l4visual/data_definitions.py` | Table/Set 定义分区、递归渲染、绑定和重命名 |
| `l4visual/codegen.py` | 表达式及 Squirrel 语句生成 |
| `l4visual/storage.py` | .l4vp 压缩文件保存/恢复 |
| `l4visual/catalog.py` | SQLite API 查询 |
| `l4visual/symbols.py` | 按 ID 修改引用 |
| `l4visual/type_inference.py` | 基础实体 SendTable 类型推断 |
| `l4visual/validation.py` | 静态检查 |
| `l4visual/ui/canvas.py` | 分区画布、变量端口、拖入/右键 |
| `l4visual/ui/chain.py` | 嵌套成员/索引表达式编辑器 |
| `l4visual/ui/dialogs.py` | 积木、函数、分区属性编辑 |
| `l4visual/ui/main_window.py` | 工程栏、工具库、API 浏览、代码预览 |

## 7. 后续重点（本次不实现）

1. 当前内层块是列表编辑，不是物理凹槽嵌套拖拽；需要构建真正的形状/连接约束引擎（语句接口、表达式接口、C 形容器）。
2. 扩充官方 API/事件字段/NetProps 数据库，并标记来源、版本和可写性，不应假设所有属性写入安全。
3. 精确的语义类型推断、函数返回路径分析、作用域生命周期、数据流 null 检查。
4. 测试完整 `Juggernaut_DLC` 案例，和原脚本逐项对比、游戏内测试。
5. 暂不做游戏运行环境、调试或 `.nut` 反向导入；这两项已明确排除。
