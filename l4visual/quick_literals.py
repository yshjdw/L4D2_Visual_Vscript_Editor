"""Curated, draggable L4D2 strings; never generate identifiers from UI captions.

Classnames are entity class strings, GiveItem entries are *give command* names,
and model entries are asset paths. Models are common stock assets, not a runtime
asset inventory; availability still depends on the game/content installation.
"""
from __future__ import annotations
import json
from .models import Block

LITERAL_GROUPS = {
    'classname': {'zh':'实体 Classname','en':'Entity classnames',
        'description_zh':'实体类名字符串，可用于查找或生成实体；并非所有类都支持 SpawnEntityFromTable。',
        'description_en':'Entity classname string for lookup/spawning; not every class supports SpawnEntityFromTable.',
        'entries': [
            ('player','玩家','Player'),('infected','普通感染者','Common infected'),
            ('witch','Witch','Witch'),('tank_rock','Tank 石头','Tank rock'),
            ('info_target','目标点实体','Info target'),('info_particle_system','粒子系统','Particle system'),
            ('env_sprite','精灵实体','Sprite entity'),('env_beam','光束实体','Beam entity'),
            ('prop_dynamic','动态模型实体','Dynamic prop'),('prop_physics','物理模型实体','Physics prop'),
            ('prop_physics_override','物理模型（覆盖）','Physics prop override'),
            ('logic_relay','逻辑中继','Logic relay'),('logic_timer','逻辑计时器','Logic timer'),
            ('trigger_multiple','多次触发器','Multiple trigger'),('point_template','实体模板','Entity template'),
            ('weapon_spawn','随机武器刷新点','Random weapon spawn'),('weapon_melee_spawn','近战武器刷新点','Melee weapon spawn'),
            ('weapon_pain_pills','止痛药实体','Pain pills entity'),('weapon_adrenaline','肾上腺素实体','Adrenaline entity'),
            ('weapon_first_aid_kit','医疗包实体','First aid kit entity'),('weapon_defibrillator','除颤器实体','Defibrillator entity'),
            ('weapon_rifle_ak47','AK47 实体','AK-47 entity'),('weapon_smg','冲锋枪实体','SMG entity'),
            ('weapon_gascan','汽油桶实体','Gas can entity'),
        ]},
    'item': {'zh':'常用物品（GiveItem）','en':'Common items (GiveItem)',
        'description_zh':'用于 player.GiveItem() 的物品名称，通常不带 weapon_ 前缀；不要当作实体 Classname。',
        'description_en':'Item name for player.GiveItem(), usually without weapon_ prefix; not an entity classname.',
        'entries': [
            ('pain_pills','止痛药','Pain pills'),('adrenaline','肾上腺素','Adrenaline'),
            ('first_aid_kit','医疗包','First aid kit'),('defibrillator','除颤器','Defibrillator'),
            ('molotov','燃烧瓶','Molotov'),('pipe_bomb','土制炸弹','Pipe bomb'),
            ('vomitjar','胆汁瓶','Bile jar'),('upgradepack_incendiary','燃烧弹药包','Incendiary ammo pack'),
            ('upgradepack_explosive','高爆弹药包','Explosive ammo pack'),
            ('pistol','手枪','Pistol'),('pistol_magnum','马格南手枪','Magnum pistol'),
            ('smg','Uzi 冲锋枪','Uzi SMG'),('smg_silenced','消音冲锋枪','Silenced SMG'),
            ('smg_mp5','MP5','MP5'),('pumpshotgun','泵动霰弹枪','Pump shotgun'),
            ('shotgun_chrome','铬合金霰弹枪','Chrome shotgun'),('autoshotgun','自动霰弹枪','Auto shotgun'),
            ('shotgun_spas','SPAS 霰弹枪','SPAS shotgun'),('rifle','M16 步枪','M16 rifle'),
            ('rifle_ak47','AK47 步枪','AK-47 rifle'),('rifle_desert','SCAR 步枪','SCAR rifle'),
            ('rifle_sg552','SG552 步枪','SG552 rifle'),('hunting_rifle','猎枪','Hunting rifle'),
            ('sniper_military','军用狙击枪','Military sniper'),('sniper_awp','AWP','AWP'),
            ('sniper_scout','Scout','Scout'),('grenade_launcher','榴弹发射器','Grenade launcher'),
            ('rifle_m60','M60','M60'),('chainsaw','电锯','Chainsaw'),
        ]},
    'model': {'zh':'实体模型路径（Model）','en':'Entity model paths',
        'description_zh':'游戏内模型的 .mdl 路径，可用于 SetModel 等；使用前可能需要 PrecacheModel，且需安装相应资源。',
        'description_en':'Stock .mdl path for SetModel and similar APIs; may require PrecacheModel and matching game assets.',
        'entries': [
            ('models/w_models/weapons/w_pistol_B.mdl','手枪世界模型','Pistol world model'),
            ('models/w_models/weapons/w_smg_uzi.mdl','Uzi 世界模型','Uzi world model'),
            ('models/w_models/weapons/w_rifle_m16a2.mdl','M16 世界模型','M16 world model'),
            ('models/w_models/weapons/w_desert_rifle.mdl','SCAR 世界模型','SCAR world model'),
            ('models/w_models/weapons/w_shotgun.mdl','泵动霰弹枪模型','Pump shotgun world model'),
            ('models/w_models/weapons/w_pumpshotgun_a.mdl','铬合金霰弹枪模型','Chrome shotgun world model'),
            ('models/w_models/weapons/w_autoshot_m4super.mdl','自动霰弹枪模型','Auto shotgun world model'),
            ('models/w_models/weapons/w_shotgun_spas.mdl','SPAS 世界模型','SPAS world model'),
            ('models/w_models/weapons/w_sniper_mini14.mdl','猎枪世界模型','Hunting rifle world model'),
            ('models/w_models/weapons/w_sniper_military.mdl','军用狙击枪模型','Military sniper world model'),
            ('models/w_models/weapons/w_eq_medkit.mdl','医疗包模型','Medkit model'),
            ('models/w_models/weapons/w_eq_molotov.mdl','燃烧瓶模型','Molotov model'),
            ('models/w_models/weapons/w_eq_pipebomb.mdl','土制炸弹模型','Pipe bomb model'),
            ('models/w_models/weapons/w_eq_painpills.mdl','止痛药模型','Pain pills model'),
            ('models/props_junk/gascan001a.mdl','汽油桶模型','Gas can model'),
            ('models/props_junk/propanecanister001a.mdl','丙烷罐模型','Propane tank model'),
            ('models/props_junk/explosive_box001.mdl','烟花箱模型','Fireworks crate model'),
            ('models/props_equipment/oxygentank01.mdl','氧气瓶模型','Oxygen tank model'),
        ]},
}


