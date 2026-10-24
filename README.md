## v0.9.9.9

一般模式的函数/事件名称已按导入的 Valve 文档重新做口语化审计，避免“调用 xxx / xxx 事件发生时”式机械标签；专业模式继续显示原 API 名。修复普通分区删除后画布仍残留的问题；`init` 和内部 `data` 分区仍受保护。详见 `CHANGELOGS/CHANGELOG_v0.9.9.9.md`。

## v0.9.9.2

实体 For 现在可从下拉框选择查找方式，并按方法显示类别名称、模型路径、中心 Vector 和半径槽；支持变量拖入。Foreach 的“索引 / 键名”可留空（只遍历值），Array 对应索引，Table 对应键名。详见 `CHANGELOGS/CHANGELOG_v0.9.9.2.md` 和 `examples/Entity_For_Methods.l4vp`。

## v0.9.7

修复嵌套分支 ScriptScope 成员识别、底部引用库布局，以及跨数据窗口拖放自动转换为仅引用。参见 CHANGELOGS/CHANGELOG_v0.9.7.md。

**v0.6.1 启动兼容修复：** 去掉 `QEventPoint` 的直接导入，避免部分 PySide6 版本启动时 ImportError；保留触点释放过滤。

**v0.5 更新：** 左侧工具库直接显示可拖动彩色积木形状（包括 C 形内部槽），并修复 SpaceModifier 崩溃。

> **v0.4 更新**：已有语句积木支持抓住 `⠿` 把手在分区和 C 形分支间拖动/磁吸重排（Ctrl+拖动复制）；输入槽与容器随内容自动增宽。详见 `CHANGELOGS/CHANGELOG_v0.4.md`。本次未增加表达式积木嵌套。

# L4D2 Visual VScript — PySide6 初步原型 v0.3

这是一个面向 **Left 4 Dead 2 / Squirrel 3.0.4** 的可视化脚本工程原型。采用 Python 3 + PySide6，按类拆成多个文件，支持独立工程格式 `.l4vp` 及 `.nut` 导出。它**不是完整的 Blockly/Scratch 编辑器，也尚未经过游戏内测试**。

## Windows 启动

需要 Python 3.10 或更新版本（建议 3.11/3.12）及可用的网络来安装 PySide6。

```powershell
cd L4D2_VScript_Visual_Prototype
py -3 -m pip install -r requirements.txt
py -3 app.py
```

或者双击 `start_windows.bat`。初次安装时需下载 PySide6。若网络连接不稳定，可自行从 PyPI 获取对应 Python 版本的 PySide6 wheels。

本项目中 `l4visual.models / codegen / storage / validation / catalog` 等核心模块**不依赖 PySide6**，可单独测试或通过命令行导出。

## 快速操作

1. 打开软件后，左侧 **工程栏** 显示 `.nut` 文件及其分区。双击文件打开画布。
2. 左侧 **积木工具库** 按类别排列。拖入画布上的分区或 C 形积木内部，参数直接在积木的浅色输入框中编辑。
3. 积木无需参数弹窗；直接在积木中编辑参数，点 ⋯ 可以复制、上下移动、删除。抓住分区标题拖动整体分区，双击标题才打开分区属性。
4. 对于变量积木，右侧黄色圆形输出端：**右键重命名，左键拖动创建变量引用**；可拖到目标积木的数值、对象、条件或参数输入槽。
5. 在命名空间或者文件初始化区添加一个变量，选择 **Table `{}`** / **Set `[]`** 类型；直接点击该变量积木上的 **打开数据定义分区**。
6. 在数据定义区添加更多变量记录：Table 的成员名由左侧变量名确定；Set 的每条变量记录按顺序生成数字索引。子成员若为 Table/Set，可以再右键建立子定义区。
7. 对支持的输入槽，使用积木编辑对话框内的 **编辑变量链** 按 `[xxx].[yyy].[zzz]` 方式访问成员；Table 提供字段下拉候选，Set 提供数值索引输入。
8. 新建项目时可以填写事件回调 Table 名称；将游戏事件积木拖进事件分区，事件块携带 `env` 圆形引用变量。
9. 在 **NetProps** 积木中选择 Get/Set、目标对象、SendTable、属性以及返回变量，属性候选会依据目标表达式推测类型并参考继承链过滤。
10. 按 `F5` 查看生成 `.nut` 和静态检查，`Ctrl+S` 保存 `.l4vp`；通过菜单导出单个或全部 `.nut`。

