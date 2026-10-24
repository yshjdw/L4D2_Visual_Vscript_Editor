"""Verbatim API/event notes extracted from user-supplied Valve/AlliedModders page copies."""
import json
from functools import lru_cache
from pathlib import Path
_RESOURCE=Path(__file__).resolve().parent.parent/'resources'
@lru_cache(maxsize=1)
def official_functions():
    with (_RESOURCE/'official_functions.json').open(encoding='utf-8') as inp:return json.load(inp)
@lru_cache(maxsize=1)
def official_events():
    with (_RESOURCE/'official_events.json').open(encoding='utf-8') as inp:return json.load(inp)
def event_fields(name):
    doc=official_events().get(name)
    return [field['name'] for field in doc['fields']] if doc is not None else None
@lru_cache(maxsize=1)
def event_field_translations():
    with (_RESOURCE/'event_field_help_zh.json').open(encoding='utf-8') as inp:
        return json.load(inp)


def event_field_help(name, field, language=None):
    """Event-specific bilingual field help; unknown fields are never invented."""
    from .display_profile import current_profile
    language=language or current_profile().language
    item=event_field_translations().get(name,{}).get(field)
    if item is None:
        return (f'{name}.env.{field} — '+
                ('No such field is documented for this event.' if language=='en'
                 else '该事件文档没有收录这个成员。'))
    english=item['en'].strip()
    chinese=item['zh'].strip()
    typ=item['type']
    status=item['source']
    if language=='en':
        return (f'{name}.env.{field} ({typ})\n'
                +(english if english else 'Inferred from field name: '+item.get('en_inferred','')+'\nThe source document does not explain this field.'))
    if status=='inferred':
        return (f'{name}.env.{field} ({typ})\n'
                +'根据字段名推断：'+chinese+'\n原始文档未说明该字段的具体含义。')
    if status=='source_inferred':
        return (f'{name}.env.{field} ({typ})\n'
                +'字段名推断：'+chinese+'\nOriginal: '+english)
    return f'{name}.env.{field} ({typ})\n{chinese}\nOriginal: {english}'
