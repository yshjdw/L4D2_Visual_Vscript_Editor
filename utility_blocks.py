"""Reusable, nestable L4D2 Squirrel expressions.

Simple wrappers are emitted directly. Multi-step wrappers use small, generated named helper functions.
`value` is the first argument for backward compatibility with v0.9.9.41;
`parameters` carries any remaining arguments.
"""


def _entry(zh, en, default, description, description_en, group, professional, params=(), return_type='unknown'):
    return dict(zh=zh, en=en, default=default, description=description,
                description_en=description_en, group=group,
                professional=professional, params=list(params), return_type=return_type)


def _param(name, default, kind, zh, en):
    return dict(name=name, default=default, type=kind, zh=zh, en=en)


UTILITY_GROUPS = {
    'players': ('玩家与武器', 'Players & weapons'),
    'inventory': ('背包与槽位', 'Inventory & slots'),
    'entities': ('实体查找与检查', 'Entity lookup & checks'),
    'scope': ('ScriptScope 数据', 'ScriptScope data'),
    'trace': ('射线追踪 / TraceLine', 'Ray tracing / TraceLine'),
}

UTILITY_BLOCKS = {
    'trace_ray': _entry('TraceLine 射线追踪 → 结果 Table', 'TraceLine ray → result table', 'Vector(0, 0, 0)',
        '原生 L4D2 TraceLine(table)：start 起点、end 终点、ignore 忽略实体、mask 碰撞掩码；返回含 hit/pos/enthit/fraction 等字段的 Table，输入无效时返回 null。',
        'Native L4D2 TraceLine(table): start/end Vectors, ignored entity and collision mask. Returns a result table containing hit, pos, enthit and fraction, or null for invalid input.',
        'trace', 'TraceRay', (
            _param('end','Vector(1000, 0, 0)','Vector','终点 Vector','End Vector'),
            _param('ignore','null','handle','忽略实体','Entity to ignore'),
            _param('mask','33579137','int','碰撞掩码','Collision mask'),
        ), 'table'),
    'trace_hit': _entry('追踪结果是否命中', 'Trace result hit?', 'trace',
        '读取 TraceLine 输出字段 hit。没有结果时返回 false；执行成功不等于命中了实体。',
        'Read TraceLine output hit; defaults to false for missing results. A successful trace call does not itself mean a collision.',
        'trace', 'TraceHit',return_type='bool'),
    'trace_pos': _entry('获取射线结束/碰撞位置', 'Trace end / hit position', 'trace',
        '读取输出 pos（Vector）；未命中时通常是射线终点。无结果时为 null。',
        'Read output pos (Vector); usually the end point if there is no hit. Null when the field is missing.',
        'trace', 'TracePosition',return_type='Vector'),
    'trace_ent': _entry('获取射线命中的实体', 'Trace hit entity or null', 'trace',
        '安全读取 enthit；击中世界或无实体时不要假定一定是可操作的玩家实体。',
        'Read optional enthit safely. A world collision or missing entity is not necessarily a usable player handle.',
        'trace', 'TraceEntity',return_type='handle'),
    'trace_fraction': _entry('获取射线行进比例', 'Trace fraction', 'trace',
        '读取 fraction（0–1），没有追踪数据时返回 1.0。',
        'Read fraction (0–1); default to 1.0 for a missing trace result.',
        'trace', 'TraceFraction',return_type='float'),
    'trace_normal': _entry('获取碰撞表面法线', 'Trace surface normal', 'trace',
        '读取 plane_normal（Vector）；不存在时返回 null。',
        'Read plane_normal (Vector); returns null if unavailable.',
        'trace', 'TraceNormal',return_type='Vector'),
    'trace_startsolid': _entry('射线起点位于固体内部？', 'Trace starts in solid?', 'trace',
        '读取可选字段 startsolid，无该字段时返回 false。',
        'Read optional startsolid; false when omitted.',
        'trace', 'TraceStartSolid',return_type='bool'),
    'trace_field': _entry('读取任意 TraceLine 结果字段', 'Read any TraceLine output field', 'trace',
        '传入字段名（如 "surface_name"），不存在时返回 null。可用字段因引擎与检测结果而异。',
        'Pass a field name (e.g. "surface_name"); null if absent. Output availability depends on the engine and collision.',
        'trace', 'TraceField', (_param('field','"surface_name"','string','结果字段名','Output field name'),), 'unknown'),
    'entity_from_index': _entry(
        '根据实体索引获取实体句柄', 'Entity from entity index', 'env.weaponentid',
        '将实体索引（entindex）转换为可操作的实体句柄。适用于事件中的 weaponentid、entityid、propid、attackerentid 等实体索引字段；不是 userid，也不是武器类型 ID（weapon）。无效或已删除的实体可能返回 null，使用前请检查有效性。',
        'Convert an entity index (entindex) into an entity handle. Accepts weaponentid, entityid, propid, attackerentid and other entity-index fields in events; NOT userid or the weapon-type ID (weapon). Invalid or removed entities may return null; validate the handle before use.',
        'entities', 'EntIndexToHScript(entindex)', return_type='handle'),
    'player_from_userid': _entry('从 (UserID) 获取玩家实体', 'Player from (UserID)', 'env.userid',
        'GetPlayerFromUserID(userid)；无效 ID 可能返回 null',
        'GetPlayerFromUserID(userid); invalid IDs may return null', 'players', 'GetPlayerFromUserID',return_type='handle'),
    'player_from_event': _entry('从 (事件 env) 获取玩家实体', 'Player from (event env)', 'env',
        '读取 env.userid；仅用于包含 userid 字段的事件',
        'Read env.userid; use only with events that provide userid', 'players', 'GetPlayerFromUserID(env)',return_type='handle'),
    'active_weapon': _entry('获取 (玩家) 手上的武器', 'Active weapon of (player)', 'player',
        'player.GetActiveWeapon()；玩家必须是有效实体',
        'player.GetActiveWeapon(); the player handle must be valid', 'players', 'GetActiveWeapon',return_type='handle'),
    'safe_active_weapon': _entry('安全获取 (玩家) 当前武器', 'Active weapon or null (player)', 'player',
        '先检查玩家实体有效性；没有当前武器时返回 null',
        'Check player validity first; return null when no active weapon exists', 'players', 'SafeGetActiveWeapon',return_type='handle'),
    'weapon_classname': _entry('获取 (武器) 的 Classname', 'Classname of (weapon)', 'weapon',
        'weapon.GetClassname()；无效武器可能报错',
        'weapon.GetClassname(); an invalid weapon may raise a runtime error', 'players', 'GetClassname',return_type='string'),
    'weapon_clip': _entry('安全获取 (武器) 弹匣弹药数', 'Clip ammo or null (weapon)', 'weapon',
        '有效武器执行 Clip1()，否则返回 null',
        'Call Clip1() on a valid weapon; otherwise return null', 'players', 'Clip1',return_type='int'),
    'weapon_max_clip': _entry('安全获取 (武器) 最大弹匣容量', 'Maximum clip or null (weapon)', 'weapon',
        '有效武器执行 GetMaxClip1()，否则返回 null',
        'Call GetMaxClip1() on a valid weapon; otherwise return null', 'players', 'GetMaxClip1',return_type='int'),
    'player_name': _entry('安全获取 (玩家) 名称', 'Player name or null (player)', 'player',
        '有效玩家返回 GetPlayerName()，否则为 null',
        'Return GetPlayerName() for a valid player, or null', 'players', 'GetPlayerName',return_type='string'),
    'player_userid': _entry('安全获取 (玩家) UserID', 'UserID or null (player)', 'player',
        '有效玩家返回 GetPlayerUserId()，否则为 null',
        'Return GetPlayerUserId() for a valid player, or null', 'players', 'GetPlayerUserId',return_type='int'),
    'player_health': _entry('安全获取 (玩家) 实际生命值', 'Health or null (player)', 'player',
        '有效玩家读取 GetHealth()；不包含临时生命值',
        'Read GetHealth() on a valid player; excludes temporary health', 'players', 'GetHealth',return_type='int'),
    'player_button': _entry('检测 (玩家) 是否按住 (按键掩码)', 'Is (player) holding (button mask)?', 'player',
        '检查 GetButtonMask() 的指定位；例如 E=32，左键=1',
        'Test GetButtonMask() against a bit mask; e.g. use=32 and attack=1', 'players', 'GetButtonMask & mask',
        (_param('mask','32','int','按键掩码','Button mask'),), 'bool'),
    'inventory_slot': _entry('获取 (玩家) 的 (slot编号) 物品实体', 'Item in (player) slot (number)', 'player',
        'GetInvTable 安全读取 slot0–slot5；不存在或无效时返回 null；slot4 为药片/肾上腺素',
        'Safely read slot0–slot5 via GetInvTable; return null if missing or invalid; slot4 holds pills/adrenaline',
        'inventory', 'GetInvTable.slot', (_param('slot','4','int','槽位（0–5）','Slot (0–5)'),), 'handle'),
    'inventory_slot4': _entry('获取 (玩家) slot4 的药品实体', 'Pills / adrenaline in (player) slot4', 'player',
        '获取 slot4 的物品实体；消耗后可能返回 null',
        'Return the slot4 item entity, or null if empty/consumed', 'inventory', 'GetInvTable.slot4',return_type='handle'),
    'inventory_has_slot': _entry('检测 (玩家) 的 (slot编号) 是否有物品', 'Does (player) have an item in slot (number)?', 'player',
        '检查指定槽位是否存在有效实体，返回 bool',
        'Return true if the specified inventory slot holds a valid entity',
        'inventory', 'HasInventorySlot', (_param('slot','4','int','槽位（0–5）','Slot (0–5)'),), 'bool'),
    'inventory_slot_classname': _entry('获取 (玩家) (slot编号) 物品 Classname', 'Classname in (player) slot (number)', 'player',
        '读取指定槽位实体 Classname；不存在返回 null',
        'Return the classname of the slotted entity, or null if absent',
        'inventory', 'InventorySlotClassname', (_param('slot','4','int','槽位（0–5）','Slot (0–5)'),), 'string'),
    'inventory_table': _entry('获取 (玩家) 完整物品栏 Table', 'Inventory table of (player)', 'player',
        '通过 GetInvTable 创建并返回 Table；无效实体时返回 null',
        'Build an inventory table using GetInvTable; return null for invalid entities',
        'inventory', 'GetInvTable',return_type='table'),
    'inventory_has_classname': _entry('检测 (玩家) 是否携带指定 Classname', 'Does (player) carry (classname)?', 'player',
        '遍历 GetInvTable 的有效物品并比较完整 Classname（含 weapon_）',
        'Scan valid GetInvTable items for the full classname (including weapon_)',
        'inventory', 'HasInventoryClassname', (_param('classname','"weapon_pain_pills"','string','完整 Classname','Full classname'),), 'bool'),
    'entity_valid': _entry('判断 (实体) 是否有效', 'Is (entity) valid?', 'entity',
        '检查不为 null 且 IsValid() 返回 true',
        'Check that the entity is not null and IsValid() is true', 'entities', 'IsValid',return_type='bool'),
    'safe_classname': _entry('安全获取 (实体) Classname', 'Classname or null (entity)', 'entity',
        '实体无效时返回 null，避免直接 GetClassname() 报错',
        'Return null for invalid entities instead of calling GetClassname() on them',
        'entities', 'SafeGetClassname',return_type='string'),
    'find_classname': _entry('按 Classname 查找首个实体', 'Find first entity by classname', '"weapon_pain_pills"',
        '调用 Entities.FindByClassname(null, classname)；没有匹配则为 null',
        'Call Entities.FindByClassname(null, classname); return null if not found',
        'entities', 'FindByClassname',return_type='handle'),
    'find_name': _entry('按 targetname 查找首个实体', 'Find first entity by targetname', '"my_target"',
        '调用 Entities.FindByName(null, targetname)；没有匹配则为 null',
        'Call Entities.FindByName(null, targetname); return null if not found',
        'entities', 'FindByName',return_type='handle'),
    'remove_weapon_prefix': _entry('去掉 (字符串) 的 weapon_ 前缀', 'Remove weapon_ prefix from (text)', 'weapon.GetClassname()',
        '仅当字符串以 weapon_ 开头时去掉前缀',
        'Remove the weapon_ prefix only when it is present', 'entities', 'RemoveWeaponPrefix',return_type='string'),
    'entity_scope': _entry('安全获取 (实体) ScriptScope', 'ScriptScope or null (entity)', 'entity',
        '仅读取已存在的 GetScriptScope()，不自动创建 ScriptScope',
        'Read GetScriptScope() if available; do not implicitly create a scope',
        'scope', 'GetScriptScope',return_type='table'),
    'scope_has_member': _entry('检查 (实体) ScriptScope 是否含有 (键)', 'Has (entity) ScriptScope key (name)?', 'entity',
        '读取已有 ScriptScope，并用 rawin(key) 检查是否存在成员',
        'Check rawin(key) in an existing ScriptScope; do not create one',
        'scope', 'ScriptScope.rawin', (_param('key','"pills_used"','string','成员键','Member key'),), 'bool'),
    'scope_get_member': _entry('安全读取 (实体) ScriptScope 的 (成员键)', 'Read (entity) ScriptScope key (name)', 'entity',
        '已存在时读取 ScriptScope 成员；缺失时返回 null',
        'Read an existing ScriptScope member or return null if it is missing',
        'scope', 'ScriptScope.member', (_param('key','"pills_used"','string','成员键','Member key'),), 'unknown'),
}


