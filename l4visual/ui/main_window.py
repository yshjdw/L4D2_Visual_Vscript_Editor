from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from ..project_files import norm_path, folder_set, rename_prefix, remove_prefix, parent_folder, list_folders
from PySide6.QtCore import Qt,QMimeData,QTimer,QSettings
from PySide6.QtGui import QAction,QDrag,QFont
from PySide6.QtWidgets import (QMainWindow,QDockWidget,QTreeWidget,QTreeWidgetItem,QLineEdit,
 QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QTabWidget,QPlainTextEdit,QFileDialog,QMessageBox,
 QInputDialog,QListWidget,QListWidgetItem,QDialog,QFormLayout,QDialogButtonBox,QComboBox,QMenu,QSplitter,QApplication,QProgressDialog)
from ..models import Project,ScriptDocument,Section,default_project
from ..storage import save_project,load_project
from ..catalog import Catalog
from ..data_definitions import DATA_BLOCKS
from ..codegen import SquirrelGenerator
from ..validation import Validator
from ..vpk_export import package_scripts, author_credit
from .dialogs import BLOCK_CATEGORIES,BLOCK_NAMES,SectionEditor
from .canvas import Canvas,MIME_BLOCK
from .palette import BlockPalette
from .trash import ProjectTree
from ..display_profile import current_profile, use_profile, event_caption, method_caption, menu_caption, category_caption
from .localization import translated_text
from ..version import APP_VERSION
from ..update_service import is_newer, RELEASES_PAGE, update_error_text
from .update_tasks import ReleaseCheckTask, ReleaseDownloadTask


class AppearanceDialog(QDialog):
    """Global presentation preferences; project source remains untouched."""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('显示设置 / Display settings')
        self.resize(460,280)
        layout=QVBoxLayout(self)
        form=QFormLayout();layout.addLayout(form)
        self.language=QComboBox()
        self.language.addItem('简体中文','zh')
        self.language.addItem('English','en')
        self.language.setCurrentIndex(self.language.findData(current_profile().language))
        form.addRow('界面语言 / Language',self.language)
        self.mode=QComboBox()
        self.mode.addItem('一般 · 易于理解的说明','general')
        self.mode.addItem('专业 · 原始 API / 事件名','professional')
        self.mode.setCurrentIndex(self.mode.findData(current_profile().style))
        form.addRow('模块风格 / Block style',self.mode)
        self.example=QLabel()
        self.example.setWordWrap(True)
        self.example.setStyleSheet('padding:14px;background:#263c51;color:white;border-radius:8px;')
        layout.addWidget(self.example)
        info=QLabel('只更改界面文字和槽位排列，不修改保存的积木数据或导出的 Squirrel 代码。')
        info.setWordWrap(True);layout.addWidget(info)
        self.language.currentIndexChanged.connect(self.update_example)
        self.mode.currentIndexChanged.connect(self.update_example)
        self.update_example()
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_example(self):
        from ..display_profile import DisplayProfile
        profile=DisplayProfile(self.language.currentData(),self.mode.currentData())
        title=method_caption('GetActiveWeapon',profile)
        event=event_caption('weapon_reload',profile)
        self.example.setText(('示例：' if profile.language=='zh' else 'Preview: ')+title+'\n'+event)

    def selection(self):
        return self.language.currentData(),self.mode.currentData()


class LibraryDialog(QDialog):
    def __init__(self,project,parent=None):
        super().__init__(parent)
        self.project=project;self.resize(560,440);self.setWindowTitle('外部 API 描述文件')
        lay=QVBoxLayout(self)
        lay.addWidget(QLabel('外部 API 保存后会在左侧生成可拖动方法块。每个描述包含 owner/name/params/returns。'))
        self.json=QPlainTextEdit(json.dumps(project.library or {'functions':[]},ensure_ascii=False,indent=2))
        lay.addWidget(self.json)
        buttons=QHBoxLayout();lay.addLayout(buttons)
        imp=QPushButton('从 JSON 导入');imp.clicked.connect(self.import_json);buttons.addWidget(imp)
        example=QPushButton('ArmorSystem 示例');example.clicked.connect(self.populate);buttons.addWidget(example)
        btn=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);btn.accepted.connect(self.parse);btn.rejected.connect(self.reject);lay.addWidget(btn)
    def populate(self):
        example={'functions':[
          {'owner':'ArmorSystem','name':'RegisterArmor','params':['id','index','data','enhanced','flag'], 'returns':'void'},
          {'owner':'ArmorSystem','name':'LoadArmor','params':['name'], 'returns':'table'},
          {'owner':'ArmorSystem','name':'SetEquipped','params':['player','id','armor','durability'], 'returns':'bool'},
          {'owner':'ArmorSystem','name':'GetEquipped','params':['player'], 'returns':'table'}]}
        self.json.setPlainText(json.dumps(example,indent=2,ensure_ascii=False))
    def import_json(self):
        path,_=QFileDialog.getOpenFileName(self,'载入外部库描述','','JSON (*.json)')
        if path:self.json.setPlainText(Path(path).read_text(encoding='utf-8'))
    def parse(self):
        try:
            obj=json.loads(self.json.toPlainText())
            if not isinstance(obj,dict) or not isinstance(obj.get('functions',[]),list):
                raise ValueError('functions 必须是数组')
            self.project.library=obj
            self.accept()
        except (ValueError,TypeError) as exc:QMessageBox.warning(self,'描述文件不合法',str(exc))

class VPKInfoDialog(QDialog):
    def __init__(self, default_title='My L4D2 Addon',parent=None):
        super().__init__(parent)
        self.setWindowTitle('VPK 模组信息')
        self.resize(500,330)
        layout=QVBoxLayout(self);form=QFormLayout();layout.addLayout(form)
        self.title=QLineEdit(default_title);form.addRow('模组名称',self.title)
        self.author=QLineEdit();self.author.setPlaceholderText('填写作者；导出自动添加 /Vscript Visual Maker')
        form.addRow('作者',self.author)
        self.version=QLineEdit('1.0');form.addRow('版本',self.version)
        self.description=QPlainTextEdit();self.description.setMaximumHeight(110);form.addRow('简介',self.description)
        self.credit=QLabel('最终作者署名：/Vscript Visual Maker');layout.addWidget(self.credit)
        self.author.textChanged.connect(lambda name:self.credit.setText('最终作者署名：'+author_credit(name)))
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verify);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def verify(self):
        if not self.title.text().strip():
            QMessageBox.warning(self,'模组名称不能为空','请输入模组名称。');return
        self.accept()
    def metadata(self):
        return dict(title=self.title.text().strip(),author=self.author.text().strip(),
                    version=self.version.text().strip() or '1.0',description=self.description.toPlainText())

