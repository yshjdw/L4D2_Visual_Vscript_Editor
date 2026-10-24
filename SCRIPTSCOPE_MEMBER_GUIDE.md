# ScriptScope Member Library / ScriptScope 成员引用库 (26.13)

## 中文

在任一 ScriptScope 的 Table 数据工作区底部点击「刷新成员」，即可查看**当前 .nut 文件**中全部已经定义的 ScriptScope 成员，不需要来源和目标的 local 变量名称相同，也不需要实体表达式一致。

- 将成员拖入目标 ScriptScope 数据容器：创建「仅引用」成员，访问的是目标自身的 ScriptScope，不重复执行初始化。
- 将成员拖入表达式参数槽：生成目标区域内 ScriptScope 变量名加成员名，如 `other_scope.pills_used`。若目标有多个可见的 ScriptScope 变量，弹窗选择使用哪一个。
- 列表显示来源工作区；悬停提示还会标注实体表达式。General 和 Professional 都保留原本的 Squirrel 成员标识符。

**注意：** 仅引用不会在其他实体上自动创建成员。如果源和目标实际上是不同实体，必须先在目标实体的 ScriptScope 中初始化该成员，再读取它。没有可见 ScriptScope 变量的代码区域不会猜测一个变量名。

## English

Click **Refresh members** at the bottom of any ScriptScope Table workspace to see all ScriptScope members **defined in the current .nut document**, regardless of the source or destination's local alias or entity expression.

- Drag into a different ScriptScope Data workspace to add a **reference-only** member. It uses the destination's own ScriptScope handle and does not initialize a duplicate.
- Drag into an expression socket to generate a reference using a ScriptScope variable visible in that code section, for example `other_scope.pills_used`. A chooser appears when more than one suitable variable is visible.
- Labels identify the defining workspace; tooltips show the source's entity expression. Squirrel identifiers remain unchanged in General and Professional modes.

**Important:** A reference-only entry does not create a member on another entity. If the source and destination refer to different entities, initialize the member on the destination entity first. If no ScriptScope variable is visible, the editor does not guess an alias.
