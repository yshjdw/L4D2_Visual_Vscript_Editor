"""Documented API display, with explicit distinction between source descriptions and signature-only metadata."""
from .event_metadata import EVENT_FIELDS
from .official_docs import official_functions, official_events

METHOD_EXPLANATIONS = {
 ('CBaseEntity','GetOrigin'): '获取实体的世界坐标，返回 Vector。',
 ('CBaseEntity','SetOrigin'): '把实体移动到指定 Vector 坐标。',
 ('CBaseEntity','GetHealth'): '读取实体当前生命值。',
 ('CBaseEntity','SetHealth'): '设置实体当前生命值。',
 ('CEntities','FindByClassname'): '按 classname 查找实体；previous 传 null 开始查找，继续查找时传入上一实体。',
 ('CEntities','FindByName'): '按 targetname 查找实体；previous 传 null 开始查找。',
}
PARAMETER_HINTS = {
 'previous': '上一轮找到的实体；首次查找传 null。',
 'classname': '实体 classname，例如 player、infected。',
 'targetname': '实体名称（targetname）。',
 'origin': 'Vector 世界坐标。',
 'distance': '距离上限（游戏单位）。',
 'userid': '事件中的玩家 UserID，不等同于实体句柄。',
}
EVENT_EXPLANATIONS = {
 'player_death': '玩家或感染者死亡事件；检查 userid/entityid 等字段以区分实体。',
 'player_hurt': '玩家受到伤害事件，字段包含攻击者与伤害数值。',
 'ability_use': '特殊感染者使用能力时触发；部分感染者存在触发例外。',
 'round_start': '回合开始时触发。',
 'player_spawn': '玩家实体生成时触发。',
}

def english_source_label(value):
    """Translate catalog provenance labels, not document text or API symbols."""
    source=str(value or 'not recorded')
    if source=='用户提供的 Valve Script Functions 页面转存':
        return 'User-supplied copy of Valve Script Functions documentation'
    if source=='用户提供的 L4D2 Events 页面转存 event(2).md':
        return 'User-supplied L4D2 Events documentation (event(2).md)'
    return source


def method_tooltip(record):
    from .display_profile import current_profile, method_caption
    if current_profile().language == 'en':
        owner=record.get('owner','');name=record.get('name','')
        param=record.get('parameters','') or ''
        doc=official_functions().get(owner+'.'+name,{})
        parts=[f'{owner}.{name}({param}) → {record.get("returns","unknown")}']
        if current_profile().style=='general':parts.append('Plain-language: '+method_caption(name,current_profile(),owner))
        if doc.get('description'):
            parts.append('Source description: '+doc['description'])
        else:
            parts.append('Only a signature is documented here; the precise behavior is not verified.')
        if owner in ('Globals','Global') and name == 'IncludeScript':
            parts.append('Editor default: scope = getroottable(). Native scope = null uses the current scope (this); you can change it.')
        if doc.get('signature'):parts.append('Signature: '+doc['signature'])
        for spec in doc.get('parameters',[]):
            parts.append('Argument '+spec['name']+': '+spec['type'])
        parts.append('Source: '+english_source_label(record.get('source')))
        parts.append('Documentation: https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions')
        return '\n'.join(parts)
    owner=record.get('owner','');name=record.get('name','')
    param=record.get('parameters','') or ''
    doc=official_functions().get(owner+'.'+name, {})
    explain=doc.get('description') or METHOD_EXPLANATIONS.get((owner,name))
    parts=[f'{owner}.{name}({param}) → {record.get("returns","unknown")}']
    from .display_profile import current_profile, method_caption
    if current_profile().style == 'general':
        parts.append('易懂说法：'+method_caption(name,current_profile(),owner))
        if not doc.get('description'):
            parts.append('注意：参考资料未提供完整文字说明；易懂说法仅由函数名称概括。')
    parts.append(('说明（文档原文）：'+explain) if explain else '说明：当前来源仅提供函数签名；未收录官方文字说明，不推测具体行为。')
    if owner in ('Globals','Global') and name == 'IncludeScript':
        parts.append('编辑器默认：scope = getroottable()。原生默认 null 表示当前作用域 this；可以手动修改。')
    if doc.get('signature'):parts.append('文档签名：'+doc['signature'])
    for spec in doc.get('parameters',[]):
        parts.append('参数 '+spec['name']+'：'+spec['type'])
    if not doc:
     for token in param.split(','):
        token=token.strip()
        if not token:continue
        arg=token.split(':',1)[0].strip()
        hint=PARAMETER_HINTS.get(arg,'参数类型/名称详见上方函数签名；未收录单独说明。')
        parts.append(f'参数 {arg}：{hint}')
    parts.append('来源：'+record.get('source','未记录'))
    parts.append('完整文档：https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions')
    return '\n'.join(parts)

def event_tooltip(record):
    from .display_profile import current_profile,event_caption,category_caption
    if current_profile().language == 'en':
        from .event_metadata import event_group
        name=record['name'];doc=official_events().get(name,{})
        parts=['OnGameEvent_'+name+'(env)', 'Category: '+category_caption(event_group(name))]
        if current_profile().style=='general':parts.append('Plain-language: '+event_caption(name))
        parts.append('Description: '+(doc.get('description') or 'No detailed description in the supplied event documentation.'))
        parts.append('env is a Squirrel Table containing event data.')
        if doc:
            for field in doc.get('fields',[]):
                parts.append('env.'+field['name']+' ('+field['type']+'): '+(field.get('description') or 'Not documented'))
        elif record.get('fields'):
            parts.append('Catalog fields: '+str(record['fields']))
        else:
            parts.append('Event fields not covered by the offline source.')
        parts.append('Source: '+english_source_label(record.get('source')))
        return '\n'.join(parts)
    name=record['name']; fields=record.get('fields','')
    from .event_metadata import event_group
    schema=EVENT_FIELDS.get(name,[])
    parts=['OnGameEvent_'+name+'(env)', '分类：'+event_group(name)]
    from .display_profile import current_profile, event_caption
    if current_profile().style == 'general':
        parts.append('易懂说法：'+event_caption(name,current_profile()))
    doc=official_events().get(name,{})
    explain=doc.get('description') or EVENT_EXPLANATIONS.get(name)
    parts.append('说明：'+explain if explain else '说明：当前参考没有完整文字说明；事件语义需要查阅来源，不做推测。')
    parts.append('env 是事件 Table。')
    if doc:
        for field in doc['fields']:
            parts.append('env.'+field['name']+' ('+field['type']+'): '+(field['description'] or '文档未说明'))
    elif schema:parts.append('已核对字段：'+', '.join(schema))
    elif fields:parts.append('数据源字段：'+str(fields))
    else:parts.append('事件字段：当前离线资料未收录。')
    parts.append('来源：'+record.get('source','未记录'))
    parts.append('事件文档：用户提供的 event.md（L4D2 事件条目转存）')
    return '\n'.join(parts)
