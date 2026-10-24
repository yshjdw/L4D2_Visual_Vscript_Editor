# v0.9.9.1

- 修复 `CTerrorWeapon.SetClip1(int amount)` 和 `SetClip2(int amount)` 在 SQLite 方法目录中遗漏参数，造成缺失输入槽。
- `block_from_method` 对照本地 Valve 官方函数转存的参数数量；目录缺失参数时以已核对的官方文档补齐，不覆盖参数数量正确的原有签名名称。
- 已有 `.l4vp` 旧工程包含无参数 SetClip1/SetClip2 的积木，在画布渲染时补充 `amount` 输入槽；已有参数值不会被覆盖。
- 审计离线官方函数文档与 SQLite 中的函数参数缺口。
- 新增 5 项回归测试，148 项非 GUI 测试通过。尚无 Windows PySide6 GUI 实机验证。
