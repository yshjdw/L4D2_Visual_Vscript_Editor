from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QScrollArea,QWidget,QGridLayout,QInputDialog
from ..event_metadata import EVENT_FIELDS
from .localization import translated_text
from ..data_definitions import linked_definition,container_kind,parse_simple_initializer

class MemberPicker(QDialog):
    """Top-level window: LMB selects a member; RMB descends into nested data.
    The back X on the toolbar returns to the previous member level.
    """
    def __init__(self,document,block,initial_path,parent=None,selected_path=None):
        super().__init__(None)
        self.setWindowTitle('选择成员变量 · '+initial_path)
        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(490,320)
        self.document=document;self.block=block;self.steps=[];self.initial=initial_path
        self.value=None;self.selected_path=selected_path;self.root=QVBoxLayout(self);self.panel=None;self.refresh()
    def current(self):
        current=self.block
        for key,child in self.steps:current=child
        return current
    def children(self):
        current=self.current()
        if not current:return []
        if current.kind=='event':
            name=current.args.get('event','')
            return [(n,None) for n in EVENT_FIELDS.get(name,[])]
        section=linked_definition(self.document,current.id) if self.document else None
        if section:
            return [(b.args.get('name',str(i)),b) for i,b in enumerate(section.blocks) if b.kind=='var']
        parsed=parse_simple_initializer(current.args.get('value',''),container_kind(current)) if container_kind(current) else None
        if parsed is not None:return [(b.args.get('name',str(i)),b) for i,b in enumerate(parsed)]
        return []
    def is_array(self):
        current=self.current()
        return current is not None and container_kind(current)=='Set'
    def path(self):
        result=self.initial
        for key,child in self.steps:
            result += '['+str(int(key))+']' if isinstance(key,str) and key.isdecimal() and self.is_array() else '.'+str(key)
        return result
    def select(self,key,child):
        full=self.initial
        current=self.block
        for prev,c in self.steps+[(key,child)]:
            full += '['+str(int(prev))+']' if container_kind(current)=='Set' and str(prev).isdecimal() else '.'+str(prev)
            current=c
        self.value=full;self.accept()
    def descend(self,key,child):
        if child is None or not container_kind(child):return
        self.steps.append((key,child));self.refresh()
    def choose_root(self):
        self.value=self.initial
        self.accept()
    def choose_current(self):
        if not self.steps:
            self.choose_root()
            return
        full=self.initial
        current=self.block
        for key,child in self.steps:
            full += "["+str(int(key))+"]" if container_kind(current)=="Set" and str(key).isdecimal() else "."+str(key)
            current=child
        self.value=full
        self.accept()
    def back(self):
        if self.steps:self.steps.pop();self.refresh()
        else:self.reject()
    def refresh(self):
        if self.panel is not None:
            self.root.removeWidget(self.panel)
            self.panel.deleteLater()
        self.panel=QWidget(self)
        lay=QVBoxLayout(self.panel)
        self.root.addWidget(self.panel)
        bar=QHBoxLayout();lay.addLayout(bar)
        back=QPushButton('× 返回上一层');back.clicked.connect(self.back);bar.addWidget(back)
        root_button=QPushButton('● 根变量');root_button.clicked.connect(self.choose_root);bar.addWidget(root_button)
        current_button=QPushButton('使用当前层');current_button.clicked.connect(self.choose_current);bar.addWidget(current_button)
        label=QLabel(' / '.join([self.initial]+[str(s[0]) for s in self.steps]));bar.addWidget(label,1)
        if self.selected_path:label.setToolTip(translated_text('当前已选择：')+self.selected_path+translated_text('；可选择根变量或重新选择成员'))
        rows=self.children();array=self.is_array()
        if not rows and array:
            rows=[(str(i),None) for i in range(5)]
        if not rows:
            lay.addWidget(QLabel('暂无已收录成员，可使用下方手动输入添加访问路径。'))
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        holder=QWidget();grid=QGridLayout(holder);grid.setSpacing(12)
        for i,(key,child) in enumerate(rows):
            btn=QPushButton(str(key));btn.setMinimumSize(105,49 if array else 32)
            from ..official_docs import event_field_help
            doc_hint=event_field_help(self.block.args.get('event',''),str(key)) if self.block and self.block.kind=='event' else ''
            btn.setToolTip(translated_text('左键：选择此成员；右键：如果是复杂成员则进入下一层')+('\n'+doc_hint if doc_hint else ''))
            btn.clicked.connect(lambda checked=False,k=key,c=child:self.select(k,c))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda p,k=key,c=child:self.descend(k,c))
            grid.addWidget(btn,i//(5 if array else 2),i%(5 if array else 2))
        scroll.setWidget(holder);lay.addWidget(scroll,1)
        row=QHBoxLayout();lay.addLayout(row)
        manual=QPushButton('手动填写成员 / 数字索引');row.addWidget(manual)
        def add_manual():
            value,ok=QInputDialog.getText(self,'成员名称或索引','成员名称（Set 必须输入整数）')
            if ok and value.strip() and (not array or value.strip().isdecimal()):self.select(value.strip(),None)
        manual.clicked.connect(add_manual)
        from .localization import localize_widget_tree
        localize_widget_tree(self.panel)
