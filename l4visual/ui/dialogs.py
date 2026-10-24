from __future__ import annotations
import json
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QHBoxLayout,QLabel,QLineEdit,
                               QPushButton,QComboBox,QDialogButtonBox,QPlainTextEdit,QCheckBox,
                               QListWidget,QMessageBox,QGroupBox,QInputDialog)
from ..models import Block,Section
from .localization import translated_text
from ..codegen import expression
from .chain import ChainEditor
from ..type_inference import infer_sendtable
from ..data_definitions import container_kind
from ..entity_search import ENTITY_SEARCH_MODES, ENTITY_FIELD_LABELS, ENTITY_FIELD_DEFAULTS, search_fields, normalize_entity_search

SECTION_KINDS = [('命名空间','namespace'),('函数','function'),('Think','think'),('游戏事件','events'),('复杂变量','data')]
BLOCK_NAMES = {
 'var':'变量定义','assign':'赋值 / 修改','member':'链式成员赋值','call':'调用自定义函数','string_call':'字符串调用函数','method':'官方方法','netprop':'NetProps Get/Set',
 'if':'If / Else','while':'While','for':'数值 For','entity_for':'实体 For','foreach':'Foreach','try':'Try / Catch',
 'return':'Return','break':'Break','continue':'Continue','throw':'Throw','raw':'高级：原始代码','expr':'表达式独立执行','event':'原版游戏事件','array_op':'Array 特殊操作','summon':'Summon 生成实体','zspawn':'生成感染者 ZSpawn','trace_line':'TraceLine 射线检测','operator':'运算符','math_call':'Math 数学函数','rawin':'Table 成员存在？','utility':'通用转换 / 获取'}
BLOCK_CATEGORIES = {
 '变量与数据':['var','assign','member','array_op','expr'],
 '通用工具':['utility'],
 '自定义函数':['call'],
 '运算与判断':['boolean','operator','rawin'],
 '数学函数':['math_call'],
 '实体生成':['summon','zspawn'],
 '射线追踪':['trace_line'],
  'NetProps':['netprop'],
 '流程与循环':['if','while','for','entity_for','foreach','try','return','break','continue','throw'],
 '高级':['raw']
}
DEFAULT_ARGS = {
 'var':{'name':'value','container_type':'普通','value':'0','scope':'auto'}, 'assign':{'target':'value','assignment':'auto','value':'0'},'member':{'target':'Data.Member','assignment':'auto','value':'null'},
 'call':{'function':'printl','parameters':['"Hello"'],'output':''},
 'method':{'target':'player','method':'GetOrigin','parameters':[],'output':'position','owner':'CBaseEntity'},
 'netprop':{'mode':'get','target':'player','table':'DT_TerrorPlayer','property':'m_iHealth','prop_type':'Int','value':'100','output':'health','array':False,'index':'0'},
 'if':{'condition':'true'},'while':{'condition':'true'},'for':{'variable':'i','source':'range(0, 10)'},
 'entity_for':{'variable':'entity','search':'FindByClassname','filter':'"player"'},
 'foreach':{'variable':'item','key':'','source':'items'}, 'try':{'error':'e'},'return':{'value':'true'},
 'break':{},'continue':{},'throw':{'value':'"error"'},'raw':{'source':'// 在此写 Squirrel'},
 'array_op':{'target':'items','operation':'append','parameters':['null'],'parameter_specs':[{'name':'value','type':'unknown'}],'return_type':'void','output':''},
 'expr':{'value':'Time()'},'event':{'event':'round_start','env':'env'},
 'summon':{'classname':'info_target','config':{},'output':''},
 'zspawn':{'infected_type':0,'pos':'Vector(0, 0, 0)'},
 'trace_line':{'start':'Vector(0, 0, 0)','end':'Vector(1000, 0, 0)','ignore':'null','mask':'33579137','output':'trace'},
 'operator':{'left':'0','operator':'+','right':'0'},
 'math_call':{'function':'sqrt','parameters':['0'],'parameter_specs':[{'name':'x','type':'float'}]},
 'rawin':{'target':'scope','key':'"ammo_keep"'},
 'utility':{'operation':'player_from_userid','value':'env.userid'}
}
BRANCHES = {'if':{'body':[]},'while':{'body':[]},'for':{'body':[]},'foreach':{'body':[]},'entity_for':{'body':[]},'try':{'body':[],'catch':[]},'event':{'body':[]}}