# The legacy `model` group is preserved for .l4vp projects saved with v0.9.9.38.
# These categories distinguish first-person view models, third-person/dropped
# world models, melee assets, and character models. Model paths are taken from
# community-maintained stock L4D2 model inventories (see DATA_SOURCES.md).
def _model_entries(prefix, rows):
    return [(prefix + filename + '.mdl', zh, en) for filename, zh, en in rows]

_MODEL_CATALOG = {
    'model_view': {
        'zh': '第一人称持有模型（V）', 'en': 'First-person held models (V)',
        'description_zh': '玩家第一人称手中的 v_models；不等于第三人称或地面物品的 w_models。SetModel 不会自动改变玩家武器的第一人称显示。',
        'description_en': 'First-person v_models, not world/dropped w_models. SetModel alone does not replace a weapon viewmodel.',
        'entries': _model_entries('models/v_models/', [
            ('v_pistola','手枪','Pistol'), ('v_dual_pistola','双持手枪','Dual pistols'), ('v_desert_eagle','马格南','Magnum'),
            ('v_smg','Uzi','Uzi SMG'),('v_silenced_smg','消音冲锋枪','Silenced SMG'),('v_smg_mp5','MP5','MP5 SMG'),
            ('v_rifle','M16','M16 rifle'),('v_rifle_ak47','AK-47','AK-47 rifle'),('v_desert_rifle','SCAR','SCAR rifle'),('v_rif_sg552','SG552','SG552 rifle'),
            ('v_pumpshotgun','泵动霰弹枪','Pump shotgun'),('v_shotgun_chrome','铬合金霰弹枪','Chrome shotgun'),
            ('v_autoshotgun','自动霰弹枪','Auto shotgun'),('v_shotgun_spas','SPAS','SPAS shotgun'),
            ('v_huntingrifle','猎枪','Hunting rifle'),('v_sniper_military','军用狙击枪','Military sniper'),
            ('v_snip_awp','AWP','AWP sniper'),('v_snip_scout','Scout','Scout sniper'),
            ('v_grenade_launcher','榴弹发射器','Grenade launcher'),
            ('v_medkit','医疗包','First aid kit'),('v_defibrillator','除颤器','Defibrillator'),
            ('v_painpills','止痛药','Pain pills'),('v_adrenaline','肾上腺素','Adrenaline'),
            ('v_pipebomb','土制炸弹','Pipe bomb'),('v_molotov','燃烧瓶','Molotov'),('v_bile_flask','胆汁瓶','Bile jar'),
            ('v_incendiary_ammopack','燃烧弹药包','Incendiary ammo pack'),
            ('v_explosive_ammopack','高爆弹药包','Explosive ammo pack'),
        ])
    },
    'model_world': {
        'zh':'第三人称与地面枪械（W）', 'en':'Third-person / dropped firearms (W)',
        'description_zh':'w_models 是第三人称与地面展示常用模型，不是第一人称持枪模型。具体武器仍由游戏自己的模型配置控制。',
        'description_en':'World/third-person models, commonly seen on the ground or other players; not first-person viewmodels.',
        'entries': _model_entries('models/w_models/weapons/', [
            ('w_pistol_B','手枪','Pistol'),('w_desert_eagle','马格南','Magnum'),
            ('w_smg_uzi','Uzi','Uzi SMG'),('w_smg_a','消音 SMG','Silenced SMG'),('w_smg_mp5','MP5','MP5 SMG'),
            ('w_rifle_m16a2','M16','M16 rifle'),('w_rifle_ak47','AK-47','AK-47 rifle'),
            ('w_desert_rifle','SCAR','SCAR rifle'),('w_rifle_sg552','SG552','SG552 rifle'),
            ('w_shotgun','泵动霰弹枪','Pump shotgun'),('w_pumpshotgun_a','铬合金霰弹枪','Chrome shotgun'),
            ('w_autoshot_m4super','自动霰弹枪','Auto shotgun'),('w_shotgun_spas','SPAS','SPAS shotgun'),
            ('w_sniper_mini14','猎枪','Hunting rifle'),('w_sniper_military','军用狙击枪','Military sniper'),
            ('w_sniper_awp','AWP','AWP sniper'),('w_sniper_scout','Scout','Scout sniper'),
            ('w_grenade_launcher','榴弹发射器','Grenade launcher'),
        ])
    },
    'model_equipment': {
        'zh':'物资与投掷物世界模型', 'en':'Equipment / throwables (W)',
        'description_zh':'医疗物品、投掷物、升级包的地面/第三人称模型。与第一人称 v_models 区分。',
        'description_en':'World models for aid items, throwables and ammunition upgrades; distinct from first-person v_models.',
        'entries': _model_entries('models/w_models/weapons/', [
            ('w_eq_medkit','医疗包','First aid kit'),('w_eq_painpills','止痛药','Pain pills'),
            ('w_eq_adrenaline','肾上腺素','Adrenaline'),('w_eq_defibrillator','除颤器','Defibrillator'),
            ('w_eq_molotov','燃烧瓶','Molotov'),('w_eq_pipebomb','土制炸弹','Pipe bomb'),
            ('w_eq_bile_flask','胆汁瓶','Bile jar'),
            ('w_eq_incendiary_ammopack','燃烧弹药包','Incendiary ammo pack'),
            ('w_eq_explosive_ammopack','高爆弹药包','Explosive ammo pack'),
        ])
    },
    'model_props': {
        'zh':'场景与任务物品模型','en':'Props and mission items',
        'description_zh':'汽油桶、氧气瓶、丙烷罐与任务物品模型；角色替换不适用。',
        'description_en':'Gas cans, propane and oxygen tanks, and mission props; not character replacement models.',
        'entries': [
            ('models/props_junk/gascan001a.mdl','汽油桶','Gas can'),
            ('models/props_junk/propanecanister001a.mdl','丙烷罐','Propane tank'),
            ('models/props_equipment/oxygentank01.mdl','氧气瓶','Oxygen tank'),
            ('models/props_junk/explosive_box001.mdl','烟花箱','Fireworks crate'),
            ('models/props_junk/gnome.mdl','侏儒玩偶','Garden gnome'),
        ]
    },
    'model_melee': {
        'zh':'近战武器世界模型', 'en':'Melee weapon world models',
        'description_zh':'近战武器放置、掉落或第三人称使用的模型路径；并非第一人称近战手臂模型。',
        'description_en':'World/third-person melee models, not the first-person melee arm animations.',
        'entries': _model_entries('models/weapons/melee/', [
            ('w_fireaxe','消防斧','Fire axe'),('w_bat','棒球棍','Baseball bat'),
            ('w_cricket_bat','板球拍','Cricket bat'),('w_crowbar','撬棍','Crowbar'),
            ('w_frying_pan','平底锅','Frying pan'),('w_golfclub','高尔夫球杆','Golf club'),
            ('w_electric_guitar','电吉他','Electric guitar'),('w_katana','武士刀','Katana'),
            ('w_machete','砍刀','Machete'),('w_tonfa','警棍','Tonfa'),
            ('w_pitchfork','干草叉','Pitchfork'),('w_shovel','铲子','Shovel'),
            ('w_chainsaw','电锯','Chainsaw'),
        ]) + [('models/w_models/weapons/w_knife_t.mdl','小刀','Knife')]
    },
    'model_melee_view': {
        'zh':'第一人称近战武器（V）', 'en':'First-person melee models (V)',
        'description_zh':'第一人称手中近战武器的独立 V 模型，与地面近战 W 模型分开。',
        'description_en':'First-person melee V models are distinct from world/dropped melee W models.',
        'entries': _model_entries('models/weapons/melee/', [
            ('v_fireaxe','消防斧','Fire axe'),('v_cricket_bat','板球拍','Cricket bat'),
            ('v_crowbar','撬棍','Crowbar'),('v_frying_pan','平底锅','Frying pan'),
            ('v_golfclub','高尔夫球杆','Golf club'),('v_electric_guitar','电吉他','Electric guitar'),
            ('v_katana','武士刀','Katana'),('v_machete','砍刀','Machete'),
            ('v_tonfa','警棍','Tonfa'),('v_shovel','铲子','Shovel'),
        ]) + [('models/v_models/v_knife_t.mdl','小刀','Knife')]
    },
    'model_survivor': {
        'zh':'幸存者角色模型', 'en':'Survivor character models',
        'description_zh':'八位幸存者的第三人称角色模型，与第一人称手臂模型分开。',
        'description_en':'Third-person character models for all eight survivors, separate from first-person arm models.',
        'entries': _model_entries('models/survivors/', [
            ('survivor_gambler','尼克','Nick'),('survivor_producer','罗雪儿','Rochelle'),
            ('survivor_coach','教练','Coach'),('survivor_mechanic','艾利斯','Ellis'),
            ('survivor_namvet','比尔','Bill'),('survivor_teenangst','佐伊','Zoey'),
            ('survivor_biker','弗朗西斯','Francis'),('survivor_manager','路易斯','Louis'),
        ])
    },
    'model_infected': {
        'zh':'特殊感染者模型', 'en':'Special infected character models',
        'description_zh':'特殊感染者、Tank 与 Witch 的第三人称角色模型；仅模型路径，不会改变实体 AI 或感染者类型。',
        'description_en':'Special infected, Tank and Witch character models. A model path does not change entity AI or infected class.',
        'entries': _model_entries('models/infected/', [
            ('smoker','Smoker','Smoker'),('boomer','Boomer','Boomer'),('boomette','女性 Boomer','Female Boomer'),
            ('hunter','Hunter','Hunter'),('spitter','Spitter','Spitter'),('jockey','Jockey','Jockey'),
            ('charger','Charger','Charger'),('hulk','Tank','Tank'),('hulk_dlc3','DLC Tank','DLC Tank'),
            ('witch','Witch','Witch'),('witch_bride','婚纱 Witch','Bride Witch'),
        ])
    },
    'model_common': {
        'zh':'特殊普通感染者模型', 'en':'Uncommon infected models',
        'description_zh':'CEDA、警察、泥人、Jimmy 等罕见普通感染者的模型。',
        'description_en':'Character models for uncommon infected variants such as CEDA, Riot, Mud Men and Jimmy.',
        'entries': _model_entries('models/infected/', [
            ('common_male_ceda','CEDA','CEDA worker'),('common_male_riot','防暴警察','Riot infected'),
            ('common_male_mud','泥人','Mud Man'),('common_male_clown','小丑','Clown'),
            ('common_male_fallen_survivor','倒地幸存者感染者','Fallen survivor'),
            ('common_male_jimmy','Jimmy Gibbs Jr.','Jimmy Gibbs Jr.'),
        ])
    },
}
LITERAL_GROUPS.update(_MODEL_CATALOG)


