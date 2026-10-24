# 26.17 / 更新检查修复

- 修复 GitHub HTTP 403 只显示英文原始错误的问题。区分 API rate limit 与一般访问受限，支持读取限额重置时间。
- 启动更新窗口先加载已保存的 English / 中文界面偏好，和主界面保持一致。
- 启动与主界面的检查、下载错误均按当前语言显示；断网不阻止编辑器启动。
- 不更改安全下载与替换机制，也不需要 GitHub 个人令牌。

## English

- Localize startup and in-editor update errors in the selected UI language.
- Distinguish HTTP 403 API quota exhaustion from a generic access denial and show reset time if GitHub provides it.
- Initialize the saved display profile before showing the startup update dialog.
- Offline use remains available; no GitHub token is requested.
