"""Typed expression sockets and API method signatures (no Qt dependency).

Nested expression nodes live in Block.args; the .l4vp v1 format stays compatible.
"""
from __future__ import annotations
import re
from .models import Block, clone_block

GLOBAL_OBJECTS = {
    'CEntities': 'Entities', 'CNetPropManager': 'NetProps',
    'CDirector': 'Director', 'CNavMesh': 'NavMesh',
    'CScriptEntityOutputs': 'EntityOutputs', 'Convars': 'Convars',
    'CScriptResponseCriteria': 'ResponseCriteria'
}


def parse_signature(parameters):
    """Split the existing SQLite `name:type,name:type` metadata.

    Some metadata is incomplete/unknown, so do not invent missing arguments.
    """
    if isinstance(parameters, list):
        return [{'name':str(x.get('name',f'arg{i+1}')),'type':str(x.get('type','unknown'))}
                if isinstance(x,dict) else {'name':str(x),'type':'unknown'}
                for i,x in enumerate(parameters)]
    if not parameters or str(parameters).strip().lower() in ('none','void'):
        return []
    result=[]
    for i,entry in enumerate(str(parameters).split(',')):
        entry=entry.strip()
        if not entry:continue
        if ':' in entry:
            name,kind=entry.split(':',1)
        else:name,kind=f'arg{i+1}',entry
        result.append({'name':name.strip() or f'arg{i+1}', 'type':kind.strip() or 'unknown'})
    return result


def block_from_method(record):
    # The SQLite catalog is a navigation index; the saved Valve documentation
    # is authoritative for a method's parameter signature when it is present.
    from .official_docs import official_functions
    record = dict(record)
    documented = official_functions().get(str(record.get('owner', ''))+'.'+str(record.get('name', '')), {})
    documented_parameters = documented.get('parameters', [])
    existing_parameters = parse_signature(record.get('parameters', ''))
    if documented_parameters and len(existing_parameters) != len(documented_parameters):
        record['parameters'] = documented_parameters
    owner=str(record.get('owner','Global'))
    spec=parse_signature(record.get('parameters',''))
    default={'int':'0','float':'0.0','bool':'false','Vector':'Vector(0, 0, 0)',
             'cstring':'""','string':'""','hscript':'null','table':'{}',
             'QAngle':'QAngle(0, 0, 0)','int[7]':'0'}
    args=[default.get(p['type'],'null') for p in spec]
    if owner in ('Global','Globals','Math','Strings'):
        b=Block('call', {'function':record['name'],'parameters':args,
                         'parameter_specs':spec,'return_type':record.get('returns','unknown'),
                         'output':''})
    else:
        b=Block('method', {'target':(owner if record.get('external') else GLOBAL_OBJECTS.get(owner,'entity')),
                           'owner':owner,'method':record['name'],'parameters':args,
                           'parameter_specs':spec,'return_type':record.get('returns','unknown'),
                           'output':''})
    if owner in ('Global','Globals') and record['name'] == 'IncludeScript':
        # Keep the documented native signature unchanged (scope = null => this),
        # but initialize new editor blocks with an explicit root scope, matching
        # project-tree drag/drop and project-level include generation.
        b.args['parameter_specs'] = [
            {'name': 'file', 'type': 'string'},
            {'name': 'scope', 'type': 'handle/table'},
        ]
        b.args['parameters'] = ['""', 'getroottable()']
    if owner in ('Global','Globals') and record['name'] in ('EntFire','DoEntFire'):
        b.args['parameters'][:2]=['"worldspawn"','"RunScriptCode"']
        if record['name']=='EntFire':
            specs=[{'name':'target','type':'string'}, {'name':'action','type':'string'},
                   {'name':'value','type':'string'}, {'name':'delay','type':'float'},
                   {'name':'activator','type':'handle'}]
            b.args['parameter_specs']=specs
            b.args['parameters']=['"worldspawn"','"RunScriptCode"','""','0.1','null']
    if str(record.get('returns','unknown')).lower() not in ('void','none'):
        b.args['output']='result_'+b.id[:5]
    return b


