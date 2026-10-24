"""UI group hints and conservative documented field suggestions.
Unknown event fields deliberately remain unrestricted dynamic table members.
"""
from .official_docs import event_fields as _documented_fields, event_field_help

LEGACY_EVENT_FIELDS = {
 'ability_use': ['userid','ability','context'],
 'ability_out_of_range': ['userid','ability'],
 'weapon_fire_on_empty': ['userid','weapon','count'],
 'player_use': ['userid','targetid'],
 'friendly_fire': ['attacker','victim','guilty','type'],
 'revive_begin': ['userid','subject'],
 'revive_end': ['userid','subject','ledge_hang'],
 'charger_carry_start': ['userid','victim'],
 'charger_carry_end': ['userid','victim'],
 'player_hurt': ['userid','attacker','health','armor','dmg_health','dmg_armor','hitgroup','type'],
 'player_death': ['userid','entityid','attacker','attackername','attackerentid','weapon','headshot','type'],
 'player_spawn': ['userid'], 'player_bot_replace':['player','bot'],
 'bot_player_replace':['player','bot'], 'weapon_fire':['userid','weapon','weaponid','count'],
 'weapon_reload':['userid','manual'], 'item_pickup':['userid','item'],
 'ammo_pickup':['userid'], 'heal_success':['userid','subject','health_restored'],
 'revive_success':['userid','subject','lastlife','ledge_hang'], 'infected_death':['attacker','infected_id','weapon_id'],
 'round_start':[], 'round_end':['winner','reason','message'],
 'tank_spawn':['userid'], 'witch_spawn':['witchid'],
}

# Use the supplied documented schema where available; preserve conservative legacy suggestions only for missing entries.
EVENT_FIELDS = dict(LEGACY_EVENT_FIELDS)
from .official_docs import official_events
for _event_name, _event_doc in official_events().items():
    EVENT_FIELDS[_event_name]=[field['name'] for field in _event_doc['fields']]


def event_group(name, original=''):
 n=name.lower()
 if any(t in n for t in ('hurt','damage','death','killed','headshot','hitgroup')):return '伤害与死亡'
 if any(t in n for t in ('weapon','ammo','item','pickup','grenade','molotov','pipe_bomb','defib','heal','pills','adrenaline')):return '物品、武器与补给'
 if any(t in n for t in ('tank','witch','boomer','smoker','hunter','jockey','charger','spitter','infected','ability','tongue','vomit')):return '特殊感染者与感染者'
 if any(t in n for t in ('survivor','player','bot','revive','incap','ledge','friendly_fire')):return '幸存者与玩家'
 if any(t in n for t in ('round','map','finale','mission','scavenge','versus','game','difficulty','flow','chapter')):return '关卡与游戏流程'
 return '其他游戏事件'

def event_tip(name, fields=None):
    from .display_profile import current_profile
    if current_profile().language=='en':
        fs=fields if fields is not None else EVENT_FIELDS.get(name,[])
        from .official_docs import official_events
        doc=official_events().get(name,{})
        lines=['OnGameEvent_'+name+'(env)',
               'env is a Squirrel table. Blocks below run when this event fires.']
        if doc.get('description'):lines.append(doc['description'][:1200])
        if fs:lines.append('Known fields: '+', '.join(fs))
        else:lines.append('Check the event documentation for its fields.')
        return '\n'.join(lines)
    fs=fields if fields is not None else EVENT_FIELDS.get(name, [])
    suffix=('\n已知字段：'+', '.join(fs)) if fs else '\n参数 env 是 table；该事件的字段请根据实际事件资料核对。'
    from .official_docs import official_events
    doc=official_events().get(name, {})
    description=doc.get('description','')
    detail='\n'+description[:1200] if description else ''
    return 'OnGameEvent_'+name+'(env)\nenv 是事件 table。当事件发生时执行下方积木。'+detail+suffix