def utility_caption(info, language='en', style='general'):
    return info['professional'] if style == 'professional' else info['en' if language=='en' else 'zh']


def create_utility_args(operation):
    info=UTILITY_BLOCKS[operation]
    params=info.get('params',[])
    args={'operation':operation,'value':info['default'],'return_type':info['return_type']}
    if params:
        args['parameters']=[p['default'] for p in params]
        args['parameter_specs']=[dict(name=p['name'],type=p['type'],zh=p['zh'],en=p['en']) for p in params]
    return args


def change_utility_operation(block, operation):
    if operation not in UTILITY_BLOCKS:raise ValueError('Unknown utility operation: '+str(operation))
    old=UTILITY_BLOCKS.get(block.args.get('operation'),{})
    old_inputs=list(block.args.get('parameters',[]))
    old_names=[s.get('name') for s in block.args.get('parameter_specs',[])]
    value=block.args.get('value',old.get('default'))
    new=create_utility_args(operation)
    if value is not None and value != old.get('default'):
        new['value']=value
    for i,spec in enumerate(new.get('parameter_specs',[])):
        if spec['name'] in old_names:
            index=old_names.index(spec['name'])
            if index<len(old_inputs):new['parameters'][i]=old_inputs[index]
    block.args.clear();block.args.update(new)