**画布导航：** 触屏双指缩放、鼠标 Ctrl+滚轮缩放、鼠标中键按住拖动画布，或在空白画布区域拖动；分区标题直接拖拽。

**快捷键：** Ctrl+N 新建工程 / Ctrl+O 打开工程 / Ctrl+S 保存 / Ctrl+Shift+S 另存为 / Ctrl+E 导出当前脚本 / Ctrl+鼠标滚轮缩放画布。

## 工程文件

- `*.l4vp`：本工具专用保存文件，包含 `L4DVPROJ` 魔数、版本、压缩 JSON AST、SHA-256 完整性摘要以及多个 `.nut` 文档、分区和位置。这是**专有工程容器格式**，不是加密机制。
- `*.nut`：按工程 AST 生成的可发布脚本。编辑 `.nut` 文件不会反向更新 `.l4vp`。暂不支持 `.nut` 反向导入。
- `resources/catalog.sqlite3`：离线事件/API/NetProp 子集，**不代表完整官方 API 镜像**。

## 示例工程

- `examples/Juggernaut_Demo.l4vp`：根据 Juggernaut DLC 脚本的主要结构手工整理的可编辑示例；不是原脚本逐行无损转换。示例涉及命名空间、第三方 `ArmorSystem`、Foreach、Try/Catch、实体 For、Think、事件及初始化。
- `examples/juggernaut_dlc_generated.nut`：同一示例的编译输出，用于检查生成风格。

## 不依赖 Qt 的测试和导出

```powershell
py -3 -m unittest discover -s tests -v
py -3 tools\export_project.py examples\Juggernaut_Demo.l4vp -o generated
```

## 已实现 / 尚未实现

已实现的初版能力：项目树、可拖动分区、半椭圆事件块、变量圆形输出端、Get/Set NetProps、基本流程/函数/事件/Think 代码生成、字符串多行编辑器、Table/Set 嵌套定义区、链式变量选择器、工程依赖与 IncludeScript、第三方 API JSON 描述、静态检查、独立工程保存（临时文件加校验后原子替换）。

仍属于原型的地方：

- C 形分支已能在画布中直接展开、拖入子积木和修改参数；暂未实现相邻积木自动磁吸堆叠、积木从一个分支直接拖到另一个分支（可使用复制 / 删除以及左侧工具库拖入）。
- 函数返回类型推断、事件 `env` 字段类型提示、动态值的数据流推断、复杂对象的 NetProp 自动识别仅为初版；数据库覆盖率有限。未知对象可手动填写。
- 专用 `Think` 绑定生成尚未覆盖所有运行时情况，不应未经游戏内验证就用于生产 Mod。
- 高级表达式及原生 Squirrel 文本块保留给无法用已实现积木表达的语句，并不承诺代码是合法或安全的。
- 暂无游戏运行环境、远程调试、脚本热加载或 `.nut` 源码反向积木化。
- 尚未在配有 PySide6 的 GUI 环境进行启动验证；本次执行环境没有 PySide6 且无法联网安装。已完成 Python 编译检查、非 GUI 单元测试及示例文件导出。

更多设计细节见 `DESIGN_SPEC.md`，数据库来源见 `DATA_SOURCES.md`。

## v0.3 交互变化

新增控件式积木、内联参数、可视化分支容器、工具库直接拖放、双指缩放和画布抓取平移。仍属于早期版本，触屏手势未在实体触屏设备上验证。

## v0.6 controls

- **New section:** click **＋ 新建分区** at the top of the editor, then select type/name in the section setup dialog.
- **Block right-click:** right-click its colored background, or use the `⋯` menu. For Table/Set declarations choose **打开独立数据工作区**.
- **Complex variable:** select Table/Set on the variable block, right-click, open dedicated workspace window. Only data-compatible blocks can be dropped here.
- **Move canvas:** left-drag an empty region, middle-drag anywhere, or enable **抓取画布**.
- **Zoom:** `＋` / `－` / `100%` in header, Ctrl+wheel, or touchscreen two-finger pinch.
- **Move section:** drag the section title. **Move existing block:** drag the `⠿` handle.

PySide6 was unavailable in the build environment; touch and GUI behavior needs Windows hardware testing.


## v0.6.2 操作

