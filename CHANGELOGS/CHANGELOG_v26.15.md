# v26.15 — GitHub release check and optional automatic updater

- Added automatic startup check for the latest published GitHub Release at `yshjdw/L4D2_Visual_Vscript_Editor`.
- Added **Help → Check GitHub updates** and **Settings → Check updates at startup**, supporting Chinese and English labels.
- Downloads are optional and non-blocking. The app prompts before downloading and again before exiting to install.
- Introduced an independent updater script to replace application files after exit, restart, and attempt rollback on write failure.
- Guarded downloads with trusted HTTPS redirects, ZIP integrity, zip-slip/symlink/size checks and SHA-256 when GitHub provides it.
- Preserves `.l4vp` projects, user-created files, display settings and saved work prompts.
- Added `l4visual/version.py` as a single application version source. See `GITHUB_UPDATES.md`.

# 中文

- 启动时异步检查 GitHub 的最新正式 Release。
- 新增“帮助 → 检查 GitHub 更新”“设置 → 启动时检查更新”。
- 有新版本时需用户确认下载及退出安装，不会自动覆盖。
- 新增独立更新器：关闭主程序后更新、尝试回滚、重新启动。
- 加入 HTTPS 来源检查、压缩包完整性及路径安全检查；支持 GitHub 提供的 SHA-256。
- 保留 `.l4vp` 工程、个人文件和界面设置；详细流程见 `GITHUB_UPDATES.md`。