def _helper(name, *values):
    return '::L4VP_Utils.' + name + '(' + ', '.join(values) + ')'


def emit_utility(args, expression):
    operation = args.get('operation', 'player_from_userid')
    if operation not in UTILITY_BLOCKS:
        raise ValueError('Unknown utility operation: ' + str(operation))
    info = UTILITY_BLOCKS[operation]
    value = expression(args.get('value', info['default']))
    provided = list(args.get('parameters', []))
    extras = [expression(provided[i] if i < len(provided) else p['default'])
              for i, p in enumerate(info.get('params', []))]
    direct = {
        'entity_from_index': lambda: 'EntIndexToHScript(' + value + ')',
        'player_from_userid': lambda: 'GetPlayerFromUserID(' + value + ')',
        'player_from_event': lambda: 'GetPlayerFromUserID((' + value + ').userid)',
        'active_weapon': lambda: '(' + value + ').GetActiveWeapon()',
        'weapon_classname': lambda: '(' + value + ').GetClassname()',
        'find_classname': lambda: 'Entities.FindByClassname(null, ' + value + ')',
        'find_name': lambda: 'Entities.FindByName(null, ' + value + ')',
    }
    if operation in direct:
        return direct[operation]()
    helpers = {
        'remove_weapon_prefix': 'RemoveWeaponPrefix',
        'entity_valid': 'Valid',
        'safe_active_weapon': 'SafeActiveWeapon',
        'safe_classname': 'SafeClassname',
        'weapon_clip': 'WeaponClip',
        'weapon_max_clip': 'WeaponMaxClip',
        'player_name': 'PlayerName',
        'player_userid': 'PlayerUserId',
        'player_health': 'PlayerHealth',
        'entity_scope': 'EntityScope',
        'player_button': 'PlayerButton',
        'inventory_slot': 'InventorySlot',
        'inventory_slot4': 'InventorySlot',
        'inventory_has_slot': 'InventoryHasSlot',
        'inventory_slot_classname': 'InventorySlotClassname',
        'inventory_table': 'InventoryTable',
        'inventory_has_classname': 'InventoryHasClassname',
        'scope_has_member': 'ScopeHasMember',
        'scope_get_member': 'ScopeGetMember',
        'trace_ray': 'TraceRay',
        'trace_hit': 'TraceHit',
        'trace_pos': 'TracePosition',
        'trace_ent': 'TraceEntity',
        'trace_fraction': 'TraceFraction',
        'trace_normal': 'TraceNormal',
        'trace_startsolid': 'TraceStartSolid',
        'trace_field': 'TraceField',
    }
    if operation not in helpers:
        raise ValueError('Unknown utility operation: ' + str(operation))
    if operation == 'inventory_slot4':
        return _helper('InventorySlot', value, '4')
    return _helper(helpers[operation], value, *extras)