- 左侧“官方方法”展开对应类，直接拖动绿色方法块到分区或 C 形内部；与自定义函数、NetProps 分类分离。
- 触屏单指按住分区标题拖动该分区；单指空白画布平移，双指缩放/平移。
- 鼠标按分区标题移动分区。
- 数据库为离线初版子集，不代表包含游戏全部官方方法。

当前未在 Windows 触屏设备上完成真实手势验证。

## v0.6.3 操作修正

- 变量圆圈右键：独立菜单（重命名变量、复制变量引用、复杂变量独立工作区）。
- 普通积木右键：复制、上移、下移、删除；不会将菜单嵌入画布导致遮挡。
- Table / Set 类型变量：右键 -> 打开独立复杂变量工作区；此窗口具有独立可拖入积木的工作区和受限工具库。
- 新增分区：在当前可视画布中央附近插入；不会重新初始化其他分区，也不会重置画布缩放或平移位置。


## v0.7.1 — 拖放 / 官方参数槽 / 坐标锁定

- 已有积木：抓住左侧 `⠿` 拖到工程树（左侧“工程栏”）或工具库底部红色删除区域，即快速删除。
- 分区坐标：只允许拖动分区标题修改。新增积木、调整块宽度、嵌套、代码预览及新建分区，不改变其他分区坐标。
- 参数槽位：从官方方法列表拖入积木，不同方法展示数据库中实际的参数数量与名称；返回值方法提供圆形结果变量。
- 嵌套：具有返回值的官方方法、调用块、Get NetProps 以及表达式块可以拖进浅色槽位。表达式展示椭圆，布尔输出展示六边形；无返回值与 C 形流程块不能嵌入。
- 置顶：拖动分区标题或积木把手时提升所属分区层级。
- 工作区：取消移动积木时整个画布清空重建，改为原位置局部更新。
- 兼容：工程格式仍为 `.l4vp`，能够读取旧版工程。

**注意：** 编译/静态测试不等同于真实 Windows 触摸屏测试，当前容器无 PySide6 且无法联网安装。此版本还需要进行 GUI 操作回归。

验证 GUI（需安装 PySide6）：`py -3 tools\gui_smoke.py`；静态测试：`py -3 -m unittest discover -s tests -v`。


## v0.7.1 修复与操作测试

1. 在函数分区放入“变量定义”积木，从“官方方法”分类展开 `CBaseEntity`，将绿色圆形 `GetOrigin` 拖到变量块的浅色 `value` 输入槽，**在输入框内部松开鼠标**。应生成 `local position = player.GetOrigin();` 类型的赋值表达式；无返回值方法不能嵌入。
2. 在变量定义的类型下拉依次选择“普通 → Table → Set → 普通”，值槽应分别切换到对应模板：普通原值、`{}`、`[]`、普通原值。复杂类型还应出现“打开数据定义分区”按钮，弹出独立窗口。
3. 画布依次缩放到 50%、100%、200%，按住分区标题拖动同样的屏幕距离；分区应随指针移动。只有拖标题才允许改变分区坐标。
4. 如果已有 `.l4vp` 项目，请先备份。此版本不更改工程文件格式，保存后仍为 `.l4vp`。
5. GUI 自检：在项目根目录运行 `py -3 tools\gui_smoke.py`，打印 PASS 后再进行触屏实测。

见 `CHANGELOGS/CHANGELOG_v0.7.1.md` 了解代码层修复和已知验证限制。


## v0.7.2

- Function 的所属 Namespace 必须选择当前文件已有的 Namespace，并显示对应的虚线连接；请先新建 Namespace，再新建 Function。
- 顶部工具栏单独有 `－`、`＋` 和 `100%` 缩放按钮。
- 非当前分区类型的属性在切换类型时禁用并清空。
- 右键菜单及标题鼠标拖动的坐标处理已调整。桌面真实鼠标和触屏请在本机验证。
- Windows 界面自检：`py -3 tools/gui_smoke.py`。

## v0.7.3 data workspace updates

- Drag the circular variable token from a Namespace or complex-variable data root into a light-colored value/expression socket. The target is resolved into `::Namespace.Table.member[index]` using the declaration's internal ID.
- Right-click a Table or Set variable and choose the separate data workspace. Its yellow C-shaped root is fixed and cannot be deleted. Drag supported variable/data/function-call blocks **inside** it.
- In a Set `[]` root, drag the **Array 特殊操作** block, then choose `append`, `insert`, `pop`, `resize`, `len`, etc. The operation's argument sockets update automatically. `len`, `top`, `pop`, `remove`, and `slice` support expression output; mutators like `append` are statements.
- The generated `.nut` creates the array first and then executes appended array mutation statements.
- The Array operation reference is Squirrel 3 official documentation: https://www.squirrel-lang.org/doc/squirrel3.html