def repair_documented_method_parameters(block):
    """Restore missing parameter sockets in projects saved with incomplete catalog metadata.

    Preserve existing argument values. Never append speculative slots for methods
    without a documented signature, and do not overwrite user-supplied arguments.
    """
    if block.kind != 'method':
        return False
    from .official_docs import official_functions
    key = str(block.args.get('owner', ''))+'.'+str(block.args.get('method', ''))
    doc = official_functions().get(key, {})
    specs = doc.get('parameters') or []
    existing = block.args.get('parameters', [])
    if not specs or not isinstance(existing, list) or len(existing) >= len(specs):
        return False
    default = {'int':'0','float':'0.0','bool':'false','Vector':'Vector(0, 0, 0)',
               'string':'""','cstring':'""','handle':'null','hscript':'null',
               'QAngle':'QAngle(0, 0, 0)'}
    block.args['parameters'] = existing + [default.get(spec['type'],'null') for spec in specs[len(existing):]]
    block.args['parameter_specs'] = specs
    return True

def can_embed(block):
    if block.kind in ('expr','operator','math_call','rawin','string_call','utility'):return True
    if block.kind=='call':return str(block.args.get('return_type','unknown')).lower() not in ('void','none')
    if block.kind=='method':return str(block.args.get('return_type','unknown')).lower() not in ('void','none')
    if block.kind=='netprop':return block.args.get('mode','get')=='get'
    if block.kind=='array_op':return str(block.args.get('return_type','void')).lower()!='void'
    return False


def as_embedded(block):
    if not can_embed(block):raise ValueError('这个积木不提供可嵌套的返回值')
    return {'kind':'embedded_block','block':clone_block(block).to_dict()}


def is_embedded(value):
    return isinstance(value,dict) and value.get('kind')=='embedded_block' and isinstance(value.get('block'),dict)


def unpack_embedded(value):
    return Block.from_dict(value['block'])


def string_argument_expression(value, kind, expression):
    """Turn an evaluated runtime value into Squirrel source for RunScriptCode."""
    kind=str(kind or 'auto').strip().lower()
    code=expression(value)
    if kind in ('auto','unknown','int','integer','float','number','bool','boolean'):
        return '('+code+')'
    if kind in ('string','cstring','str'):
        import json
        # GetClassname() and similar string expressions need only surrounding
        # source-code quotes for RunScriptCode. Do not generate a Squirrel IIFE.
        # Statically quoted strings can be escaped completely at compile time.
        if isinstance(value, str):
            try:
                literal = json.loads(code)
            except (ValueError, TypeError):
                literal = None
            if isinstance(literal, str):
                return json.dumps(json.dumps(literal, ensure_ascii=False), ensure_ascii=False)
        return '(' + json.dumps('"') + ' + (' + code + ') + ' + json.dumps('"') + ')'
    if kind in ('vector','handle','hscript','table','array','entity'):
        raise ValueError('字符串调用不能直接序列化 '+kind+' 参数；请传递可重建的名称或数值')
    raise ValueError('字符串调用的参数类型不支持：'+kind)


