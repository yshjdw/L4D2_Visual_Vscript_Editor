from dataclasses import dataclass
from .models import Project, ScriptDocument, Block
from .codegen import IDENT, SquirrelGenerator
from .data_definitions import DATA_BLOCKS, find_source, container_kind,linked_definition
from .scope_visibility import visible_local, _locations

@dataclass
class Issue:
    level: str
    text: str
    section: str = ''
    section_id: str = ''
    block_id: str = ''

class Validator:
    def __init__(self, catalog):
        self.catalog = catalog

    def check(self, project: Project, document: ScriptDocument):
        issues = []
        self._current_document=document
        names = {doc.name for doc in project.documents}
        graph = {d.name: d.includes for d in project.documents}
        def cyclic(node, path):
            if node in path:
                return True
            return any(cyclic(next_name,path | {node}) for next_name in graph.get(node, []) if next_name in graph)
        for name in graph:
            if cyclic(name,set()):
                issues.append(Issue('错误', 'IncludeScript 存在循环依赖：'+name))
        for include in document.includes:
            if include not in names:
                issues.append(Issue('错误','引用了不存在的工程文件：'+include))
        sections = {}
        for section in document.sections:
            section_issues_start=len(issues)
            k = (section.kind,section.name,section.args.get('owner',''))
            if k in sections and section.kind in ('function','think','events','data','namespace'):
                issues.append(Issue('错误','重复的分区符号：'+section.name,section.name))
            sections[k] = True
            if section.kind in ('function','think','data','namespace','events') and not IDENT.fullmatch(section.name):
                issues.append(Issue('错误','非法的分区名称：'+section.name,section.name))
            if section.kind == 'data':
                for block in section.blocks:
                    if block.kind == 'array_op' and section.args.get('container') != 'Set':
                        issues.append(Issue('错误','Array 操作只能放入 Set [] 数据区',section.name))
                    if block.kind not in DATA_BLOCKS:
                        issues.append(Issue('错误','复杂数据定义分区仅允许变量相关及调用积木',section.name))
                if section.args.get('source_id'):
                    source=find_source(document,section)
                    if not source:
                        issues.append(Issue('提示' if not section.blocks else '错误','复杂数据分区所绑定的变量已不存在' + ('（空分区会在加载时自动清理）' if not section.blocks else ''),section.name))
                    else:
                        parent,block=source
                        if parent.kind=='data' and section.args.get('parent_section_id')!=parent.id:
                            issues.append(Issue('错误','嵌套数据分区父节点不一致',section.name))
                        if section.args.get('container')!=container_kind(block):
                            if section.blocks or section.args.get('fallback_expression'):
                                issues.append(Issue('错误','复杂数据分区与变量的 Table/Set 类型不一致',section.name))
                            else:
                                issues.append(Issue('提示','空数据工作区未参与代码生成；关联变量现已不是 Table/Set',section.name))
                        if section.name!=block.args.get('name'):
                            issues.append(Issue('警告','数据定义分区名称与其变量不同步',section.name))
            if section.kind == 'namespace':
                for block in section.blocks:
                    if block.kind=='var' and not IDENT.fullmatch(str(block.args.get('name',''))):
                        issues.append(Issue('错误','非法的 Table 成员名：'+str(block.args.get('name')),section.name))
            if section.kind == 'events':
                for block in section.blocks:
                    if block.kind != 'event':
                        issues.append(Issue('错误','事件区域只能放半椭圆事件积木',section.name))
            for block in section.blocks:
                self._check_block(issues,block,section,0)
            for issue in issues[section_issues_start:]:
                if not issue.section_id:
                    issue.section_id=section.id
        compiler = SquirrelGenerator()
        compiler.compile(project,document)
        for e in compiler.errors:
            from .diagnostic_navigation import find_block
            import re
            block_match=re.search(r'\(([a-f0-9]{12})\)',e)
            detected_section=None
            detected_block=None
            if block_match:
                for section in document.sections:
                    detected_block=find_block(section.blocks,block_match.group(1))
                    if detected_block is not None:
                        detected_section=section
                        break
            if detected_section is None:
                detected_section=next((s for s in document.sections
                                       if e.startswith(s.name+':') or e.startswith(s.name+' ')),None)
            issues.append(Issue('错误','代码生成：'+e,
                                detected_section.name if detected_section else '',
                                detected_section.id if detected_section else '',
                                detected_block.id if detected_block else ''))
        return issues

    def _data_execution_site(self, section):
        """Return the actual statement evaluating a linked data member.

        ScriptScope member initializers are inlined at the source variable's
        declaration. Nested table/array definitions inherit that lexical scope.
        A standalone data workspace has no lexical source statement.
        """
        seen = set()
        current = section
        while current.kind == 'data' and current.args.get('source_id'):
            if current.id in seen:
                return section, None
            seen.add(current.id)
            owner = find_source(self._current_document, current)
            if not owner:
                return section, None
            parent, declaration = owner
            if parent.kind != 'data':
                return parent, declaration.id
            current = parent
        return section, None

    def _check_block(self,issues,block: Block,section,loop_depth):
        block_issues_start=len(issues)
        if block.kind in ('break','continue') and not loop_depth:
            issues.append(Issue('错误',block.kind+' 必须放在循环内部',section.name))
        if block.kind == 'event':
            if section.kind != 'events':
                issues.append(Issue('错误','事件只能属于事件分区',section.name))
            if not any(e['name'] == block.args.get('event') for e in self.catalog.events(block.args.get('event',''))):
                issues.append(Issue('警告','未收录事件：'+str(block.args.get('event')),section.name))
        if block.kind == 'netprop':
            prop_name = block.args.get('property','')
            table = block.args.get('table','')
            from .netprop_catalog import resolve_property
            known = resolve_property(table,prop_name)
            if not known:
                issues.append(Issue('警告','NetProp 未在离线索引中查到：'+str(prop_name),section.name))
            else:
                if known['type']=='array' and not block.args.get('array'):
                    issues.append(Issue('错误','数组 NetProp '+prop_name+' 需要使用 Array 方法与索引',section.name))
                elif known['type'] not in ('array','integer') and block.args.get('prop_type')=='Int':
                    issues.append(Issue('提示','当前 NetProp 的类型与 Int 不一致：'+prop_name,section.name))
            if not table:
                issues.append(Issue('提示','NetProp 未指定实体网络类，请在属性选择窗口中选择',section.name))
        if block.kind == 'method':
            if block.args.get('method')=='GetPlayerUserId' and isinstance(block.args.get('target'),dict) and str(block.args['target'].get('path','')).startswith('env.'):
                issues.append(Issue('警告','GetPlayerUserId 的对象是 env 数值字段，应先用 GetPlayerFromUserID(env.userid) 获取玩家实体',section.name))
            if not block.args.get('target'):
                issues.append(Issue('错误','官方方法缺少对象插槽',section.name))
            found=[m for m in self.catalog.methods(owner=block.args.get('owner','')) if m['name']==block.args.get('method')]
            if found and found[0]['returns']=='void' and block.args.get('output'):
                issues.append(Issue('错误','void 官方方法不允许创建返回变量：'+block.args.get('method',''),section.name))
        if block.kind == 'raw':
            issues.append(Issue('提示','原始代码节点不做语义检查',section.name))
        # Enforce Squirrel lexical boundaries for stored symbol references.
        # The same event section may contain many OnGameEvent_x callbacks:
        # two local declarations with the same name in different callbacks
        # are *not* the same variable.
        from .block_reorder import locate_block
        effective_section, effective_block_id = self._data_execution_site(section)
        reference_block_id = effective_block_id or block.id
        checked=set()
        def validate_ref(value):
            if isinstance(value,list):
                for sub in value:validate_ref(sub)
            elif isinstance(value,dict):
                if value.get('kind')=='variable_ref':
                    ref=value.get('symbol_id')
                    if not ref or ref in checked:return
                    checked.add(ref)
                    if str(ref).startswith('parameter:'):
                        parameter_id=str(ref).split(':',2)
                        valid=bool(len(parameter_id)==3 and section.kind=='function'
                                   and section.id==parameter_id[1]
                                   and parameter_id[2] in section.args.get('params',[]))
                        if not valid:
                            issues.append(Issue('错误','Function 形参超出所属函数作用域：'+str(value.get('name')),section.name))
                        return
                    source=locate_block(self._current_document,ref)
                    if source:
                        source_section,_,source_block=source
                        if (source_section.kind in ('events','function','think')
                            and (source_block.kind=='event' or
                                 source_block.kind=='var' and source_block.args.get('scope','auto') in ('local','auto'))):
                            visible=(effective_section.id==source_section.id
                                     and visible_local(effective_section,ref,reference_block_id))
                            # Copies of event env can retain a symbol ID from
                            # another event, while the target's lexical `env`
                            # is still valid. Resolve that parameter by name.
                            if not visible and source_block.kind=='event' and effective_section.kind=='events':
                                location=_locations(effective_section).get(reference_block_id)
                                if location and location[1]:
                                    enclosing=next((b for b in effective_section.blocks if b.id==location[1][0][0] and b.kind=='event'),None)
                                    if enclosing:
                                        dest_env=enclosing.args.get('env','env')
                                        path=str(value.get('path') or value.get('name') or '')
                                        if path==dest_env or path.startswith(dest_env+'.'):
                                            visible=True
                            if not visible:
                                # A copied expression can retain the source symbol ID while
                                # the target callback has its own local declaration.  A
                                # same-name declaration is valid only when it is actually
                                # visible at this exact statement, never by name alone.
                                token=str(value.get('path') or value.get('name') or '')
                                local_name=str(source_block.args.get('name','')) if source_block.kind=='var' else ''
                                if local_name and effective_section.kind in ('events','function','think') and (token==local_name or token.startswith(local_name+'.') or token.startswith(local_name+'[')):
                                    for candidate_id,(candidate,_,_,_,_) in _locations(effective_section).items():
                                        if (candidate.kind=='var' and candidate.args.get('name')==local_name
                                                and candidate.args.get('scope','auto') in ('local','auto')
                                                and visible_local(effective_section,candidate_id,reference_block_id)):
                                            visible=True
                                            break
                            if not visible:
                                issues.append(Issue('错误','局部变量 / env 跨函数、事件或分支引用：'+str(value.get('path') or value.get('name')),section.name))
                    return
                for sub in value.values():validate_ref(sub)
        for value in block.args.values():validate_ref(value)
        if block.kind=='method' and block.args.get('owner') in ('CTerrorWeapon','CBaseCombatWeapon'):
            target=block.args.get('target')
            if isinstance(target,dict) and target.get('kind')=='variable_ref' and target.get('name')=='player':
                issues.append(Issue('警告','武器方法 '+str(block.args.get('method'))+' 当前对象为 player；通常应使用 player.GetActiveWeapon() 获取的 weapon',section.name))
        if block.kind=='netprop':
            target=block.args.get('target')
            if (str(block.args.get('table','')).lower().find('weapon')>=0 or
                    'rifle' in str(block.args.get('table','')).lower()) and isinstance(target,dict) and target.get('name')=='player':
                issues.append(Issue('警告','武器 NetProp '+str(block.args.get('property'))+' 的读取对象为 player，请检查是否应使用 weapon',section.name))
        # Methods nested as expression values are not root statement blocks;
        # their NetProp selector state must still be checked.
        from .netprop_method import is_netprop_method, selected_property, property_parameter_index, repair_saved_netprop_selection
        from .netprop_catalog import resolve_property
        def scan_expression(value):
            if isinstance(value,list):
                for sub in value:scan_expression(sub)
            elif isinstance(value,dict):
                if value.get('kind')=='embedded_block':
                    child=Block.from_dict(value['block'])
                    repair_saved_netprop_selection(child)
                    if child.kind=='method' and child.args.get('method')=='GetPlayerUserId':
                        target=child.args.get('target')
                        if isinstance(target,dict) and str(target.get('path','')).startswith('env.'):
                            issues.append(Issue('警告','GetPlayerUserId 的对象是 env 数值字段，应先用 GetPlayerFromUserID(env.userid) 获取玩家实体',section.name))
                    if is_netprop_method(child):
                        idx=property_parameter_index(child)
                        prop=selected_property(child,idx) if idx is not None else ''
                        cls=child.args.get('netprop_class','')
                        row=resolve_property(cls,prop)
                        if row:
                            from .netprop_catalog import api_type
                            expected=api_type(row)
                            method=child.args.get('method','')
                            if expected not in method or (row['type']=='array' and not method.endswith('Array')):
                                issues.append(Issue('警告',f'NetProp {prop} 类型为 {row["type"]}；当前调用 {method} 不匹配',section.name))
                    for sub in child.args.values():scan_expression(sub)
                else:
                    for sub in value.values():scan_expression(sub)
        for value in block.args.values():scan_expression(value)
        # A diagnostic belongs to the *exact* block where it originated,
        # not merely to an event/function whose name may be duplicated.
        for issue in issues[block_issues_start:]:
            if not issue.block_id:
                issue.block_id=block.id
                issue.section_id=section.id
        if block.kind in ('while','for','foreach','entity_for'):
            loop_depth += 1
        for nested in block.branches.values():
            for child in nested:
                self._check_block(issues,child,section,loop_depth)
