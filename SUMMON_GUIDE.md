# Summon & infected spawning / 实体生成与感染者生成

## 中文

在左侧 **Summon / 生成实体 Classname** 展开二级分类，拖动字符串积木（例如 `weapon_rifle_ak47`、`weapon_first_aid_kit`、`weapon_melee_spawn`）到 Summon 积木的 `classname` 槽。只会放入类名字符串，不会再套一层 `SpawnEntityFromTable`。

通过右键 **Summon 配置** 打开二级分类树，单击类名选择；也可以自己输入任意合法 classname。使用 `origin` 指定位置；具体实体可能需要 `ammo`、`count`、`spawnflags`、`melee_weapon` 或其他引擎专用 KeyValues。`weapon_melee_spawn` 常用 `melee_weapon = "katana"`（武器能否出现还受到任务地图的近战武器配置影响）。

- **直接实体**（`weapon_*`）：真实的武器/补给物品实体。示例：`weapon_rifle_ak47`、`weapon_pain_pills`。
- **刷新点**（`weapon_*_spawn`）：地图上的生成位置，可能受 Director 规则影响；不等同于直接物品实体。
- **特殊感染者**：请用「实体生成 → 生成感染者 ZSpawn」积木，不要把 `smoker` 等名字当作 `SpawnEntityFromTable` 的 classname。`player` 也不是可直接生成的特感类型。

感染者积木选择类型（0=普通、1=Smoker、2=Boomer、3=Hunter、4=Spitter、5=Jockey、6=Charger、7=Witch、8=Tank）并设置 Vector 位置，生成：

```nut
ZSpawn({type = 1, pos = Vector(0, 0, 0)});
```

`ZSpawn` 仍由游戏引擎决定最终生成位置、导航与容量限制。具体行为应在实际模式中测试。

## English

Expand **Summon / spawn entity classnames** and its subcategories in the block palette. Drag a classname constant (e.g. `weapon_rifle_ak47`, `weapon_first_aid_kit`, or `weapon_melee_spawn`) into the `classname` input of a Summon block. The literal inserts only the quoted classname, never a nested `SpawnEntityFromTable()` call.

Right-click Summon to access its two-level classname tree and optional KeyValues. `origin` specifies the desired location; individual classes may need `ammo`, `count`, `spawnflags`, `melee_weapon`, or other game-specific properties. The `weapon_melee_spawn` entity accepts a melee script name via `melee_weapon = "katana"`, subject to mission/map availability.

- **Direct entities**: `weapon_*` weapon/item entities.
- **Spawn points**: `weapon_*_spawn` entities, which can be influenced by the Director; they are not equivalent to the held entity.
- **Infected**: use the separate **Spawn infected (ZSpawn)** statement block. Do not pass names like `smoker` to `SpawnEntityFromTable()` as if they were entity classnames.

Select an infected type (0=common, 1=Smoker, 2=Boomer, 3=Hunter, 4=Spitter, 5=Jockey, 6=Charger, 7=Witch, 8=Tank) and provide a Vector location. It emits native `ZSpawn({type = ..., pos = ...});`. Actual placement, spawn caps and navigation depend on game state.

## References / 参考

- Valve Developer Community, L4D2 Weapon and Item Spawning: https://developer.valvesoftware.com/wiki/L4D2_Level_Design/Weapon_and_Item_Spawning
- VScript spawning weapons: https://steamcommunity.com/app/550/discussions/3/4520010047765369140/
- VScript infected spawning with `ZSpawn`: https://steamcommunity.com/app/550/discussions/3/4848777619240717767/
