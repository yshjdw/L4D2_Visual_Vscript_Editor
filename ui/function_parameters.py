"""Manage the optional, editor-only schema of structured function arguments."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QTreeWidget,QTreeWidgetItem,
    QPushButton,QInputDialog,QMessageBox,QComboBox,QDialogButtonBox,QLabel)
from ..codegen import IDENT


class FunctionParameterEditor(QDialog):
    def __init__(self,section,parameter,parent=None):
        super().__init__(parent)
        self.section=section;self.parameter=parameter
        self.setWindowTitle('形参结构与成员 · '+parameter)
        self.resize(550,470)
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel('此结构仅供编辑器显示和拖放，不会在函数中创建额外变量。\n选中成员后点“使用选中路径”，可以将它拖进函数内部表达式槽。'))
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['字段 / 索引','类型'])
        layout.addWidget(self.tree)
        controls=QHBoxLayout();layout.addLayout(controls)
        add=QPushButton('添加成员');add.clicked.connect(self.add_member);controls.addWidget(add)
        remove=QPushButton('删除成员');remove.clicked.connect(self.remove_member);controls.addWidget(remove)
        self.selected_path=parameter
        choose=QPushButton('使用选中路径');choose.clicked.connect(self.choose);layout.addWidget(choose)
        buttons=QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.schema=dict(section.args.get('param_schema',{}))
        self.schema.setdefault(parameter,[])
        self.rebuild()

    def rebuild(self):
        self.tree.clear()
        def insert(parent,rows):
            for row in rows:
                item=QTreeWidgetItem([row['name'],row.get('type','普通')])
                if parent is None:self.tree.addTopLevelItem(item)
                else:parent.addChild(item)
                insert(item,row.get('children',[]))
        insert(None,self.schema[self.parameter]);self.tree.expandAll()

    def _path(self,item):
        path=self.parameter
        chain=[]
        while item is not None:
            chain.append(item.text(0));item=item.parent()
        for part in reversed(chain):
            path += '['+part+']' if part.isdecimal() else '.'+part
        return path

    def choose(self):
        item=self.tree.currentItem()
        self.selected_path=self._path(item) if item else self.parameter
        self.save();self.accept()

    def _row_for(self,item):
        if item is None:return self.schema[self.parameter]
        chain=[]
        while item is not None:
            chain.append(item.text(0));item=item.parent()
        rows=self.schema[self.parameter]
        for key in reversed(chain):
            row=next((v for v in rows if v['name']==key),None)
            if row is None:return []
            rows=row.setdefault('children',[])
        return rows

    def add_member(self):
        item=self.tree.currentItem()
        name,ok=QInputDialog.getText(self,'新建形参成员','字段名（Array 可用数字索引）')
        if not ok:return
        name=name.strip()
        if not IDENT.fullmatch(name) and not name.isdecimal():
            QMessageBox.warning(self,'无效名称','字段需要合法标识符，Array 索引可以使用数字。');return
        options=['普通','Table','Set']
        kind,ok=QInputDialog.getItem(self,'成员类型','类型',options,0,False)
        if not ok:return
        rows=self._row_for(item)
        if any(row['name']==name for row in rows):return
        rows.append({'name':name,'type':kind,'children':[]})
        self.save();self.rebuild()

    def remove_member(self):
        item=self.tree.currentItem()
        if item is None:return
        parent=item.parent();rows=self._row_for(parent)
        rows[:]=[row for row in rows if row['name']!=item.text(0)]
        self.save();self.rebuild()

    def save(self):
        self.section.args['param_schema']=self.schema
