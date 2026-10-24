# v0.7.4 — 事件积木 / 成员选择 / Help / 作用域

在 v0.7.3 基础上追加，不改变 `.l4vp` 工程模式版本。

## 本次新增

1. 变量圆圈右键新增“选择成员变量…”，弹出带系统窗口标题栏的独立 MemberPicker。支持 Table 的成员网格、Set（Squirrel Array）的索引网格、左键选择引用、右键进入嵌套、× 返回上一级和手动输入动态成员。选择作用于拖出的引用，不会重命名原始声明。
2. 游戏事件从统一的可编辑事件工具块改为按用途分类的单独帽子积木，基于本地事件数据库提供名字。只接受事件积木进入事件分区。常见事件有经过人工核对的字段提示，其他事件允许在选择器内手填字段；未声称拥有完整事件字段数据库。
3. 左侧工具栏不再提供自由填写名字的“官方方法”和“原版游戏事件”通用积木入口。官方方法、事件从数据库生成实际积木。旧工程的已有事件节点继续支持。
4. 新增 Help / 帮助 > 实体获取与组合实例，介绍幸存者、player、普通感染者、特感、Witch、物品、武器以及 FindByClassname + GetOrigin 的安全组合示例。
5. API 字典增加常驻“展开 / 收起 API 字典”按钮。
6. 新建变量的 scope 改为 auto、local、无、static；`local` 禁止跨所属分区拖动引用，auto 在 Function/Think/Events 分区中视为局部声明。`无` 对已存在的变量赋值（不会创建新槽）；Squirrel 静态变量只合法用于 class 内，当前项目尚无 class 编辑分区，因此 static 会被编译器明确提示错误。
7. 增加官方方法的对象、参数槽说明及常见事件 env Table 字段提示。

## 数据源

- AlliedModders: https://wiki.alliedmods.net/Left_4_Dead_2_Events
- Squirrel 3 Reference Manual: https://squirrel-lang.org/doc/squirrel3.html
- 继续使用原有 resources/catalog.sqlite3 的 API、事件与 NetProps 离线子集。

## 范围与限制

- 本次对已收录事件进行自动分组，分组按事件名关键词推断，部分可能需要人工修订。
- 事件字段只为少数常用事件人工录入；其他事件以动态 Table 成员输入兼容。
- local 的跨 Function/Think/Events 分区拖入受到约束，另有按 C 形分支路径和声明顺序进行的保守可见性校验（尚非完整 Squirrel 闭包、遮蔽与绑定语义解析）。
- GUI 的触控和实际拖放尚未在 Windows 运行测试（开发环境没有 PySide6）。
- `static` 暂保留为选项并提供编译时诊断，不能在普通函数中生成不合法的 static 语句。