from .extra_literals import extend_literals
extend_literals(LITERAL_GROUPS)


# Dedicated subset of entity classnames used in the SpawnEntityFromTable
# classname socket. Keep these as literal strings, not a nested spawn call.
# Runtime spawning is class/keyvalue dependent; these are reference options,
# not a guarantee every entity can be created in every game mode.
from .spawn_catalog import SPAWN_GROUPS
_spawn_labels = {
    'info_target': ('目标标记实体', 'Target marker'),
    'prop_dynamic': ('动态场景模型', 'Dynamic prop'),
    'prop_physics': ('物理道具实体', 'Physics prop'),
}
_spawn_entries=[]
for _group in SPAWN_GROUPS:
    for _name in SPAWN_GROUPS[_group]:
        _zh, _en = _spawn_labels.get(_name, (_name, _name))
        _spawn_entries.append((_name, _zh, _en))
LITERAL_GROUPS['trace_mask'] = {
    'zh': 'TraceLine 碰撞掩码（数值）',
    'en': 'TraceLine collision masks (numeric)',
    'description_zh': '拖入 mask 参数槽，生成整数而非字符串；掩码决定射线检测的碰撞类型。',
    'description_en': 'Drop into a mask socket. Emits an integer, not a quoted string; the mask controls collision categories.',
    'entries': [
        ('33579137','可见物体与 NPC','Visible objects and NPCs'),
        ('1174421507','子弹射线','Shot / bullet trace'),
        ('33579073','视觉检测','Vision trace'),
        ('33636363','玩家实体阻挡','Player-solid trace'),
        ('33701899','NPC 实体阻挡','NPC-solid trace'),
        ('-1','所有碰撞内容','All trace contents'),
    ],
}
LITERAL_GROUPS['spawn_classname'] = {
    'zh': 'Summon / 生成实体 Classname',
    'en': 'Summon / spawn entity classnames',
    'description_zh': '拖入 Summon 的 classname 槽，仅填实体类名字符串（例如 "info_target"）。不生成嵌套 SpawnEntityFromTable；武器/物品生成点及 prop 实体可能需要额外 KeyValues，实际可否生成请在游戏内验证。',
    'description_en': 'Drag into the Summon classname socket to insert only a quoted entity classname (e.g. "info_target"). Does not nest SpawnEntityFromTable; props and item spawners may require special KeyValues and game verification.',
    'entries': _spawn_entries,
}


