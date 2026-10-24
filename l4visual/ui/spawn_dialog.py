from PySide6.QtCore import Qt
import json
from ..codegen import expression
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QGridLayout,QCheckBox,QLineEdit,QLabel,QComboBox,QDialogButtonBox,QScrollArea,QWidget,QTreeWidget,QTreeWidgetItem,QPushButton
from ..spawn_catalog import SPAWN_GROUPS, SPAWN_GROUP_META, CONFIG_FIELDS,enabled_config,DOCUMENTATION
from ..display_profile import current_profile
class SpawnConfigDialog(QDialog):
    def __init__(self,block,parent=None):
        super().__init__(parent,Qt.Dialog)
        self.block=block;self.setWindowTitle('Spawn configuration - SpawnEntityFromTable' if current_profile().language=='en' else 'Summon 配置 - SpawnEntityFromTable');self.resize(650,690)
        main=QVBoxLayout(self)
        main.addWidget(QLabel('Only enabled KeyValues are emitted into .nut.' if current_profile().language=='en' else '仅启用的配置生成到 .nut。未启用的配置在生成时完全省略。'))
        profile=current_profile()
        english=profile.language=='en'
        self._original_classname=block.args.get('classname','info_target')
        if isinstance(self._original_classname, dict):
            try:
                computed=expression(self._original_classname)
                initial=json.loads(computed) if computed.startswith('"') else computed
            except (ValueError, TypeError, KeyError):
                initial=''
        else:
            initial=str(self._original_classname)
        self._initial_display=str(initial)
        self.classname=QLineEdit(self._initial_display)
        self.classname.setPlaceholderText('Entity classname (weapon_rifle_ak47)' if english else '实体 Classname（如 weapon_rifle_ak47）')
        main.addWidget(self.classname)
        main.addWidget(QLabel('Browse by category (double-click a classname):' if english else '按二级分类选择（双击实体名填入）：'))
        self.class_tree=QTreeWidget()
        self.class_tree.setHeaderHidden(True)
        self.class_tree.setMinimumHeight(140)
        for group,items in SPAWN_GROUPS.items():
            zh,en,desc_zh,desc_en=SPAWN_GROUP_META[group]
            header=QTreeWidgetItem([en if english else zh]);header.setToolTip(0,desc_en if english else desc_zh)
            self.class_tree.addTopLevelItem(header)
            for name in items:
                child=QTreeWidgetItem([name]);child.setData(0,Qt.UserRole,name)
                child.setToolTip(0,desc_en if english else desc_zh)
                header.addChild(child)
        self.class_tree.itemDoubleClicked.connect(lambda item,column:self.classname.setText(str(item.data(0,Qt.UserRole))) if item.data(0,Qt.UserRole) else None)
        self.class_tree.itemClicked.connect(lambda item,column:self.classname.setText(str(item.data(0,Qt.UserRole))) if item.data(0,Qt.UserRole) else None)
        main.addWidget(self.class_tree)
        main.addWidget(QLabel(('For infected, use the separate ZSpawn block; player is not a spawnable special-infected classname.' if english else '普通/特殊感染者请使用单独的 ZSpawn 积木；player 不是可生成的特感类名。')))
        scroll=QScrollArea();scroll.setWidgetResizable(True);host=QWidget();grid=QGridLayout(host)
        config=enabled_config(block.args.get('config',{}));self.fields={}
        for i,(key,default) in enumerate(CONFIG_FIELDS):
            toggle=QCheckBox(key);toggle.setChecked(key in config)
            value=QLineEdit(config.get(key,default));value.setEnabled(toggle.isChecked())
            toggle.toggled.connect(value.setEnabled)
            grid.addWidget(toggle,i,0);grid.addWidget(value,i,1)
            self.fields[key]=(toggle,value)
        scroll.setWidget(host);main.addWidget(scroll)
        main.addWidget(QLabel('Spawning depends on classname, map rules and required KeyValues.' if english else '实体是否可生成取决于 classname、地图规则及必需的 KeyValues。'))
        main.addWidget(QLabel(DOCUMENTATION))
        actions=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        actions.accepted.connect(self.accept);actions.rejected.connect(self.reject);main.addWidget(actions)
    def accept(self):
        if self.classname.text().strip()!=self._initial_display:
            self.block.args['classname']=self.classname.text().strip()
        self.block.args['config']={name:field.text() for name,(check,field) in self.fields.items() if check.isChecked()}
        super().accept()
