"""Additional L4D2 resource literals cross-checked against Valve map docs,
L4D2 weapon stock tables and an indexed stock .mdl filename inventory.

Deliberately keep classnames, GiveItem names, and models in separate groups.
A model V/W counterpart is listed only if a real asset name was identified.
"""
from .spawn_catalog import SPAWN_GROUPS

WEAPONS = [
    ('pistol','手枪','Pistol'), ('pistol_magnum','马格南手枪','Magnum'),
    ('smg','Uzi 冲锋枪','Uzi SMG'), ('smg_silenced','消音冲锋枪','Silenced SMG'),
    ('smg_mp5','MP5 冲锋枪','MP5 SMG'), ('pumpshotgun','泵式霰弹枪','Pump shotgun'),
    ('shotgun_chrome','铬合金霰弹枪','Chrome shotgun'), ('autoshotgun','自动霰弹枪','Auto shotgun'),
    ('shotgun_spas','SPAS 霰弹枪','SPAS shotgun'), ('rifle','M16','M16 rifle'),
    ('rifle_ak47','AK-47','AK-47'), ('rifle_desert','SCAR','SCAR rifle'),
    ('rifle_sg552','SG552','SG552 rifle'), ('rifle_m60','M60','M60'),
    ('hunting_rifle','猎枪','Hunting rifle'), ('sniper_military','军用狙击枪','Military sniper'),
    ('sniper_awp','AWP','AWP sniper'), ('sniper_scout','Scout','Scout sniper'),
    ('grenade_launcher','榴弹发射器','Grenade launcher'),
    ('chainsaw','电锯','Chainsaw'),
]
SUPPLIES = [
    ('first_aid_kit','医疗包','First aid kit'),('defibrillator','除颤器','Defibrillator'),
    ('pain_pills','止痛药','Pain pills'),('adrenaline','肾上腺素','Adrenaline'),
    ('molotov','燃烧瓶','Molotov'),('pipe_bomb','土制炸弹','Pipe bomb'),
    ('vomitjar','胆汁瓶','Bile jar'),
    ('upgradepack_incendiary','燃烧弹药包','Incendiary ammo pack'),
    ('upgradepack_explosive','高爆弹药包','Explosive ammo pack'),
]
WORLD_ITEMS = [
    ('gascan','汽油桶','Gas can'),('propanetank','丙烷罐','Propane tank'),
    ('oxygentank','氧气瓶','Oxygen tank'),('fireworkcrate','烟花箱','Fireworks crate'),
    ('gnome','侏儒玩偶','Garden gnome'),('cola_bottles','可乐瓶','Cola bottles'),
]
MELEE = [
    ('baseball_bat','棒球棍','Baseball bat'),('cricket_bat','板球拍','Cricket bat'),
    ('crowbar','撬棍','Crowbar'),('electric_guitar','电吉他','Electric guitar'),
    ('fireaxe','消防斧','Fire axe'),('frying_pan','平底锅','Frying pan'),
    ('golfclub','高尔夫球杆','Golf club'),('katana','武士刀','Katana'),
    ('knife','小刀','Knife'),('machete','砍刀','Machete'),
    ('pitchfork','干草叉','Pitchfork'),('shovel','铲子','Shovel'),
    ('tonfa','警棍','Tonfa'),
]

def _group(zh, en, desc_zh, desc_en, entries):
    return dict(zh=zh,en=en,description_zh=desc_zh,description_en=desc_en,entries=entries)

def _add_group(groups, name, zh, en, desc_zh, desc_en, entries):
    seen=set()
    cleaned=[]
    for row in entries:
        if row[0] and row[0] not in seen:
            seen.add(row[0]);cleaned.append(row)
    groups[name]=_group(zh,en,desc_zh,desc_en,cleaned)

def _append(groups,name,entries):
    seen={v for v,_,_ in groups[name]['entries']}
    for row in entries:
        if row[0] not in seen:
            groups[name]['entries'].append(row)
            seen.add(row[0])

