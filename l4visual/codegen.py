from __future__ import annotations
import json
import re
from .models import Block, ScriptDocument, Project
from .data_definitions import render_definition, linked_definition, container_kind, is_script_scope, script_scope_entity, dynamic_table_assignments

IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
QUALIFIED = re.compile(r'^(?:::)?[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$')


def require_name(value, qualified=False):
    value = str(value).strip()
    if not (QUALIFIED if qualified else IDENT).fullmatch(value):
        raise ValueError('无效的 Squirrel 标识符：' + repr(value))
    return value


def expression(expr):
    if isinstance(expr, bool):
        return 'true' if expr else 'false'
    if expr is None:
        return 'null'
    if isinstance(expr, (int, float)):
        return str(expr)
    if isinstance(expr, str):
        return expr.strip() or 'null'
    if not isinstance(expr, dict):
        raise ValueError('非法表达式节点')
    kind = expr.get('kind', 'raw')
    if kind == 'embedded_block':
        from .expressions import unpack_embedded, method_call_expression
        return method_call_expression(unpack_embedded(expr), expression)
    if kind == 'literal':
        value = expr.get('value')
        return json.dumps(value, ensure_ascii=False) if isinstance(value, str) else expression(value)
    if kind in ('raw','variable'):
        return str(expr.get('value','null'))
    if kind == 'variable_ref':
        return str(expr.get('path') or expr.get('name') or 'null')
    if kind == 'member':
        base = expression(expr.get('base'))
        return base + '.' + require_name(expr.get('name',''))
    if kind == 'index':
        return expression(expr.get('base')) + '[' + expression(expr.get('index')) + ']'
    if kind == 'unary':
        return '(' + str(expr.get('op','!')) + expression(expr.get('value')) + ')'
    if kind == 'binary':
        return '(' + expression(expr.get('left')) + ' ' + str(expr.get('op','==')) + ' ' + expression(expr.get('right')) + ')'
    if kind == 'call':
        return expression(expr.get('target')) + '(' + ', '.join(expression(a) for a in expr.get('params',[])) + ')'
    if kind == 'array':
        return '[' + ', '.join(expression(x) for x in expr.get('items', [])) + ']'
    if kind == 'table':
        return '{' + ', '.join(require_name(k) + ' = ' + expression(v) for k,v in expr.get('items',{}).items()) + '}'
    if kind == 'multiline':
        value = str(expr.get('value',''))
        return ' +\n'.join(json.dumps(part, ensure_ascii=False) for part in value.splitlines(keepends=True)) or '""'
    raise ValueError('未实现的表达式类型：' + str(kind))


