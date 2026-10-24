# v0.9.9.22

- 单一 Delete：右键删除精确命中的节点及所有内部积木；保留兄弟积木。
- 参数槽内部表达式（包括 operator）独立命中；删除后参数恢复 null。
- 新增变量默认作用域恢复 auto；旧工程维持原有设定。
- 工程树 .nut 文件拖至 IncludeScript 参数槽时显式生成 getroottable() 第二参数。
- 文件拖入独立 IncludeScript 文本框同样显式生成 getroottable()。