def extend_literals(groups):
    weapon_rows=[('weapon_'+value,zh+'实体',en+' entity') for value,zh,en in WEAPONS+SUPPLIES+WORLD_ITEMS]
    weapon_rows += [('weapon_melee','近战武器实体（具体类型在脚本名中）','Melee weapon entity'),
                    ('weapon_ammo_spawn','弹药补给点','Ammo pile spawn'),
                    ('weapon_ammo','弹药实体','Ammo entity'),
                    ('weapon_spawn','随机武器生成点','Random weapon spawn'),
                    ('weapon_item_spawn','随机物品生成点','Random item spawn'),
                    ('weapon_melee_spawn','近战武器生成点','Melee weapon spawn'),
                    ('weapon_scavenge_item_spawn','清道夫模式物品点','Scavenge item spawn'),
                    ('weapon_machinegun','机枪武器实体','Mounted machinegun weapon'),
                    ('weapon_tank_claw','Tank 爪子','Tank claws'),
                    ('weapon_hunter_claw','Hunter 爪子','Hunter claws'),
                    ('weapon_charger_claw','Charger 爪子','Charger claws'),
                    ('weapon_boomer_claw','Boomer 爪子','Boomer claws'),
                    ('weapon_smoker_claw','Smoker 爪子','Smoker claws'),
                    ('weapon_spitter_claw','Spitter 爪子','Spitter claws'),
                    ('weapon_jockey_claw','Jockey 爪子','Jockey claws')]
    _append(groups,'classname',weapon_rows)
    _add_group(groups,'classname_weapons','武器与补给实体 Classname','Weapon and supply entity classnames',
        '真实的 weapon_* 实体类名。近战类型使用 weapon_melee；不是所有实体都能直接 SpawnEntityFromTable。',
        'Real weapon_* entity classnames. Melee types use weapon_melee; not every class is directly spawnable.',
        weapon_rows)

    spawn_rows=[]
    for label, values in SPAWN_GROUPS.items():
        if label not in ('武器生成点','物品生成点'): continue
        for value in values:
            spawn_rows.append((value,'刷新点 '+value,'Spawn '+value))
    spawn_rows += [('upgrade_spawn','升级部件生成点','Upgrade spawn'),('weapon_spawn','随机武器生成点','Random weapon spawn'),
                   ('weapon_scavenge_item_spawn','清道夫模式物品点','Scavenge item spawn')]
    _add_group(groups,'classname_spawns','武器与物资生成点','Weapon and supply spawners',
        '地图中的刷新点实体 Classname。可用于查找，实际创建依赖地图和实体规则。',
        'Map spawner entity classnames. Usable for lookup; spawning depends on entity/map rules.',spawn_rows)

    entities=[
       ('info_target','目标点实体','Info target'),('info_player_start','玩家起点','Player start'),
       ('info_landmark','关卡切换标记','Changelevel landmark'),('info_changelevel','关卡切换点','Changelevel marker'),
       ('info_director','导演控制实体','Director entity'),('info_particle_system','粒子系统','Particle system'),
       ('info_map_parameters','地图物品参数','Map item parameters'),
       ('env_sprite','精灵显示','Sprite'),('env_beam','光束','Beam'),('env_laser','激光','Laser'),
       ('env_smokestack','烟雾柱','Smoke stack'),('env_shake','屏幕震动','Screen shake'),
       ('env_fade','画面淡入淡出','Screen fade'),('env_soundscape','环境音景','Soundscape'),
       ('env_fog_controller','雾控制器','Fog controller'),('env_fire','火焰','Fire'),
       ('env_explosion','爆炸','Explosion'),('env_entity_maker','实体制造器','Entity maker'),
       ('logic_relay','逻辑中继','Logic relay'),('logic_timer','定时逻辑','Logic timer'),
       ('logic_auto','自动触发逻辑','Logic auto'),('logic_branch','分支条件','Logic branch'),
       ('logic_case','多分支条件','Logic case'),('logic_compare','数值比较器','Logic compare'),
       ('logic_script','脚本实体','Logic script'),('math_counter','计数器','Math counter'),
       ('point_template','实体模板','Point template'),('point_hurt','范围伤害点','Point hurt'),
       ('point_teleport','瞬间传送点','Point teleport'),
       ('prop_dynamic','动态模型','Dynamic prop'),('prop_dynamic_override','动态模型覆盖','Dynamic prop override'),
       ('prop_physics','物理模型','Physics prop'),('prop_physics_override','物理模型覆盖','Physics prop override'),
       ('prop_static','静态模型','Static prop'),('prop_ragdoll','布娃娃模型','Ragdoll prop'),
       ('prop_minigun_l4d1','L4D1 迷你机枪','L4D1 minigun'),
       ('prop_mounted_machine_gun','固定机枪','Mounted machine gun'),
       ('func_door','门实体','Door'),('func_button','按钮实体','Button'),
       ('func_breakable','可破坏实体','Breakable entity'),('func_rotating','旋转实体','Rotating entity'),
       ('func_movelinear','直线移动实体','Linear mover'),
       ('trigger_multiple','多次触发器','Multiple trigger'),('trigger_once','一次触发器','Trigger once'),
       ('trigger_hurt','伤害触发器','Hurt trigger'),('trigger_push','推力触发器','Push trigger'),
       ('trigger_teleport','传送触发器','Teleport trigger'),
       ('infected','普通感染者','Common infected'),('witch','Witch','Witch'),
       ('player','玩家 / 特感','Player / special infected'),('tank_rock','Tank 石块','Tank rock'),
       ('grenade_launcher_projectile','榴弹投射物','Grenade launcher projectile'),
       ('pipe_bomb_projectile','土制炸弹投射物','Pipe bomb projectile'),
       ('molotov_projectile','燃烧瓶投射物','Molotov projectile'),
       ('vomitjar_projectile','胆汁瓶投射物','Bile jar projectile'),
    ]
    _add_group(groups,'classname_entities','地图逻辑、特效和感染者 Classname','Logic, effects and infected classnames',
        '通用 Source/L4D2 实体名称；仅表示查找用字符串，部分为地图内部实体，不保证可以动态创建。',
        'Source/L4D2 entity classnames for lookup. Some are map-only and cannot be dynamically spawned.',entities)
    _append(groups,'classname',entities)
    _append(groups,'classname',spawn_rows)

    _append(groups,'item',WEAPONS+SUPPLIES+MELEE)
    _add_group(groups,'item_melee','近战武器名称（GiveItem / Spawn）','Melee names (GiveItem / spawns)',
        '近战武器脚本名，不是独立 Classname。通常使用 weapon_melee 或 weapon_melee_spawn 并指定近战脚本名；GiveItem 是否接受取决于实际游戏版本。',
        'Melee script names, not separate entity classnames. Typically use weapon_melee/weapon_melee_spawn with a melee script name; GiveItem acceptance is game-dependent.',MELEE)
    _add_group(groups,'item_world','可携带任务物品名称','Carryable mission-item names',
        '汽油桶、可乐、侏儒等物品名称。不是每个都能通过 GiveItem 直接给予玩家；可作为查找/脚本参数使用。',
        'Names of carryable props such as gas cans, cola and gnomes. Not all can be given through GiveItem; useful as string parameters.', WORLD_ITEMS)

    view_equipment=[
        ('v_medkit','医疗包','First aid kit'),('v_defibrillator','除颤器','Defibrillator'),
        ('v_painpills','止痛药','Pain pills'),('v_adrenaline','肾上腺素','Adrenaline'),
        ('v_molotov','燃烧瓶','Molotov'),('v_pipebomb','土制炸弹','Pipe bomb'),
        ('v_bile_flask','胆汁瓶','Bile jar'),('v_incendiary_ammopack','燃烧弹药包','Incendiary ammo pack'),
        ('v_explosive_ammopack','高爆弹药包','Explosive ammo pack'),
        ('v_cola','可乐瓶','Cola bottles'),
    ]
    _add_group(groups,'model_equipment_view','手持补给、投掷和任务物品（V）','Held supplies, throwables and mission items (V)',
        '确认存在的第一人称物品 V 模型（含可乐）。与地面模型 W 分开；不是所有可携带物品都有 V 模型。',
        'Verified first-person item V models (including cola). Separate from dropped W models; not every carryable prop has a V model.',
        [('models/v_models/'+name+'.mdl',zh,en) for name,zh,en in view_equipment])
    _append(groups,'model_view', [('models/v_models/'+name+'.mdl',zh,en) for name,zh,en in view_equipment])
    _append(groups,'model_equipment', [('models/w_models/weapons/w_cola.mdl','可乐瓶','Cola bottles')])
    groups['model_props']['entries']=[row for row in groups['model_props']['entries'] if row[0]!='models/props_junk/propanecanister001a.mdl']
    _append(groups,'model_props', [('models/props_junk/propanecanister001.mdl','丙烷罐','Propane tank')])
    _append(groups,'model_world',[('models/w_models/weapons/w_m60.mdl','M60','M60')])
    _append(groups,'model_view',[('models/v_models/v_M60.mdl','M60','M60')])
    _append(groups,'model_melee_view',[
        ('models/weapons/melee/v_bat.mdl','棒球棍','Baseball bat'),
        ('models/weapons/melee/v_chainsaw.mdl','电锯','Chainsaw'),
        ('models/weapons/melee/v_pitchfork.mdl','干草叉','Pitchfork'),
    ])
    _add_group(groups,'model_survivor_arms','八位幸存者第一人称手臂模型','Survivor first-person arm models',
        '第一人称角色手臂模型，不是幸存者第三人称身体模型；仅用于模型路径参数。',
        'First-person arm models, not third-person survivor bodies; usable as string model paths.',
        [('models/weapons/arms/'+name+'.mdl',zh,en) for name,zh,en in [
            ('v_arms_gambler_new','尼克','Nick'),('v_arms_producer_new','罗雪儿','Rochelle'),
            ('v_arms_coach_new','教练','Coach'),('v_arms_mechanic_new','艾利斯','Ellis'),
            ('v_arms_bill','比尔','Bill'),('v_arms_zoey','佐伊','Zoey'),
            ('v_arms_francis','弗朗西斯','Francis'),('v_arms_louis','路易斯','Louis')]])
    _add_group(groups,'model_infected_view','感染者第一人称爪子与手臂','Infected first-person claws and arms',
        '部分特感的第一人称爪子和手臂模型。没有对应文件的种类不虚构路径。',
        'Verified first-person infected claw/arm assets only; missing variants are not fabricated.',
        [('models/v_models/weapons/'+name+'.mdl',zh,en) for name,zh,en in [
            ('v_claw_boomer','Boomer 爪子','Boomer claws'),('v_claw_hulk','Tank 爪子','Tank claws'),
            ('v_claw_hunter','Hunter 爪子','Hunter claws'),('v_claw_smoker','Smoker 爪子','Smoker claws')]]+
        [('models/weapons/arms/'+name+'.mdl',zh,en) for name,zh,en in [
            ('v_charger_arms','Charger 手臂','Charger arms'),('v_jockey_arms','Jockey 手臂','Jockey arms'),
            ('v_spitter_arms','Spitter 手臂','Spitter arms')]])
    _add_group(groups,'model_dropped_accessory','角色武器附属模型','Character equipment attachment models',
        '原始模型文件中的配件与附属部件路径；不等于地面拾取物。部分配件没有对应 V 模型。',
        'Accessory models from the stock asset inventory, not necessarily ground pickups. Some have no corresponding V model.',
        [('models/weapons/arms/w_laser_sights.mdl','激光瞄具','Laser sight'),
         ('models/weapons/arms/w_eq_defibrillator_paddles.mdl','除颤器电极','Defibrillator paddles')])
