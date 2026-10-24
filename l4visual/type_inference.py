"""Conservative type hints for NetProp's first slot. Not a runtime type oracle."""
import re


def infer_sendtable(value, document=None, seen=None):
    if isinstance(value,dict):
        if value.get('kind')=='variable':value=value.get('value','')
        else:return None
    value=str(value).strip()
    if re.search(r'\bGetActiveWeapon\s*\(',value):return 'DT_TerrorWeapon'
    if re.search(r'Entities\.FindByClassname\s*\([^,]*,\s*[\'\"]player[\'\"]',value):return 'DT_TerrorPlayer'
    if re.search(r'Entities\.FindByClassname\s*\([^,]*,\s*[\'\"]weapon_',value):return 'DT_TerrorWeapon'
    if not re.fullmatch(r'[A-Za-z_]\w*',value):return None
    if document:
        seen=seen or set()
        if value in seen:return None
        seen.add(value)
        for section in document.sections:
            for block in section.blocks:
                if block.kind=='entity_for' and block.args.get('variable')==value:
                    filter_expr=str(block.args.get('filter',''))
                    if '"player"' in filter_expr or "'player'" in filter_expr:return 'DT_TerrorPlayer'
                if block.kind=='var' and block.args.get('name')==value:
                    resolved=infer_sendtable(block.args.get('value'),document,seen)
                    if resolved:return resolved
                if block.kind=='method' and block.args.get('output')==value and block.args.get('method')=='GetActiveWeapon':
                    return 'DT_TerrorWeapon'
    # Familiar variable names are suggestions, not hard guarantees.
    if value in ('player','survivor','p'):return 'DT_TerrorPlayer'
    if value in ('weapon','gun','activeWeapon'):return 'DT_TerrorWeapon'
    return None
