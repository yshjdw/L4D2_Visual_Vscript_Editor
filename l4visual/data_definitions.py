"""Links complex variable declarations to restricted definition sections.

A definition section is an editor-only representation of a Squirrel table/array
initializer. It is NOT a separate top-level declaration when bound to a variable.
Links use persistent block/section IDs instead of matching display names.
"""
from __future__ import annotations
from .models import Section, ScriptDocument, Block

CONTAINER_KINDS = {'Table', 'Set'}  # UI "Set" == Squirrel array []
DATA_BLOCKS = frozenset(('var', 'assign', 'member', 'method', 'call', 'netprop', 'array_op'))



def split_initializer(source: str):
    """Split top-level commas, respecting quotes and nested brackets."""
    text = source.strip()
    pieces = []
    start = 0
    depth = 0
    quote = None
    escape = False
    for i, char in enumerate(text):
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char in '[{(':
            depth += 1
        elif char in ']})':
            depth -= 1
        elif char == ',' and depth == 0:
            piece = text[start:i].strip()
            if piece:pieces.append(piece)
            start = i + 1
    piece = text[start:].strip()
    if piece:pieces.append(piece)
    return pieces


def parse_simple_initializer(value, dtype):
    """Extract fields of a literal array/table. Never evaluates Squirrel code.

    Returns None for unknown syntaxes, which must be preserved as a fallback.
    """
    if not isinstance(value, str):return None
    text = value.strip()
    if dtype=='Set' and text.startswith('[') and text.endswith(']'):
        pieces=split_initializer(text[1:-1])
        return [Block('var',{'name':str(i),'value':item,'container_type':'普通'}) for i,item in enumerate(pieces)]
    if dtype=='Table' and text.startswith('{') and text.endswith('}'):
        pieces=split_initializer(text[1:-1])
        result=[]
        for item in pieces:
            if '=' not in item:return None
            name,expr=item.split('=',1)
            name=name.strip()
            if not name.isidentifier() or expr.lstrip().startswith('='):return None
            result.append(Block('var',{'name':name,'value':expr.strip(),'container_type':'普通'}))
        return result
    return None

def is_script_scope(block: Block):
    """ScriptScope is an entity-backed Table, never a Table literal."""
    if block.kind != 'var':
        return False
    if block.args.get('container_type') == 'ScriptScope':
        return True
    value = block.args.get('value', '')
    if isinstance(value, dict) and value.get('kind') == 'embedded_block':
        method = value.get('block', {}).get('args', {}).get('method')
        return method == 'GetScriptScope'
    if isinstance(value, str):
        import re
        return bool(re.fullmatch(r'\s*[A-Za-z_][\w.]*(?:\[[^\]]+\])?\.GetScriptScope\(\s*\)\s*', value))
    return False


def script_scope_entity(block: Block):
    if block.args.get('container_type') == 'ScriptScope':
        return block.args.get('value', 'ent')
    value = block.args.get('value', '')
    if isinstance(value, str) and value.strip().endswith('.GetScriptScope()'):
        return value.strip()[:-len('.GetScriptScope()')]
    if isinstance(value, dict) and value.get('kind') == 'embedded_block':
        return value.get('block', {}).get('args', {}).get('target', 'ent')
    return None


def dynamic_table_assignments(document, section, target, render):
    """Generate slots after acquiring a live ScriptScope. Nested tables remain editable."""
    from .codegen import require_name, expression
    result = []
    for block in section.blocks:
        if block.kind != 'var':
            continue
        name = require_name(block.args.get('name', ''))
        child = linked_definition(document, block.id, section.id)
        value = render(document, child) if child else block.args.get('value', 'null')
        member = target + '.' + name
        mode = block.args.get('init_mode', 'once')
        if mode == 'reference':
            continue
        if mode == 'once':
            result.append('if (!' + target + '.rawin(' + expression({'kind':'literal','value':name}) + ')) ' + member + ' <- ' + expression(value) + ';')
        elif mode == 'overwrite':
            result.append(member + ' <- ' + expression(value) + ';')
        elif mode == 'existing':
            result.append('if (' + target + '.rawin(' + expression({'kind':'literal','value':name}) + ')) ' + member + ' = ' + expression(value) + ';')
        else:
            raise ValueError('未知 ScriptScope 成员初始化方式：' + str(mode))
    return result