def split_parameters(text):
    result=[];start=0;depth=0;quote=None;escaped=False
    for i,ch in enumerate(text):
        if quote:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch==quote:quote=None
        elif ch in ('"',"'"):quote=ch
        elif ch in '([{':depth+=1
        elif ch in ')]}':depth=max(0,depth-1)
        elif ch==',' and depth==0:
            if text[start:i].strip():result.append(text[start:i].strip())
            start=i+1
    if text[start:].strip():result.append(text[start:].strip())
    return result


def new_block(kind):
    return Block(kind,deepcopy(DEFAULT_ARGS.get(kind,{})),deepcopy(BRANCHES.get(kind,{})))

def new_block_payload(payload):
    """Create operator variants without treating the dragged name as Squirrel code."""
    if payload.startswith('literal:'):
        from ..quick_literals import new_literal_block
        _tag, group, value = payload.split(':',2)
        return new_literal_block(group,value)
    if payload.startswith('boolean:'):
        value=payload.split(':',1)[1]
        if value not in ('true','false'):raise ValueError('Invalid boolean literal')
        block=new_block('expr')
        block.args.update(value=value,return_type='bool')
        return block
    if payload.startswith('utility:'):
        from ..utility_blocks import UTILITY_BLOCKS, create_utility_args
        operation=payload.split(':',1)[1]
        if operation not in UTILITY_BLOCKS:raise ValueError('未知通用工具')
        block=new_block('utility');block.args.update(create_utility_args(operation))
        return block
    if payload.startswith('math:'):
        from ..math_blocks import MATH_FUNCTIONS
        name=payload.split(':',1)[1]
        if name not in ('max','min') or MATH_FUNCTIONS.get(name)!=2:
            raise ValueError('Invalid custom math function')
        block=new_block('math_call')
        block.args.update(function=name, parameters=['0','0'],
                          parameter_specs=[{'name':'a','type':'float'}, {'name':'b','type':'float'}])
        return block
    if payload.startswith('operator:'):
        from ..math_blocks import OPERATOR_SET
        op=payload.split(':',1)[1]
        if op not in OPERATOR_SET:raise ValueError('未支持的运算符')
        block=new_block('operator')
        block.args['operator']=op
        if op=='!':block.args['left']='false'
        return block
    return new_block(payload)

