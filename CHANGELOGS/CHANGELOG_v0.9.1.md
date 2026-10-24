# v0.9.1 — NetProp 选择器

- 从用户提供的 `List of L4D2 Netprops` 文本建立 `resources/netprops_2024.json`，含 278 个实体网络类、1586 条原始属性记录。附带字段类型、offset、继承表类型和来源说明。
- `netprop_catalog.py` 提供实体类过滤、继承属性查找与网络类型到 GetProp API 类型的初步映射。
- `NetPropPicker` 是独立的两级窗口：先选择实体网络类，再展开嵌套成员并双击末级属性；支持搜索和返回上一步。
- 积木上的 NetProps `property` 现在是按钮，而不是可编辑文本槽；BlockEditor 也使用同一选择器。
- 右侧 NetProps 词典以实体类作为父节点，并展开多级属性路径。
- 保持原有 `.l4vp` 中保存的属性字符串可读取，重新选择后会同步写回 `table/property/prop_type/netprop_type`。
- 107 项纯 Python 测试通过。Windows PySide6 图形界面与游戏内 NetProps API 调用未实测。

## 限制

- 来自 SendTable 的 `type integer` 可能是网络实体 handle 或 bool，不能仅凭文档的粗类型自动区分。此版本默认映射为 Int，需要后续补充具体验证后的 API 特例。
- 继承成员通过 DT 基类链展开；文档中不提供继承类或列为 Exclude 的属性不会编造。
- `m_Collision.m_vecMins` 这样的嵌套路径来自文档层级，实际 NetProps API 可访问路径请在 L4D2 里验证。