def container_kind(block: Block):
    if block.kind != 'var':
        return None
    if is_script_scope(block):
        return 'Table'
    declared = block.args.get('container_type', '')
    if declared in CONTAINER_KINDS:
        return declared
    if declared == '普通':
        return None
    value = block.args.get('value', '')
    if isinstance(value, dict):
        return {'table': 'Table', 'array': 'Set'}.get(value.get('kind'))
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed.startswith('{') and trimmed.endswith('}'):
            return 'Table'
        if trimmed.startswith('[') and trimmed.endswith(']'):
            return 'Set'
    return None


def linked_definition(document: ScriptDocument, block_id: str, parent_id=None):
    for section in document.sections:
        if section.kind != 'data' or section.args.get('source_id') != block_id:
            continue
        if parent_id is None or section.args.get('parent_section_id', '') == parent_id:
            return section
    return None


def create_definition(document: ScriptDocument, parent: Section, block: Block):
    if parent.kind not in ('namespace', 'init', 'data', 'function', 'think', 'events'):
        raise ValueError('当前区域不支持创建复杂变量定义工作区')
    if block.kind != 'var':
        raise ValueError('数据定义分区只能绑定复杂变量声明')
    dtype = container_kind(block)
    if not dtype:
        raise ValueError('请先将变量类型设为 Table 或 Set')
    exists = linked_definition(document, block.id)
    if exists:
        return exists
    if parent.kind == 'namespace':
        owner, parent_id = parent.name, ''
    elif parent.kind == 'data':
        owner = parent.args.get('owner', '')
        parent_id = parent.id
    else:
        owner, parent_id = '', ''
    initial=block.args.get('value', '{}')
    sections=[] if is_script_scope(block) else parse_simple_initializer(initial,dtype)
    section = Section('data', block.args.get('name', 'NewData'),
                      blocks=sections or [],
                      args={'owner': owner, 'container': dtype, 'source_id': block.id,
                            'parent_section_id': parent_id,
                            'fallback_expression': initial if sections is None else ''},
                      x=parent.x + 480, y=parent.y + 60 + (len(document.sections) % 3) * 70)
    document.sections.append(section)
    if not is_script_scope(block):
        block.args['container_type'] = dtype
    return section


def find_source(document, section):
    source_id = section.args.get('source_id')
    if not source_id:
        return None
    def walk(blocks):
        for block in blocks:
            if block.id == source_id:
                return block
            for branch in block.branches.values():
                found = walk(branch)
                if found is not None:
                    return found
        return None
    for parent in document.sections:
        found = walk(parent.blocks)
        if found is not None:
            return parent, found
    return None


def synchronize_symbol(document: ScriptDocument, symbol_id: str, new_name: str):
    for sec in document.sections:
        if sec.kind == 'data' and sec.args.get('source_id') == symbol_id:
            sec.name = new_name


def render_definition(document: ScriptDocument, section: Section, visited=None):
    """Returns a structured AST expression, preserving nested table/array definitions."""
    visited = set(visited or ())
    if section.id in visited:
        raise ValueError('数据定义存在循环嵌套：' + section.name)
    visited.add(section.id)
    dtype = section.args.get('container', 'Table')
    if dtype not in CONTAINER_KINDS:
        raise ValueError('无效的数据容器类型：' + dtype)
    if not any(b.kind=='var' for b in section.blocks) and section.args.get('fallback_expression'):
        return {'kind':'raw','value':section.args['fallback_expression']}
    entries = []
    for block in section.blocks:
        if block.kind != 'var':
            continue
        child = linked_definition(document, block.id, section.id)
        value = render_definition(document, child, visited) if child else block.args.get('value', 'null')
        entries.append((str(block.args.get('name', '')).strip(), value))
    if dtype == 'Set':
        return {'kind': 'array', 'items': [value for _, value in entries]}
    output = {}
    for name, value in entries:
        if name in output:
            raise ValueError(f'重复的 Table 成员：{section.name}.{name}')
        output[name] = value
    return {'kind': 'table', 'items': output}


