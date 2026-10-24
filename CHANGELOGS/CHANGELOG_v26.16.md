# v26.16 — Visible pre-startup GitHub update check / 启动前可见检查更新

- Added a pre-editor GitHub Releases check dialog showing installed version and a busy indicator.
- The dialog explicitly reports latest version, available update, missing compatible asset, and network/API failure.
- Users may skip checking and work offline, retry, or open the official Releases page.
- The user can download, validate, confirm installation, and restart via the detached updater before opening the main window.
- Avoids a second automatic check after the pre-startup dialog; retains Help → Check GitHub updates.
- Startup update checking can still be disabled through Settings; existing preference is respected.
- Chinese / English UI based on saved language setting; normal editor startup works without network.

---

- 新增启动前更新窗口：展示版本号、检查进度及结果。
- 最新版、可更新、无可安装 ZIP、网络失败都明确显示，不再仅依赖短暂状态栏提示。
- 支持跳过、重试、查看 Releases、下载安装，更新失败不影响进入编辑器。
- 下载安装沿用原有 ZIP 校验与独立进程安装机制；不会覆盖 .l4vp 工程。
- 启动前已检查时不再重复自动请求；保留帮助菜单手动检查。
- 遵循现有自动检查开关与界面语言（中文 / English）。
