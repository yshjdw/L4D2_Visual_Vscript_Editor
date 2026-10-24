"""Verified entity classnames; spawning is not guaranteed for every entity."""
from __future__ import annotations
# Exact entity names, not GiveItem names or model files. Spawning support is
# classname-dependent. Infected use ZSpawn rather than treating monster names
# as interchangeable SpawnEntityFromTable classnames.
SPAWN_GROUPS = {
    '基础实体': ['info_target','prop_dynamic','prop_physics','prop_physics_override','prop_dynamic_override',
                 'info_particle_system','env_sprite','env_beam','logic_relay','logic_timer','point_template'],
    '主武器实体': ['weapon_smg','weapon_smg_silenced','weapon_smg_mp5',
                 'weapon_pumpshotgun','weapon_shotgun_chrome','weapon_autoshotgun','weapon_shotgun_spas',
                 'weapon_rifle','weapon_rifle_ak47','weapon_rifle_desert','weapon_rifle_sg552','weapon_rifle_m60',
                 'weapon_hunting_rifle','weapon_sniper_military','weapon_sniper_awp','weapon_sniper_scout','weapon_grenade_launcher'],
    '副武器与近战实体': ['weapon_pistol','weapon_pistol_magnum','weapon_melee','weapon_chainsaw'],
    '医疗与补给实体': ['weapon_first_aid_kit','weapon_defibrillator','weapon_pain_pills','weapon_adrenaline',
                     'weapon_upgradepack_incendiary','weapon_upgradepack_explosive'],
    '投掷物与任务物品': ['weapon_molotov','weapon_pipe_bomb','weapon_vomitjar','weapon_gascan',
                     'weapon_propanetank','weapon_oxygentank','weapon_fireworkcrate','weapon_gnome','weapon_cola_bottles'],
    '武器生成点': ['weapon_spawn','weapon_smg_spawn','weapon_smg_silenced_spawn','weapon_smg_mp5_spawn',
                 'weapon_pumpshotgun_spawn','weapon_shotgun_chrome_spawn','weapon_autoshotgun_spawn','weapon_shotgun_spas_spawn',
                 'weapon_rifle_spawn','weapon_rifle_ak47_spawn','weapon_rifle_desert_spawn','weapon_rifle_sg552_spawn',
                 'weapon_rifle_m60_spawn','weapon_hunting_rifle_spawn','weapon_sniper_military_spawn',
                 'weapon_sniper_awp_spawn','weapon_sniper_scout_spawn','weapon_grenade_launcher_spawn',
                 'weapon_pistol_spawn','weapon_pistol_magnum_spawn','weapon_chainsaw_spawn','weapon_melee_spawn'],
    '物品生成点': ['weapon_item_spawn','weapon_adrenaline_spawn','weapon_ammo_spawn','weapon_defibrillator_spawn',
                 'weapon_first_aid_kit_spawn','weapon_gascan_spawn','weapon_molotov_spawn','weapon_pain_pills_spawn',
                 'weapon_pipe_bomb_spawn','weapon_upgradepack_explosive_spawn','weapon_upgradepack_incendiary_spawn',
                 'weapon_vomitjar_spawn','weapon_scavenge_item_spawn','upgrade_spawn'],
    '感染者（使用 ZSpawn）': ['infected','witch','player'],
}

SPAWN_GROUP_META = {
    '基础实体': ('基础与逻辑实体','Basic & logic entities', '普通地图实体，部分类型需要特定 KeyValues 或模型。', 'Ordinary map entities; some require class-specific KeyValues or models.'),
    '主武器实体': ('直接生成：主武器','Direct: primary weapons', '直接武器实体类名；使用 SpawnEntityFromTable，可能需要 ammo、origin 等配置。', 'Weapon entity classnames for SpawnEntityFromTable; may require ammo/origin KeyValues.'),
    '副武器与近战实体': ('直接生成：副武器与近战','Direct: sidearms & melee', '近战武器使用 weapon_melee 类名；若使用 weapon_melee_spawn，可设置 melee_weapon 等专用键值指定种类。', 'Melee uses weapon_melee, not weapon_katana; weapon_melee_spawn accepts a melee_weapon keyvalue to select a type.'),
    '医疗与补给实体': ('直接生成：医疗与补给','Direct: health & supplies', '医疗物品和弹药升级包的 weapon_* 实体名。', 'weapon_* classnames for medical items and ammo upgrades.'),
    '投掷物与任务物品': ('直接生成：投掷与任务物品','Direct: throwables & props', '投掷物及任务物品；部分物品受关卡/实体特殊参数限制。', 'Throwables and carryables; some require class/map-specific settings.'),
    '武器生成点': ('刷新点：枪械与近战','Spawners: firearms & melee', '生成点不是背包里的武器实体；可能由 Director 决定实际物品。', 'Spawn-point entities, not the held weapons; the Director may select actual items.'),
    '物品生成点': ('刷新点：补给与物品','Spawners: supplies & items', '物资生成点，可使用 count、spawnflags 等适当键值。', 'Supply spawners; relevant KeyValues can include count/spawnflags.'),
    '感染者（使用 ZSpawn）': ('感染者（请使用 ZSpawn）','Infected (use ZSpawn)', '普通感染者、特感、Tank、Witch 请使用 ZSpawn 积木选择类型；player 并非可直接生成的特感 Classname。', 'Use the dedicated ZSpawn block for common/special infected, Tank and Witch. player is not a special-infected classname to spawn.'),
}

# Numeric ZSpawn type IDs (L4D2 ZOMBIE_* indices).
INFECTED_TYPES = [
    (0, '普通感染者', 'Common infected'),
    (1, 'Smoker', 'Smoker'), (2, 'Boomer', 'Boomer'),
    (3, 'Hunter', 'Hunter'), (4, 'Spitter', 'Spitter'),
    (5, 'Jockey', 'Jockey'), (6, 'Charger', 'Charger'),
    (7, 'Witch', 'Witch'), (8, 'Tank', 'Tank'),
]

def spawn_subgroups():
    """Display metadata for the two-tier Summon classname palette."""
    return [dict(id='spawn_'+str(index), name=name, zh=SPAWN_GROUP_META[name][0],
                 en=SPAWN_GROUP_META[name][1],
                 description_zh=SPAWN_GROUP_META[name][2],
                 description_en=SPAWN_GROUP_META[name][3], entries=list(dict.fromkeys(names)))
            for index,(name,names) in enumerate(SPAWN_GROUPS.items())]

def spawn_category(classname):
    return next((name for name,items in SPAWN_GROUPS.items() if classname in items), None)

DOCUMENTATION = 'https://developer.valvesoftware.com/wiki/L4D2_Level_Design/Weapon_and_Item_Spawning'
CONFIG_FIELDS = [('origin','Vector(0, 0, 0)'), ('angles','Vector(0, 0, 0)'), ('targetname','""'), ('model','""'), ('solid','0'), ('spawnflags','0'), ('count','1'), ('weaponskin','0'), ('melee_weapon','"any"'), ('ammo','100'), ('skin','0'), ('body','0')]
def enabled_config(config):
    return {str(k):str(v) for k,v in (config or {}).items() if k in dict(CONFIG_FIELDS) and isinstance(v,(str,int,float))}