## v0.7.4 新增交互

**成员选择**：右键 Table / Set 变量圆圈、或事件 `env` 圆圈 → **选择成员变量**。打开独立窗口；左键单击成员选中引用（不改声明名称），右键复杂成员继续展开，窗口左上角 `× 返回上一层`；Set 使用数字索引网格。选择后左键拖出圆形引用，放入 Value 等槽位。

**事件工具库**：左侧的原版事件按“伤害与死亡 / 物品、武器与补给 / 特殊感染者与感染者 / 幸存者与玩家 / 关卡与游戏流程 / 其他游戏事件”分组。直接将指定事件帽子拖入 Events 分区。事件 `env` 是 Squirrel Table，并非 Array。

**Help**：菜单 `Help / 帮助` → `实体获取与组合实例`。右侧 API 数据库可以从底部 `展开 / 收起 API 字典` 控制。

**变量作用域**：`auto` 自动判断、`local` 局部、`无` 只赋值、`static` 为将来 class 支持预留且当前普通分区编译时会报错。局部变量不允许跨函数/事件分区拖出；对 C 形嵌套分支进行保守的词法路径与先声明后引用检查，暂非完整 Squirrel 语义分析。

**验证限制**：开发环境未安装 PySide6，源码检查与 57 项非 GUI 测试通过，但 Windows 触屏/拖放图形交互需用户端实际验证。

## v0.7.5 修复说明

修复分区标题拖动松开后可能引发的 `NameError: name 'scene' is not defined`。Function 分区右上角新增 `⠿ 调用`，拖动至工作区即插入此函数的调用积木（原函数定义不移动）。参数槽初始填入 `null` 占位，请按实际函数参数修改。详见 `CHANGELOGS/CHANGELOG_v0.7.5.md`。

## v0.7.8 Summon / project file drag

在左侧“实体生成”拖动 Summon 积木，右键选择“Summon 配置工作区...”打开独立窗口。选中所需 KeyValues 后生成 `SpawnEntityFromTable`；全部未选中则只生成空 `{}`。`scripts/vscripts/` 工程文件可直接拖入画布表达式槽生成 `IncludeScript("文件名")`。

如果使用外部 API，可从“工具 → 外部自定义 API”设置 JSON；确认后在左侧“外部 API · 工程自定义”找到对应积木。外部 API 的合法性由用户或所依赖 Mod 保证。

本地数据库不包含全部事件与函数的完整、逐条官方文字说明；未验证的说明项会显示来源及现有签名，而不是编造含义。详情参见 `CHANGELOGS/CHANGELOG_v0.7.8.md`。

## v0.7.9 文档更新

新版本使用随工程提供的 `resources/official_functions.json` 与 `resources/official_events.json`：函数按官方转存签名及英文说明显示，事件的 `env` 字段按转存数据动态展开，字段上悬停显示其类型与描述。未收录的成员仍可手动输入。

工程树支持右键新建/重命名/删除相对 `scripts/vscripts` 的文件和文件夹；也可从子目录拖动完整路径供 IncludeScript 使用。包含 Scratch 风格运算及数学积木。请查看 `CHANGELOGS/CHANGELOG_v0.7.9.md`。


## v0.8.2

复制的 Table/Set 连同成员子工作区复制；成员窗口提供根变量及上一层选择；变量、文件、文件夹可双击重命名；NetProps 属性槽及 Summon classname 槽可拖变量。参见 CHANGELOGS/CHANGELOG_v0.8.2.md。


## v0.8.3 修复
打开已有项目时清空旧画布连接线缓存，避免已经由 Qt 销毁的 `QGraphicsPathItem` 被重复访问。详情见 CHANGELOGS/CHANGELOG_v0.8.3.md。

### v0.8.4：嵌套 env 成员选择

嵌入函数参数或 Operator 的 `env`、Table、Set 变量引用支持右键或双击打开成员选择。可选择 `env.userid` 等字段，也可使用“● 根变量”恢复 `env`。仅改变引用，不重命名变量声明。若源变量已经删除，将提示源引用失效。

