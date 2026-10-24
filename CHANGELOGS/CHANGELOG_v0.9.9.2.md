# v0.9.9.2 — 实体 For 查找方式下拉框

- 将实体 For 的“查找方式”从自由文本改成带中文说明的下拉框，列出 Valve L4D2 脚本函数文档中能够进行多实体遍历的方法。
- 切换查找方式时动态生成相应参数槽（name/model/classname、中心 Vector、搜索半径），这些槽支持变量圆块及嵌套表达式拖入。
- 支持：`FindByClassname`, `FindByName`, `FindByModel`, `FindByTarget`, `FindByClassnameWithin`, `FindByNameWithin`, `FindInSphere`, `Entities.First / Next`（全部实体遍历）。
- `FindByClassnameNearest`、`FindByNameNearest` 不属于重复遍历方法，未放入实体 For。需要查找单个最近实体时应直接使用相应官方方法积木。
- 新增 `l4visual/entity_search.py`，将可选择模式、需要的槽、参数默认值与 Squirrel 生成器收敛到同一份定义。切换模式时保留先前输入的参数，切换回来仍可使用。
- 保留 v0.9.9.1 的旧工程 `entity_for` 格式兼容性。旧版 `filter` 参数照常加载；新模式的参数缺省时自动填入合法默认值。
- `AllEntities` 生成 `for (local e = Entities.First(); e != null; e = Entities.Next(e))`，保证分支内 `continue` 后仍会推进循环。
- 将 Foreach 的可选键变量明确提示为“索引 / 键名（可选）”：Array 是序号（从 0 开始），Table 是键名，空白表示只遍历值。
- 新增实体循环示例工程 `examples/Entity_For_Methods.l4vp` 和对应生成代码。
- 新增 14 项生成器和兼容性回归测试，原有测试保留。当前环境未安装 PySide6，需在 Windows 实测下拉框与槽位尺寸。

参考资料：用户提供的 Valve 《Left 4 Dead 2 / Scripting / Script Functions》转存，以及 https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions 。
