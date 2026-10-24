"""Documented CEntities iteration strategies for Entity For (no GUI dependency).

The one-shot nearest methods are intentionally omitted: they do not
iterate multiple matching entities and therefore are not loop strategies.
"""
from __future__ import annotations

from .models import Block

# Keys remain identical to the CEntities methods documented in Valve's
# Left 4 Dead 2 Script Functions reference (except AllEntities, an IDE helper).
ENTITY_SEARCH_MODES = {
    'FindByClassname': {
        'label': '按实体 classname · FindByClassname',
        'fields': ('filter',), 'hint': '例如 "player"、"infected"、"weapon_*"。支持通配符 *。',
    },
    'FindByName': {
        'label': '按 targetname · FindByName',
        'fields': ('filter',), 'hint': '实体的 targetname，非 classname。',
    },
    'FindByModel': {
        'label': '按模型路径 · FindByModel',
        'fields': ('filter',), 'hint': '实体 model keyvalue 的完整模型路径。',
    },
    'FindByTarget': {
        'label': '按目标键 · FindByTarget',
        'fields': ('filter',), 'hint': '按照实体的 target 键查找，不等同于 targetname。',
    },
    'FindByClassnameWithin': {
        'label': '按 classname + 范围 · FindByClassnameWithin',
        'fields': ('filter','origin','radius'), 'hint': '按 classname 筛选，并限制在指定中心与半径内。',
    },
    'FindByNameWithin': {
        'label': '按 targetname + 范围 · FindByNameWithin',
        'fields': ('filter','origin','radius'), 'hint': '按 targetname 筛选，并限制在指定中心与半径内。',
    },
    'FindInSphere': {
        'label': '按球形范围 · FindInSphere',
        'fields': ('origin','radius'), 'hint': '搜索指定中心和半径内的所有实体，不附加名称过滤。',
    },
    'AllEntities': {
        'label': '遍历全部实体 · First / Next',
        'fields': (), 'hint': '使用 Entities.First() 和 Entities.Next() 遍历实体。',
    },
}

ENTITY_FIELD_DEFAULTS = {'filter':'"player"','origin':'Vector(0, 0, 0)','radius':'512'}
ENTITY_FIELD_LABELS = {'filter':'实体名 / 路径','origin':'查找中心 (Vector)','radius':'查找半径 (单位 u)'}


def search_fields(method):
    return ENTITY_SEARCH_MODES[method]['fields']


def normalize_entity_search(block: Block, method: str):
    """Switch methods without destroying earlier user-entered values."""
    if method not in ENTITY_SEARCH_MODES:
        raise ValueError('未支持的实体查找方式：' + str(method))
    block.args['search'] = method
    for key in search_fields(method):
        if key not in block.args:
            block.args[key] = ENTITY_FIELD_DEFAULTS[key]
    return block


def entity_for_lines(block: Block, depth: int, expression, require_name, emit_blocks, ctx='function'):
    """Compile an entity loop; the prior-entity argument is advanced every pass."""
    a = block.args
    method = str(a.get('search','FindByClassname'))
    if method not in ENTITY_SEARCH_MODES:
        raise ValueError('未支持的实体查找方式：' + method)
    name = require_name(a.get('variable','entity'))
    pad = '    ' * depth
    body = emit_blocks(block.branches.get('body',[]), depth+1, ctx)
    if method == 'AllEntities':
        # A for statement guarantees Next even after a `continue`.
        header = f'for (local {name} = Entities.First(); {name} != null; {name} = Entities.Next({name}))'
        return [pad+header, pad+'{', *body, pad+'}']
    params = [name]
    for key in search_fields(method):
        source = a.get(key, ENTITY_FIELD_DEFAULTS[key])
        val = expression(source)
        if not str(val).strip() or val == 'null':
            raise ValueError(f'查找方式 {method} 的 {key} 参数不能为空')
        if key == 'radius':
            try:
                if float(val) < 0:
                    raise ValueError('实体查找半径不能为负数')
            except (TypeError,ValueError) as exc:
                if str(exc) == '实体查找半径不能为负数':raise
        params.append(val)
    call = f'Entities.{method}(' + ', '.join(params) + ')'
    return [pad+f'local {name} = null;', pad+f'while (({name} = {call}) != null)', pad+'{', *body, pad+'}']
