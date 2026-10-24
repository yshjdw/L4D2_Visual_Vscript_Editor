# v0.8.3 — 工程打开时的 Qt 场景连线生命周期修复

- 修复打开 `.l4vp` 工程、切换文件、重新加载画布时，Qt `QGraphicsPathItem already deleted` 错误。
- 在调用 `QGraphicsScene.clear()` 前清空 `_links` 和 `items_by_id` 缓存，避免访问已销毁的 C++ 图形对象。
- 刷新连接线时先摘除旧引用，再从场景中移除仍属于该场景的旧连线。
- 新增两项源代码生命周期回归检查；由于构建环境没有 PySide6，Windows GUI 实测仍需用户验证。
