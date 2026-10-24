"""Draggable ScriptScope members shared by every open Data workspace."""
import json
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
from ..scope_members import member_sources, scope_binding
from ..display_profile import current_profile

MIME_SCOPE_MEMBER='application/x-l4dv-scope-member'

class ScopeMemberToken(QLabel):
    def __init__(self,section,block,parent=None):
        profile = current_profile()
        label = section.name + '.' + str(block.args.get('name', ''))
        super().__init__(('● ' if profile.style == 'general' else '') + label, parent)
        self.section=section;self.block=block;self._press=None
        self.setStyleSheet('background:#e9c17b;color:#3e301d;padding:6px;border-radius:9px;')
        self.setToolTip('')
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:self._press=event.position().toPoint();event.accept()
    def mouseMoveEvent(self,event):
        if self._press is None or (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None
        mime=QMimeData();mime.setData(MIME_SCOPE_MEMBER,json.dumps({
            'source_section_id':self.section.id,'member_id':self.block.id,
            'name':self.block.args['name']}).encode())
        drag=QDrag(self);drag.setMimeData(mime);drag.exec(Qt.CopyAction)
    def mouseReleaseEvent(self,event):self._press=None

class ScopeMemberPalette(QFrame):
    """Bottom-docked, horizontally scrolling ScriptScope reference tray."""
    def __init__(self,document,destination,parent=None):
        super().__init__(parent)
        self.document=document
        self.destination=destination
        self.setObjectName('scopeMemberTray')
        self.setStyleSheet('#scopeMemberTray { border:1px solid #56739d; background:#172334; border-radius:8px; }')
        outer=QVBoxLayout(self)
        outer.setContentsMargins(10,8,10,8)
        heading=QHBoxLayout()
        title=QLabel('ScriptScope 成员引用库  ·  拖入目标窗口自动设为「仅引用」')
        title.setStyleSheet('font-weight:bold; color:#dbeafe; border:0;')
        heading.addWidget(title,1)
        refresh=QPushButton('刷新成员')
        refresh.clicked.connect(self.reload)
        heading.addWidget(refresh)
        outer.addLayout(heading)
        self.scroll=QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFixedHeight(75)
        outer.addWidget(self.scroll)
        self.reload()
    def reload(self):
        content=QFrame()
        lay=QHBoxLayout(content)
        lay.setContentsMargins(4,4,4,4)
        count=0
        for section,block in member_sources(self.document,self.destination):
            token=ScopeMemberToken(section,block)
            binding=scope_binding(self.document,section) or '?'
            if current_profile().language=='en':
                token.setToolTip('Defined in: '+section.name+'\nEntity expression: '+binding
                    +'\nDrag to reference this member through the destination ScriptScope.'
                    +'\nReference only: does not create the member on another entity.')
            else:
                token.setToolTip('定义来源：'+section.name+'\n实体表达式：'+binding
                    +'\n拖入后使用目标 ScriptScope 的变量名引用该成员。'
                    +'\n仅引用：不会在其他实体上自动创建此成员。')
            token.setMinimumWidth(140)
            lay.addWidget(token)
            count+=1
        if not count:
            label=QLabel('当前脚本中尚未定义 ScriptScope 成员；请先在任一 ScriptScope 数据工作区添加成员，再刷新。')
            label.setStyleSheet('color:#cbd5e1; border:0;')
            lay.addWidget(label)
        lay.addStretch(1)
        self.scroll.setWidget(content)
        from .localization import localize_widget_tree
        localize_widget_tree(self)
