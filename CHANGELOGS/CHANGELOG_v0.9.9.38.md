# v0.9.9.38 — Draggable entity strings and search-state restoration

## 中文
- 新增三组可直接拖入参数槽的字符串常量：实体 Classname、常用 GiveItem 名称、常见实体 `.mdl` 模型路径。
- 常量积木按中文 / English、General / Professional 显示对应名称，悬停提示包含实际生成的字符串、适用范围和注意事项。
- 常量生成双引号字符串字面量，而非裸标识符；已有项目格式不变。
- 搜索之前保存所有可展开组的状态（官方方法、事件、字符串分类）；搜索仅按 Enter 激活，清空搜索框立即还原未筛选列表及原始展开状态。
- 内嵌的较长模型路径标签限制单行宽度并换行，不影响生成的完整路径。

## English
- Added draggable string constants for entity classnames, common GiveItem names, and stock `.mdl` model paths.
- Labels and tooltips follow both language and display-style settings; tooltips include the exact generated string and usage cautions.
- Generated expressions use quoted string literals rather than unbound identifiers; existing project formats remain compatible.
- Preserve expansion state for official method, event, and new literal groups before the first search. Search still runs on Enter; clearing the field immediately restores all items and the saved expansion state.
- Long model paths wrap within embedded expression labels instead of widening the canvas unnecessarily.

**Validation**: 293 tests (292 passed, one skipped), Python compilation, ZIP integrity. Qt live GUI has not been exercised in this environment.