class SectionEditor(QDialog):
    def __init__(self,section=None, parent=None, document=None):
        super().__init__(parent)
        self.document=document
        self.setWindowTitle('分区属性')
        self.section = section or Section('function','NewFunction')
        lay=QVBoxLayout(self)
        form=QFormLayout(); lay.addLayout(form)
        self.type=QComboBox()
        for label,k in SECTION_KINDS: self.type.addItem(label,k)
        self.type.setCurrentIndex(max(0,self.type.findData(self.section.kind)))
        if self.section.args.get('source_id'):
            self.type.setEnabled(False)
        self.name=QLineEdit(self.section.name)
        if self.section.args.get('source_id'):
            self.name.setReadOnly(True)
            self.name.setToolTip('已绑定变量。请到变量圆圈右键重命名。')
        self.owner=QComboBox()
        self.owner.addItem('全局函数（不使用 Namespace）', '')
        for namespace in (section for section in (document.sections if document else []) if section.kind=='namespace'):
            self.owner.addItem(namespace.name, namespace.name)
        selected_owner=self.section.args.get('owner','')
        self.owner.setCurrentIndex(max(0,self.owner.findData(selected_owner)))
        self.owner.setToolTip('可选 Namespace；留空时生成 ::FunctionName')
        self.params=QLineEdit(', '.join(self.section.args.get('params',[])))
        self.param_types=QLineEdit(', '.join(self.section.args.get('param_types',[])))
        self.param_types.setPlaceholderText(translated_text('int, string, bool  (auto 为旧版直接拼接)'))
        self.param_types.setToolTip(translated_text('与形参依次对应。支持 auto/int/float/bool/string；handle 和 Vector 不可直接字符串调用。'))
        self.container=QComboBox();self.container.addItems(['Table','Set']);self.container.setCurrentText(self.section.args.get('container','Table'))
        self.interval=QLineEdit(str(self.section.args.get('interval','0.5')))
        self.auto_attach=QCheckBox('自动创建 / 绑定 info_target');self.auto_attach.setChecked(self.section.args.get('auto_attach',False))
        self.entity_name=QLineEdit(self.section.args.get('entity_name',''))
        self.property_form=form
        for label,widget in [('类型',self.type),('名称',self.name),('函数所属 Table',self.owner),('形参（逗号隔开）',self.params),('字符串调用参数类型（逗号隔开）',self.param_types),('容器类型',self.container),('Think 返回间隔',self.interval),('自动绑定',self.auto_attach),('绑定实体 targetname',self.entity_name)]: form.addRow(label,widget)
        self.type.currentIndexChanged.connect(self.update_fields);self.update_fields()
        btn=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept);btn.rejected.connect(self.reject);lay.addWidget(btn)
    def update_fields(self):
        kind=self.type.currentData()
        rules={'owner':kind=='function', 'params':kind=='function','param_types':kind=='function', 'container':kind=='data',
               'interval':kind=='think','auto_attach':kind=='think','entity_name':kind=='think'}
        for field,enabled in rules.items():
            widget=getattr(self,field)
            widget.setVisible(enabled)
            label=self.property_form.labelForField(widget)
            if label is not None:label.setVisible(enabled)
        if kind=='function':
            self.owner.setToolTip('留空生成全局函数；选择 Namespace 则生成成员函数')

    def accept(self):
        super().accept()

    def apply(self):
        kind=self.type.currentData()
        self.section.kind=kind;self.section.name=self.name.text().strip()
        preserved={key:value for key,value in self.section.args.items() if key not in
                   ('owner','params','param_types','container','interval','auto_attach','entity_name')}
        if kind=='function':
            preserved.update(owner=self.owner.currentData(),params=[x.strip() for x in self.params.text().split(',') if x.strip()],
                             param_types=[x.strip().lower() or 'auto' for x in self.param_types.text().split(',')] if self.param_types.text().strip() else [])
        elif kind=='think':
            preserved.update(interval=self.interval.text().strip() or '0.5',
                             auto_attach=self.auto_attach.isChecked(),entity_name=self.entity_name.text().strip())
        elif kind=='data':preserved['container']=self.container.currentText()
        self.section.args=preserved
        return self.section

class BranchEditor(QDialog):
    def __init__(self, title, blocks, catalog, parent=None):
        super().__init__(parent);self.setWindowTitle('内部积木：'+title);self.resize(630,400)
        self.catalog=catalog;self.blocks=deepcopy(blocks)
        outer=QVBoxLayout(self);self.list=QListWidget();outer.addWidget(self.list)
        row=QHBoxLayout(); outer.addLayout(row)
        add=QPushButton('添加积木');edit=QPushButton('编辑');remove=QPushButton('删除');up=QPushButton('上移');down=QPushButton('下移')
        for w in (add,edit,remove,up,down):row.addWidget(w)
        add.clicked.connect(self.add);edit.clicked.connect(self.edit);remove.clicked.connect(self.remove)
        up.clicked.connect(lambda:self.shift(-1));down.clicked.connect(lambda:self.shift(1))
        self.list.itemDoubleClicked.connect(lambda _:self.edit())
        bb=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);bb.accepted.connect(self.accept);bb.rejected.connect(self.reject);outer.addWidget(bb)
        self.refresh()
    def refresh(self):
        self.list.clear()
        for b in self.blocks:
            self.list.addItem(f'{BLOCK_NAMES.get(b.kind,b.kind)}  {str(b.args)[:85]}')
    def chosen(self):return self.list.currentRow()
    def add(self):
        names=list(BLOCK_NAMES.items());labels=[name for k,name in names if k!='event']
        value,ok=QInputDialog.getItem(self,'添加内部积木','类型',labels,0,False)
        if ok:
            kind=next(k for k,label in names if label==value)
            new=new_block(kind)
            dialog=BlockEditor(new,self.catalog,self)
            if dialog.exec():self.blocks.append(dialog.apply());self.refresh()
    def edit(self):
        i=self.chosen()
        if i<0:return
        dialog=BlockEditor(self.blocks[i],self.catalog,self)
        if dialog.exec():self.blocks[i]=dialog.apply();self.refresh()
    def remove(self):
        i=self.chosen()
        if i>=0:self.blocks.pop(i);self.refresh()
    def shift(self,delta):
        i=self.chosen();j=i+delta
        if 0<=i<len(self.blocks) and 0<=j<len(self.blocks):
            self.blocks[i],self.blocks[j]=self.blocks[j],self.blocks[i];self.refresh();self.list.setCurrentRow(j)

