# TraceLine (L4D2 Squirrel 3.0.4) / 射线追踪说明

## Native API / 原生函数
`TraceLine(table)` returns a bool for whether the trace request was processed; collision results are written into the same table. In Left 4 Dead 2, **do not** replace this with the unrelated TF2-style three-argument `TraceLine(Vector, Vector, handle)` or assume `TraceLineEx` is available.

`TraceLine(table)` 接收含 `start`、`end` 的 Table，可加入 `ignore`、`mask`。函数返回值不代表是否命中，需读取 `table.hit`。

```nut
local tr = {start = player.EyePosition(), end = player.EyePosition() + Vector(1000, 0, 0), ignore = player, mask = 33579137};
if (TraceLine(tr) && tr.rawin("hit") && tr.hit)
{
    local location = tr.pos;
    local entity = tr.rawin("enthit") ? tr.enthit : null;
}
```

## Statement block and configuration / 语句积木与右键配置

The editor offers **two** TraceLine workflows:

1. **Ray tracing → Run TraceLine raycast** in the ordinary/source block palette: a statement block (not nestable), generates native `TraceLine(table)`, saves the mutated result table to the **output variable** (default `trace`). Right-click the block or press its `⋯` button to configure `start` / `end` / `ignore` / `mask` and output name.
2. **Utilities → Ray tracing / TraceLine → TraceRay**: a nestable expression returning a table or `null`. Right-click the teal expression shell (also supported inside other expressions) to configure its four arguments. The result reader blocks remain in Utilities.

源码积木库新增 **「射线追踪 → 执行 TraceLine 射线追踪」**，这是独立语句积木。它生成原生 `TraceLine(table)` 并把追踪结果写入 `trace` 等结果变量。右键积木或点击 `⋯` 可配置起点、终点、忽略实体、mask 以及结果变量名。

「通用工具 → 射线追踪」中的 `TraceRay` 则是能嵌套在表达式槽里的积木，右键表达式外壳也可编辑四个参数。两种方式都保留在 26.11 中，彼此独立，旧 `.l4vp` 无需迁移。

```nut
local ray = {start = player.EyePosition(), end = player.EyePosition() + Vector(1000, 0, 0), ignore = player, mask = 33579137};
TraceLine(ray);
if (ray.rawin("hit") && ray.hit)
{
    printl(ray.pos);
}
```

The configuration dialog accepts Squirrel expressions. **Do not add quotes** around Vector expressions, entity handles or numeric mask values. Unchanged existing nested expression blocks are preserved; to drag new expressions into a parameter, use the canvas sockets. The optional output variable must be a valid Squirrel identifier.

配置窗口填写的是 Squirrel 表达式，Vector、实体句柄与数值掩码不要加引号。已嵌套的参数若未修改会原样保留；要拖入新参数积木，请在画布插槽中操作。结果变量名需符合 Squirrel 标识符规则。

## Editor blocks / 编辑器积木
Under `Utilities > Ray tracing / TraceLine` use `TraceLine ray → result table` with four expression sockets: start, end, ignored entity, mask. Assign this returned table to a variable, then use the result reader blocks (`hit`, `pos`, `enthit`, `fraction`, `plane_normal`, `startsolid`, or arbitrary field). The editor emits named helper functions only when those blocks are used. No anonymous functions are generated.

在「通用工具 → 射线追踪」中拖出 `TraceRay`，设置起点、终点、忽略实体及 mask。再把结果 Table 存到变量，利用输出字段积木读取。读取不存在的字段时返回约定默认值，以免对空字段直接访问。

Common mask references (these are numeric bitmasks, not values guaranteed in every map script scope): `33579137` visible and NPCs, `1174421507` shot, `-1` all. Choose according to the trace's purpose. The editor does not define these constants globally.

Reference: https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions
Community example: https://steamcommunity.com/sharedfiles/filedetails/?id=3681946356