## v0.9.0 ScriptScope 与 Table 编辑

Variable 类型列表新增 ScriptScope（Value=实体表达式）；直接使用 `ent.GetScriptScope()` 的普通变量也会推断为 Table。两者都可以用 Table 的独立嵌套工作区创建成员和子 Table/Array，代码会先取得实体 ScriptScope，再逐一用 `<-` 加入成员。赋值块新增 `auto`、`=`、`<-` 及复合赋值。完整例子见 `examples/ScriptScope_Demo.l4vp` 与 `CHANGELOGS/CHANGELOG_v0.9.0.md`。

### v0.9.1 NetProp 字典

NetProps 积木点击“选择属性”，打开独立两步选择窗口；先选实体网络类（如 CTerrorPlayer），再选属性。数据来自用户提供的 L4D2 NetProps 文档，存放于 `resources/netprops_2024.json`。右侧 NetProps 字典也按类和属性层级显示。嵌套字段的实际运行时名称及部分类型仍需要游戏内确认。

## v0.9.4 拖放复制与边缘移动
- 已嵌入变量圆块可按住左键拖到另一个数据槽进行复制，原块不删除。
- 已嵌入椭圆/菱形计算模块左侧有 `⠿` 拖动柄，可复制包含嵌套参数的表达式。
- 拖放积木时接近画布四周边缘会自动滚动，距离边沿越近移动越快。

## v0.9.5 ScriptScope 成员初始化
在 ScriptScope 变量的“打开数据定义分区”中，Table 成员下方有初始化策略：仅首次创建（默认）、每次覆盖、仅修改已有成员。针对实体 ScriptScope 的成员生成 `rawin` 检查或对应 `=` / `<-` 操作。普通 Table 构造器不受影响。示例：`if (!scope.rawin("ammo_keep")) scope.ammo_keep <- 0;`。

## v0.9.6 — ScriptScope 引用与拖放修复

- ScriptScope Table 数据窗口左侧新增“ScriptScope 成员引用库”，可从其它已初始化成员拖入当前数据窗口；仅接受相同实体表达式绑定的 ScriptScope，自动生成“仅引用”成员。点击“刷新已有成员”可同步显示其它正在编辑窗口的新成员。
- ScriptScope Table 成员初始化策略新增“仅引用”，此模式不生成 `<-`、`=` 或 `rawin()` 初始化语句；只提供编辑器内的成员引用信息。
- 跨函数/事件的成员引用必须在目标分区已有同一实体表达式绑定的 ScriptScope 变量，避免错误地使用其它分区的局部变量名称。
- 拖入分支标题区会插在分支首个积木之前；修复普通 Drop 由 viewport 事件过滤器处理完后边缘滚动计时器没有停止的问题。

注意：仅引用不负责在运行时创建数据；源 ScriptScope 必须先初始化，并保证操作的是同一个仍然有效的实体。不同表达式即使运行时可能指向相同对象，也不会自动判定等价。

## v0.9.8 导出 VPK

可在“文件 → 导出 VPK 模组”直接导出整个工程，或在导出单个 / 批量 `.nut` 后选择是否同时打包。弹窗内填写标题、作者、版本及简介，作者最终值自动拼接 `/Vscript Visual Maker`。生成的 VPK 根目录包含 `addoninfo.txt`，代码放于 `scripts/vscripts/`，带子目录的工程文件按相对路径保留。此打包器采用无外部依赖的单文件 VPK v1 编码；尚未在游戏中实际加载测试。


## v0.9.9 停靠面板

通过「视图」菜单重新显示已关闭的工程栏、积木工具库或 API 资料库；「恢复默认布局」可恢复停靠位置和标签布局。

## v0.9.9.3 补充：NetProps、ScriptScope 与输入框