def prune_empty_orphan_data(document):
    """Discard empty editor-only Data workspaces that can no longer emit code.

    Legacy projects can retain a linked Table/Set workspace after its source
    variable has been changed back to a scalar.  If the workspace is empty and
    has no fallback initializer, keeping it only creates misleading validation
    noise.  Non-empty workspaces and fallback expressions are never discarded.
    """
    removed=[]
    for section in tuple(document.sections):
        if section.kind!='data' or not section.args.get('source_id') or section.blocks:
            continue
        if section.args.get('fallback_expression'):
            continue
        source=find_source(document,section)
        stale = source is None
        if source is not None:
            _, block = source
            stale = section.args.get('container') != container_kind(block)
        if stale:
            document.sections.remove(section)
            removed.append(section.id)
    return removed



def prune_redundant_orphan_data(document):
    """Remove *only* proven duplicates of live Namespace data declarations.

    A nonempty orphan is ordinarily valuable user work and must NOT be deleted.
    The only safe case here is a standalone Table workspace with a missing
    declaration and an exactly matching Namespace member list.  Nested data,
    member behaviors and unresolved values are intentionally excluded.

    Return removed (Section, Namespace) pairs so the caller can archive them.
    """
    def members(blocks):
        values = {}
        for block in blocks:
            if block.kind != 'var' or block.branches:
                return None
            name = str(block.args.get('name', '')).strip()
            if not name or name in values:
                return None
            # Only compare ordinary, direct definitions; ScriptScope mode has
            # separate initialization semantics.
            if block.args.get('init_mode', 'once') != 'once':
                return None
            value = block.args.get('value', 'null')
            if not isinstance(value, str):
                return None
            values[name] = (value.strip(), block.args.get('container_type', '普通'))
        return values or None

    removed = []
    for section in tuple(document.sections):
        if (section.kind != 'data' or not section.args.get('source_id')
                or section.args.get('parent_section_id')
                or section.args.get('container') != 'Table'
                or section.args.get('fallback_expression')
                or not section.blocks or find_source(document, section) is not None):
            continue
        # Never discard workspaces that own nested definitions; their content
        # can have semantics not represented by the immediate member values.
        if any(other.kind == 'data' and other.args.get('parent_section_id') == section.id
               for other in document.sections):
            continue
        data_members = members(section.blocks)
        if data_members is None:
            continue
        matching_namespaces = [namespace for namespace in document.sections
                               if namespace.kind == 'namespace' and namespace.name == section.name
                               and members(namespace.blocks) == data_members]
        if len(matching_namespaces) != 1:
            continue
        # Require the member sets to be identical, not merely a shared name.
        namespace = matching_namespaces[0]
        document.sections.remove(section)
        removed.append((section, namespace))
    return removed


def prune_unlinked_orphan_data(document):
    """Remove all detached Data workspaces, regardless of their content.

    A Data section without source_id can be an intentional top-level global
    and must never be removed automatically. Linked workspaces whose owner
    still exists must also be preserved. Iterating is important: removing an
    orphan parent can detach any nested child workspace.

    Return removed (Section, reason) pairs for project-level recovery records.
    """
    removed = []
    while True:
        detached = [section for section in tuple(document.sections)
                    if section.kind == 'data'
                    and section.args.get('source_id')
                    and find_source(document, section) is None]
        if not detached:
            return removed
        for section in detached:
            document.sections.remove(section)
            removed.append((section, 'missing_owner'))


def repair_orphan_workspaces(project):
    """Remove detached Data workspaces; archive meaningful content first.

    Every Data section whose *previously recorded* source declaration is
    missing is removed, even with unique or nested content. Truly standalone
    Data sections (without source_id) generate global declarations and must
    NEVER be removed automatically. Nonempty and fallback-only removed
    sections are stored in project recovery records for Tools-menu export.
    Removing an orphan containing executable blocks may affect generated code.
    """
    removed = []
    for document in project.documents:
        for section_id in prune_empty_orphan_data(document):
            removed.append((document.name, section_id, 'empty'))
        for section, namespace in prune_redundant_orphan_data(document):
            project.recovered_workspaces.append({
                'document': document.name,
                'reason': 'duplicate_namespace',
                'namespace_id': namespace.id,
                'section': section.to_dict(),
            })
            removed.append((document.name, section.id, 'duplicate_namespace'))
        for section, reason in prune_unlinked_orphan_data(document):
            if section.blocks or section.args.get('fallback_expression'):
                project.recovered_workspaces.append({
                    'document': document.name,
                    'reason': reason,
                    'section': section.to_dict(),
                })
            removed.append((document.name, section.id, reason))
    return removed
