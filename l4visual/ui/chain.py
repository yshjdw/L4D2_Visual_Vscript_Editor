from __future__ import annotations
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QComboBox,QListWidget,
                                QPushButton,QHBoxLayout,QInputDialog,QDialogButtonBox,QLabel,QMessageBox)
from ..codegen import expression
from .localization import translated_text
from ..data_definitions import container_kind,linked_definition


class ChainEditor(QDialog):
    """Path selector for member .xxx and numeric-expression [index] access.

    Typed paths are suggested from the project AST, not from random identifier
    spelling. Unknown dynamic members remain editable.
    """
    def __init__(self, document=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('链式变量访问 [xxx].[yyy].[zzz]')
        self.resize(600,470)
        self.document=document
        self.segments=[]
        root_names={'player','weapon','entity','Entities','Director','NetProps','Convars'}
        if document:
            for s in document.sections:
                if s.kind=='namespace':root_names.add(s.name)
                if s.kind=='data' and not s.args.get('parent_section_id'):
                    owner=s.args.get('owner','')
                    root_names.add((owner+'.' if owner else '')+s.name)
                if s.kind=='function':
                    root_names.update(s.args.get('params',[]))
                for b in s.blocks:
                    if b.kind in ('var','method','call','netprop'):
                        key='name' if b.kind=='var' else 'output'
                        if b.args.get(key):root_names.add(str(b.args[key]))
        outer=QVBoxLayout(self)
        outer.addWidget(QLabel('按变量结构递进选择。Table 使用 .成员；Set 使用 [数值/数值表达式]。'))
        form=QFormLayout();outer.addLayout(form)
        self.root=QComboBox();self.root.setEditable(True);self.root.addItems(sorted(root_names))
        form.addRow('根变量',self.root)
        self.steps=QListWidget();outer.addWidget(self.steps)
        tools=QHBoxLayout();outer.addLayout(tools)
        for label,callback in [('＋ Table 成员',self.member),('＋ Set 索引',self.index),('编辑最后一级',self.edit),('移除最后一级',self.remove)]:
            button=QPushButton(label);button.clicked.connect(callback);tools.addWidget(button)
        self.hint=QLabel();outer.addWidget(self.hint)
        self.output=QLabel();self.output.setWordWrap(True);outer.addWidget(self.output)
        self.root.currentTextChanged.connect(self.refresh)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);outer.addWidget(buttons)
        self.refresh()

    def resolve(self):
        if not self.document:return None, None
        root=self.root.currentText().strip().removeprefix('::')
        section=next((s for s in self.document.sections if s.kind=='namespace' and s.name==root),None)
        current_data=next((s for s in self.document.sections
                           if s.kind=='data' and (s.args.get('owner','')+'.' if s.args.get('owner') else '')+s.name==root and not s.args.get('parent_section_id')),None)
        container='Table' if section else current_data.args.get('container') if current_data else None
        for kind,value in self.segments:
            if kind=='index':
                if container!='Set':return None,None
                # A Set element has no declared field in the index itself; if the
                # element was defined from an item var, use its nested schema.
                if current_data:
                    items=[b for b in current_data.blocks if b.kind=='var']
                    try:
                        idx=int(value)
                        block=items[idx] if 0<=idx<len(items) else None
                    except ValueError: block=None
                else:block=None
            else:
                if container!='Table':return None,None
                blocks=(current_data.blocks if current_data else section.blocks if section else [])
                block=next((b for b in blocks if b.kind=='var' and b.args.get('name')==value),None)
            if block is None:return None,None
            current_data=linked_definition(self.document,block.id)
            container=current_data.args.get('container') if current_data else container_kind(block)
            section=None
        return container, current_data or section

    def suggestion(self):
        container,section=self.resolve()
        if container=='Table' and section:
            return [str(b.args.get('name','')) for b in section.blocks if b.kind=='var']
        return []

    def member(self):
        container,_=self.resolve()
        if container=='Set':
            QMessageBox.information(self,'当前是 Set','当前为 [] 数组，请改用数值索引槽。')
            return
        names=self.suggestion()
        if names:value,ok=QInputDialog.getItem(self,'Table 成员','选择成员（支持手动输入）',names,0,True)
        else:value,ok=QInputDialog.getText(self,'Table 成员','成员名称')
        if ok and value.strip():self.segments.append(('member',value.strip()));self.refresh()

    def index(self):
        container,_=self.resolve()
        if container=='Table':
            QMessageBox.information(self,'当前是 Table','当前为 {} 成员访问，通常应选择成员名称。')
            return
        value,ok=QInputDialog.getText(self,'Set 数字索引','数字或返回数字的表达式',text='0')
        if ok and value.strip():self.segments.append(('index',value.strip()));self.refresh()

    def edit(self):
        if not self.segments:return
        kind,old=self.segments[-1]
        value,ok=QInputDialog.getText(self,'编辑访问层级','成员名称' if kind=='member' else '索引表达式',text=old)
        if ok and value.strip():self.segments[-1]=(kind,value.strip());self.refresh()

    def remove(self):
        if self.segments:self.segments.pop();self.refresh()

    def path_node(self):
        root=self.root.currentText().strip() or 'player'
        if self.document and not root.startswith('::') and (any(s.kind=='namespace' and s.name==root for s in self.document.sections) or any(s.kind=='data' and (s.args.get('owner','')+'.' if s.args.get('owner') else '')+s.name==root and not s.args.get('parent_section_id') for s in self.document.sections)):
            root='::'+root
        result={'kind':'variable','value':root}
        for kind,value in self.segments:
            if kind=='member':result={'kind':'member','base':result,'name':value}
            else:result={'kind':'index','base':result,'index':value}
        return result

    def refresh(self):
        self.steps.clear()
        for kind,value in self.segments:self.steps.addItem(translated_text('成员 . ' if kind=='member' else '索引 [ ] ')+value)
        container,_=self.resolve()
        self.hint.setText(translated_text('当前数据结构：')+(container or translated_text('未知（允许手动添加）')))
        try:self.output.setText(translated_text('生成：')+expression(self.path_node()))
        except ValueError as exc:self.output.setText(translated_text('无效的成员名称：')+str(exc))
