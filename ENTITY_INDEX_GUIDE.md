# Entity index conversion / 实体索引转换 (v26.12)

## English

Use **General utilities → Entity lookup & checks → Entity from entity index**.

The default input is `env.weaponentid`, producing:

```nut
local weapon = EntIndexToHScript(env.weaponentid);
if (weapon != null && weapon.IsValid())
{
    printl(weapon.GetClassname());
}
```

For events that expose other entity indices, replace the input with e.g. `env.entityid`, `env.propid`, or `env.attackerentid`. **Only use fields actually present in that event.** The field `env.weapon` in `weapon_given` is the *weapon type ID*, not its entity index. `env.userid` is a *player userID*; use `GetPlayerFromUserID(env.userid)` for it. Indexes may be invalid or refer to an entity that has been removed; check the result before calling entity methods. No intermediate Squirrel helper is required.

The block is an expression, so it can be dragged into variable values and function arguments. General mode uses a descriptive label; Professional mode shows `EntIndexToHScript(entindex)`. Tooltips and the editor palette support English and Chinese.

## 中文

从 **通用工具 → 实体查找与检查 → 根据实体索引获取实体句柄** 拖出积木。

默认参数为 `env.weaponentid`，生成：

```nut
local weapon = EntIndexToHScript(env.weaponentid);
if (weapon != null && weapon.IsValid())
{
    printl(weapon.GetClassname());
}
```

其他事件如提供 `entityid`、`propid` 或 `attackerentid` 等**实体索引**字段，也可修改参数为相应的 `env.xxx`；使用前必须确认该事件确实含有该字段。`weapon_given` 事件的 `env.weapon` 表示**武器类型 ID**，不能用作实体索引。`env.userid` 是**玩家 UserID**，应使用 `GetPlayerFromUserID(env.userid)`。实体可能已被销毁或索引无效，因此在调用 `GetClassname()` 等实体方法前检查返回句柄是否有效。

本积木是可嵌套表达式，支持直接拖入变量值、函数参数等输入槽。General 模式显示易懂名称，Professional 模式显示 `EntIndexToHScript(entindex)`；中英文悬停提示也分别提供。