class BlockEditor(QDialog):
    def __init__(self, block, catalog, parent=None, document=None):
        super().__init__(parent)
        self.block=deepcopy(block);self.catalog=catalog
        self.document=document or getattr(parent,'current_document',None) or getattr(parent,'document',None)
        self._linked_expressions={}
        self.setWindowTitle('编辑积木 — '+BLOCK_NAMES.get(block.kind,block.kind));self.resize(570,400)
        self.main=QVBoxLayout(self);self.form=QFormLayout();self.main.addLayout(self.form)
        self.controls={}
        if block.kind=='netprop':self.create_netprop_form()
        elif block.kind=='method':self.create_method_form()
        elif block.kind=='call':self.create_call_form()
        elif block.kind=='event':self.create_event_form()
        elif block.kind=='entity_for':self.create_entity_for_form()
        else:self.create_generic_form()
        if self.block.branches:
            group=QGroupBox('内部容器（独立编辑，不受普通积木层级限制）');g=QVBoxLayout(group)
            for branch in self.block.branches:
                btn=QPushButton('编辑 '+branch+' ...');btn.clicked.connect(lambda _,key=branch:self.edit_branch(key));g.addWidget(btn)
            self.main.addWidget(group)
        self.main.addStretch(1)
        bb=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);bb.accepted.connect(self.accept);bb.rejected.connect(self.reject);self.main.addWidget(bb)
    def line(self,key,label=None):
        value=self.block.args.get(key,'')
        if isinstance(value,list):value=', '.join(map(str,value))
        if isinstance(value,dict) and value.get('kind')!='multiline':
            self._linked_expressions[key]=deepcopy(value)
            value=expression(value)
        control=QLineEdit(str(value));self.controls[key]=control
        self.form.addRow(label or key,control)
        return control
    def combo(self,key,options,label=None,editable=False):
        c=QComboBox();c.setEditable(editable)
        if key in ('scope','container_type','array'):
            for item in options:c.addItem(translated_text(item),item)
            c.setCurrentIndex(max(0,c.findData(str(self.block.args.get(key,'')))))
        else:
            c.addItems(list(options));c.setCurrentText(str(self.block.args.get(key,'')))
        self.controls[key]=c;self.form.addRow(label or key,c);return c
    def create_generic_form(self):
        for key,value in self.block.args.items():
            if key=='scope':self.combo(key,['root','auto','local','无','static'],'变量作用域')
            elif key=='container_type':self.combo(key,['普通','Table','Set'],'数据类型（Set = []）')
            elif key=='search':self.combo(key,list(ENTITY_SEARCH_MODES),'查找方式')
            elif key=='source' and self.block.kind=='raw':
                widget=QPlainTextEdit(str(value));self.controls[key]=widget;self.form.addRow('Squirrel 原始代码',widget)
            elif key=='value' and isinstance(value,dict) and value.get('kind')=='multiline':
                w=QPlainTextEdit(value.get('value',''));self.controls[key]=w;self.form.addRow('多行文本',w)
            else:self.line(key,{'name':'变量名称（右键可改）','output':'结果变量（空=忽略返回值）','parameters':'参数表达式（英文逗号隔开）','value':'初始值 / 表达式','source':'遍历目标','condition':'布尔表达式'}.get(key,key))
        if self.block.kind=='var':
            btn=QPushButton('将值切换为多行字符串编辑器');btn.clicked.connect(self.multiline);self.main.addWidget(btn)
        selectable=[key for key in ('target','value','source','condition','filter') if key in self.controls and isinstance(self.controls[key],QLineEdit)]
        if selectable:
            btn=QPushButton('编辑变量链 [xxx].[yyy].[zzz] ...')
            btn.clicked.connect(lambda:self.chain_dialog(selectable))
            self.main.addWidget(btn)
        if self.block.kind=='if':
            btn=QPushButton('添加 Else If 分支');btn.clicked.connect(self.add_elif);self.main.addWidget(btn)
        if self.block.kind=='for' and 'source' in self.controls:
            btn=QPushButton('编辑 range(起点, 终点, 步长) 辅助函数');btn.clicked.connect(self.range_builder);self.main.addWidget(btn)
    def create_entity_for_form(self):
        self.line('variable','当前实体变量名')
        combo=QComboBox()
        for method,meta in ENTITY_SEARCH_MODES.items():combo.addItem(translated_text(meta['label']),method)
        combo.setCurrentIndex(max(0,combo.findData(self.block.args.get('search','FindByClassname'))))
        self.controls['search']=combo
        self.form.addRow('实体查找方式',combo)
        self._entity_optional={}
        for key in ('filter','origin','radius'):
            widget=self.line(key,ENTITY_FIELD_LABELS[key])
            if key not in self.block.args:widget.setText(ENTITY_FIELD_DEFAULTS[key])
            self._entity_optional[key]=widget
        def update(i):
            method=combo.itemData(i)
            if method not in ENTITY_SEARCH_MODES:return
            fields=search_fields(method)
            for key,widget in self._entity_optional.items():
                show=key in fields
                widget.setVisible(show)
                label=self.form.labelForField(widget)
                if label:label.setVisible(show)
                widget.setToolTip(translated_text(ENTITY_SEARCH_MODES[method]['hint']))
            combo.setToolTip(translated_text(ENTITY_SEARCH_MODES[method]['hint']))
        combo.currentIndexChanged.connect(update)
        update(combo.currentIndex())

    def chain_dialog(self,keys):
        key,ok=QInputDialog.getItem(self,'链式编辑','替换哪个输入槽？',keys,0,False)
        if not ok:return
        dlg=ChainEditor(self.document,self)
        if dlg.exec():
            expr=dlg.path_node()
            self._linked_expressions[key]=expr
            self.controls[key].setText(expression(expr))

    def range_builder(self):
        start,ok=QInputDialog.getText(self,'Range','起点',text='0')
        if not ok:return
        stop,ok=QInputDialog.getText(self,'Range','终点（不包含）',text='10')
        if not ok:return
        step,ok=QInputDialog.getText(self,'Range','步长（不能为 0）',text='1')
        if not ok:return
        if step.strip() in ('0','0.0'):
            QMessageBox.warning(self,'无效步长','步长不能为零');return
        self.controls['source'].setText(f'range({start}, {stop}, {step})')

    def multiline(self):
        w=self.controls.get('value')
        raw=w.text() if isinstance(w,QLineEdit) else w.toPlainText()
        self.form.removeRow(w)
        edit=QPlainTextEdit(raw);self.form.addRow('多行文本',edit);self.controls['value']=edit
        self.block.args['value']={'kind':'multiline','value':raw}
    def add_elif(self):
        condition,ok=QInputDialog.getText(self,'Else If','判断表达式')
        if not ok:return
        dialog=BranchEditor('Else If',[],self.catalog,self)
        if dialog.exec():self.block.args.setdefault('elif',[]).append({'condition':condition,'blocks':[b.to_dict() for b in dialog.blocks]})
    def edit_branch(self,key):
        editor=BranchEditor(key,self.block.branches[key],self.catalog,self)
        if editor.exec():self.block.branches[key]=editor.blocks
    def create_call_form(self):
        options=['printl','Time','SpawnEntityFromTable','IncludeScript','AddThinkToEnt']
        if self.document:
            for section in self.document.sections:
                if section.kind=='function':
                    owner=section.args.get('owner','')
                    options.append((owner+'.' if owner else '')+section.name)
        cb=self.combo('function',sorted(set(options)),'调用自定义函数',True)
        self.line('parameters','参数插槽（动态展开）')
        self.line('output','右侧变量（若无返回值则留空）')
        cb.currentTextChanged.connect(self.update_function_params)
        self.update_function_params()

    def update_function_params(self):
        selected=self.controls['function'].currentText()
        if self.document:
            for section in self.document.sections:
                if section.kind != 'function':continue
                owner=section.args.get('owner','')
                label=(owner+'.' if owner else '')+section.name
                if label==selected:
                    self.controls['parameters'].setPlaceholderText(', '.join(section.args.get('params',[])) or '(无参数)')
                    return

    def create_event_form(self):
        self.combo('event',[r['name'] for r in self.catalog.events()],'原版事件',True)
        self.line('env','回调变量（圆形可拖动）')
    def create_method_form(self):
        owners=sorted(set(r['owner'] for r in self.catalog.methods() if r['owner']!='Global'))
        self.combo('owner',owners,'API 类型')
        self.combo('method',[],'官方方法',True)
        self.line('target','对象插槽')
        self.line('parameters','方法参数')
        self.line('output','右侧结果变量')
        self.controls['owner'].currentTextChanged.connect(self.update_methods)
        self.controls['method'].currentTextChanged.connect(self.update_method_params)
        self.update_methods()
    def update_methods(self):
        owner=self.controls['owner'].currentText()
        combo=self.controls['method'];current=self.block.args.get('method','')
        combo.blockSignals(True);combo.clear();combo.addItems([r['name'] for r in self.catalog.methods(owner=owner)]);combo.setCurrentText(current)
        combo.blockSignals(False);self.update_method_params()
    def update_method_params(self):
        owner=self.controls['owner'].currentText();name=self.controls['method'].currentText()
        items=[r for r in self.catalog.methods(owner=owner) if r['name']==name]
        if items:self.controls['parameters'].setPlaceholderText(items[0]['parameters'] or '(无参数)')
    def create_netprop_form(self):
        self.combo('mode',['get','set'],'读 / 写')
        self.line('target','实体对象')
        from .netprop_picker import NetPropPicker
        pick=QPushButton('选择 NetProp（实体大类 → 具体属性）')
        self.form.addRow('属性',pick)
        summary=QLabel('');self.form.addRow('当前选择',summary)
        self._netprop_summary=summary
        def choose():
            dialog=NetPropPicker(self.block.args.get('table',''),self.block.args.get('property',''))
            if dialog.exec() and dialog.selection:
                self.block.args.update(dialog.selection)
                self._netprop_summary.setText(self.block.args['table']+' / '+self.block.args['property']+' ('+self.block.args['prop_type']+')')
        pick.clicked.connect(choose)
        summary.setText(str(self.block.args.get('table',''))+' / '+str(self.block.args.get('property','')))
        self.line('value','Set 的值')
        self.line('output','Get 的结果变量')
        self.block.args['array']='是' if self.block.args.get('array') else '否'
        self.combo('array',['否','是'],'数组 API（仅确认实际属性为数组时使用）')
        self.line('index','数组索引')
        self.controls['mode'].currentTextChanged.connect(self.update_netprop_ui)
        self.update_netprop_ui()
    def update_netprop_ui(self):
        mode=self.controls['mode'].currentText()
        self.controls['value'].setEnabled(mode=='set')
        self.controls['output'].setEnabled(mode=='get')
    def apply(self):
        for key,widget in self.controls.items():
            if isinstance(widget,QComboBox):value=widget.currentData() if key in ('search','scope','container_type','array') else widget.currentText()
            elif isinstance(widget,QPlainTextEdit):value=widget.toPlainText()
            else:value=widget.text().strip()
            if key=='parameters':
                # 用户可用 JSON 数组形式输入带逗号的复杂参数
                if value.startswith('['):
                    try: value=json.loads(value)
                    except json.JSONDecodeError:value=split_parameters(value)
                else:value=split_parameters(value)
            if key=='array':value=(value=='是')
            if key in self._linked_expressions and isinstance(widget,QLineEdit) and value==expression(self._linked_expressions[key]):
                value=deepcopy(self._linked_expressions[key])
            if key=='value' and isinstance(widget,QPlainTextEdit) and self.block.kind=='var':
                value={'kind':'multiline','value':value}
            self.block.args[key]=value
        if self.block.kind=='entity_for':normalize_entity_search(self.block,self.block.args.get('search','FindByClassname'))
        if self.block.kind=='var':
            dtype=self.block.args.get('container_type','普通')
            if dtype in ('Table','Set') and str(self.block.args.get('value','0')).strip() in ('','0','null'):
                self.block.args['value']='{}' if dtype=='Table' else '[]'
        return self.block