def method_call_expression(block, expression):
    if block.kind=='method':
        from .netprop_method import repair_saved_netprop_selection
        repair_saved_netprop_selection(block)
    a=block.args
    params=', '.join(expression(v) for v in a.get('parameters',[]))
    if block.kind=='method':
        name=str(a.get('method','GetOrigin'))
        if name.startswith(('GetProp','SetProp','HasProp')) and str(a.get('owner','')) in ('CNetPropManager','NetProps'):
            from .netprop_catalog import runtime_property_name
            from .netprop_method import property_parameter_index
            args=list(a.get('parameters',[]))
            idx=property_parameter_index(block)
            if idx is not None and idx<len(args) and isinstance(args[idx],dict) and args[idx].get('kind')=='literal':
                args[idx]={**args[idx],'value':runtime_property_name(args[idx]['value'])}
            params=', '.join(expression(v) for v in args)
        return expression(a.get('target','entity'))+'.'+name+'('+params+')' 
    if block.kind=='string_call':
        import json
        name=str(a.get('function','')).strip()
        from .codegen import QUALIFIED
        if not QUALIFIED.fullmatch(name):raise ValueError('非法字符串调用函数名')
        values=list(a.get('parameters',[]))
        if not values:return json.dumps(name+'()',ensure_ascii=False)
        parts=[json.dumps(name+'(',ensure_ascii=False)]
        for i,v in enumerate(values):
            if i:parts.append(json.dumps(', ',ensure_ascii=False))
            specs=a.get('parameter_specs',[])
            kind=specs[i].get('type','auto') if i<len(specs) and isinstance(specs[i],dict) else 'auto'
            parts.append(string_argument_expression(v,kind,expression))
        parts.append(json.dumps(')',ensure_ascii=False))
        return '('+' + '.join(parts)+')'
    if block.kind=='call':
        return expression(a.get('function','printl'))+'('+params+')'
    if block.kind=='netprop':
        import json
        mode=str(a.get('mode','get')).lower()
        suffix=str(a.get('prop_type','Int'))
        array=bool(a.get('array',False))
        api=('GetProp' if mode=='get' else 'SetProp')+suffix+('Array' if array else '')
        property_arg = a.get('property','m_iHealth')
        from .netprop_catalog import runtime_property_name
        prop_expr = expression(property_arg) if isinstance(property_arg,dict) else json.dumps(runtime_property_name(str(property_arg)),ensure_ascii=False)
        parts=[expression(a.get('target','player')),prop_expr]
        if mode=='set':parts.append(expression(a.get('value','0')))
        if array:parts.append(expression(a.get('index','0')))
        return 'NetProps.'+api+'('+', '.join(parts)+')'
    if block.kind=='array_op':
        from .array_ops import array_call
        return array_call(block, expression)
    if block.kind=='operator':
        from .math_blocks import emit_operator
        return emit_operator(a,expression)
    if block.kind=='math_call':
        from .math_blocks import emit_math
        return emit_math(a,expression)
    if block.kind=='rawin':
        return expression(a.get('target','scope'))+'.rawin('+expression(a.get('key','"ammo_keep"'))+')'
    if block.kind=='utility':
        from .utility_blocks import emit_utility
        return emit_utility(a,expression)
    if block.kind=='expr':return expression(a.get('value','null'))
    raise ValueError('不支持的嵌套表达式积木：'+block.kind)


def embedded_ids(block):
    """IDs of nested expressions owned by a block, useful for cycle guards."""
    ids=set()
    def visit(value):
        if is_embedded(value):
            child=unpack_embedded(value)
            ids.add(child.id)
            visit(child.args)
        elif isinstance(value,dict):
            for x in value.values():visit(x)
        elif isinstance(value,list):
            for x in value:visit(x)
    visit(block.args)
    for branch in block.branches.values():
        for child in branch:ids.add(child.id);ids.update(embedded_ids(child))
    return ids


def iter_expr_nodes(block):
    """All nested expression block IDs, recursively."""
    for value in block.args.values():
        yield from _iter_value(value)


def _iter_value(value):
    if is_embedded(value):
        item=unpack_embedded(value)
        yield item
        yield from iter_expr_nodes(item)
    elif isinstance(value,list):
        for child in value:yield from _iter_value(child)
    elif isinstance(value,dict):
        for child in value.values():yield from _iter_value(child)


def is_boolean_return(block):
    return block.kind=='rawin' or (block.kind=='netprop' and block.args.get('prop_type')=='Bool') or str(block.args.get('return_type', '')).casefold() in ('bool','boolean')


def is_value_block(block):
    return can_embed(block)


def remove_embedded_expression(document, expression_id):
    """Delete exactly one embedded expression in a document, preserving its owner."""
    def remove_value(value):
        if is_embedded(value):
            block=value['block']
            if block.get('id')==expression_id:
                return 'null', True
            _,removed=remove_value(block)
            return value,removed
        if isinstance(value,dict):
            for key,child in value.items():
                replacement,removed=remove_value(child)
                if removed:
                    value[key]=replacement
                    return value,True
        elif isinstance(value,list):
            for index,child in enumerate(value):
                replacement,removed=remove_value(child)
                if removed:
                    value[index]=replacement
                    return value,True
        return value,False

    def scan_blocks(blocks):
        for block in blocks:
            _,removed=remove_value(block.args)
            if removed:return True
            if any(scan_blocks(branch) for branch in block.branches.values()):return True
        return False

    return any(scan_blocks(section.blocks) for section in document.sections)
