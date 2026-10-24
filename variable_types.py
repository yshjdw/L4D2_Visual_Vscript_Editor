"""Type changes for variable declarations, independent of the Qt widget lifetime.

The two data containers are UI types: Table={} and Set=[].  Each one has a
separate data-definition workspace; switching to a scalar must not silently
emit a stale linked table initializer.
"""
from __future__ import annotations

from .data_definitions import linked_definition, is_script_scope

VALID_TYPES = ('普通', 'Table', 'Set', 'ScriptScope')
DEFAULT_VALUES = {'普通': '0', 'Table': '{}', 'Set': '[]', 'ScriptScope': 'ent'}


def change_variable_type(document, block, new_type):
    if block.kind != 'var':
        raise ValueError('只有变量声明积木可以切换变量类型')
    if new_type not in VALID_TYPES:
        raise ValueError('未知的变量类型：' + str(new_type))
    old_type = block.args.get('container_type', '普通')
    if old_type == new_type:
        return False
    cache = block.args.setdefault('_type_value_cache', {})
    was_dynamic = is_script_scope(block)
    cache[old_type] = block.args.get('value', DEFAULT_VALUES.get(old_type, '0'))
    # Only the active value is authoritative. Historical per-type values are
    # retained for navigation, never silently applied over an edited value.
    new_value = cache.get(new_type, DEFAULT_VALUES[new_type])
    if new_type == 'Table' and was_dynamic:
        new_value = block.args.get('value', new_value)
    elif new_type in ('Table','Set') and (not isinstance(new_value,str) or not new_value.strip().startswith('{' if new_type=='Table' else '[')):
        new_value = DEFAULT_VALUES[new_type]
    elif new_type == '普通' and (new_value is None or new_value == ''):
        new_value = DEFAULT_VALUES[new_type]
    block.args['container_type'] = new_type
    block.args['value'] = new_value
    if new_type == 'ScriptScope' and isinstance(new_value, str) and not new_value.strip():
        new_value = 'ent'
        block.args['value'] = new_value
    if document is not None:
        section = linked_definition(document, block.id)
        if section is not None and new_type in ('Table', 'Set', 'ScriptScope'):
            section.args['container'] = 'Table' if new_type == 'ScriptScope' else new_type
            # A previous raw literal of the opposite container has no meaning
            # for the new shape. Existing child definition blocks are kept.
            section.args['fallback_expression'] = ''
    return True


def sync_active_variable_value(block):
    """Keep the active type's saved editor state consistent after a socket edit."""
    if block.kind != 'var':
        return
    cache=block.args.setdefault('_type_value_cache', {})
    cache[block.args.get('container_type','普通')]=block.args.get('value')


def reconcile_variable_cache(block):
    """On load, prefer the current expression to stale copies in type cache."""
    if block.kind != 'var':
        return
    sync_active_variable_value(block)