def lookup_literal(group, value):
    data=LITERAL_GROUPS.get(group)
    if data is None:raise ValueError('Unknown literal group: '+str(group))
    for entry in data['entries']:
        if entry[0]==value:return entry
    raise ValueError('Unknown literal: '+str(value))


def literal_label(group, value, language='en', style='general'):
    entry=lookup_literal(group, value)
    if style=='professional':return value
    return (entry[1] if language=='zh' else entry[2])+'  ·  '+value


def corresponding_view_or_world_model(group, value):
    """Return the known V/W counterpart, not a guessed prefix substitution."""
    if group in ('model_view','model_melee_view','model_equipment_view'):
        search=('model_world','model_melee','model_equipment')
    elif group in ('model_world','model_melee','model_equipment'):
        search=('model_view','model_melee_view','model_equipment_view')
    else:
        return None
    label=lookup_literal(group,value)[2]
    for kind in search:
        for other,zh,en in LITERAL_GROUPS[kind]['entries']:
            if en==label:
                return other
    return None


def literal_tooltip(group, value, language='en', style='general'):
    data=LITERAL_GROUPS[group]
    label=literal_label(group,value,language,style)
    prefix=data['description_zh' if language=='zh' else 'description_en']
    counterpart=corresponding_view_or_world_model(group,value)
    details=('\n对应 V/W 模型：' if language=='zh' else '\nV/W counterpart: ')+counterpart if counterpart else ''
    if group=='spawn_classname':
        from .spawn_catalog import spawn_category, SPAWN_GROUP_META
        category=spawn_category(value)
        if category:
            note=SPAWN_GROUP_META[category][2 if language=='zh' else 3]
            details+='\n'+note
    rendered=value if group=='trace_mask' else json.dumps(value,ensure_ascii=False)
    type_label=('生成 Squirrel 整数：' if language=='zh' else 'Squirrel integer: ') if group=='trace_mask' else ('生成 Squirrel 字符串：' if language=='zh' else 'Squirrel string literal: ')
    return label+'\n'+prefix+details+'\n'+type_label+rendered


def new_literal_block(group, value):
    lookup_literal(group, value)
    integer = group == 'trace_mask'
    return Block('expr', {'value':value if integer else json.dumps(value,ensure_ascii=False),
                          'return_type':'int' if integer else 'string',
                          'literal_group':group, 'literal_name':value})
