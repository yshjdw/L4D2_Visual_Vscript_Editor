# v0.9.9.3 — NetProps 属性路径、ScriptScope 工程关联与文本编辑修复

## 2026-10-22

### 官方 NetProp 选择器
- 根据用户提供的 2024 L4D2 NetProps SendTable 文档补充 `CBasePlayer.localdata.m_iAmmo`：整数数组，32 个元素。`CTerrorPlayer` 继承后也可以选择。
- 属性浏览保留文档分组路径 `LocalWeaponData.m_iPrimaryAmmoType`；生成 Squirrel 时去掉 `LocalWeaponData.` 这类仅表示 SendTable 分组的前缀，使用 `"m_iPrimaryAmmoType"`。`m_Collision.m_vecMins` 等真实嵌套属性路径仍保留。
- 点击 `m_iAmmo` 后自动启用 NetProps Array 模式及索引槽；普通 NetProps 方法在选择属性时也按文档类型转换为 `GetPropIntArray`、`SetPropIntArray` 等兼容方法。
- 修复已保存的 NetProps 官方方法中 `GetPropFloat` 被用于已选择的整数属性的问题：当工程带有明确的 NetProp 选择类和属性元数据时，代码生成和界面会转换到对应的整数方法，不会猜测没有元数据的调用。
- 静态检查不再只依赖早期 SQLite NetProp 索引，而是与 `resources/netprops_2024.json` 中继承的属性记录对照；补充武器方法错误地以玩家作为目标的提示。

### ScriptScope 和局部作用域
- 加载旧 `.l4vp` 时，自动剔除“无绑定源且不含任何积木”的废弃 Data 分区；不删除任何含内容的分区，也不删除仍有效绑定的 ScriptScope 引用。自动清理后工程会提示保存。
- 对跨事件/分支错误引用 `local` 变量进行静态报错，例如 `weapon_fire` 使用了只在 `weapon_reload` 内声明的 `player`。
- 如果引用的原始 `env` 积木符号 ID 来自另一事件，但目标事件本身有同名 `env` 形参，仍按当前事件的合法参数处理。

### 文本与自定义 Squirrel 模块
- 画布 `Space` 拖拽快捷键不再抢占正在输入的 `QLineEdit`、`QTextEdit` 或 `QPlainTextEdit` 中的空格。
- 点击非文本区域结束正在编辑的输入框焦点；点击同一文本框仍可正常选择文本。
- `ClientPrint(message)` 等普通表达式槽可按输入内容自动加宽（最大宽度 900 px，超长文本仍可在框内移动光标）。
- 高级“原始代码”积木使用多行 `QPlainTextEdit`，支持回车、粘贴多行 Squirrel 代码，并依据行数自动扩大高度。

### 验证
- 175 项非 GUI unittest 通过。
- `python -m compileall` 通过；完整 ZIP 已校验。
- 当前环境没有 PySide6，也未在 Windows 与 L4D2 游戏中实测鼠标操作和脚本效果。

### 用户上传的 keep_ammo_on_relaod(1).l4vp 检查结论
- 保留有一个不含积木的废弃 `scope [data]`，新版本打开时会清理。
- `weapon_fire` 中的 `player` 指向 `weapon_reload` 声明的局部变量，无法跨事件直接使用。每个事件都必须取得自己的 `player` 句柄，或另行定义可共享的数据存储。
- `m_iClip1` 是武器属性，不应对 `player` 调用 `GetPropInt` / `SetPropInt`，应传入 `weapon`。
- `SetClip1` 是武器方法，应该由 `weapon.SetClip1(amount)` 调用。
- 判断 `weapon == null && weapon.IsValid()` 会对 null 调用方法；应先判断 `weapon != null` 再调用 `weapon.IsValid()`。

这些是用户工程自身的逻辑问题，加载时不自动改写原事件流程；静态分析会反馈其中能明确识别的问题。
