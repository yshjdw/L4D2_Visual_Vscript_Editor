# L4D2 Visual VScript Editor 26.8

## 修复 / Fixes
- 修复不同分区相互重叠时，右侧嵌套表达式、变量引用和文本框无法操作的问题。
- 打开项目时为分区恢复明确且唯一的 Z 层级，确保 Qt 绘制层级与画布鼠标命中顺序一致。
- 在重叠区域只允许最上方分区参与鼠标命中；上方分区的空白处也会阻止事件误传至被遮住的分区。
- 保持 26.4 的尺寸计算方式、26.5–26.7 的深层命中机制及原有 .l4vp 格式不变。

## Verification
- Static regression for coincident section Z values and overlapping panel backgrounds.
- Automated Python tests; Qt GUI interaction still requires Windows validation.
