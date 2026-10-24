"""Discover and reuse ScriptScope members without relying on local alias names."""
from .models import Block
from .data_definitions import find_source, is_script_scope
from .codegen import require_name


def scope_binding(document, section):
    if section is None:
        return None
    source = find_source(document, section)
    if not source or not is_script_scope(source[1]):
        return None
    value = source[1].args.get('value', '')
    if isinstance(value, dict):
        from .codegen import expression
        return expression(value).strip()
    return str(value).strip()


def member_sources(document, destination=None):
    """List all defined ScriptScope members in the current script document.

    Unlike previous versions, no equality test is performed on the entity
    expression or local variable name. Reference-only imported members are
    excluded so the catalog lists declarations rather than their copies.
    """
    for section in document.sections:
        if section.kind != 'data' or scope_binding(document, section) is None:
            continue
        for block in section.blocks:
            if block.kind == 'var' and block.args.get('init_mode') != 'reference':
                yield section, block


def _source_member(document, payload):
    source = next((s for s in document.sections
                   if s.id == payload.get('source_section_id')), None)
    if source is None or scope_binding(document, source) is None:
        raise ValueError('来源 ScriptScope 已不存在。')
    member = next((b for b in source.blocks if b.id == payload.get('member_id')
                   and b.kind == 'var' and b.args.get('init_mode') != 'reference'), None)
    if member is None:
        raise ValueError('来源 ScriptScope 成员已经不存在。')
    # Do not trust the displayed name in a drag payload: a member may have
    # been renamed after the palette was last refreshed.
    name = require_name(str(member.args.get('name', '')))
    return source, member, name


def copy_scope_reference(document, payload, destination):
    source, member, name = _source_member(document, payload)
    if destination.kind != 'data' or scope_binding(document, destination) is None:
        raise ValueError('目标不是 ScriptScope 的 Table 数据编辑分区。')
    if destination.id == source.id:
        raise ValueError('不能把成员引用复制到定义它的同一个数据分区。')
    if any(b.kind == 'var' and b.args.get('name') == name for b in destination.blocks):
        raise ValueError('目标 ScriptScope 已存在同名成员。')
    # The destination always uses its own ScriptScope handle. This is a
    # reference-only schema entry; it does NOT initialize that member at run time.
    return Block('var', {'name': name, 'container_type': '普通', 'value': 'null',
                         'scope': 'auto', 'init_mode': 'reference',
                         'reference_source_id': member.id,
                         'reference_source_section_id': source.id})


def scope_member_candidates(document, payload, destination, destination_block_id=None):
    """Return possible target-local access paths for a catalog member.

    In a Data workspace the target ScriptScope is explicit. In ordinary code
    a ScriptScope variable must already be declared in the destination; never
    leak the local alias used in a different event/function.
    """
    try:
        _, _, name = _source_member(document, payload)
    except (ValueError, KeyError):
        return []
    if destination.kind == 'data':
        if scope_binding(document, destination) is None:
            return []
        from .variable_paths import reference_for_symbol
        base = reference_for_symbol(document, destination.args.get('source_id'))
        return [base + '.' + name] if base else []
    from .scope_visibility import visible_local
    def all_blocks(items):
        for block in items:
            yield block
            for branch in block.branches.values():
                yield from all_blocks(branch)
    candidates = [b for b in all_blocks(destination.blocks) if is_script_scope(b)
                  and (destination_block_id is None
                       or visible_local(destination, b.id, destination_block_id))]
    result = []
    for b in candidates:
        alias = str(b.args.get('name', '')).strip()
        try:
            qualified = require_name(alias) + '.' + name
        except ValueError:
            continue
        if qualified not in result:
            result.append(qualified)
    return result


def scope_member_path(document, payload, destination, destination_block_id=None):
    paths = scope_member_candidates(document, payload, destination, destination_block_id)
    return paths[0] if len(paths) == 1 else None