class MainWindow(QMainWindow):
    def __init__(self, startup_checked=False):
        super().__init__()
        self.setWindowTitle('L4D2 Visual VScript '+APP_VERSION+' — '+('Unsaved' if current_profile().language=='en' else '未保存'))
        self.resize(1500,920)
        self.preferences=QSettings('VScript Visual Maker','L4D2 Visual VScript')
        self._check_task=None
        self._download_task=None
        self._download_progress=None
        self._update_pending=None
        self._last_release=None
        self._manual_update_check=False
        self._close_pending=False
        self.ignore_static_checks=str(self.preferences.value('export/ignore_static_checks','false')).lower() in ('true','1','yes')
        language=self.preferences.value('display/language','en')
        style=self.preferences.value('display/style','general')
        try:use_profile(language,style)
        except ValueError:use_profile('en','general')
        self.catalog=Catalog()
        self.validator=Validator(self.catalog)
        self.project=default_project();self.current_doc=self.project.documents[0]
        self.file_path=None;self.dirty=False
        self._building_tree=False;self._loading=False;self._scope_cleanup_pending=False
        from .localization import DialogLocalizationFilter
        self._dialog_translation_filter=DialogLocalizationFilter.make()
        QApplication.instance().installEventFilter(self._dialog_translation_filter)
        self.build_ui();self.build_actions()
        self.load_document(self.current_doc)
        self.set_style()
        self.apply_interface_language()
        # Defer until the central widget and tabified docks have actual sizes.
        # Only the initial demonstration receives a startup camera position.
        QTimer.singleShot(0,self.focus_starter_blocks)
        QTimer.singleShot(300,self._show_prior_update_result)
        if not startup_checked and str(self.preferences.value('updates/check_on_startup','true')).lower() not in ('false','0','no'):
            QTimer.singleShot(1500,lambda:self.check_for_updates(manual=False))

    def focus_starter_blocks(self):
        """Show the bundled starter blocks immediately, without searching the canvas."""
        if self.file_path is not None or self.dirty or not self.current_doc:
            return
        from PySide6.QtCore import QRectF
        from PySide6.QtWidgets import QApplication
        items=list(self.canvas.board.items_by_id.values())
        if not items:
            return
        QApplication.processEvents()
        bounds=items[0].sceneBoundingRect()
        for item in items[1:]:
            bounds=bounds.united(item.sceneBoundingRect())
        bounds=bounds.adjusted(-35,-35,35,35)
        if bounds.width()>0 and bounds.height()>0:
            self.canvas.fitInView(bounds,Qt.KeepAspectRatio)
            # Keep text usable on very large examples. Panning remains available.
            if self.canvas.transform().m11()<0.55:
                self.canvas.resetTransform()
                self.canvas.scale(0.55,0.55)
                self.canvas.centerOn(bounds.center())

    def set_style(self):
        self.setStyleSheet('''
            QMainWindow, QWidget { background: #192232; color: #E8EDF7; font-family: Segoe UI, Microsoft YaHei; font-size: 11pt; }
            QDockWidget::title { background: #2A3A55; padding: 8px; }
            QTreeWidget,QListWidget,QPlainTextEdit,QLineEdit,QComboBox { background: #111827; border:1px solid #3B4B65; border-radius:5px; padding:5px; color:#ECF1FC; }
            QPushButton { background:#334F74; border:1px solid #506E99; border-radius:5px; padding:7px; }
            QPushButton:hover {background:#416491;}
            QComboBox {color:#000000;background:#f4f0df;}
            QComboBox QAbstractItemView {color:#000000;background:#ffffff;selection-color:#000000;selection-background-color:#b9d6f4;}
            QMenu, QDialog {background:#202C40;}
            QTabBar::tab {padding:8px 18px; background:#22344D;}
            QTabBar::tab:selected {background:#385D87;}
        ''')

    def build_ui(self):
        self.canvas=Canvas(self.catalog,self)
        self.canvas.edited.connect(self.mark_dirty)
        self.preview=QPlainTextEdit();self.preview.setReadOnly(True)
        self.preview.setFont(QFont('Consolas',10))
        self.issues=QListWidget()
        self.issues.setToolTip(translated_text('点击错误信息，定位到对应积木 / Click an issue to focus its block'))
        self.issues.itemClicked.connect(self.jump_to_issue)
        self.output_tabs=QTabWidget()
        self.output_tabs.addTab(self.preview,'Squirrel .nut 预览')
        self.output_tabs.addTab(self.issues,'静态检查')
        splitter=QSplitter(Qt.Vertical);splitter.addWidget(self.canvas);splitter.addWidget(self.output_tabs);splitter.setSizes([650,245]);self.setCentralWidget(splitter)
        # 左侧工程树
        self.project_tree=ProjectTree();self.project_tree.setHeaderLabels(['工程 / scripts/vscripts/ · 拖动 .nut 到槽位']);self.project_tree.setMinimumWidth(230)
        self.project_tree.blockDropped.connect(self.delete_dropped_block)
        self.project_tree.embeddedDropped.connect(self.delete_dropped_expression)
        self.project_tree.itemDoubleClicked.connect(self.choose_document)
        self.project_tree.fileMoved.connect(self.move_project_file)
        self.project_tree.folderMoved.connect(self.move_project_folder)
        self.project_tree.itemClicked.connect(self.choose_document)
        self.project_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.project_menu)
        dock=QDockWidget('工程栏',self);dock.setObjectName('projectDock');dock.setWidget(self.project_tree);self.addDockWidget(Qt.LeftDockWidgetArea,dock)
        self.project_dock=dock
        palette_panel=QWidget();palette_layout=QVBoxLayout(palette_panel)
        palette_layout.addWidget(QLabel('从积木库拖出添加积木；将已有积木拖回积木库可删除'))
        self.palette=BlockPalette(catalog=self.catalog,library=self.project.library);palette_layout.addWidget(self.palette)
        self.palette.blockDropped.connect(self.delete_dropped_block)
        self.palette.embeddedDropped.connect(self.delete_dropped_expression)
        dock2=QDockWidget('积木工具库',self);dock2.setObjectName('paletteDock');dock2.setWidget(palette_panel);dock2.setMaximumWidth(420);self.addDockWidget(Qt.LeftDockWidgetArea,dock2)
        self.palette_dock=dock2
        self.tabifyDockWidget(dock,dock2);dock2.raise_()
        # 右侧 API 浏览器
        api=QWidget();v=QVBoxLayout(api)
        self.api_tabs=QTabWidget();v.addWidget(self.api_tabs)
        self.api_browser=QTreeWidget();self.api_browser.setHeaderLabels(['API',translated_text('返回类型')]);self.api_browser.setColumnCount(2)
        self.netprop_browser=QTreeWidget();self.netprop_browser.setHeaderLabels([translated_text('字段'),translated_text('类型')]);self.netprop_browser.setColumnCount(2)
        self.event_browser=QTreeWidget();self.event_browser.setHeaderLabels([translated_text('事件'),translated_text('分类')]);self.event_browser.setColumnCount(2)
        self.api_tabs.addTab(self.api_browser,'方法')
        self.api_tabs.addTab(self.netprop_browser,'NetProps')
        self.api_tabs.addTab(self.event_browser,'事件')
        self.api_filter=QLineEdit();self.api_filter.setPlaceholderText('搜索官方 API / 事件 / NetProp')
        v.insertWidget(0,self.api_filter)
        self.api_filter.textChanged.connect(self.populate_catalog)
        self.api_browser.itemDoubleClicked.connect(self.insert_method)
        self.event_browser.itemDoubleClicked.connect(self.insert_event)
        dock3=QDockWidget('L4D2 API 资料库（离线）',self);dock3.setObjectName('apiDock');dock3.setWidget(api);self.addDockWidget(Qt.RightDockWidgetArea,dock3)
        self.api_dock=dock3
        toggle_api=QPushButton('展开 / 收起 API 字典')
        toggle_api.clicked.connect(lambda:self.show_dock(dock3) if not dock3.isVisible() else dock3.hide())
        self.statusBar().addPermanentWidget(toggle_api)
        self.populate_catalog('');self.refresh_tree()
        self.statusBar().showMessage(translated_text('离线数据库已加载。Ctrl+滚轮缩放画布。右键积木可编辑/复制。'))

    def build_actions(self):
        menu=self.menuBar().addMenu('文件')
        self.action(menu,'新建工程','Ctrl+N',self.new_project)
        self.action(menu,'打开 .l4vp 工程','Ctrl+O',self.open_project)
        self.action(menu,'保存工程','Ctrl+S',self.save)
        self.action(menu,'工程另存为','Ctrl+Shift+S',self.save_as)
        menu.addSeparator();self.action(menu,'新建 .nut 文件',None,self.add_document)
        self.action(menu,'导出当前 .nut','Ctrl+E',self.export_current)
        self.action(menu,'批量导出工程 .nut',None,self.export_all)
        self.action(menu,'导出 VPK 模组',None,self.export_vpk)
        settings_menu=self.menuBar().addMenu('设置 / Settings')
        self.action(settings_menu,'语言与模块风格 / Language & Block style',None,self.edit_display_settings)
        self.ignore_check_action=QAction('忽略静态检查，允许导出 NUT / VPK',self)
        self.ignore_check_action.setCheckable(True)
        self.ignore_check_action.setChecked(self.ignore_static_checks)
        self.ignore_check_action.toggled.connect(self.set_ignore_static_checks)
        settings_menu.addAction(self.ignore_check_action)
        self.check_updates_on_startup_action=QAction('启动时检查更新',self)
        self.check_updates_on_startup_action.setCheckable(True)
        self.check_updates_on_startup_action.setChecked(
            str(self.preferences.value('updates/check_on_startup','true')).lower() not in ('false','0','no'))
        self.check_updates_on_startup_action.toggled.connect(
            lambda enabled:self.preferences.setValue('updates/check_on_startup',bool(enabled)))
        settings_menu.addAction(self.check_updates_on_startup_action)
        view_menu=self.menuBar().addMenu('视图')
        for dock_widget in (self.project_dock,self.palette_dock,self.api_dock):
            act=dock_widget.toggleViewAction()
            view_menu.addAction(act)
        view_menu.addSeparator()
        self.action(view_menu,'恢复默认布局',None,self.restore_default_layout)
        help_menu=self.menuBar().addMenu('Help / 帮助')
        self.action(help_menu,'编辑器使用指南 / Editor Guide',None,self.show_entity_help)
        self.action(help_menu,'检查 GitHub 更新',None,lambda:self.check_for_updates(manual=True))
        build=self.menuBar().addMenu('可视化')
        self.action(build,'新增分区',None,self.add_section)
        self.action(build,'新增事件监听分区',None,lambda:self.add_section('events'))
        # 复杂变量定义区只能从复杂变量右键创建，且在独立窗口编辑
        self.action(build,'预览 / 检查','F5',self.update_preview)
        tool=self.menuBar().addMenu('工具')
        self.action(tool,'外部自定义 API',None,self.external_library)
        self.action(tool,'API 数据库信息',None,self.catalog_about)
        self.action(tool,'导出已恢复的 Data 分区 / Export recovered Data',None,self.export_recovered_workspaces)
        bar=self.addToolBar('编辑')
        for label,callback in [('新建工程',self.new_project),('新建文件',self.add_document),('添加分区',self.add_section),('保存',self.save),('生成代码',self.update_preview),('导出 .nut',self.export_current)]:
            action=QAction(label,self);action.triggered.connect(callback);bar.addAction(action)
        bar.addSeparator()
        for label,kind in [('＋函数','function'),('＋Namespace','namespace'),('＋复杂变量','complex_data')]:
            action=QAction(label,self)
            action.triggered.connect(lambda checked=False,k=kind:self.quick_create_section(k))
            bar.addAction(action)
        bar.addSeparator()
        for label,factor in [('－',1/1.2),('＋',1.2)]:
            action=QAction(label,self)
            action.setToolTip('画布缩放 '+label)
            action.triggered.connect(lambda checked=False,f=factor:self.canvas.zoom(f))
            bar.addAction(action)
        reset=QAction('100%',self);reset.triggered.connect(self.canvas.resetTransform);bar.addAction(reset)

    def set_ignore_static_checks(self, enabled):
        self.ignore_static_checks=bool(enabled)
        self.preferences.setValue('export/ignore_static_checks',self.ignore_static_checks)
        self.statusBar().showMessage(('Static validation bypass is on; code-generation errors still block export.' if current_profile().language=='en' else '已忽略静态检查拦截；代码生成错误仍会阻止导出。') if enabled else ('Static validation gate restored.' if current_profile().language=='en' else '已恢复静态检查拦截。'),6000)

    def edit_display_settings(self):
        dialog=AppearanceDialog(self)
        if not dialog.exec():return
        language,style=dialog.selection()
        if current_profile().language==language and current_profile().style==style:return
        use_profile(language,style)
        self.preferences.setValue('display/language',language)
        self.preferences.setValue('display/style',style)
        # Repaint active scene without turning a presentation change into a
        # modification of the .l4vp file or moving the blocks on the canvas.
        was_loading=self._loading
        self._loading=True
        try:
            self.canvas.board.refresh_sections()
            self.palette.refresh_language()
            self.apply_interface_language()
            from PySide6.QtWidgets import QApplication
            for window in QApplication.topLevelWidgets():
                if window is self:continue
                if hasattr(window,'canvas') and hasattr(window.canvas,'board'):
                    window.canvas.board.refresh_sections()
            from .localization import translated_text
            self.statusBar().showMessage(translated_text('界面语言与积木风格已更新；导出代码不变。'),7000)
        finally:
            self._loading=was_loading

    def apply_interface_language(self):
        english=current_profile().language=='en'
        from .localization import localize_widget_tree, translated_text
        # Translate first, then refresh manually managed tabs/placeholders.
        # Otherwise a tab created directly in English could be remembered as
        # the 'original' text and refuse to switch back to Chinese.
        localize_widget_tree(self)
        self.project_dock.setWindowTitle('Project' if english else '工程栏')
        self.palette_dock.setWindowTitle('Block library' if english else '积木工具库')
        self.api_dock.setWindowTitle('L4D2 API catalog (offline)' if english else 'L4D2 API 资料库（离线）')
        self.output_tabs.setTabText(0,'Squirrel .nut preview' if english else 'Squirrel .nut 预览')
        self.output_tabs.setTabText(1,'Validation' if english else '静态检查')
        self.api_tabs.setTabText(0,'Methods' if english else '方法')
        self.api_tabs.setTabText(1,'NetProps')
        self.api_tabs.setTabText(2,'Events' if english else '事件')
        self.api_filter.setPlaceholderText('Search official API / event / NetProp' if english else '搜索官方 API / 事件 / NetProp')
        self.api_browser.setHeaderLabels(['API',translated_text('返回类型')])
        self.netprop_browser.setHeaderLabels([translated_text('字段'),translated_text('类型')])
        self.event_browser.setHeaderLabels([translated_text('事件'),translated_text('分类')])
        self.populate_catalog(self.api_filter.text())
        self.project_tree.setHeaderLabels(['Project / scripts/vscripts/ · drag .nut to socket' if english else '工程 / scripts/vscripts/ · 拖动 .nut 到槽位'])
        for dock in (self.project_dock,self.palette_dock,self.api_dock):
            for widget in dock.findChildren(__import__('PySide6.QtWidgets',fromlist=['QAbstractButton']).QAbstractButton):
                if widget.objectName()=='qt_dockwidget_closebutton':
                    widget.setToolTip('Close' if english else '关闭')
                elif widget.objectName()=='qt_dockwidget_floatbutton':
                    widget.setToolTip('Undock' if english else '浮动窗口')
        # Window title is not a project identifier and can be localized.
        if self.windowTitle().endswith('— 未保存') or self.windowTitle().endswith('— Unsaved'):
            self.setWindowTitle('L4D2 Visual VScript '+APP_VERSION+' — '+('Unsaved' if english else '未保存'))
        self.statusBar().showMessage(translated_text('离线数据库已加载。Ctrl+滚轮缩放画布。右键积木可编辑/复制。'),5000)
        # Preserve original labels on QAction objects, even if the user changes
        # languages multiple times in the same session.
        for menu_action in self.menuBar().actions():
            menu=menu_action.menu()
            if menu is None:continue
            original=menu_action.property('l4_original_text')
            if original is None:
                original=menu_action.text()
                menu_action.setProperty('l4_original_text',original)
            menu_action.setText(menu_caption(original))
            for action in menu.actions():
                dock_titles={d.toggleViewAction():d.windowTitle() for d in
                             (self.project_dock,self.palette_dock,self.api_dock)}
                if action in dock_titles:
                    action.setText(dock_titles[action])
                    continue
                old=action.property('l4_original_text')
                if old is None:
                    old=action.text()
                    action.setProperty('l4_original_text',old)
                action.setText(menu_caption(old))
        for toolbar in self.findChildren(__import__('PySide6.QtWidgets',fromlist=['QToolBar']).QToolBar):
            for action in toolbar.actions():
                old=action.property('l4_original_text')
                if old is None:
                    old=action.text()
                    action.setProperty('l4_original_text',old)
                action.setText(menu_caption(old))

    def show_dock(self,dock):
        """Restore even a hidden, tabified dock and bring its tab to the front."""
        dock.show()
        dock.raise_()

    def restore_default_layout(self):
        """Recover from closed/detached panels without recreating their widgets."""
        for dock in (self.project_dock,self.palette_dock,self.api_dock):
            dock.setFloating(False)
            dock.show()
        self.removeDockWidget(self.project_dock)
        self.removeDockWidget(self.palette_dock)
        self.removeDockWidget(self.api_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.project_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.palette_dock)
        self.tabifyDockWidget(self.project_dock,self.palette_dock)
        self.addDockWidget(Qt.RightDockWidgetArea,self.api_dock)
        self.palette_dock.raise_()

    def action(self,menu,title,shortcut,callback):
        act=QAction(title,self)
        if shortcut:act.setShortcut(shortcut)
        act.triggered.connect(callback);menu.addAction(act)

    def populate_catalog(self,text):
        self.api_browser.clear();self.netprop_browser.clear();self.event_browser.clear()
        for row in self.catalog.methods(text)[:350]:
            i=QTreeWidgetItem([row['owner']+'.'+row['name'],row['returns']]);from ..api_docs import method_tooltip
            i.setToolTip(0,method_tooltip(row));i.setData(0,Qt.UserRole,row);self.api_browser.addTopLevelItem(i)
        from ..netprop_catalog import list_classes,list_properties
        class_names=list_classes(text) if text else list_classes()
        if text:
            class_names=sorted(set(class_names)|{c for c in list_classes() if list_properties(c,text)})
        for cls in class_names:
            root=QTreeWidgetItem([cls,translated_text('实体网络类')])
            self.netprop_browser.addTopLevelItem(root)
            paths={}
            for row in list_properties(cls,text):
                parent=root
                parts=row['name'].split('.')
                for n,part in enumerate(parts):
                    key=tuple(parts[:n+1]);node=paths.get(key)
                    if node is None:
                        node=QTreeWidgetItem(parent,[part,''])
                        paths[key]=node
                    if n==len(parts)-1:
                        node.setText(1,row['type'])
                        node.setToolTip(0,f"{cls} / {row['name']}\n{translated_text('类型：')}{row['type']}\n{translated_text('偏移：')}{row['offset']}")
                        node.setData(0,Qt.UserRole,{'table':cls,'property':row['name'],**row})
                    parent=node
            if text:root.setExpanded(True)
        for row in self.catalog.events(text)[:350]:
            i=QTreeWidgetItem([row['name'],category_caption(row['category'])]);from ..api_docs import event_tooltip
            i.setToolTip(0,event_tooltip(row));i.setData(0,Qt.UserRole,row);self.event_browser.addTopLevelItem(i)

    def refresh_tree(self):
        self._building_tree=True
        self.project_tree.clear()
        root=QTreeWidgetItem([self.project.name]);root.setData(0,Qt.UserRole,('root',''));self.project_tree.addTopLevelItem(root)
        scripts=QTreeWidgetItem(['scripts']);scripts.setData(0,Qt.UserRole,('root',''));root.addChild(scripts)
        vscripts=QTreeWidgetItem(['vscripts']);vscripts.setData(0,Qt.UserRole,('folder',''));scripts.addChild(vscripts)
        folders={'':vscripts}
        for path in sorted(list_folders(self.project)):
            prefix=''
            for part in path.split('/'):
                dest=(prefix+'/'+part).strip('/')
                if dest not in folders:
                    item=QTreeWidgetItem([part]);item.setData(0,Qt.UserRole,('folder',dest))
                    folders[prefix].addChild(item);folders[dest]=item
                prefix=dest
        for doc in self.project.documents:
            name=norm_path(doc.name)
            folder=parent_folder(name)
            item=QTreeWidgetItem([name.rsplit('/',1)[-1]])
            item.setData(0,Qt.UserRole,('file',doc.id))
            item.setData(0,Qt.UserRole+1,name)
            folders.get(folder,vscripts).addChild(item)
            for section in doc.sections:
                if section.kind == "data":
                    continue
                child=QTreeWidgetItem([section.kind+' · '+section.name]);child.setData(0,Qt.UserRole,('file',doc.id));item.addChild(child)
            if self.current_doc is doc:self.project_tree.setCurrentItem(item)
        self.project_tree.expandToDepth(4)
        self._building_tree=False

    def move_project_file(self,doc_id,destination):
        doc=next((d for d in self.project.documents if d.id==doc_id),None)
        if doc is None:return
        destination=norm_path(destination) if destination else ""
        new=(destination+"/" if destination else "")+doc.name.rsplit("/",1)[-1]
        if new==doc.name:return
        if any(d is not doc and d.name==new for d in self.project.documents):
            QMessageBox.warning(self,"名称冲突","目标目录已有同名 .nut 文件")
            self.refresh_tree();return
        old=doc.name
        doc.name=new
        for other in self.project.documents:
            other.includes=[new if item==old else item for item in other.includes]
        self.refresh_tree();self.mark_dirty()

    def move_project_folder(self,source,destination):
        try:
            source=norm_path(source)
            destination=norm_path(destination) if destination else ''
            if destination==source or destination.startswith(source+'/'):
                raise ValueError('不能将文件夹移入自身或其子目录')
            new=(destination+'/' if destination else '')+source.rsplit('/',1)[-1]
            existing=list_folders(self.project)
            if new!=source and new in existing:
                raise ValueError('目标目录已有同名文件夹')
            if new!=source:
                rename_prefix(self.project,source,new)
                self.refresh_tree();self.mark_dirty()
        except ValueError as error:
            QMessageBox.warning(self,'移动失败',str(error))
            self.refresh_tree()

    def rename_tree_item(self,item,column=0):
        meta=item.data(0,Qt.UserRole)
        if not isinstance(meta,tuple):return
        kind,identity=meta
        if kind=='file':
            doc=next((d for d in self.project.documents if d.id==identity),None)
            if doc:self._rename_file(doc)
        elif kind=='folder' and identity:
            self._rename_folder(identity)
        else:
            self.choose_document(item,column)

    def _rename_folder(self,old):
        value,ok=QInputDialog.getText(self,'重命名文件夹','文件夹名',text=old.split('/')[-1])
        if not ok or not value.strip():return
        name=value.strip()
        if '/' in name or '\\' in name or name in ('.','..'):
            QMessageBox.warning(self,'非法名称','文件夹名不能含路径符号');return
        new=(parent_folder(old)+'/'+name).strip('/')
        if new==old:return
        if new in list_folders(self.project):
            QMessageBox.warning(self,'重复目录','文件夹已存在');return
        rename_prefix(self.project,old,new)
        self.refresh_tree();self.mark_dirty()

    def choose_document(self,item,column=0):
        if self._building_tree:return
        meta=item.data(0,Qt.UserRole)
        doc_id=meta[1] if isinstance(meta,tuple) and meta[0]=="file" else None
        doc=next((d for d in self.project.documents if d.id==doc_id),None)
        if doc:self.load_document(doc)

    def load_document(self,doc):
        self._loading=True
        try:
            # Older projects can contain an outdated per-type expression cache.
            # The visible active expression is the only source of truth on load.
            from ..variable_types import reconcile_variable_cache
            def visit(block):
                if block.kind=='var':reconcile_variable_cache(block)
                for children in block.branches.values():
                    for child in children:visit(child)
            for section in doc.sections:
                for block in section.blocks:visit(block)
            self.current_doc=doc;self.canvas.load_document(doc);self.refresh_tree();self.palette.reload_external(self.project.library);self.update_preview()
        finally:
            self._loading=False
        from .localization import translated_text
        self.statusBar().showMessage(translated_text('当前文件 ')+doc.name if doc else translated_text('当前工程没有 .nut 文件，请新建脚本。'))

    def export_recovered_workspaces(self):
        """Export the archived original sections for recovery or inspection."""
        english=current_profile().language=='en'
        saved=self.project.recovered_workspaces
        if not saved:
            QMessageBox.information(self,
                'Recovered Data' if english else '已恢复的 Data 分区',
                'No archived workspaces in this project.' if english else '工程中没有已归档的失效工作区。')
            return
        path,_=QFileDialog.getSaveFileName(self,
            'Export recovered Data' if english else '导出 Data 工作区恢复记录',
            self.project.name+'_recovered_data.json','JSON (*.json)')
        if not path:return
        if not path.lower().endswith('.json'):path+='.json'
        try:
            Path(path).write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding='utf-8')
            self.statusBar().showMessage(('Recovered workspaces exported: ' if english else '已导出恢复记录：')+path,7000)
        except OSError as error:
            QMessageBox.warning(self,'Export failed' if english else '导出失败',str(error))

    def _cleanup_orphan_data(self, refresh_canvas=True):
        from ..data_definitions import repair_orphan_workspaces
        changes=repair_orphan_workspaces(self.project)
        current_changed=any(doc_name==self.current_doc.name for doc_name,_,_ in changes) if self.current_doc else False
        if current_changed and refresh_canvas:
            self._loading=True
            try:
                self.canvas.board.load(self.current_doc)
            finally:
                self._loading=False
        if changes:
            self.dirty=True
            duplicates=sum(reason=='duplicate_namespace' for _,_,reason in changes)
            english=current_profile().language=='en'
            if english:
                message=f'Cleaned {len(changes)} orphan Data workspace(s). {duplicates} redundant workspace(s) archived in project recovery records; save the project.'
            else:
                message=f'已清理 {len(changes)} 个失效 Data 工作区，其中 {duplicates} 个冗余分区已存入工程恢复记录；请保存工程。'
            self.statusBar().showMessage(message,10000)
        return len(changes)

    def _scheduled_scope_cleanup(self):
        self._scope_cleanup_pending=False
        if self._loading:return
        self._cleanup_orphan_data()

    def mark_dirty(self):
        if self._loading:return
        self.dirty=True;self.setWindowTitle(f'L4D2 Visual VScript {APP_VERSION} — {self.project.name} *')
        if not self._scope_cleanup_pending:
            self._scope_cleanup_pending=True
            QTimer.singleShot(0,self._scheduled_scope_cleanup)
        self.update_preview()

    def new_project(self):
        if not self.check_unsaved():return
        name,ok=QInputDialog.getText(self,'新建工程','工程名称',text='My VScript Project')
        if not ok:return
        event_name,ok=QInputDialog.getText(self,'事件回调表','OnGameEvent 统一归属 Table 名称',text='MyEvents')
        if not ok:return
        entry,ok=QInputDialog.getItem(self,'选择入口文件','L4D2 自动加载入口',[
            'director_base_addon.nut','scriptedmode_addon.nut','mapspawn_addon.nut'],0,False)
        if not ok:return
        self.project=Project(name or 'Untitled',event_name or 'MyEvents',[
            ScriptDocument(entry,[Section('events',event_name or 'MyEvents',x=80,y=60),Section('init','文件初始化',x=560,y=60)])
        ])
        self.file_path=None;self.dirty=False;self.load_document(self.project.documents[0]);self.mark_dirty()
        QTimer.singleShot(0,lambda:self.canvas.focus_diagnostic(self.project.documents[0].sections[0].id))

    def open_project(self):
        if not self.check_unsaved():return
        path,_=QFileDialog.getOpenFileName(self,'打开工程','','L4D2 可视化工程 (*.l4vp)')
        if not path:return
        try:
            self.project=load_project(path);self.file_path=path;self.dirty=False
            from ..data_definitions import repair_orphan_workspaces
            repairs=repair_orphan_workspaces(self.project)
            self._repaired_orphans=len(repairs)
            archived=sum(reason=='duplicate_namespace' for _,_,reason in repairs)
            self.load_document(self.project.documents[0] if self.project.documents else None)
            self.setWindowTitle(f'L4D2 Visual VScript {APP_VERSION} — '+self.project.name)
            if self._repaired_orphans:
                self.mark_dirty()
                english=current_profile().language=='en'
                message=(f'Cleaned {self._repaired_orphans} orphan Data workspace(s), archived {archived} duplicate(s); save the project.' if english
                         else f'已清理 {self._repaired_orphans} 个失效 Data 工作区，其中 {archived} 个重复分区已归档；请保存工程。')
                self.statusBar().showMessage(message,10000)
        except Exception as exc:QMessageBox.critical(self,'打开失败',str(exc))

    def save(self):
        if not self.file_path:return self.save_as()
        try:
            self._cleanup_orphan_data()
            save_project(self.file_path,self.project)
            self.dirty=False
            self.setWindowTitle(f'L4D2 Visual VScript {APP_VERSION} — '+self.project.name)
            self.statusBar().showMessage(translated_text('已保存到 ')+self.file_path,6000)
            return True
        except Exception as exc:QMessageBox.critical(self,'保存失败',str(exc));return False

    def save_as(self):
        path,_=QFileDialog.getSaveFileName(self,'保存工程',self.project.name+'.l4vp','L4D2 可视化工程 (*.l4vp)')
        if not path:return False
        if not path.lower().endswith('.l4vp'):path+='.l4vp'
        self.file_path=path;return self.save()

    def check_unsaved(self):
        if not self.dirty:return True
        choice=QMessageBox.question(self,'未保存修改','保存当前工程？',QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
        if choice==QMessageBox.Cancel:return False
        if choice==QMessageBox.Save:return bool(self.save())
        return True

    def add_document(self,folder=''):
        if not isinstance(folder,str):folder=''
        folder=norm_path(folder)
        name,ok=QInputDialog.getText(self,'新建脚本','文件名（.nut）',text='new_script.nut')
        if not ok or not name.strip():return
        name=name.strip()
        if not name.lower().endswith('.nut'):name+='.nut'
        if '/' in name or "\\" in name or name in ('.','..'):
            QMessageBox.warning(self,'文件名无效','请输入不含路径分隔符的文件名。');return
        full=(folder+'/'+name).strip('/')
        if any(d.name==full for d in self.project.documents):
            QMessageBox.warning(self,'重复文件','同一目录中已存在这个文件。');return
        doc=ScriptDocument(full,[Section('init','文件初始化',x=70,y=55)])
        self.project.documents.append(doc)
        self.load_document(doc);self.mark_dirty()

    def _rename_file(self,doc):
        value,ok=QInputDialog.getText(self,'重命名 .nut','新文件名',text=doc.name.rsplit('/',1)[-1])
        if not ok or not value.strip():return
        new=value.strip()
        if '/' in new or '\\' in new or new in ('.','..'):
            QMessageBox.warning(self,'非法文件名','不能包含路径分隔符');return
        if not new.lower().endswith('.nut'):new+='.nut'
        full=(parent_folder(doc.name)+'/'+new).strip('/')
        if full!=doc.name and any(d.name==full for d in self.project.documents):
            QMessageBox.warning(self,'重复文件','该文件名已存在');return
        old=doc.name;doc.name=full
        for item in self.project.documents:
            item.includes=[full if v==old else v for v in item.includes]
        self.refresh_tree();self.mark_dirty()

    def _new_folder(self,parent=''):
        name,ok=QInputDialog.getText(self,'创建文件夹','文件夹名')
        if not ok or not name.strip():return
        try:
            path=norm_path((parent+'/'+name.strip()).strip('/'))
            if not path or path==parent or '/' in name.strip() or not path.split('/')[-1]:raise ValueError('非法目录名称')
            folders=folder_set(self.project)
            if path in list_folders(self.project):raise ValueError('文件夹已存在')
            folders.append(path)
            self.refresh_tree();self.mark_dirty()
        except ValueError as error:QMessageBox.warning(self,'创建失败',str(error))

    def project_menu(self,pos):
        item=self.project_tree.itemAt(pos)
        meta=item.data(0,Qt.UserRole) if item is not None else ('folder','')
        if not isinstance(meta,tuple):meta=('folder','')
        kind,identity=meta
        doc=next((d for d in self.project.documents if d.id==identity),None) if kind=='file' else None
        folder=identity if kind=='folder' else parent_folder(doc.name) if doc else ''
        menu=QMenu(None)
        open_file=menu.addAction('打开文件') if doc else None
        add_file=menu.addAction('新建 .nut 文件')
        add_folder=menu.addAction('新建文件夹')
        menu.addSeparator()
        rename=menu.addAction('重命名文件' if doc else '重命名文件夹') if doc or kind=='folder' and folder else None
        remove=menu.addAction('删除文件' if doc else '删除文件夹') if doc or kind=='folder' and folder else None
        edit=menu.addAction('编辑 IncludeScript 依赖') if doc else None
        result=menu.exec(self.project_tree.viewport().mapToGlobal(pos))
        if result==open_file and doc:self.load_document(doc)
        elif result==add_file:self.add_document(folder)
        elif result==add_folder:self._new_folder(folder)
        elif result==rename and doc:self._rename_file(doc)
        elif result==rename:
            self._rename_folder(folder)
        elif result==remove and doc:
            if QMessageBox.question(self,'删除文件',translated_text('删除 ')+doc.name+translated_text('？此操作同时移除项目中的引用。'),QMessageBox.Yes|QMessageBox.No)!=QMessageBox.Yes:return
            self.project.documents.remove(doc)
            for d in self.project.documents:d.includes=[x for x in d.includes if x!=doc.name]
            self.load_document(self.project.documents[0] if self.project.documents else None);self.mark_dirty()
        elif result==remove:
            if QMessageBox.question(self,'删除目录',translated_text('删除 ')+folder+translated_text(' 及其中全部文件？'),QMessageBox.Yes|QMessageBox.No)!=QMessageBox.Yes:return
            remove_prefix(self.project,folder)
            self.load_document(self.project.documents[0] if self.project.documents else None);self.mark_dirty()
        elif result==edit and doc:self.edit_includes(doc)

    def edit_includes(self,doc):
        candidates=[d.name for d in self.project.documents if d is not doc]
        values=', '.join(doc.includes)
        selected,ok=QInputDialog.getText(self,'文件 IncludeScript 列表',translated_text('逗号隔开的已有 .nut 文件名\n可选：')+', '.join(candidates),text=values)
        if not ok:return
        new=[x.strip() for x in selected.split(',') if x.strip()]
        if any(x not in candidates for x in new):
            QMessageBox.warning(self,'包含错误','只能引用项目内已有文件。');return
        doc.includes=new;self.mark_dirty()

    def quick_create_section(self,kind):
        if kind!='complex_data':
            self.add_section(kind)
            return
        if not self.current_doc:return
        from .dialogs import new_block
        from ..data_definitions import create_definition
        from .canvas import DefinitionWorkspace
        section=next((part for part in self.current_doc.sections if part.kind=='namespace'),None)
        if section is None:
            section=next((part for part in self.current_doc.sections if part.kind in ('init','function')),None)
        if section is None:
            QMessageBox.information(self,'复杂变量','请先创建 Namespace 或 Function 分区。')
            return
        name,ok=QInputDialog.getText(self,'创建复杂变量','变量名称',text='NewTable')
        if not ok or not name.strip():return
        block=new_block('var')
        block.args.update({'name':name.strip(),'container_type':'Table','value':'{}','scope':'root'})
        section.blocks.append(block)
        workspace=create_definition(self.current_doc,section,block)
        self.canvas.board.refresh_sections([section.id])
        self.mark_dirty()
        dialog=DefinitionWorkspace(self.current_doc,workspace,self.catalog,self)
        dialog.exec()
        self.mark_dirty()

    def add_section(self,kind=None):
        if not self.current_doc:return
        default=kind if isinstance(kind,str) else 'function'
        if default in ('init','data'):
            QMessageBox.information(self,'不可创建','初始化分区由工程自动维护；复杂数据分区从变量创建。')
            return
        count=len(self.current_doc.sections)
        name={'function':'NewFunction','think':'NewThink','events':self.project.event_namespace,'data':'NewData','namespace':'MyNamespace','init':'文件初始化'}.get(default,'NewFunction')
        # New sections are located near the visible canvas, never rebase existing sections.
        from PySide6.QtCore import QPoint
        visible_center=self.canvas.mapToScene(self.canvas.viewport().rect().center())
        offset=(count % 4)*32
        section=Section(default,name,x=visible_center.x()-180+offset,y=visible_center.y()-85+offset)
        if default=='data':
            QMessageBox.information(self,'复杂变量','请在 Table / Set 变量上右键，选择“打开独立数据工作区”。');return
        dialog=SectionEditor(section,self,document=self.current_doc)
        if dialog.exec():
            section=dialog.apply()
            if section.kind=='events' and any(s.kind=='events' and s.name==section.name for s in self.current_doc.sections):
                QMessageBox.warning(self,'重复','已有同名事件回调分区');return
            self.current_doc.sections.append(section)
            # Incremental insertion preserves existing scene item positions, pan and zoom.
            self.canvas.board.add_section_item(section)
            self.canvas.board.update_connections()
            self.refresh_tree();self.mark_dirty()

    def show_entity_help(self):
        from .help_dialog import EntityHelpDialog
        EntityHelpDialog(self).exec()

    def quick_add(self,item,column=0):
        kind=item.data(0,Qt.UserRole)
        if not kind or not self.current_doc:return
        selected=[s for s in self.canvas.board.selectedItems() if hasattr(s,'model')]
        if not selected:
            QMessageBox.information(self,'使用方法','先单击选中画布上的分区，再双击工具库积木；或直接拖入分区。');return
        section=selected[0]
        if section.model.kind=='events' and kind!='event' or section.model.kind=='data' and kind not in DATA_BLOCKS:
            QMessageBox.warning(self,'分区限制','当前分区不允许这种积木。');return
        if kind=='event' and section.model.kind!='events':
            QMessageBox.warning(self,'分区限制','事件帽子只能放入事件分区。');return
        from .dialogs import new_block
        section.model.blocks.append(new_block(kind));section.update_size();self.mark_dirty()

    def delete_dropped_expression(self,expression_id):
        if self.canvas.delete_embedded_block(expression_id):
            self.statusBar().showMessage(translated_text('已删除拖入模块区的嵌套表达式'),3500)
            self.mark_dirty()

    def delete_dropped_block(self,block_id):
        if self.canvas.delete_existing_block(block_id):
            self.statusBar().showMessage(translated_text('已将积木拖回积木库并删除'),3500)
            self.mark_dirty()

    def insert_method(self,item,col=0):
        row=item.data(0,Qt.UserRole)
        if not row:return
        from ..expressions import block_from_method
        block=block_from_method(row)
        self.insert_block_selected(block)

    def insert_event(self,item,col=0):
        row=item.data(0,Qt.UserRole)
        from .dialogs import new_block
        block=new_block('event');block.args['event']=row['name']
        candidates=[s for s in self.current_doc.sections if s.kind=='events'] if self.current_doc else []
        if not candidates:
            QMessageBox.warning(self,'缺少事件区','请先创建一个事件分区。');return
        candidates[0].blocks.append(block);self.canvas.board.refresh_sections([candidates[0].id]);self.mark_dirty()

    def insert_block_selected(self,block):
        selected=[s for s in self.canvas.board.selectedItems() if hasattr(s,'model')]
        if not selected:
            QMessageBox.information(self,'提示','先选中一个画布分区。');return
        section=selected[0]
        if section.model.kind=='events' or section.model.kind=='data' and block.kind not in DATA_BLOCKS:
            QMessageBox.warning(self,'分区限制','此分区不能放入这种 API 积木。');return
        section.model.blocks.append(block);section.update_size();self.mark_dirty()

    def jump_to_issue(self, item):
        """Jump to a specific diagnostic without modifying project contents."""
        target=item.data(Qt.UserRole)
        if not isinstance(target,dict) or not target.get('section_id'):
            return
        doc=next((d for d in self.project.documents if d.id==target.get('document_id')),None)
        if doc is None:
            return
        if self.current_doc is not doc:
            self.load_document(doc)
        # Wait for QGraphicsProxyWidget to finish Qt's deferred flow layout.
        QTimer.singleShot(0,lambda document_id=doc.id, sid=target['section_id'], bid=target.get('block_id',''):
                          self._focus_issue_block(document_id,sid,bid))

    def _focus_issue_block(self, document_id, section_id, block_id):
        if not self.current_doc or self.current_doc.id!=document_id:
            return
        section=next((s for s in self.current_doc.sections if s.id==section_id),None)
        if section is None:
            return
        # Data sections are edited through their linked variable's definition
        # workspace and are not rendered as independent main-canvas objects.
        if section.kind=='data':
            from ..data_definitions import find_source
            source=find_source(self.current_doc,section)
            if source:
                source_section,source_block=source
                section_id=source_section.id
                block_id=source_block.id
        self.canvas.focus_diagnostic(section_id,block_id)

    def update_preview(self):
        if not self.current_doc:return
        generator=SquirrelGenerator()
        code=generator.compile(self.project,self.current_doc)
        self.preview.setPlainText(code)
        self.issues.clear()
        from .localization import localized_issue, translated_text
        for issue in self.validator.check(self.project,self.current_doc):
            row=QListWidgetItem(localized_issue(issue.level,issue.text,section=issue.section))
            row.setData(Qt.UserRole,{'document_id':self.current_doc.id,
                                    'section_id':issue.section_id,'block_id':issue.block_id})
            if issue.section_id:
                row.setToolTip('点击跳转到对应积木' if current_profile().language=='zh' else 'Click to jump to the affected block')
            self.issues.addItem(row)
        if not self.issues.count():self.issues.addItem(translated_text('未检测到当前静态规则覆盖范围内的问题。'))

    def export_current(self):
        if not self.current_doc:return
        problems=[] if self.ignore_static_checks else [i.text for i in self.validator.check(self.project,self.current_doc) if i.level=='错误']
        if problems:
            QMessageBox.warning(self,'导出中止','静态检查有错误：\n'+'\n'.join(problems[:12]));return
        filename=self.current_doc.name
        output,_=QFileDialog.getSaveFileName(self,'导出单个 VScript',filename,'VScript (*.nut)')
        if not output:return
        generator=SquirrelGenerator();code=generator.compile(self.project,self.current_doc)
        if generator.errors:
            QMessageBox.warning(self,'导出中止','代码生成存在错误：\n'+'\n'.join(generator.errors));return
        if not output.endswith('.nut'):output+='.nut'
        Path(output).write_text(code,encoding='utf-8')
        self.statusBar().showMessage(translated_text('已导出 ')+output,7000)
        ask=QMessageBox.question(self,'VPK 打包','是否同时打包为 VPK 模组？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ask==QMessageBox.Yes:
            self._package_vpk({self.current_doc.name:code},Path(output).with_suffix('.vpk'))

    def export_all(self):
        folder=QFileDialog.getExistingDirectory(self,'选择导出目录')
        if not folder:return
        generator=SquirrelGenerator();result={};errors=[]
        for doc in self.project.documents:
            problems=[] if self.ignore_static_checks else [i.text for i in self.validator.check(self.project,doc) if i.level=='错误']
            if problems:
                errors.extend([doc.name+': '+msg for msg in problems]);continue
            text=generator.compile(self.project,doc)
            if generator.errors:errors.extend([doc.name+': '+msg for msg in generator.errors])
            result[doc.name]=text
        if errors:
            QMessageBox.warning(self,'生成错误','有文件导出失败：\n'+'\n'.join(errors[:12]));return
        root=Path(folder)/'scripts'/'vscripts'
        root.mkdir(parents=True,exist_ok=True)
        for name,code in result.items():
            target=root/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(code,encoding='utf-8')
        QMessageBox.information(self,'导出成功',f'已导出 {len(result)} 个 .nut 文件到 scripts/vscripts。')
        ask=QMessageBox.question(self,'VPK 打包','是否同时打包整个工程为 VPK？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ask==QMessageBox.Yes:
            self._package_vpk(result,Path(folder)/(Path(folder).name+'.vpk'))

    def _package_vpk(self,scripts,default_path):
        details=VPKInfoDialog(default_path.stem,self)
        if details.exec()!=QDialog.Accepted:return
        dest,_=QFileDialog.getSaveFileName(self,'保存 VPK 模组',str(default_path),'Valve VPK (*.vpk)')
        if not dest:return
        if not dest.lower().endswith('.vpk'):dest+='.vpk'
        try:
            package_scripts(dest,scripts,**details.metadata())
        except (OSError,ValueError,TypeError) as exc:
            QMessageBox.warning(self,'VPK 打包失败',str(exc));return
        QMessageBox.information(self,translated_text('VPK 导出成功'),translated_text('已创建 ')+str(dest)+'\n'+translated_text('包含 addoninfo.txt 和 scripts/vscripts/*.nut。'))

    def export_vpk(self):
        result={};errors=[]
        for doc in self.project.documents:
            problems=[] if self.ignore_static_checks else [i.text for i in self.validator.check(self.project,doc) if i.level=='错误']
            if problems:errors.extend(doc.name+': '+problem for problem in problems);continue
            generator=SquirrelGenerator();result[doc.name]=generator.compile(self.project,doc)
            if generator.errors:errors.extend(doc.name+': '+err for err in generator.errors)
        if errors:
            QMessageBox.warning(self,'导出中止','代码生成存在错误：\n'+'\n'.join(errors[:12]));return
        self._package_vpk(result,Path.cwd()/'addon.vpk')

    def external_library(self):
        dlg=LibraryDialog(self.project,self)
        if dlg.exec():
            self.palette.reload_external(self.project.library)
            self.palette.filter('')
            self.statusBar().showMessage(translated_text('外部 API 已同步为 ')+str(len(self.project.library.get('functions',[])))+translated_text(' 个可拖动方法积木'),7000)
            self.mark_dirty()

    def catalog_about(self):
        stats=self.catalog.stats()
        QMessageBox.information(self,translated_text('资料库覆盖范围'),translated_text('游戏事件：')+str(stats['events'])+'\n'+translated_text('方法记录：')+str(stats['methods'])+'\nSendTable: '+str(stats['sendtables'])+'\nNetProp: '+str(stats['netprops'])+'\n\n'+translated_text('离线基础索引，非完整官方镜像。参见 DATA_SOURCES.md。'))

    def _update_text(self, en, zh):
        return en if current_profile().language=='en' else zh

    def _show_prior_update_result(self):
        path=Path.home()/'.l4vp_visual_editor'/'update_status.json'
        if not path.is_file():return
        try:
            result=json.loads(path.read_text(encoding='utf-8'))
            path.unlink(missing_ok=True)
            if result.get('success'):
                self.statusBar().showMessage(self._update_text(
                    'Editor updated to ','编辑器已更新至 ')+str(result.get('version','')),10000)
            else:
                QMessageBox.warning(self,self._update_text('Update failed','更新失败'),str(result.get('message','')))
        except (OSError,ValueError):
            pass

    def check_for_updates(self,manual=True):
        if self._check_task is not None and self._check_task.isRunning():return
        if self._download_task is not None and self._download_task.isRunning():return
        self._manual_update_check=bool(manual)
        self.statusBar().showMessage(self._update_text(
            'Checking GitHub Releases…','正在检查 GitHub Release…'),8000)
        task=ReleaseCheckTask()
        self._check_task=task
        task.found.connect(self._release_checked)
        task.failed.connect(self._release_check_failed)
        task.finished.connect(self._release_check_finished)
        task.start()

    def _release_check_finished(self):
        if self._close_pending:
            self._close_pending=False
            QTimer.singleShot(0,self.close)

    def _release_check_failed(self,message):
        if self._close_pending:return
        message=update_error_text(message, current_profile().language)
        if self._manual_update_check:
            QMessageBox.information(self,self._update_text('Update check','检查更新'),message)
        else:
            self.statusBar().showMessage(message,8000)

    def _release_checked(self, info):
        if self._close_pending:return
        self._last_release=info
        if not is_newer(info.version,APP_VERSION):
            message=self._update_text(f'You are using the latest version ({APP_VERSION}).',f'当前已是最新版本（{APP_VERSION}）。')
            if self._manual_update_check:
                QMessageBox.information(self,self._update_text('Update check','检查更新'),message)
            else:self.statusBar().showMessage(message,5000)
            return
        if not self._manual_update_check and str(self.preferences.value('updates/skipped_tag',''))==info.tag:
            return
        message=self._update_text(
            f'New version {info.version} is available (installed: {APP_VERSION}).',
            f'检测到新版本 {info.version}（当前：{APP_VERSION}）。')
        if not info.asset_url and not self._manual_update_check:
            self.statusBar().showMessage(self._update_text(
                'New GitHub Release has no installable ZIP asset.',
                'GitHub 新版本没有可安装的 ZIP 附件。'),10000)
            return
        if not info.asset_url:
            QMessageBox.information(self,self._update_text('New GitHub Release','GitHub 新版本'),
                message+'\n'+self._update_text(
                    'No packaged editor ZIP found in the Release assets. Please download manually from GitHub.',
                    '该 Release 未附带编辑器 ZIP 安装包，请前往 GitHub 手动下载。')+'\n'+info.html_url)
            return
        dialog=QMessageBox(self)
        dialog.setWindowTitle(self._update_text('Editor update available','发现编辑器更新'))
        dialog.setText(message)
        dialog.setInformativeText(self._update_text(
            'Download the official Release ZIP, then close the editor and install it? Your .l4vp projects will be preserved.',
            '是否下载官方 Release ZIP，并在关闭编辑器后安装？不会覆盖你的 .l4vp 工程。'))
        install=dialog.addButton(self._update_text('Download update','下载更新'),QMessageBox.AcceptRole)
        later=dialog.addButton(self._update_text('Later','稍后'),QMessageBox.RejectRole)
        open_page=dialog.addButton(self._update_text('Open Release page','打开 Release 页面'),QMessageBox.ActionRole)
        dialog.exec()
        if dialog.clickedButton() is install:
            self._begin_download(info)
        elif dialog.clickedButton() is open_page:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl(info.html_url))
        elif dialog.clickedButton() is later and not self._manual_update_check:
            self.preferences.setValue('updates/skipped_tag',info.tag)

    def _begin_download(self,info):
        if self._download_task is not None and self._download_task.isRunning():return
        task=ReleaseDownloadTask(info)
        self._download_task=task
        progress=QProgressDialog(self._update_text('Downloading verified update…','正在下载并校验更新…'),
                                 self._update_text('Cancel','取消'),0,100,self)
        progress.setWindowTitle(self._update_text('Editor updater','编辑器更新'))
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.canceled.connect(task.cancel)
        task.progress.connect(progress.setValue)
        task.completed.connect(lambda archive,folder:self._download_ready(info,archive,folder))
        task.failed.connect(self._download_failed)
        self._download_progress=progress
        task.start()

    def _download_failed(self,message):
        was_cancelled = isinstance(message, Exception) and message.__class__.__name__ == 'UpdateCancelled'
        message=update_error_text(message, current_profile().language)
        if self._download_progress is not None:
            self._download_progress.close()
            self._download_progress=None
        if not was_cancelled:
            QMessageBox.warning(self,self._update_text('Download failed','下载失败'),message)

    def _download_ready(self,info,archive,folder):
        if self._download_progress is not None:
            self._download_progress.close()
            self._download_progress=None
        if self._download_task is not None:
            self._download_task.wait(1500)
        self._update_pending=(archive,folder,info.tag)
        answer=QMessageBox.question(self,self._update_text('Install update','安装更新'),
            self._update_text(
                'ZIP downloaded and validated. Close the editor, install the update, then restart?\nSave your projects before continuing.',
                '更新包下载及校验成功。是否关闭编辑器、安装更新并重新启动？\n请先保存工程。'),
            QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if answer==QMessageBox.Yes:
            self.close() # closeEvent honours Save / Discard / Cancel.
        else:
            self._discard_pending_update()

    def _discard_pending_update(self):
        if self._update_pending:
            shutil.rmtree(self._update_pending[1],ignore_errors=True)
            self._update_pending=None

    def _launch_external_updater(self):
        archive,folder,version=self._update_pending
        source=Path(__file__).resolve().parents[1]/'updater_worker.py'
        worker=Path(folder)/'updater_worker.py'
        shutil.copy2(source,worker)
        args=[sys.executable,str(worker),'--parent-pid',str(os.getpid()),
              '--install-dir',str(Path(__file__).resolve().parents[2]),
              '--archive',archive,'--working-dir',folder,'--version',version]
        subprocess.Popen(args,cwd=folder,
                         creationflags=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
        self._update_pending=None

    def closeEvent(self,event):
        if self._check_task is not None and self._check_task.isRunning():
            self._close_pending=True
            event.ignore()
            return
        if self._download_task is not None and self._download_task.isRunning():
            self._download_task.cancel()
            QMessageBox.information(self,self._update_text('Download running','下载中'),
                self._update_text('Download cancellation requested. Close the editor after it stops.',
                                  '已请求取消下载；请在下载停止后退出编辑器。'))
            event.ignore()
            return
        if not self.check_unsaved():
            self._discard_pending_update()
            event.ignore()
            return
        if self._update_pending:
            try:
                self._launch_external_updater()
            except (OSError,ValueError) as exc:
                QMessageBox.warning(self,self._update_text('Update error','更新错误'),str(exc))
                self._discard_pending_update()
                event.ignore()
                return
        self.catalog.close()
        event.accept()