- NetProps 选择器使用**实体类别 → 文档属性分组 → 实际运行时属性名**。例如 `LocalWeaponData.m_iPrimaryAmmoType` 在预览代码中应生成 `"m_iPrimaryAmmoType"`，而 `m_Collision.m_vecMins` 仍保留必要的嵌套访问路径。
- 玩家后备弹药使用 `m_iAmmo` **数组属性**，需要通过 `NetProps.GetPropIntArray(player, "m_iAmmo", ammoType)` 获取；`ammoType` 可由 `NetProps.GetPropInt(weapon, "m_iPrimaryAmmoType")` 得到。
- ScriptScope 依附于实体，`weapon_fire` 和 `weapon_reload` 之间的 `local player` **不会自动共享**。两个事件必须各自获取当前玩家实体，再对同一有效实体调用 `GetScriptScope()`。静态检查会尝试检测跨事件的局部引用。
- 打开旧工程时，编辑器会清理“完全空白且已失去变量绑定”的 Data 分区；有内容的分区不受影响，清理后请保存工程。
- 普通参数输入槽支持空格输入和按文本内容扩展宽度。高级“原始代码”积木支持多行 Squirrel 代码；点击非输入区域可结束编辑。

详细修复记录见 `CHANGELOGS/CHANGELOG_v0.9.9.3.md`。

### v0.9.9.4
- If block: a single default branch; '+' adds Else, then Else If before Else; '-' on Else If removes that branch and its contents.
- NetProp selector: all array and indexed-range entries transcribed from supplied SendTable documentation; some paths may not work with VScript NetProps at runtime.
- Raw Squirrel text editing supports spaces and newlines.


### v0.9.9.5
Removed the Space-key canvas panning shortcut entirely. Space is reserved for text editing in ClientPrint message and multiline Squirrel code fields. Pan using the middle mouse button, an empty canvas region, or the grab-canvas mode.

## v0.9.9.7：语言、积木风格与换行布局

菜单 **设置 / Settings → 语言与模块风格 / Language & Block style** 可分别选择 `简体中文 / English` 与 `一般 / 专业`。一般模式仅更换界面用途描述、参数槽位标签及其展示顺序；专业模式保留函数及事件的原始名字。语言/风格设置保存在本机 Qt 设置中，不影响 `.l4vp` 工程或导出的 Squirrel 代码。

复杂官方方法的参数槽现在按完整内容计算高度并向父积木传递；如果整条嵌入表达式本身宽度超过窗口，仍可以通过横向滚动查看。界面中没有来源支持的 API 释义将同时保留原名称，避免编造说明。Windows 上的真实 PySide6 GUI 交互仍待验证。

## v0.9.9.10 补充

- 原始 Squirrel 多行代码积木会按照手动换行和自动折行的可见行数增高；删除文本时也会缩小，不再限制为 390px。
- **设置 → 语言与模块风格** 可选中文 / English 和一般 / 专业。英语模式扩展覆盖固定按钮、输入提示、Data/ScriptScope 工作区、NetProps 选择器、函数/事件文档提示与常用静态检查信息；此设置不会修改 `.nut` 代码。
- 跨窗口实际 GUI 效果和完整英文覆盖仍应在 Windows PySide6 环境确认。


## v0.9.9.12：全量事件 env 字段提示及静态检查跳转

- 事件文档：301 个正式收录事件、620 条 env 字段。
- 鼠标悬停 env 成员时根据**事件名和字段名**显示相应中英文说明。
- 中文模式保留英文原始说明；英文模式优先显示原文。
- 原始事件资料缺少说明的 192 条字段标为推断。具体对照表：`resources/event_env_field_reference.tsv`。
- 点击静态检查中的分区/积木问题，会将对应积木移到画布上方、水平居中并高亮。
- 工程格式没有变化；旧版 `.l4vp` 可继续打开。


## v0.9.9.13：动态画布与复杂数据分区静态检查修复

画布不再受固定工作区限制：保留原始最小范围，并随分区移动、积木高度和边缘滚动动态扩展。静态检查会按复杂 Data 分区真正生成代码的位置判断 local/env 可见性，避免 ScriptScope 数据成员造成跨事件误报。

## GitHub automatic update / GitHub 自动更新 (v26.16)

Before the workspace opens, a visible dialog checks the latest published GitHub Release; you can skip it and work offline. Downloads and installation require your confirmation. Manual check: **Help → Check GitHub updates**. Disable the startup dialog in Settings. For publishing Releases and safety details, see [GITHUB_UPDATES.md](GITHUB_UPDATES.md).

默认在进入主工作区前弹出 GitHub 更新检查窗口，显示版本号、进度和结果；可以跳过并离线使用。下载及安装均需用户确认。可在“帮助 → 检查 GitHub 更新”手动检查，在“设置”关闭启动检查。发布新版及更新安全说明详见 [GITHUB_UPDATES.md](GITHUB_UPDATES.md)。
