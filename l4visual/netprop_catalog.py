"""Source-backed L4D2 NetProp catalog, separate from Squirrel Table members."""
from functools import lru_cache
from pathlib import Path
import json

@lru_cache(maxsize=1)
def load_netprops():
    path=Path(__file__).resolve().parent.parent/'resources'/'netprops_2024.json'
    return json.loads(path.read_text(encoding='utf-8'))['classes']

def list_classes(query=''):
    return [name for name in sorted(load_netprops()) if query.casefold() in name.casefold()]

# SendTable groups with offset 0 describe the structure of the networked
# object; they are not necessarily parts of the VScript netprop key. Keep both
# names: the full documentation path is used in the selector, and the netprop
# runtime name is used in emitted Squirrel.
_SENDTABLE_GROUPS = ('LocalWeaponData.', 'LocalActiveWeaponData.', 'localdata.',
                     'bcc_localdata.', 'terrorlocaldata.', 'baseclass.')

def runtime_property_name(name):
    result=str(name)
    for prefix in _SENDTABLE_GROUPS:
        if result.startswith(prefix):
            return result[len(prefix):]
    return result

def resolve_property(class_name, property_name):
    """Resolve both current and legacy (documentation-prefixed) saved names."""
    for row in list_properties(class_name):
        if property_name in (row['name'],row.get('document_path')):
            return row
    return None

def list_properties(class_name,query=''):
    classes=load_netprops()
    by_dt={c['sendtable']:name for name,c in classes.items()}
    collected={};seen=set();name=class_name
    while name and name not in seen:
        seen.add(name)
        row=classes.get(name,{})
        for original in row.get('props',[]):
            path=original['name']
            prop={**original,'document_path':path,'name':runtime_property_name(path),
                  'declaring_class':name}
            if query.casefold() in (prop['name']+' '+path).casefold():
                collected.setdefault(prop['name'],prop)
        name=by_dt.get(row.get('base_type'))
    return sorted(collected.values(), key=lambda p:p['name'].casefold())

def api_type(prop):
    kind=prop['type'].lower()
    if kind=='float':return 'Float'
    if kind=='vector':return 'Vector'
    if kind=='string':return 'String'
    if kind=='array':
        element=str(prop.get('element_type','integer')).lower()
        return 'Float' if element=='float' else 'Vector' if element=='vector' else 'String' if element=='string' else 'Int'
    return 'Int'
