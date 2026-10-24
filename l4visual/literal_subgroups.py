"""Two-level Classname/Item palette organization without changing saved literals.

The complete legacy dictionaries in quick_literals remain available to loaded
.l4vp projects.  This module only partitions their draggable palette entries.
"""
from __future__ import annotations

from .quick_literals import LITERAL_GROUPS
from .extra_literals import WEAPONS, SUPPLIES, MELEE, WORLD_ITEMS

_SUBGROUPS = {
    'classname': [
        ('actors', '玩家与感染者', 'Players & infected', '玩家、普通感染者及 Tank 石块等实体。', 'Players, infected and Tank rock entities.'),
        ('weapons', '枪械与武器实体', 'Weapon entities', '武器实体的 weapon_* 类名。', 'weapon_* entity classnames for firearms and weapons.'),
        ('supplies', '补给与任务物品实体', 'Supplies & mission items', '医疗物品、投掷物和任务物品等实体。', 'Health items, throwables and carried mission-item entities.'),
        ('spawners', '武器与物品刷新点', 'Weapon & item spawners', '地图上刷出武器或物资的实体，不等同于拾取后的物品。', 'Map weapon/item spawn entities, not the item held after pickup.'),
        ('logic', '逻辑与信息实体', 'Logic & information', 'info_*、logic_*、point_*、math_* 等实体。', 'info_*, logic_*, point_* and math_* entities.'),
        ('effects', '环境与特效实体', 'Environment & effects', 'env_* 类型的视觉和环境控制实体。', 'env_* effects and environment controllers.'),
        ('props', '场景与触发器', 'Props & triggers', 'prop_*、func_*、trigger_* 等场景实体。', 'prop_*, func_* and trigger_* map entities.'),
        ('projectiles', '投射物与感染者武器', 'Projectiles & infected weapons', '投射物和特殊感染者爪子类实体。', 'Projectiles and special-infected claw weapon entities.'),
        ('other', '其他实体', 'Other entities', '未归入以上类别的实体名称。', 'Other classnames not covered by the categories above.'),
    ],
    'item': [
        ('medical', '医疗用品', 'Medical items', '常用治疗与救援物品的 GiveItem 名称。', 'GiveItem names for healing and rescue equipment.'),
        ('throwables', '投掷物', 'Throwables', '燃烧瓶、土制炸弹和胆汁瓶。', 'Molotovs, pipe bombs and bile jars.'),
        ('upgrades', '弹药升级包', 'Ammo upgrade packs', '高爆与燃烧弹药包。', 'Explosive and incendiary ammunition packs.'),
        ('primary', '主武器与重型武器', 'Primary & heavy weapons', '冲锋枪、霰弹枪、步枪、狙击枪和榴弹发射器等。', 'SMGs, shotguns, rifles, snipers and grenade launchers.'),
        ('secondary', '副武器与电锯', 'Sidearms & chainsaw', '手枪、马格南手枪与电锯。', 'Pistols, magnum and chainsaw.'),
        ('melee', '近战武器脚本名', 'Melee script names', '近战武器的脚本名称；GiveItem 是否接受取决于游戏行为。', 'Melee script names; GiveItem support depends on the game.'),
        ('mission', '任务及可携带物品', 'Mission & carryable items', '汽油桶、可乐、侏儒等；不保证能直接 GiveItem。', 'Gas cans, cola and gnomes; not necessarily supported by GiveItem.'),
        ('other', '其他物品', 'Other items', '其他物品名称。', 'Other item names.'),
    ],
}

_SUPPLY_SET = {name for name, _, _ in SUPPLIES + WORLD_ITEMS}
_MELEE_SET = {name for name, _, _ in MELEE}
_WORLD_SET = {name for name, _, _ in WORLD_ITEMS}
_MEDICAL = {'first_aid_kit','defibrillator','pain_pills','adrenaline'}
_THROWABLE = {'molotov','pipe_bomb','vomitjar'}
_UPGRADE = {'upgradepack_incendiary','upgradepack_explosive'}
_SECONDARY = {'pistol','pistol_magnum','chainsaw'}
_PRIMARY = {name for name, _, _ in WEAPONS} - _SECONDARY


def _classname_category(name):
    if name.endswith('_spawn') or name in ('upgrade_spawn', 'weapon_spawn'):
        return 'spawners'
    if name in ('player','infected','witch','tank_rock'):
        return 'actors'
    if name.endswith('_projectile') or name.endswith('_claw'):
        return 'projectiles'
    if name.startswith('weapon_'):
        return 'supplies' if name[7:] in _SUPPLY_SET or name == 'weapon_ammo' else 'weapons'
    if name.startswith('env_'):
        return 'effects'
    if name.startswith(('info_','logic_','math_','point_')):
        return 'logic'
    if name.startswith(('prop_','func_','trigger_')):
        return 'props'
    return 'other'


def _item_category(name):
    if name in _MEDICAL:return 'medical'
    if name in _THROWABLE:return 'throwables'
    if name in _UPGRADE:return 'upgrades'
    if name in _PRIMARY:return 'primary'
    if name in _SECONDARY:return 'secondary'
    if name in _MELEE_SET:return 'melee'
    if name in _WORLD_SET:return 'mission'
    return 'other'


def literal_subgroups(parent):
    """Ordered display groups, each with (source_group, value) entry references.

    Duplicate entries are shown once. The underlying group/value pair remains
    unchanged for drag payloads, tooltip lookup and .l4vp compatibility.
    """
    if parent == 'spawn_classname':
        from .spawn_catalog import spawn_subgroups
        available={v for v,_,_ in LITERAL_GROUPS['spawn_classname']['entries']}
        return [dict(id=group['id'], zh=group['zh'],en=group['en'],
                     description_zh=group['description_zh'],description_en=group['description_en'],
                     entries=[('spawn_classname',v) for v in group['entries'] if v in available])
                for group in spawn_subgroups()]
    if parent not in _SUBGROUPS:
        return []
    rows={key:[] for key, *_ in _SUBGROUPS[parent]}
    seen=set()
    sources=('classname',) if parent=='classname' else ('item','item_melee','item_world')
    for source in sources:
        for value, _, _ in LITERAL_GROUPS[source]['entries']:
            if value in seen:continue
            seen.add(value)
            category=(_classname_category(value) if parent=='classname' else _item_category(value))
            rows[category].append((source,value))
    return [dict(id=key,zh=zh,en=en,description_zh=desc_zh,description_en=desc_en,
                 entries=rows[key])
            for key,zh,en,desc_zh,desc_en in _SUBGROUPS[parent] if rows[key]]
