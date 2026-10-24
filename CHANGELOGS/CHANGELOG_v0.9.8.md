# v0.9.8

## 普通变量成员选择误触发
- 普通变量（container_type=普通）不能右键选择成员；只对 Table/Set/ScriptScope 和事件 env 显示成员选择入口。
- 嵌入表达式里的普通变量也不再通过右键/双击打开 MemberPicker，避免打开无内容的窗口并干扰画布。
- Table、Set、ScriptScope 和事件 env 原有成员选择与返回根变量功能保留。

## .nut / VPK 导出
- 文件菜单新增“导出 VPK 模组”。
- “导出当前 .nut”及“批量导出工程 .nut”完成后，可选择是否同时打包 VPK。
- 独立 VPK 信息窗口支持模组名称、作者、版本、简介。作者自动追加 `/Vscript Visual Maker`，已有后缀不会重复添加。
- 自动生成 VPK v1 单文件存档，内含 `addoninfo.txt` 和 `scripts/vscripts/<文件名>.nut`，支持子目录。
- 阻止 `..` 等不安全的归档路径。

## 验证
- 140 项非 GUI unittest 通过、Python 编译通过。
- 无 Windows PySide6 GUI 和 L4D2 游戏运行环境：VPK 的游戏内加载及 GUI 交互尚未实机验证。