class SquirrelGenerator:
    def __init__(self):
        self.errors = []

    def emit_blocks(self, blocks, depth=1, ctx='function'):
        lines = []
        for block in blocks:
            try:
                lines.extend(self.emit_block(block, depth, ctx))
            except (ValueError, KeyError) as exc:
                self.errors.append(f'{block.kind} ({block.id}): {exc}')
                lines.append(('    '*depth) + '// ERROR: block ' + block.id)
        return lines

    def emit_block(self, block, depth=1, ctx='function'):
        a = block.args
        kind = block.kind
        pad = '    ' * depth
        body = block.branches.get('body', [])
        statements = []
        if kind == 'var':
            name = require_name(a.get('name','value'))
            definition = linked_definition(self._document, block.id) if getattr(self, '_document', None) and container_kind(block) else None
            dynamic = is_script_scope(block)
            value = expression(render_definition(self._document, definition) if definition and not dynamic else a.get('value','null'))
            scope = a.get('scope','auto')
            if scope=='static':
                raise ValueError('static 仅能定义在 Squirrel class 内；普通变量请使用 local 或 auto')
            if scope=='无':
                operator=name+' = '
            else:
                operator = ('local ' + name + ' = ') if (scope == 'local' or scope == 'auto' and ctx == 'function') else ('::' + name + ' <- ')
            if dynamic:
                entity = script_scope_entity(block)
                source = expression(entity) if entity is not None else None
                if a.get('container_type') == 'ScriptScope':
                    if not source:
                        raise ValueError('ScriptScope 需要实体表达式')
                    value = source + '.GetScriptScope()'
                lines = ([pad + source + '.ValidateScriptScope();'] if source else [])
                lines.append(pad + operator + value + ';')
                if definition:
                    lines.extend(pad + line for line in dynamic_table_assignments(self._document, definition, name, render_definition))
                return lines
            return [pad + operator + value + ';']
        if kind in ('assign','member'):
            target = expression(a.get('target','x'))
            mode = a.get('assignment','=' )
            if mode not in ('=', '<-', '+=', '-=', '*=', '/=', '%=', 'auto'):
                raise ValueError('不支持的赋值运算符')
            if mode == 'auto':
                mode = '<-' if '.' in target or '[' in target else '='
            if mode == '<-' and not ('.' in target or '[' in target):
                raise ValueError('新槽位操作 <- 只适用于 Table 成员或索引')
            return [pad + target + ' ' + mode + ' ' + expression(a.get('value','null')) + ';']
        if kind in ('call','method','netprop','expr','array_op','operator','math_call','rawin','utility','string_call'):
            from .expressions import method_call_expression
            code = method_call_expression(block, expression)
            output = str(a.get('output','')).strip()
            if output and kind != 'expr' and (kind != 'netprop' or a.get('mode','get') == 'get'):
                name = require_name(output)
                prefix = 'local ' if ctx == 'function' else '::'
                assign = ' = ' if ctx == 'function' else ' <- '
                return [pad + prefix + name + assign + code + ';']
            return [pad + code + ';']
        if kind == 'trace_line':
            # Native L4D2 TraceLine modifies the supplied table in-place.
            params = ', '.join(name + ' = ' + expression(a.get(name, default))
                              for name, default in [('start','Vector(0, 0, 0)'),
                                                    ('end','Vector(1000, 0, 0)'),
                                                    ('ignore','null'),('mask','33579137')])
            table = '{' + params + '}'
            result = str(a.get('output','trace')).strip()
            if result:
                result = require_name(result)
                if ctx == 'function':
                    return [pad + 'local ' + result + ' = ' + table + ';',
                            pad + 'TraceLine(' + result + ');']
                return [pad + '::' + result + ' <- ' + table + ';',
                        pad + 'TraceLine(::' + result + ');']
            return [pad + 'TraceLine(' + table + ');']
        if kind == 'zspawn':
            from .spawn_catalog import INFECTED_TYPES
            species = int(a.get('infected_type',0))
            if species not in {item[0] for item in INFECTED_TYPES}:
                raise ValueError('Unknown ZSpawn infected type: '+str(species))
            position = expression(a.get('pos','Vector(0, 0, 0)'))
            return [pad + 'ZSpawn({type = '+str(species)+', pos = '+position+'});']
        if kind == 'summon':
            from .spawn_catalog import enabled_config
            classname_value = a.get('classname','info_target')
            if isinstance(classname_value,dict):
                classname_expr = expression(classname_value)
            else:
                classname = str(classname_value).strip()
                if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', classname):
                    raise ValueError('非法实体 classname')
                classname_expr = json.dumps(classname)
            config = enabled_config(a.get('config',{}))
            keyvalues = '{' + ', '.join(require_name(k)+' = '+expression(v) for k,v in config.items()) + '}'
            call = 'SpawnEntityFromTable('+classname_expr+', '+keyvalues+')'
            output = str(a.get('output','')).strip()
            if output:
                name=require_name(output)
                return [pad + ('local '+name+' = ' if ctx=='function' else '::'+name+' <- ') + call + ';']
            return [pad+call+';']
        if kind == 'raw':
            return [pad + line for line in str(a.get('source','')).splitlines()]
        if kind == 'return':
            value = a.get('value','')
            return [pad + 'return' + (' ' + expression(value) if str(value).strip() else '') + ';']
        if kind in ('break','continue'):
            return [pad + kind + ';']
        if kind == 'throw':
            return [pad + 'throw ' + expression(a.get('value','"Error"')) + ';']
        if kind == 'if':
            result = [pad + 'if (' + expression(a.get('condition','true')) + ')', pad + '{']
            result += self.emit_blocks(body, depth+1, ctx)
            result.append(pad + '}')
            for branch in a.get('elif',[]):
                result.extend([pad + 'else if (' + expression(branch.get('condition','true')) + ')', pad + '{'])
                result += self.emit_blocks([Block.from_dict(b) for b in branch.get('blocks',[])], depth+1, ctx)
                result.append(pad + '}')
            for key, children in block.branches.items():
                if key.startswith('elif__'):
                    condition=expression(a.get('elif_condition_'+key,'true'))
                    result.extend([pad+'else if ('+condition+')',pad+'{'])
                    result+=self.emit_blocks(children,depth+1,ctx)
                    result.append(pad+'}')
            if block.branches.get('else'):
                result += [pad + 'else',pad + '{']
                result += self.emit_blocks(block.branches['else'],depth+1,ctx)
                result.append(pad + '}')
            return result
        if kind == 'while':
            return [pad + 'while (' + expression(a.get('condition','true')) + ')',pad + '{', *self.emit_blocks(body, depth+1,ctx),pad + '}']
        if kind == 'foreach':
            name = require_name(a.get('variable','item'))
            key = require_name(a['key']) + ', ' if a.get('key') else ''
            return [pad + 'foreach (' + key + name + ' in ' + expression(a.get('source','items')) + ')',pad + '{', *self.emit_blocks(body, depth+1,ctx),pad + '}']
        if kind == 'for':
            name = require_name(a.get('variable','i'))
            if 'source' in a:
                # The range helper is an IDE construct, not a call to an
                # unavailable runtime function. Standalone number = count.
                source = a['source']
                if isinstance(source,dict) and source.get('kind')=='range':
                    start,stop,step=(expression(source.get(k,v)) for k,v in [('start','0'),('stop','10'),('step','1')])
                elif isinstance(source,str) and re.fullmatch(r'\s*range\(.*\)\s*',source,re.S):
                    from .data_definitions import split_initializer
                    parts=split_initializer(source.strip()[6:-1])
                    if not 1<=len(parts)<=3:
                        raise ValueError('range 参数数量应为 1～3 个')
                    start,stop,step = ('0',parts[0],'1') if len(parts)==1 else (parts[0],parts[1],'1') if len(parts)==2 else tuple(parts)
                else:
                    start,stop,step='0',expression(source),'1'
            else:
                start,stop,step = (expression(x) for x in (a.get('start','0'),a.get('stop','10'),a.get('step','1')))
            if step.strip() in ('0','0.0'):
                raise ValueError('For 的 step 不能为 0')
            op = '>' if re.fullmatch(r'-\d+(?:\.\d+)?',step) else '<'
            update = name + ' += ' + step
            return [pad + f'for (local {name} = {start}; {name} {op} {stop}; {update})',pad + '{', *self.emit_blocks(body,depth+1,ctx),pad + '}']
        if kind == 'entity_for':
            from .entity_search import entity_for_lines
            return entity_for_lines(block,depth,expression,require_name,self.emit_blocks,ctx)
        if kind == 'try':
            error = require_name(a.get('error','e'))
            return [pad + 'try',pad + '{',*self.emit_blocks(body,depth+1,ctx),pad + '}',pad + f'catch ({error})',pad + '{',*self.emit_blocks(block.branches.get('catch',[]),depth+1,ctx),pad + '}']
        if kind == 'event':
            raise ValueError('事件帽子积木仅允许放在事件分区')
        raise ValueError('未知的积木类型：' + kind)

    def compile(self, project: Project, document: ScriptDocument):
        self.errors = []
        self._document = document
        lines = ['// Generated by L4D2 VScript Visual Prototype', '// Target: L4D2 Squirrel 3.0.4', '']
        for include in document.includes:
            if include not in [x.name for x in project.documents]:
                self.errors.append('不存在的 IncludeScript 文件：'+include)
                continue
            path = include[:-4] if include.lower().endswith('.nut') else include
            lines.append('IncludeScript(' + json.dumps(path,ensure_ascii=False) + ', getroottable());')
        if document.includes:
            lines.append('')
        namespace_names = {s.name for s in document.sections if s.kind == 'namespace'}
        for s in document.sections:
            if s.kind in ('function','data') and s.args.get('owner'):
                namespace_names.add(s.args['owner'])
        for name in sorted(namespace_names):
            try:
                lines.append('::'+require_name(name)+' <- {};')
            except ValueError as exc:
                self.errors.append(str(exc))
        if namespace_names:
            lines.append('')
        # 先声明数据，再声明函数，最后执行顶层初始化
        # Table 成员应先于任何执行流程初始化。
        for s in document.sections:
            if s.kind != 'namespace':continue
            for b in s.blocks:
                if b.kind != 'var':continue
                key=str(b.args.get('name',''))
                try:
                    definition = linked_definition(document, b.id) if container_kind(b) else None
                    dynamic = is_script_scope(b)
                    value = render_definition(document, definition) if definition and not dynamic else b.args.get('value','null')
                    entity = script_scope_entity(b) if dynamic else None
                    if dynamic and entity is not None:
                        lines.append(expression(entity)+'.ValidateScriptScope();')
                        if b.args.get('container_type')=='ScriptScope':
                            value = expression(entity)+'.GetScriptScope()'
                    target='::'+require_name(s.name)+'.'+require_name(key)
                    lines.append(target+' <- '+expression(value)+';')
                    if dynamic and definition:
                        lines.extend(dynamic_table_assignments(document,definition,target,render_definition))
                except ValueError as exc:self.errors.append(s.name+': '+str(exc))
        lines.append('')
        # Bound data sections are rendered INSIDE their owning declaration.
        # Standalone data sections remain legitimate root globals.
        for s in document.sections:
            if s.kind != 'data' or s.args.get('source_id'):
                continue
            try:
                name = require_name(s.name)
                owner = s.args.get('owner','')
                target = ('::'+require_name(owner)+'.'+name) if owner else ('::'+name)
                lines.append(target+' <- '+expression(render_definition(document,s))+';')
            except ValueError as exc:
                self.errors.append(f'{s.name}: {exc}')
        # Root complex globals created within the file-init section, if any.
        # They are declared before functions; init actions still run in order.
        init_bound_ids = set()
        for s in document.sections:
            if s.kind != 'init':
                continue
            for b in s.blocks:
                if b.kind != 'var':
                    continue
                definition = linked_definition(document, b.id) if container_kind(b) else None
                if definition:
                    try:
                        dynamic = is_script_scope(b)
                        name='::'+require_name(b.args.get('name'))
                        if dynamic:
                            entity=script_scope_entity(b)
                            if entity is not None:
                                lines.append(expression(entity)+'.ValidateScriptScope();')
                            val=expression(entity)+'.GetScriptScope()' if b.args.get('container_type')=='ScriptScope' else expression(b.args.get('value'))
                            lines.append(name+' <- '+val+';')
                            lines.extend(dynamic_table_assignments(document,definition,name,render_definition))
                        else:
                            lines.append(name+' <- '+expression(render_definition(document,definition))+';')
                        init_bound_ids.add(b.id)
                    except ValueError as exc:
                        self.errors.append(f'{s.name}: {exc}')
        if init_bound_ids:
            lines.append('')
        # Data operations must run AFTER the containing Table/Array has been initialized.
        from .variable_paths import reference_for_symbol
        for data_section in document.sections:
            if data_section.kind != 'data':
                continue
            if not data_section.args.get('source_id'):
                continue
            for action in data_section.blocks:
                if action.kind != 'array_op':
                    continue
                target = reference_for_symbol(document, data_section.args.get('source_id'))
                if not target:
                    self.errors.append('无法解析数据区 Array 操作所属变量：' + data_section.name)
                    continue
                from .array_ops import array_call
                try:
                    lines.append(array_call(Block('array_op', {**action.args, 'target': target}), expression) + ';')
                except ValueError as exc:
                    self.errors.append(str(exc))
        for s in document.sections:
            if s.kind not in ('function','think'):
                continue
            try:
                name = require_name(s.name)
                owner = s.args.get('owner','')
                target = '::'+require_name(owner)+'.'+name if owner else '::'+name
                params = [require_name(x) for x in s.args.get('params',[])]
                lines.extend([target+' <- function('+', '.join(params)+')','{'])
                lines += self.emit_blocks(s.blocks,1,'function')
                if s.kind == 'think' and not any(b.kind=='return' for b in s.blocks):
                    lines.append('    return '+expression(s.args.get('interval','0.5'))+';')
                lines += ['};','']
            except ValueError as exc:
                self.errors.append(f'{s.name}: {exc}')
        for s in document.sections:
            if s.kind != 'events':
                continue
            name = require_name(s.name)
            if name not in namespace_names:
                lines.append('::'+name+' <- {};')
            for event in s.blocks:
                if event.kind != 'event':
                    self.errors.append(f'{s.name} 包含非事件积木：{event.kind}')
                    continue
                event_name = require_name(event.args.get('event','round_start'))
                env = require_name(event.args.get('env','env'))
                lines += ['::'+name+'.OnGameEvent_'+event_name+' <- function('+env+')','{']
                lines += self.emit_blocks(event.branches.get('body',[]),1,'function')
                lines += ['};','']
            lines += ['__CollectGameEventCallbacks(::'+name+');','']
        for s in document.sections:
            if s.kind == 'namespace':
                lines += self.emit_blocks([b for b in s.blocks if b.kind != 'var'],0,'global')
        for s in document.sections:
            if s.kind == 'data':
                lines += self.emit_blocks([b for b in s.blocks if b.kind in ('call','method','assign','netprop')],0,'global')
        # The explicit initializer runs before automatically attaching Think
        # callbacks. Section positions and canvas ordering do not reorder it.
        for s in document.sections:
            if s.kind == 'init':
                lines += self.emit_blocks([b for b in s.blocks if b.id not in init_bound_ids],0,'global')
        for s in document.sections:
            if s.kind == 'think' and s.args.get('auto_attach',False):
                label = s.args.get('entity_name',s.name+'_thinker')
                lines += [f'local thinker_{s.id} = Entities.FindByName(null, {json.dumps(label)});',
                          f'if (thinker_{s.id} == null || !thinker_{s.id}.IsValid())',
                          '{',f'    thinker_{s.id} = SpawnEntityFromTable("info_target", {{targetname = {json.dumps(label)}}});','}',
                          f'if (thinker_{s.id} != null && thinker_{s.id}.IsValid())',
                          '{',f'    thinker_{s.id}.ValidateScriptScope();',
                          f'    thinker_{s.id}.GetScriptScope()["{s.name}"] <- ::{s.name};',
                          f'    AddThinkToEnt(thinker_{s.id}, "{s.name}");','}']
        from .utility_helpers import insert_named_helpers
        return insert_named_helpers('\n'.join(lines).rstrip()+'\n')
