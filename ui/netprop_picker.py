from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
    QListWidget,QTreeWidget,QTreeWidgetItem,QPushButton,QStackedWidget,QWidget)
from ..netprop_catalog import list_classes,list_properties,api_type
from .localization import translated_text

class NetPropPicker(QDialog):
    """Choose a documented server-class and a netprop; no free-form property input."""
    def __init__(self,table='',prop='',parent=None):
        super().__init__(None)
        self.setWindowFlag(Qt.Window,True)
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(860,640)
        self.setWindowTitle('选择 L4D2 NetProp · 实体类 / 属性')
        self.setMinimumSize(680,520)
        self.selection=None
        self.current_class=table if table in list_classes() else ''
        root=QVBoxLayout(self)
        self.pages=QStackedWidget();root.addWidget(self.pages)
        page1=QWidget();one=QVBoxLayout(page1)
        one.addWidget(QLabel('第一步：选择实体网络类（例如 CTerrorPlayer、CBaseCombatWeapon）'))
        self.class_search=QLineEdit();self.class_search.setPlaceholderText('按类名筛选');one.addWidget(self.class_search)
        self.classes=QListWidget();one.addWidget(self.classes)
        self.pages.addWidget(page1)
        page2=QWidget();two=QVBoxLayout(page2)
        header=QHBoxLayout();two.addLayout(header)
        back=QPushButton('← 返回实体类别');back.clicked.connect(lambda:self.pages.setCurrentIndex(0));header.addWidget(back)
        self.class_label=QLabel();header.addWidget(self.class_label,1)
        self.prop_search=QLineEdit();self.prop_search.setPlaceholderText('查找属性名 / 成员路径');two.addWidget(self.prop_search)
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['属性 / 嵌套表','数据类型','Offset']);self.tree.setColumnWidth(0,390);two.addWidget(self.tree)
        two.addWidget(QLabel('双击末级属性选择；数组属性（如 m_iAmmo）会启用 Array 模式和索引槽。\n资料分组名不等于运行时属性名，保存时自动使用可调用的属性键。'))
        self.pages.addWidget(page2)
        self.class_search.textChanged.connect(self.refresh_classes)
        self.classes.itemDoubleClicked.connect(lambda item:self.enter_class(item.text()))
        self.prop_search.textChanged.connect(self.refresh_props)
        self.tree.itemDoubleClicked.connect(self.choose_property)
        self.refresh_classes()
        if self.current_class:
            self.enter_class(self.current_class)
            if prop:
                self.prop_search.setText(prop)
    def refresh_classes(self):
        self.classes.clear();self.classes.addItems(list_classes(self.class_search.text()))
    def enter_class(self,name):
        self.current_class=name;self.class_label.setText(name);self.prop_search.clear()
        self.pages.setCurrentIndex(1);self.refresh_props()
    def refresh_props(self):
        self.tree.clear();nodes={}
        for p in list_properties(self.current_class,self.prop_search.text()):
            parts=p.get('document_path',p['name']).split('.');parent=None
            for i,part in enumerate(parts):
                key=tuple(parts[:i+1]);item=nodes.get(key)
                if item is None:
                    item=QTreeWidgetItem(parent if parent is not None else self.tree,[part,'',''])
                    nodes[key]=item
                if i==len(parts)-1:
                    item.setText(1,p['type']+(' ['+str(p.get('length','?'))+']' if p['type']=='array' else ''));item.setText(2,str(p['offset']))
                    item.setData(0,Qt.UserRole,p)
                    item.setToolTip(0,(translated_text('注意：SendTable 数组范围，不保证 VScript 可直接访问。')+'\n' if p.get('access','').startswith('unverified') else '')+translated_text('运行时：')+p['name']+'\n'+translated_text('资料分组：')+p.get('document_path',p['name'])+'\n'+translated_text('类型：')+p['type']+'\nOffset: '+str(p['offset'])+'\n'+translated_text('来源：L4D2 NetProps 文档'))
                parent=item
        self.tree.expandAll()
    def choose_property(self,item,column=0):
        p=item.data(0,Qt.UserRole)
        if not isinstance(p,dict):return
        self.selection={'table':self.current_class,'property':p['name'],'prop_type':api_type(p), 'netprop_type':p['type'],'array':p['type']=='array','document_path':p.get('document_path',p['name'])}
        self.accept()
