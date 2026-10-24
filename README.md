# L4D2 Visual VScript Editor

**A Scratch-like visual programming editor for Left 4 Dead 2 VScript.**

[中文说明](#中文说明) · [English](#english) · [Releases](https://github.com/yshjdw/L4D2_Visual_Vscript_Editor/releases) · [Example Mod](https://steamcommunity.com/sharedfiles/filedetails/?id=3825417222)

> **Beta software.** The editor can generate Squirrel scripts and VPK addons, but the generated code should always be tested in Left 4 Dead 2. This is a Python application, not a standalone Windows executable.

## English

### Overview

L4D2 Visual VScript Editor is a Scratch-inspired block editor for **Left 4 Dead 2 / Squirrel 3.0.4**. Create and organize VScript projects visually, combine blocks into expressions and event handlers, and export scripts without writing everything by hand.

### Features

- Drag-and-drop blocks for variables, functions, namespaces, conditions, loops, events, and Think functions.
- Nested expressions, tables/arrays, ScriptScope members, and reusable utility blocks.
- Offline L4D2 VScript API, game-event, and NetProp catalogs.
- Entity classname, item, model-path, spawning, and TraceLine helpers.
- English / Chinese interface and General / Professional display modes.
- `.l4vp` project saving, Squirrel `.nut` generation, static checks, and VPK export.
- Optional GitHub Release update checks with user confirmation before installing.

### Technology stack

**Python + PySide6 (UI framework) + SQLite (offline catalog/database)**

### Installation (Windows)

1. Download the full editor ZIP from [GitHub Releases](https://github.com/yshjdw/L4D2_Visual_Vscript_Editor/releases), when a release is available.
2. Extract the ZIP to a writable folder.
3. Install **Python 3.10+** and ensure the Windows `py` launcher is available.
4. Double-click **`start_windows.bat`** in the editor folder. On first launch, it attempts to install PySide6 from `requirements.txt` if missing (internet access required).

Alternatively, open a terminal in the editor directory and run:

```powershell
py -3 -m pip install -r requirements.txt
py -3 app.py
```

**Steam Workshop distribution:** If you obtained the editor through a Workshop VPK, use [GCFScape](https://nemstools.github.io/pages/GCFScape-Download.html) to open the VPK, extract the included `.7z` archive, then unpack it with 7-Zip before following the steps above.

### Quick start

1. Create a new project or open an existing `.l4vp` file.
2. Open a `.nut` file in the project tree and add function, namespace, event, or initialization sections.
3. Drag blocks from the block library into the workspace and connect parameters or nested expressions.
4. Preview generated Squirrel code and review static validation results.
5. Save the project, export `.nut` or VPK, and **test in L4D2**.

`.l4vp` is the editable project format. Exported `.nut` code is not automatically converted back into visual blocks.

### Example project

**[[VScript] Use Pills Multiple Times](https://steamcommunity.com/sharedfiles/filedetails/?id=3825417222)**

This example demonstrates functions, namespaces, Think entities, event handling, and delayed execution with `DoEntFire`. Example `.l4vp` files are also available under [`examples/`](examples/).

### Updates, documentation, and testing

The editor can check the latest **published GitHub Release** at startup, or manually through **Help → Check GitHub updates**. Automatic installation requires a compatible ZIP attached to the Release; pushing source code to `main` alone does not publish an installable update. See [`GITHUB_UPDATES.md`](GITHUB_UPDATES.md).

- [Change history](CHANGELOGS/)
- [TraceLine guide](TRACELINE_GUIDE.md)
- [Entity spawning guide](SUMMON_GUIDE.md)
- [API/data sources](DATA_SOURCES.md)

For developers:

```powershell
py -3 -m unittest discover -s tests -v
```

### Development credits

As the author is a student with limited time for hands-on programming, AI was used for code implementation, while the author handled Squirrel syntax verification, UI design, bug testing, and user-experience testing.

---

## 中文说明

### 项目简介

**L4D2 Visual VScript Editor** 是一款面向《求生之路 2》**VScript / Squirrel 3.0.4** 的类 Scratch 可视化编程编辑器。通过拖拽和组合积木创建脚本工程，无需完全依赖手动编写 Squirrel 代码。

> **目前仍处于 Beta 阶段。** 虽然支持生成 `.nut` 脚本和 VPK 模组，但生成结果仍需在 L4D2 中测试。本项目是 Python 程序，尚非免安装 Python 的独立 EXE。

### 主要功能

- 可视化编辑变量、函数、Namespace、判断、循环、事件和 Think。
- 支持嵌套表达式、Table/Array、ScriptScope 成员及常用封装积木。
- 内置离线 VScript API、游戏事件及 NetProp 目录。
- 提供实体 Classname、物品、模型路径、实体生成及 TraceLine 工具。
- 中英文界面、General（一般）/ Professional（专业）模式。
- 保存 `.l4vp` 工程，生成 `.nut`，进行基础静态检查并导出 VPK。
- 可检查 GitHub Release 新版本，经用户确认后下载安装。

### 技术栈

**Python + PySide6（UI 框架）+ SQLite（离线目录/数据库）**

### 安装方法（Windows）

1. 在 [GitHub Releases](https://github.com/yshjdw/L4D2_Visual_Vscript_Editor/releases) 下载完整编辑器 ZIP（如果已有发布版本）。
2. 将 ZIP 解压到具有写入权限的文件夹。
3. 安装 **Python 3.10 或更高版本**，确认 Windows 的 `py` 命令可用。
4. 双击编辑器目录中的 **`start_windows.bat`** 启动。首次启动若缺少 PySide6，脚本会尝试联网安装 `requirements.txt` 中的依赖。

也可以在程序根目录的终端运行：

```powershell
py -3 -m pip install -r requirements.txt
py -3 app.py
```

**从 Steam 创意工坊获取：** 如果编辑器放在创意工坊 VPK 内，请先使用 [GCFScape](https://nemstools.github.io/pages/GCFScape-Download.html) 打开 VPK，提取其中的 `.7z`，再用 7-Zip 解压，最后运行 `start_windows.bat`。

### 简单使用

1. 新建工程或打开已有 `.l4vp` 工程。
2. 在工程树中打开 `.nut` 文件，添加函数、命名空间、事件或初始化分区。
3. 从积木库拖出积木，连接输入槽并组合表达式。
4. 查看生成的 Squirrel 代码及静态检查结果。
5. 保存工程，导出 `.nut` 或 VPK，并**进入 L4D2 实际测试**。

`.l4vp` 是可继续编辑的工程格式；导出的 `.nut` 代码目前不会自动反向转换成积木。

### 示例 MOD

**[[VScript] Use Pills Multiple Times（一瓶止痛药，多次服用）](https://steamcommunity.com/sharedfiles/filedetails/?id=3825417222)**

示例展示 Function、Namespace、Think 实体、事件回调，以及通过 `DoEntFire` 进行延迟执行的基本方法。仓库内的 [`examples/`](examples/) 也提供其他 `.l4vp` 示例。

### 更新、文档与测试

程序可以在启动时检查最新**正式 GitHub Release**，也可以从 **Help → Check GitHub updates** 手动检查。自动安装需要 Release 附带符合要求的编辑器 ZIP；仅向 `main` 分支上传源码并不会触发安装更新。详见 [`GITHUB_UPDATES.md`](GITHUB_UPDATES.md)。

- [更新日志](CHANGELOGS/)
- [TraceLine 使用说明](TRACELINE_GUIDE.md)
- [实体生成说明](SUMMON_GUIDE.md)
- [API 与数据来源](DATA_SOURCES.md)

运行自动化测试：

```powershell
py -3 -m unittest discover -s tests -v
```

### 关于开发

由于作者目前还是学生，没有太多时间亲自参与代码编写，因此项目主要由 AI 负责代码实现，而作者负责 Squirrel 语言语法检查、UI 设计、Bug 测试和用户体验测试。
