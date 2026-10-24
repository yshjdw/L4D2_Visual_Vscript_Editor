# GitHub Releases updater / GitHub Release 自动更新

## English

The editor checks the latest **published GitHub Release** after startup (non-blocking) and offers to download an update only if its version is greater than the installed editor version. You can also select **Help → Check GitHub updates**. Toggle **Settings → Check updates at startup** to disable/enable startup checks. Nothing is installed without your approval.

Repository: https://github.com/yshjdw/L4D2_Visual_Vscript_Editor

### Publishing a compatible update

1. Change `APP_VERSION` in `l4visual/version.py` (e.g., `26.16`). This is the one authoritative application version; `.l4vp` document format versions are unrelated.
2. Package the entire `L4D2_VScript_Visual_Prototype` folder into a `.zip`. It must include `app.py`, `l4visual/ui/main_window.py`, `l4visual/codegen.py`, and `l4visual/version.py`.
3. Under the GitHub repository's **Releases**, create a published (non-draft, non-prerelease) Release tagged `v26.16` or `26.16`.
4. Attach the ZIP as an Asset with a name such as `L4D2_VScript_Visual_Prototype_v26.16.zip`. **Do not rely on GitHub's automatically generated “Source code (zip)” archive**, which isn't a Release Asset.
5. Users starting an older version will receive an update offer. They can choose to download the ZIP, quit, install, and relaunch.

No GitHub release or no properly named ZIP asset → the editor cannot automatically install. The manual update check gives a diagnostic. If GitHub is unreachable, the editor starts normally and a network error is shown only for manual checks.

### Safety and preservation

- Network requests use HTTPS and an 8-second check timeout. No GitHub login/token is required for a **public repository**.
- Packages are downloaded to a temporary folder and checked for ZIP integrity, path traversal, symlinks, unsafe sizes, mandatory files, and matching app version. The GitHub-provided SHA-256 digest is verified when available.
- Installation happens **after the application exits**, in an independent Python process. Existing application files are backed up and replaced one by one, with rollback on ordinary write failures.
- `.l4vp` project files are never installed from the update archive or overwritten. Unknown files in the installation directory are preserved. User display preferences are held in Windows `QSettings` and are not changed.
- The updater cannot reliably recover from a power failure during replacement. Keeping a backup of important projects is always recommended.
- The original folder must be writable. If installing under a protected location such as Program Files, launch with appropriate permissions or move the editor into a normal writable folder.

## 中文

编辑器启动后会**异步**读取 GitHub 最新正式 Release，仅当远程版本高于本地版本时询问是否下载更新。也可通过 **帮助 → 检查 GitHub 更新** 手动检查；在 **设置 → 启动时检查更新** 中可关闭自动检查。不会未经确认直接下载安装。

### 发布可自动更新的版本

1. 将 `l4visual/version.py` 的 `APP_VERSION` 改成新版本号，例如 `26.16`。
2. 将完整的 `L4D2_VScript_Visual_Prototype` 文件夹压缩为 ZIP，必须包含 `app.py` 和上述核心源码。
3. 在 GitHub 仓库 **Releases** 页面创建正式 Release，标签使用 `v26.16` 或 `26.16`。
4. **手动上传**附件，例如 `L4D2_VScript_Visual_Prototype_v26.16.zip`。GitHub 自动提供的“Source code (zip)”不属于此更新器识别的 Release 附件。
5. 旧版用户启动后就会收到提示；确认后下载安装，退出编辑器并由独立进程完成更新、重启。

如果还没有正式 Release 或 ZIP 附件，则无法自动安装新版。GitHub 不可访问时，不影响编辑器离线运行。

### 安全与数据

使用 HTTPS；下载至临时文件夹；检查 ZIP、文件路径、大小、版本及可用的 SHA-256；主程序退出后更新；出现一般写入错误则回滚已替换的文件。**不会安装或覆盖 `.l4vp` 工程文件，也不会删除未知的个人文件。** 请避免把编辑器装入无写入权限的系统目录。

## v26.16: startup update window / 启动前检查窗口

The editor now opens an update-check dialog *before* displaying the main workspace (unless startup checks are disabled in Settings). It shows the installed version and an explicit result, including when GitHub is unreachable, no Release exists, or the installed version is already the latest.

Use **Enter editor** to skip the network request; no account or download is required. **Retry** checks again, and **GitHub Releases** opens the repository's release list. When a newer official Release has a matching editor ZIP, **Download update** downloads and verifies it, then asks whether to install and restart. Installation is performed by a separate process after the editor exits.

从 26.16 起，默认在主工作区打开前弹出更新检查窗口，明确显示本地版本、检查结果、网络错误及是否有新版本。可以随时选择“进入编辑器”跳过，无需联网。新版本需要 GitHub 正式 Release 和匹配的编辑器 ZIP 附件；下载校验成功后，再由独立进程安装、重启。

If you publish only `v26.16` while the installed editor is already `26.16`, **Already up to date** is the expected result. / 如果本地已是 26.16，而 GitHub 最新也是 26.16，显示“已是最新版本”属于正常情况。
