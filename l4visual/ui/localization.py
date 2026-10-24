"""Translate UI chrome, never project identifiers, source editors or script output.

Qt's screens are assembled dynamically, including member pickers and floating
workspaces. Store the original control text so language switching is reversible.
"""
from __future__ import annotations
from ..display_profile import current_profile

UI_EN = {
    '字符串调用函数':'Function call as string',
    '⠿ 字符串调用':'⠿ String call',
    '生成可嵌入 RunScriptCode 的调用字符串':'Generate a call string for RunScriptCode',
    'Delete': 'Delete',
    '拖动积木到分区或 C 形内部 · 直接编辑浅色参数框': 'Drag blocks into sections or C-shaped containers; edit light-colored fields',
    '展开 / 收起 API 字典': 'Show / hide API catalog',
    '拖动已有积木到此处即可删除；不影响已有分区坐标': 'Drop an existing block here to delete it without moving sections',
    '  ⌫  拖动已有积木到这里快速删除  ': '  ⌫  Drop a block here to delete it  ',
    '将积木放入此处': 'Drop blocks here',
    '将积木拖放到这里': 'Drop blocks here',
    '将变量和数据操作积木拖入根容器内部': 'Drop variables and data blocks inside the fixed container',
    '打开数据定义分区': 'Open data workspace',
    '选择属性：': 'Select property: ',
    '选择 NetProp：': 'Select NetProp: ',
    '未选择': 'Not selected',
    '无': 'None',
    'root': 'Root (global)',
    '普通': 'Regular',
    '每次覆盖': 'Overwrite every time',
    '仅首次创建（推荐）': 'Create if absent (recommended)',
    '仅修改已有成员': 'Update existing member only',
    '仅引用（不生成初始化代码）': 'Reference only (no initialization)',
    'ScriptScope 成员初始化：': 'ScriptScope member initialization:',
    '否则如果 / else if': 'Else if',
    '删除此 else if 分支及其内部的全部积木': 'Delete this else-if branch and all its blocks',
    '首次添加 else；已有 else 时在它前面插入 else if。': 'First click adds else; later clicks insert else-if before else.',
    '输入 Squirrel 脚本；Enter 换行，支持多行': 'Enter Squirrel code; press Enter for a new line',
    '复制 / 删除 / 移动积木': 'Copy / delete / move block',
    '只删除当前积木（保留内部积木）': 'Delete this block only (keep inner blocks)',
    '只删除当前表达式积木': 'Delete this expression block only',
    '删除 operator，保留左值': 'Delete operator and keep left value',
    '删除 operator，保留右值': 'Delete operator and keep right value',
    '删除表达式外壳，保留内部值': 'Delete expression wrapper and keep inner value',
    '删除当前积木及全部内部积木': 'Delete block and all inner blocks',
    '无法单独删除': 'Cannot delete wrapper only',
    '此位置不能容纳内部积木。请先移动内部积木，再删除外层积木。': 'Inner blocks cannot be placed here. Move them elsewhere before deleting the outer block.',
    '左键拖出变量引用；右键可以修改名称或选择 Table / Set 成员': 'Drag to copy a variable reference; right-click to rename or choose Table/Array members',
    '重命名变量': 'Rename variable',
    '复制变量引用': 'Copy variable reference',
    '选择成员变量…': 'Choose member…',
    '打开独立复杂变量工作区': 'Open complex-data workspace',
    '仅执行方法，不生成结果变量': 'Call method without a result variable',
    '左键：选择此成员；右键：如果是复杂成员则进入下一层': 'Left-click to choose; right-click a complex member to browse it',
    '返回上一层': 'Back one level',
    '× 返回上一层': '× Back',
    '● 根变量': '● Root variable',
    '使用当前层': 'Use current level',
    '手动填写成员 / 数字索引': 'Enter member / numeric index manually',
    '成员名称或索引': 'Member name or index',
    '成员名称（Set 必须输入整数）': 'Member name (Array requires an integer)',
    '暂无已收录成员，可使用下方手动输入添加访问路径。': 'No cataloged members; use manual entry below.',
    '索引 / 键名（可选）': 'Index / key (optional)',
    '当前元素的值。Table 是成员值；Array 是元素值。': 'Current value: Table member value or Array element value.',
    '可选：Array 为从 0 开始的索引；Table 为成员键名。': 'Optional: Array index starts at zero; Table uses member key.',
    '变量和数据': 'Variables & data',
    '属性 / 嵌套表': 'Property / nested table',
    '数据类型': 'Data type',
    '第一步：选择实体网络类（例如 CTerrorPlayer、CBaseCombatWeapon）': 'Step 1: choose entity network class (e.g. CTerrorPlayer, CBaseCombatWeapon)',
    '按类名筛选': 'Filter entity classes',
    '← 返回实体类别': '← Back to entity classes',
    '查找属性名 / 成员路径': 'Search property or member path',
    '运行时：': 'Runtime: ',
    '资料分组：': 'Documentation group: ',
    '成员名称': 'Member name',
    '成员类型': 'Member type',
    '添加成员': 'Add member',
    '删除成员': 'Remove member',
    '使用选中路径': 'Use selected path',
    '新建形参成员': 'Add parameter member',
    '字段名（Array 可用数字索引）': 'Field name (Array may use numeric indices)',
    '类型': 'Type',
    '参数': 'Arguments',
    '变量': 'Variable',
    '执行': 'Execute',
    '否则': 'Else',
    '捕获': 'Catch',
    '设置': 'Settings',
    '确定': 'OK',
    '取消': 'Cancel',
    '关闭': 'Close',
    '新建文件': 'New file',
    '新建文件夹': 'New folder',
    '删除文件': 'Delete file',
    '删除文件夹': 'Delete folder',
    '重命名文件': 'Rename file',
    '重命名文件夹': 'Rename folder',
    '修改': 'Edit',
    '编辑': 'Edit',
    'TraceLine 射线检测': 'TraceLine raycast',
    'TraceLine 配置工作区...': 'TraceLine configuration…',
    'TraceLine 语句块：设置 start/end/ignore/mask，追踪结果写入 output Table；右键打开配置。': 'TraceLine statement: configure start/end/ignore/mask, write results into the output table; right-click to configure.',
    '删除': 'Delete',
    '上移': 'Move up',
    '下移': 'Move down',
    '添加积木': 'Add block',
    '添加内部积木': 'Add inner block',
    '确认删除分区': 'Delete section?',
    '编辑分区': 'Edit section',
    '删除分区': 'Delete section',
    '编辑 / 删除分区': 'Edit / delete section',
    '拖入工作区：': 'Drag into workspace: ',
    '搜索积木...': 'Search blocks…',
    '拖动已有积木到这里快速删除': 'Drop existing blocks here to delete',
    '仅启用的配置生成到 .nut。未启用的配置在生成时完全省略。': 'Only enabled configuration is written to .nut; disabled settings are omitted.',
    '模组名称': 'Addon name',
    '作者': 'Author',
    '版本': 'Version',
    '简介': 'Description',
    'VPK 模组信息': 'VPK addon information',
    '填写作者；导出自动添加 /Vscript Visual Maker': 'Enter author; /Vscript Visual Maker is appended on export',
    'Squirrel 原始代码': 'Raw Squirrel code',
    '多行文本': 'Multiline text',
    '变量作用域': 'Variable scope',
    '数据类型（Set = []）': 'Data type (Set = [])',
    '查找方式': 'Search method',
    '结果变量（空=忽略返回值）': 'Result variable (empty = discard result)',
    '变量名称（右键可改）': 'Variable name (right-click to rename)',
    '初始值 / 表达式': 'Initial value / expression',
    '遍历目标': 'Iterable',
    '布尔表达式': 'Boolean expression',
    '编辑变量链 [xxx].[yyy].[zzz] ...': 'Edit variable access chain [xxx].[yyy].[zzz] ...',
    '将值切换为多行字符串编辑器': 'Switch value to multiline string editor',
    '添加 Else If 分支': 'Add else-if branch',
    '内部容器（独立编辑，不受普通积木层级限制）': 'Inner blocks (independent editor)',
    '返回': 'Back',
    '移除变量引用，恢复文本输入': 'Remove variable reference and restore text input',
    '移除嵌套积木，恢复文字输入': 'Remove nested block and restore text input',
    '对象': 'Object',
    '目标': 'Target',
    '左值': 'Left operand',
    '右值': 'Right operand',
    '属性名称': 'Property name',
    '圆形=可放入表达式插槽；方形=仅执行': 'Rounded = can be embedded; square = statement only',
    '形参 →': 'Parameters →',
    '刷新成员': 'Refresh members',
    'ScriptScope 成员引用库  ·  拖入目标窗口自动设为「仅引用」': 'ScriptScope member library · drop to reuse a member as a reference only',
    '当前脚本中尚未定义 ScriptScope 成员；请先在任一 ScriptScope 数据工作区添加成员，再刷新。': 'No ScriptScope members are defined in this script yet. Add a member to any ScriptScope workspace, then refresh.',
    '拖入其他 ScriptScope 数据窗口：自动创建“仅引用”成员，不重复初始化': 'Drop into another ScriptScope workspace to reference the member without reinitializing it',
    '暂无已定义的 ScriptScope 成员': 'No defined ScriptScope members',
    '放弃更改': 'Discard changes',
    '完成 / 返回主工作区': 'Done / back to main workspace',
    '外部自定义 API': 'External custom API',
    '搜索官方 API / 事件 / NetProp': 'Search official APIs, events and NetProps',
    '选择 L4D2 NetProp · 实体类 / 属性': 'Choose L4D2 NetProp · entity class / property',
    '固定数据根容器（不可删除）': 'Fixed data container (cannot be removed)',
    '数据分区': 'Data workspace',
    '载入外部库描述': 'Load external API description',
    '导出中止': 'Export cancelled',
    '分区限制': 'Section restriction',
    '离线数据库已加载。Ctrl+滚轮缩放画布。右键积木可编辑/复制。': 'Offline catalog loaded. Ctrl+wheel zooms; right-click blocks to edit or copy.',
    '界面语言与积木风格已更新；导出代码不变。': 'Display language and block style updated; exported code is unchanged.',
}


def translated_text(text: str, language: str | None = None) -> str:
    """Only translate editor-owned labels; never guess about user source text."""
    if (language or current_profile().language) != 'en':
        return text
    return UI_EN.get(text, text)


def localize_widget_tree(root):
    """Refresh already-built Qt labels/buttons/tooltips, reversible on zh/en switch.

    Source editors and values in QLineEdit/QPlainTextEdit are explicitly untouched.
    """
    from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QToolButton,
                                    QGroupBox, QLineEdit, QPlainTextEdit, QComboBox, QTreeWidget, QTabWidget, QCheckBox, QRadioButton)
    from PySide6.QtCore import QSignalBlocker
    if not isinstance(root, QWidget):
        return
    lang=current_profile().language
    if isinstance(root, QWidget):
        title_key=root.property('l4_i18n_title')
        if title_key is None and (root.windowTitle() in UI_EN or any(root.windowTitle().startswith(prefix) for prefix in UI_PREFIX_EN)):
            title_key=root.windowTitle();root.setProperty('l4_i18n_title',title_key)
        if title_key is not None:root.setWindowTitle(translated_text(title_key,lang))
    widgets=[root]+root.findChildren(QWidget)
    for widget in widgets:
        if isinstance(widget, (QLabel,QPushButton,QToolButton,QGroupBox,QCheckBox,QRadioButton)):
            key=widget.property('l4_i18n_text')
            if key is None:
                existing=widget.text() if hasattr(widget,'text') else widget.title()
                if existing in UI_EN or any(existing.startswith(prefix) for prefix in UI_PREFIX_EN):
                    key=existing
                    widget.setProperty('l4_i18n_text',key)
            if key is not None:
                desired=translated_text(key,lang)
                if hasattr(widget,'setText'):widget.setText(desired)
                elif hasattr(widget,'setTitle'):widget.setTitle(desired)
        if isinstance(widget,QComboBox):
            # Only data-backed choices. For text-backed enum controls (e.g.
            # '普通' / 'Table'), translating currentText would change codegen.
            if widget.count() and all(widget.itemData(i) is not None for i in range(widget.count())):
                originals=widget.property('l4_i18n_items')
                if originals is None:
                    originals=[widget.itemText(i) for i in range(widget.count())]
                    widget.setProperty('l4_i18n_items',originals)
                if len(originals)==widget.count():
                    blocker=QSignalBlocker(widget)
                    for i,label in enumerate(originals):
                        widget.setItemText(i,translated_text(label,lang))
                    del blocker
        if isinstance(widget,QTreeWidget):
            header=widget.headerItem()
            originals=widget.property('l4_i18n_headers')
            if header is not None:
                if originals is None:
                    originals=[header.text(i) for i in range(widget.columnCount())]
                    widget.setProperty('l4_i18n_headers',originals)
                if len(originals)==widget.columnCount():
                    for i,label in enumerate(originals):header.setText(i,translated_text(label,lang))
        if isinstance(widget,QTabWidget):
            originals=widget.property('l4_i18n_tabs')
            if originals is None:
                originals=[widget.tabText(i) for i in range(widget.count())]
                widget.setProperty('l4_i18n_tabs',originals)
            if len(originals)==widget.count():
                for i,label in enumerate(originals):widget.setTabText(i,translated_text(label,lang))
        if isinstance(widget,QLineEdit):
            key=widget.property('l4_i18n_placeholder')
            if key is None and (widget.placeholderText() in UI_EN or any(widget.placeholderText().startswith(prefix) for prefix in UI_PREFIX_EN)):
                key=widget.placeholderText()
                widget.setProperty('l4_i18n_placeholder',key)
            if key is not None:widget.setPlaceholderText(translated_text(key,lang))
        if isinstance(widget,QPlainTextEdit):
            key=widget.property('l4_i18n_placeholder')
            if key is None and (widget.placeholderText() in UI_EN or any(widget.placeholderText().startswith(prefix) for prefix in UI_PREFIX_EN)):
                key=widget.placeholderText()
                widget.setProperty('l4_i18n_placeholder',key)
            if key is not None:widget.setPlaceholderText(translated_text(key,lang))
        tip=widget.property('l4_i18n_tooltip')
        if tip is None and (widget.toolTip() in UI_EN or any(widget.toolTip().startswith(prefix) for prefix in UI_PREFIX_EN)):
            tip=widget.toolTip()
            widget.setProperty('l4_i18n_tooltip',tip)
        if tip is not None:widget.setToolTip(translated_tooltip(tip,lang))


class DialogLocalizationFilter:
    """Qt event filter adapter; imported lazily so core modules need no Qt."""
    @staticmethod
    def make():
        from PySide6.QtCore import QObject, QEvent
        from PySide6.QtWidgets import QDialog, QMenu
        class Filter(QObject):
            def eventFilter(self,object,event):
                if event.type()==QEvent.ToolTip and hasattr(object,'toolTip') and hasattr(object,'setToolTip'):
                    tip=object.toolTip()
                    original=object.property('l4_original_runtime_tip')
                    last=object.property('l4_last_runtime_tip')
                    if original is None or (last is not None and tip!=last and tip!=original):
                        original=tip
                        object.setProperty('l4_original_runtime_tip',original)
                    desired=translated_tooltip(original)
                    if desired!=tip:
                        object.setToolTip(desired)
                    object.setProperty('l4_last_runtime_tip',desired)
                if event.type()==QEvent.Show and isinstance(object,(QDialog,QMenu)):
                    if isinstance(object,QDialog):localize_widget_tree(object)
                    else:
                        lang=current_profile().language
                        for act in object.actions():
                            key=act.property('l4_i18n_text')
                            if key is None and (act.text() in UI_EN or any(act.text().startswith(prefix) for prefix in UI_PREFIX_EN)):
                                key=act.text();act.setProperty('l4_i18n_text',key)
                            if key is not None:act.setText(translated_text(key,lang))
                return False
        return Filter()

# Extended coverage for contextual dialogs, variable workspaces and section UI.
# Text describing a concrete runtime API remains in the original API's name.
UI_EN.update({
    '固定初始化分区': 'Fixed initialization section',
    '初始化分区由文件自动维护，不可删除、转换或重复创建。': 'The file owns its initialization section; it cannot be deleted, converted or duplicated.',
    '该变量不是 Table / Set，没有已登记的成员。': 'This is not a Table/Array, so it has no registered members.',
    '引用已失效': 'Broken reference',
    '普通变量': 'Regular variable',
    '找不到原始变量声明，可能已经被删除。': 'Original variable declaration not found; it may have been deleted.',
    '生成感染者 ZSpawn': 'Spawn infected (ZSpawn)',
    '感染者种类': 'Infected type',
    '生成位置 Vector': 'Spawn position Vector',
    'Summon 配置工作区...': 'Spawn configuration workspace…',
    '选择属性': 'Select property',
    '复制积木': 'Copy block',
    '删除积木': 'Delete block',
    '上移积木': 'Move block up',
    '下移积木': 'Move block down',
    '局部变量作用域': 'Local variable scope',
    '复合表达式：请在生成器检查后手动修改': 'Complex expression: review the generated Squirrel code',
    '重新选择成员': 'Choose a different member',
    'ScriptScope 引用': 'ScriptScope reference',
    '未定义的 ScriptScope 成员': 'Undefined ScriptScope member',
    '编辑积木': 'Edit block',
    '自动创建 / 绑定 info_target': 'Automatically create / bind info_target',
    '方法参数': 'Method parameters',
    '参数插槽（动态展开）': 'Argument slots (dynamically expanded)',
    '实体对象': 'Entity object',
    '游戏事件': 'Game event',
    '原版游戏事件': 'Built-in game event',
    '官方方法': 'Official method',
    '调用自定义函数': 'Call custom function',
    '复杂变量': 'Complex variable',
    '判断表达式': 'Condition expression',
    '(无参数)': '(no arguments)',
    'Array 特殊操作': 'Array operations',
    'Get 的结果变量': 'Get result variable',
    '编辑访问层级': 'Edit access hierarchy',
    '链式变量访问 [xxx].[yyy].[zzz]': 'Chained variable access [xxx].[yyy].[zzz]',
    '根变量': 'Root variable',
    '当前是 Table': 'Current object is a Table',
    '编辑最后一级': 'Edit last segment',
    '移除最后一级': 'Remove last segment',
    '＋ Table 成员': '＋ Table member',
    '＋ Set 索引': '＋ Array index',
    '索引表达式': 'Index expression',
    '数字或返回数字的表达式': 'Number or expression returning a number',
    '当前为 [] 数组，请改用数值索引槽。': 'Current value is an Array; use a numeric index.',
    '成员 . ': 'Member . ',
    '索引 [ ] ': 'Index [ ] ',
    '选择成员变量 · ': 'Choose member · ',
    '当前已选择：': 'Current selection: ',
    '形参结构与成员 · ': 'Parameter structure & members · ',
    '字段 / 索引': 'Field / index',
    '无效名称': 'Invalid name',
    '字段需要合法标识符，Array 索引可以使用数字。': 'Fields require valid identifiers; Array indices can be numeric.',
    '此结构仅供编辑器显示和拖放，不会在函数中创建额外变量。\n选中成员后点“使用选中路径”，可以将它拖进函数内部表达式槽。': 'This is editor-only structure metadata; it creates no extra runtime variables.\nSelect a member and click “Use selected path” to drag it into a function expression slot.',
    '编辑访问层级': 'Edit access levels',
    'Help - 常见实体获取方式': 'Help - Common entity lookup methods',
    'Summon 配置 - SpawnEntityFromTable': 'Spawn configuration - SpawnEntityFromTable',
    '注意：实体可否在运行时创建、需要哪些专用 KeyValues，应以该 classname 的引擎定义为准。': 'Note: whether an entity can be spawned, and which KeyValues it requires, depends on its class definition.',
    '双击末级属性选择；数组属性（如 m_iAmmo）会启用 Array 模式和索引槽。\n资料分组名不等于运行时属性名，保存时自动使用可调用的属性键。': 'Double-click a leaf property. Arrays (e.g. m_iAmmo) enable array mode and an index slot.\nDocumentation table groups are not runtime keys; the selectable property key is saved.',
    '注意：SendTable 数组范围，不保证 VScript 可直接访问。\n': 'Note: SendTable array range; direct VScript access has not been verified.\n',
    '外部 API 保存后会在左侧生成可拖动方法块。每个描述包含 owner/name/params/returns。': 'Saved external APIs appear as draggable method blocks. Each requires owner/name/params/returns.',
    '从 JSON 导入': 'Import JSON',
    '外部 API 描述文件': 'External API definition file',
    '模组名称不能为空': 'Addon name is required',
    '请输入模组名称。': 'Enter an addon name.',
    '最终作者署名：/Vscript Visual Maker': 'Final author credit: /Vscript Visual Maker',
    '使用方法': 'Usage instructions',
    '文件夹名不能含路径符号': 'Folder name cannot contain path separators',
    '打开文件': 'Open file',
    '选择导出目录': 'Choose export folder',
    'VPK 打包': 'Package VPK',
    '事件回调表': 'Event callback table',
    '先单击选中画布上的分区，再双击工具库积木；或直接拖入分区。': 'Select a section and double-click a palette block, or drag blocks into a section.',
    '属性': 'Property',
    '键': 'Key',
    '值': 'Value',
    '固定数据根容器（不可删除）': 'Fixed data container (cannot be removed)',
    '实体类别': 'Entity class',
    '查找属性名 / 成员路径': 'Search attribute name / member path',
    '仅引用': 'Reference only',
    '编辑分区属性': 'Edit section properties',
    '找不到工程文件': 'Project file not found',
    '打开失败': 'Failed to open',
    '保存失败': 'Failed to save',
    '删除失败': 'Failed to delete',
    '新建工程': 'New project',
    '新建 .nut 文件': 'New .nut file',
    '删除确认': 'Confirm deletion',
    '创建文件夹': 'Create folder',
    '重命名': 'Rename',
    '查看': 'View',
    '新建': 'New',
    '返回主工作区': 'Back to main workspace',
    '复制': 'Copy',
    '错误': 'Error',
    '警告': 'Warning',
    '选择': 'Choose',
    '来源：': 'Source: ',
})

# Dynamic captions with a stable UI prefix and a project-specific suffix.
UI_PREFIX_EN = {
    '选择成员变量 · ': 'Choose member · ',
    '当前已选择：': 'Current selection: ',
    '形参结构与成员 · ': 'Parameter structure & members · ',
    '选择属性：': 'Select property: ',
    '选择 NetProp：': 'Select NetProp: ',
    '编辑积木 — ': 'Edit block — ',
    '内部积木：': 'Inner blocks: ',
    '删除 ': 'Delete ',
    '无效的成员名称：': 'Invalid member name: ',
}

_old_translated_text = translated_text

def translated_text(text: str, language: str | None = None) -> str:
    lang=language or current_profile().language
    if lang!='en':return text
    if text in UI_EN:return UI_EN[text]
    for prefix,english in UI_PREFIX_EN.items():
        if text.startswith(prefix):return english+text[len(prefix):]
    return text

UI_EN.update({
    '按实体 classname · FindByClassname': 'By entity classname · FindByClassname',
    '按 targetname · FindByName': 'By targetname · FindByName',
    '按模型路径 · FindByModel': 'By model path · FindByModel',
    '按目标键 · FindByTarget': 'By target key · FindByTarget',
    '按 classname + 范围 · FindByClassnameWithin': 'By classname within radius · FindByClassnameWithin',
    '按 targetname + 范围 · FindByNameWithin': 'By targetname within radius · FindByNameWithin',
    '按球形范围 · FindInSphere': 'Within a sphere · FindInSphere',
    '遍历全部实体 · First / Next': 'All entities · First / Next',
    '简体中文': 'Simplified Chinese',
    '一般 · 易于理解的说明': 'General · plain-language labels',
    '专业 · 原始 API / 事件名': 'Professional · original API/event names',
    '界面语言 / Language': 'Interface language',
    '模块风格 / Block style': 'Block style',
    '只更改界面文字和槽位排列，不修改保存的积木数据或导出的 Squirrel 代码。': 'Changes only captions and slot layout, never block data or exported Squirrel code.',
    '显示设置 / Display settings': 'Display settings',
    '当前文件': 'Current file',
    '当前工程没有 .nut 文件，请新建脚本。': 'No .nut files in this project; create a script.',
    '已保存到 ': 'Saved to ',
    '编辑积木 — ': 'Edit block — ',
    '搜索积木...': 'Search blocks…',
    '自动选择': 'Auto-select',
    '信息': 'Information',
})
UI_PREFIX_EN.update({
    '当前文件 ': 'Current file ',
    '已保存到 ': 'Saved to ',
    '最终作者署名：': 'Final author credit: ',
    '固定数据根容器': 'Fixed data container',
})

UI_EN.update({
    '忽略静态检查，允许导出 NUT / VPK': 'Ignore static validation when exporting NUT / VPK',
    '左键拖出变量引用；右键可以修改名称或选择 Table / Set 成员': 'Drag out a variable reference; right-click to rename or choose Table/Array members.',
    '拖动以复制引用；Table、Array 和事件 env 可以右键选择成员。普通变量不支持成员访问。': 'Drag to copy a reference; right-click Table, Array or event env to choose members. Scalars have no members.',
    '拖动复制已嵌入的表达式；原位置保持不变': 'Drag to copy this embedded expression; the original remains in place.',
    '拖动重排积木、移动至其他分支或分区；Ctrl 拖动复制': 'Drag to rearrange blocks or move to another branch/section; Ctrl-drag to copy.',
    '布尔条件表达式': 'Boolean condition expression',
    '可作为返回值的表达式': 'Value-returning expression',
    '点击选择 NetProp 属性': 'Click to choose a NetProp property.',
    '复合表达式：请在生成器检查后手动修改': 'Compound expression: review the generated code manually.',
    '根据 classname 与勾选的 KeyValues 创建实体。右键 -> Summon 配置工作区。请检查实体是否可由该 API 创建。': 'Spawn an entity with the selected classname and KeyValues; right-click for Summon settings. Verify this entity can be spawned by the API.',
    '先选择实体网络类，再选择属性。属性会被保存为字符串字面量，不再允许自由输入。': 'Choose the network class, then its property. The property is saved as a string literal.',
    '右键可选择 env 的字段。': 'Right-click to choose event env fields.',
    '可选：Array 为从 0 开始的索引；Table 为成员键名。': 'Optional: Array indices start at 0; Table uses member keys.',
    'ScriptScope：Value 填实体表达式，打开 Table 数据窗口定义其成员；普通 Table 的 GetScriptScope() 返回值也会推断为 Table。': 'ScriptScope: Value is the entity expression. Open the Table workspace to define members. GetScriptScope() also infers a Table return.',
    'auto: 函数中 local、根位置全局；local: 仅当前作用域；无: 不声明，只对已有变量赋值；static: 仅合法 Squirrel class 静态成员可用。': 'auto: local inside functions, global at root; local: current scope only; none: assign an existing variable; static: valid Squirrel class static member only.',
    '选择实体类与属性。m_iAmmo 等数组自动打开索引槽；LocalWeaponData 等资料分组不会被误加到运行时键名中。': 'Choose entity class and property. Arrays such as m_iAmmo expose an index slot; documentation groups are excluded from runtime keys.',
    '仅当该数据分区属于 ScriptScope 时生效。普通 Table 构造器保持原样。': 'Only applies to ScriptScope workspaces; ordinary Table constructors are unaffected.',
    '形参属于此函数作用域；拖入函数内部槽位，不会重新声明形参。': 'Parameters belong to this function scope. Drag into sockets without redeclaring them.',
    '向工作区拖出此函数的调用积木，原函数分区保持不变': 'Drag a call to this function into the workspace; the function definition stays unchanged.',
    '抓取标题移动分区；双击修改分区属性': 'Drag title to move section; double-click to edit section properties.',
    '圆形=可放入表达式插槽；方形=仅执行': 'Round: expression that fits in a socket; rectangular: statement only.',
    '当前元素的值。Table 是成员值；Array 是元素值。': 'Current element value, from a Table member or Array item.',
    '可选：Array 为从 0 开始的索引；Table 为成员键名。': 'Optional: zero-based Array index or Table member key.',
})

UI_EN.update({
    '命名空间': 'Namespace',
    '函数': 'Function',
    '游戏事件': 'Game events',
    '复杂变量': 'Complex data',
    '分区属性': 'Section properties',
    '函数所属 Table': 'Function owner Table',
    '形参（逗号隔开）': 'Parameters (comma-separated)',
    '容器类型': 'Container type',
    'Think 返回间隔': 'Think return interval',
    '自动绑定': 'Auto-attach',
    '绑定实体 targetname': 'Attached entity targetname',
    '全局函数（不使用 Namespace）': 'Global function (no Namespace)',
    '已绑定变量。请到变量圆圈右键重命名。': 'Bound to a variable. Right-click its token to rename.',
    '可选 Namespace；留空时生成 ::FunctionName': 'Optional Namespace; empty generates ::FunctionName',
    '留空生成全局函数；选择 Namespace 则生成成员函数': 'Leave empty for a global function; select a Namespace for a member function.',
    '添加 Else If 分支': 'Add else-if branch',
    '数据': 'Data',
    '返回类型': 'Return type',
    '分类': 'Category',
    '属性 / 嵌套表': 'Property / nested table',
    '属性': 'Property',
    '数据类型': 'Data type',
    '文件初始化': 'File initialization',
    '静态检查': 'Validation',
    '错误': 'Error',
    '获取实体': 'Find entity',
    '浏览字段': 'Browse members',
    '选择实体类': 'Choose entity class',
})

# Presentation-only English validation labels. Runtime and compile diagnostics
# remain original in the project model and are never edited by this function.
ISSUE_EN = {
    '错误': 'Error', '警告': 'Warning', '提示': 'Info',
    '局部变量 / env 跨函数、事件或分支引用：': 'Local variable / env referenced outside its function, event or branch: ',
    'Function 形参超出所属函数作用域：': 'Function parameter used outside its owning function: ',
    'NetProp 未在离线索引中查到：': 'NetProp not found in the offline catalog: ',
    '未收录事件：': 'Unknown event: ',
    '重复的分区符号：': 'Duplicate section symbol: ',
    '非法的分区名称：': 'Invalid section name: ',
    '非法的 Table 成员名：': 'Invalid Table member name: ',
    'IncludeScript 存在循环依赖：': 'Circular IncludeScript dependency: ',
    '引用了不存在的工程文件：': 'Referenced project file does not exist: ',
    'void 官方方法不允许创建返回变量：': 'A void method cannot assign a result: ',
    '官方方法缺少对象插槽': 'Official method is missing its receiver slot',
    '事件只能属于事件分区': 'Events may only be placed in event sections',
    '事件区域只能放半椭圆事件积木': 'The event section only accepts event hat blocks',
    '原始代码节点不做语义检查': 'Raw Squirrel code is not semantically validated',
    'NetProp 未指定实体网络类，请在属性选择窗口中选择': 'Select a NetProp network class in the property picker',
    '复杂数据定义分区仅允许变量相关及调用积木': 'Complex-data sections only accept variables, member operations and calls',
    'Array 操作只能放入 Set [] 数据区': 'Array operations require an Array (Set []) data workspace',
    '复杂数据分区所绑定的变量已不存在': 'The variable owning this data workspace no longer exists',
    '嵌套数据分区父节点不一致': 'Nested data workspace parent mismatch',
    '复杂数据分区与变量的 Table/Set 类型不一致': 'Table/Array type does not match the owner variable',
    '数据定义分区名称与其变量不同步': 'Data workspace name does not match its variable',
    '当前 NetProp 的类型与 Int 不一致：': 'NetProp type is not Int: ',
}


def localized_issue(level: str, description: str, language: str | None = None, section: str = '') -> str:
    location=(section+'  ') if section else ''
    if (language or current_profile().language) != 'en':
        return f'[{level}] {location}{description}'
    result=description
    for original,english in ISSUE_EN.items():
        if result.startswith(original):
            result=english+result[len(original):]
            break
    return f'[{ISSUE_EN.get(level,level)}] {location}{result}'
UI_EN['未检测到当前静态规则覆盖范围内的问题。'] = 'No issues found by the current static checks.'


def translated_tooltip(text: str, language: str | None = None) -> str:
    """Translate fixed tooltips and annotated slot hints on demand."""
    lang=language or current_profile().language
    if lang!='en':return text
    result=translated_text(text,lang)
    if result!=text:return result
    if text.startswith('引用：'):
        return 'Reference: '+text[len('引用：'):].replace('；右键重新选择成员','; right-click to choose another member')
    if text.startswith('API: '):return text
    if '；' in text:
        head,sep,rest=text.partition('；')
        translated=translated_text(rest,lang)
        if translated!=rest:return head+'; '+translated
    return text

# v0.9.9.33: editor UI strings, including menus, dialogs, dynamic status captions.
UI_EN.update({
    '对象/目标': 'Object / target',
    '条件': 'Condition',
    '集合/range': 'Collection / range',
    '方法': 'Methods',
    '事件': 'Events',
    '实体名称': 'Entity name',
    '查找': 'Find',
    '结果变量': 'Result variable',
    '模式': 'Mode',
    '异常变量': 'Error variable',
    '中心 Vector': 'Center Vector',
    '半径 u': 'Radius (units)',
    '赋值方式': 'Assignment',
    '运算符': 'Operator',
    '索引': 'Index',
    '属性类型': 'Property type',
    '所属类': 'Owner class',
    '作用域': 'Scope',
    '名称': 'Name',
    '变量定义': 'Define variable',
    '赋值 / 修改': 'Assign / modify',
    '链式成员赋值': 'Set chained member',
    '数值 For': 'Numeric For',
    '实体 For': 'Entity For',
    '高级：原始代码': 'Advanced: raw code',
    '表达式独立执行': 'Standalone expression',
    'Summon 生成实体': 'Spawn entity',
    'Math 数学函数': 'Math function',
    'Table 成员存在？': 'Table member exists?',
    '通用转换 / 获取': 'General conversions / lookup',
    '通用工具': 'Utilities',
    '字符串调用参数类型（逗号隔开）': 'String-call parameter types (comma-separated)',
    'int, string, bool  (auto 为旧版直接拼接)': 'int, string, bool (auto: legacy concatenation)',
    '与形参依次对应。支持 auto/int/float/bool/string；handle 和 Vector 不可直接字符串调用。': 'One type per argument: auto/int/float/bool/string. Handles and Vectors cannot be serialized into call strings directly.',
    '打开独立数据工作区': 'Open separate data workspace',
    '切换运算符 / Switch operator': 'Switch operator',
    '切换 Math 函数 / Switch Math': 'Switch Math function',
    '编辑参数槽 / Edit arguments…': 'Edit argument slots…',
    '调用参数 / Arguments': 'Call arguments',
    '参数槽数量 / Number of slots': 'Number of argument slots',
    '删除分区及内部积木': 'Delete section and all inner blocks',
    '⠿ 调用': '⠿ Call',
    '不可删除': 'Cannot delete',
    '初始化分区不可删除；Data 由所属变量管理。': 'The initialization section cannot be deleted; Data workspaces belong to their variables.',
    ' 及其内部全部积木？': ' and all its child blocks?',
    '固定根容器不能删除；在这里添加 Table/Array 成员。ScriptScope 的成员在获取实体作用域后用 <- 创建；Array 的 append 等操作在初始化完成后执行。': 'The fixed root cannot be deleted. Add Table/Array members here. Create ScriptScope members with <- after obtaining an entity scope. Perform Array append operations after initialization.',
    '＋ 添加 else if / else': '＋ Add else if / else',
    '含有键': 'Has key',
    '包含键': 'Has key',
    '布尔值': 'Boolean value',
    '成员键 / key': 'Member key',
    '可选。Array：索引 0、1、2…；Table：成员键名。留空只遍历值。': 'Optional: Array index 0, 1, 2… or Table member key. Leave blank to iterate only values.',
    'root: 根作用域全局变量；auto: 函数中 local、根位置全局；local: 仅当前作用域；无: 不声明，只对已有变量赋值；static: 仅合法 Squirrel class 静态成员可用。': 'root: global root-table variable; auto: local in functions, global at root; local: current scope; none: assign an existing variable; static: valid Squirrel class members only.',
    '字符串调用时将参数转换为 Squirrel 源码；string 会自动转义引号和反斜杠': 'Convert each string-call argument into Squirrel source; string arguments automatically escape quotes and backslashes.',
    '选择成员变量 / 返回根变量…': 'Choose a member / return to root…',
    '名称非法': 'Invalid name',
    '请输入合法的 Squirrel 标识符': 'Enter a valid Squirrel identifier.',
    '变量引用': 'Variable reference',
    '请把圆形变量拖放到积木的浅色输入框。': 'Drop the rounded variable token into the light-colored input socket.',
    'local 变量不能拖出其词法作用域，或引用尚未声明的局部变量。': 'Local variables cannot be dragged outside their lexical scope or referenced before declaration.',
    '当前实体变量名': 'Entity variable name',
    '实体查找方式': 'Entity search method',
    '链式编辑': 'Edit expression path',
    '替换哪个输入槽？': 'Which input socket should be replaced?',
    '起点': 'Start',
    '终点（不包含）': 'End (exclusive)',
    '步长（不能为 0）': 'Step (nonzero)',
    '右侧变量（若无返回值则留空）': 'Result variable (leave blank for void)',
    '原版事件': 'Game event',
    '回调变量（圆形可拖动）': 'Callback variable (draggable token)',
    'API 类型': 'API owner class',
    '对象插槽': 'Receiver socket',
    '右侧结果变量': 'Result variable',
    '读 / 写': 'Read / write',
    '选择 NetProp（实体大类 → 具体属性）': 'Choose NetProp (entity class → property)',
    '当前选择': 'Current selection',
    'Set 的值': 'Set value',
    '是': 'Yes',
    '否': 'No',
    '数组 API（仅确认实际属性为数组时使用）': 'Array API (only for actual array properties)',
    '数组索引': 'Array index',
    '未知通用工具': 'Unknown utility block',
    '未支持的运算符': 'Unsupported operator',
    '编辑 range(起点, 终点, 步长) 辅助函数': 'Edit range(start, end, step)',
    '无效步长': 'Invalid step',
    '步长不能为零': 'Step cannot be zero.',
    '编辑 ': 'Edit ',
    '参数表达式（英文逗号隔开）': 'Parameter expressions (comma-separated)',
    'Set 数字索引': 'Array numeric index',
    '按变量结构递进选择。Table 使用 .成员；Set 使用 [数值/数值表达式]。': 'Build a path using the variable structure: Table uses .member; Array uses [numeric index/expression].',
    '当前是 Set': 'Current value is an Array',
    'Table 成员': 'Table member',
    '选择成员（支持手动输入）': 'Choose member (manual entry allowed)',
    '当前为 {} 成员访问，通常应选择成员名称。': 'This is a Table ({}); select a member name instead.',
    '当前数据结构：': 'Current structure: ',
    '未知（允许手动添加）': 'Unknown (manual entry allowed)',
    '生成：': 'Generated: ',
    '可从工程树拖入 .nut 文件以生成 IncludeScript(...)': 'Drag a .nut file from the project tree to insert only its filename.',
    '当前文件': 'Current file',
    '当前工程没有 .nut 文件，请新建脚本。': 'No .nut files in the project. Create a script.',
    '点击错误信息，定位到对应积木 / Click an issue to focus its block': 'Click a diagnostic to locate the related block.',
    '从积木库拖出添加积木；将已有积木拖回积木库可删除': 'Drag a block into the editor; drag an existing block back to this library to delete it.',
    '工程栏': 'Project',
    '积木工具库': 'Block library',
    'L4D2 API 资料库（离线）': 'L4D2 API catalog (offline)',
    '字段': 'Field',
    '＋函数': '＋Function',
    '＋复杂变量': '＋Complex variable',
    '＋Namespace': '＋Namespace',
    '文件夹名': 'Folder name',
    '工程名称': 'Project name',
    'OnGameEvent 统一归属 Table 名称': 'Shared OnGameEvent owner Table',
    '选择入口文件': 'Choose entry script',
    'L4D2 自动加载入口': 'L4D2 autoload entry',
    '打开工程': 'Open project',
    'L4D2 可视化工程 (*.l4vp)': 'L4D2 visual project (*.l4vp)',
    '未保存修改': 'Unsaved changes',
    '保存当前工程？': 'Save current project?',
    '新建脚本': 'New script',
    '文件名（.nut）': '.nut filename',
    '重命名 .nut': 'Rename .nut file',
    '新文件名': 'New filename',
    '文件 IncludeScript 列表': 'File IncludeScript dependencies',
    '创建复杂变量': 'Create complex variable',
    '导出单个 VScript': 'Export VScript',
    '是否同时打包为 VPK 模组？': 'Package as a VPK addon too?',
    '是否同时打包整个工程为 VPK？': 'Package the entire project as a VPK?',
    '导出成功': 'Export successful',
    '保存 VPK 模组': 'Save VPK addon',
    'VPK 导出成功': 'VPK export successful',
    '资料库覆盖范围': 'Catalog coverage',
    '工程 / scripts/vscripts/ · 拖动 .nut 到槽位': 'Project / scripts/vscripts/ · drag .nut into a socket',
    '名称冲突': 'Name conflict',
    '目标目录已有同名 .nut 文件': 'The destination already contains a .nut file with this name.',
    '非法名称': 'Invalid name',
    '重复目录': 'Duplicate folder',
    '文件夹已存在': 'Folder already exists.',
    '文件名无效': 'Invalid filename',
    '请输入不含路径分隔符的文件名。': 'Enter a filename without path separators.',
    '重复文件': 'Duplicate file',
    '同一目录中已存在这个文件。': 'A file with this name already exists in the same folder.',
    '非法文件名': 'Invalid filename',
    '不能包含路径分隔符': 'Path separators are not allowed.',
    '该文件名已存在': 'This filename already exists.',
    '编辑 IncludeScript 依赖': 'Edit IncludeScript dependencies',
    '逗号隔开的已有 .nut 文件名\n可选：': 'Existing .nut filenames, comma-separated\nOptional:',
    '包含错误': 'IncludeScript dependency error',
    '只能引用项目内已有文件。': 'Only existing project files may be included.',
    '请先创建 Namespace 或 Function 分区。': 'Create a Namespace or Function section first.',
    '不可创建': 'Cannot create',
    '初始化分区由工程自动维护；复杂数据分区从变量创建。': 'Initialization sections are managed by the project; create complex data sections from variables.',
    '请在 Table / Set 变量上右键，选择“打开独立数据工作区”。': 'Right-click a Table / Array variable and choose Open separate data workspace.',
    '当前分区不允许这种积木。': 'This block is not allowed in the current section.',
    '事件帽子只能放入事件分区。': 'Event hat blocks can only be placed in event sections.',
    '已删除拖入模块区的嵌套表达式': 'Deleted embedded expression dropped into the library.',
    '已将积木拖回积木库并删除': 'Deleted block dropped back into the library.',
    '缺少事件区': 'Event section missing',
    '请先创建一个事件分区。': 'Create an event section first.',
    '提示': 'Notice',
    '先选中一个画布分区。': 'Select a canvas section first.',
    '此分区不能放入这种 API 积木。': 'This API block is not allowed in this section.',
    '生成错误': 'Code generation error',
    'VPK 打包失败': 'VPK packaging failed',
    '静态检查有错误：\n': 'Static validation found errors:\n',
    '代码生成存在错误：\n': 'Code generation failed:\n',
    '有文件导出失败：\n': 'Some files failed to export:\n',
    '非法目录名称': 'Invalid folder name',
    '创建失败': 'Creation failed',
    '重复': 'Duplicate',
    '已有同名事件回调分区': 'An event callback section with that name already exists.',
    '已自动清理 ': 'Automatically cleaned ',
    ' 个空的失效 Data / ScriptScope 隐藏分区': ' empty invalid Data / ScriptScope hidden sections',
    '已清理 ': 'Cleaned ',
    ' 个空的失效 Data 分区；请保存工程': ' empty invalid Data sections; save the project.',
    '点击跳转到对应积木': 'Click to jump to this block.',
    ' 个 .nut 文件到 scripts/vscripts。': ' .nut files into scripts/vscripts.',
    '包含 addoninfo.txt 和 scripts/vscripts/*.nut。': 'Contains addoninfo.txt and scripts/vscripts/*.nut.',
    '游戏事件：': 'Game events:',
    '方法记录：': 'Method records:',
    '离线基础索引，非完整官方镜像。参见 DATA_SOURCES.md。': 'Offline index, not a complete official mirror. See DATA_SOURCES.md.',
    '不能将文件夹移入自身或其子目录': 'A folder cannot be moved into itself or its descendants.',
    '目标目录已有同名文件夹': 'The target already contains a folder with that name.',
    '移动失败': 'Move failed',
    'VPK 模组信息': 'VPK addon information',
    '打开数据定义分区': 'Open data workspace',
    '编辑器使用指南 / Editor Guide': 'Editor user guide',
    '检查 GitHub 更新':'Check GitHub updates',
    '启动时检查更新':'Check updates at startup',
    '编辑器使用指南 / Editor User Guide': 'Editor user guide',
    '关闭 / Close': 'Close',
    '根作用域': 'Root scope',
    '文件初始化': 'File initialization',
    '当前为 Table': 'Current value is a Table',
    '当前为 [] 数组，请改用数值索引槽。': 'This is an Array ([]); use a numeric index.',
    '未收录': 'Not documented',
    '选择属性': 'Choose property',
    '不含路径分隔符': 'No path separators',
    '此结构仅供编辑器显示和拖放，不会在函数中创建额外变量。\n选中成员后点“使用选中路径”，可以将它拖进函数内部表达式槽。': 'This schema is only for editor navigation and drag/drop; it does not declare variables in your function.\nSelect a member and choose Use selected path to insert it into a function socket.',
    '字段 / 索引': 'Field / index',
    '双击末级属性选择；数组属性（如 m_iAmmo）会启用 Array 模式和索引槽。\n资料分组名不等于运行时属性名，保存时自动使用可调用的属性键。': 'Double-click a leaf property to select it. Array properties, such as m_iAmmo, enable an Array index slot.\nDocumentation group names are excluded from the runtime property key.',
    '注意：SendTable 数组范围，不保证 VScript 可直接访问。': 'Note: a SendTable array range may not be directly accessible from VScript.',
    '运行时：': 'Runtime: ',
    '资料分组：': 'Documentation group: ',
    '类型：': 'Type: ',
    '来源：L4D2 NetProps 文档': 'Source: L4D2 NetProps documentation',
    '创建文件夹': 'Create folder',
    '新建形参成员': 'New parameter member',
    '无效名称': 'Invalid name',
    '字段需要合法标识符，Array 索引可以使用数字。': 'Fields must be valid identifiers; Array indices may be numeric.',
    '当前已选择：': 'Selected: ',
    '；可选择根变量或重新选择成员': '; choose the root variable or another member',
    '打开独立复杂变量工作区': 'Open complex data workspace',
    '已绑定变量。请到变量圆圈右键重命名。': 'Bound variable. Right-click its token to rename it.',
    '查找中心 (Vector)': 'Search center (Vector)',
    '查找半径 (单位 u)': 'Search radius (units)',
    '实体名 / 路径': 'Entity name / path',
    '例如 "player"、"infected"、"weapon_*"。支持通配符 *。': 'For example: "player", "infected", "weapon_*". Supports * wildcards.',
    '实体的 targetname，非 classname。': 'Entity targetname, not classname.',
    '实体 model keyvalue 的完整模型路径。': 'Full model path from the entity model keyvalue.',
    '按照实体的 target 键查找，不等同于 targetname。': 'Search by the target key, not targetname.',
    '按 classname 筛选，并限制在指定中心与半径内。': 'Filter by classname inside the specified center/radius.',
    '按 targetname 筛选，并限制在指定中心与半径内。': 'Filter by targetname inside the specified center/radius.',
    '搜索指定中心和半径内的所有实体，不附加名称过滤。': 'Find all entities within the specified center/radius, without a name filter.',
    '使用 Entities.First() 和 Entities.Next() 遍历实体。': 'Iterate entities with Entities.First() and Entities.Next().',
    '拖动以复制引用；Table、Array 和事件 env 可以右键选择成员。普通变量不支持成员访问。': 'Drag to copy this reference. Right-click to pick members for Table, Array, or event env. Scalars do not have members.',
    '可将 .nut 文件拖入 IncludeScript 参数槽，也可将文件和文件夹移动至其他文件夹': 'Drag .nut files into text sockets to insert the filename, or move files/folders into another folder.',
    'Squirrel 运算符 ': 'Squirrel operator ',
    '；拖入 Value 或 If 条件槽，可修改左右操作数。': '; drop into Value or If condition sockets to edit operands.',
    '工程外部接口（用户自行声明，非 Valve 官方 API）': 'External project API (declared by user, not an official Valve API)',
    '点此打开独立数据工作区': 'Open separate data workspace',
    '未保存': 'Unsaved',
})

# v0.9.9.33: dynamic labels with project-specific suffixes.
UI_PREFIX_EN.update({
    '复杂变量工作区 · ': 'Complex data workspace · ',
    '编辑 ': 'Edit ',
    '已保存到 ': 'Saved to ',
    '已导出 ': 'Exported ',
    '外部 API 已同步为 ': 'External APIs refreshed: ',
    '已自动清理 ': 'Automatically cleaned ',
    '已清理 ': 'Cleaned ',
    '画布缩放 ': 'Canvas zoom ',
    '固定根容器': 'Fixed root container',
    'Squirrel 运算符 ': 'Squirrel operator ',
})

UI_EN.update({
    '来源：': 'Source: ',
    '偏移：': 'Offset: ',
    '删除目录': 'Delete folder',
    '目标目录已有同名 .nut 文件': 'Target already contains a .nut file with that name.',
    '当前为 [] 数组，请改用数值索引槽。':'Current value is an Array; use a numeric index.',
    '未找到文件': 'File not found',
    '名称': 'Name',
    '返回类型': 'Return type',
    '关闭': 'Close',
    '取反': 'Logical NOT',
    '选择成员（支持手动输入）': 'Select member (manual entry allowed)',
    '当前范围：': 'Current scope: ',
    '向工作区拖出此函数的调用积木，原函数分区保持不变':'Drag this function call into the workspace; its definition stays unchanged.',
    '数据分区': 'Data workspace',
})

UI_EN.update({
    '方法': 'Method',
    '事件': 'Event',
    '打开文件': 'Open file',
    '删除文件': 'Delete file',
    '删除目录': 'Delete folder',
    ' 及其中全部文件？': ' and all files inside it?',
    '？此操作同时移除项目中的引用。': '? This also removes references from the project.',
    '已创建 ': 'Created ',
    ' 包含 addoninfo.txt 和 scripts/vscripts/*.nut。': ' Includes addoninfo.txt and scripts/vscripts/*.nut.',
    ' 方法记录：': ' Methods: ',
    ' 离线基础索引，非完整官方镜像。参见 DATA_SOURCES.md。': ' Offline index, not an official mirror. See DATA_SOURCES.md.',
    ' 个可拖动方法积木': ' draggable method blocks',
    'functions 必须是数组': 'functions must be an array',
    '描述文件不合法': 'Invalid API description',
    'ArmorSystem 示例': 'ArmorSystem example',
    '实体网络类': 'Entity network class',
    '浮动窗口': 'Float window',
    '来源：': 'Source: ',
    '只在根位置声明的静态变量': 'Static variable declared at root only',
    '重命名 .nut': 'Rename .nut file',
    '未保存修改': 'Unsaved changes',
    '分区': 'Section',
    '字段类型': 'Field type',
    '数组 / Set': 'Array / Set',
    '模型路径': 'Model path',
    '来源': 'Source',
    '类型': 'Type',
    '属性': 'Property',
    '分类': 'Category',
    '关闭': 'Close',
    '右键可选择 env 的字段。': 'Right-click to choose an env field.',
})

UI_EN.update({
    'Squirrel .nut 预览': 'Squirrel .nut preview',
    '变量名称': 'Variable name',
    '— 未保存': '— Unsaved',
    '已忽略静态检查拦截；代码生成错误仍会阻止导出。': 'Static validation bypass enabled; code generation errors still prevent export.',
    '已恢复静态检查拦截。': 'Static validation gate restored.',
    '示例：': 'Preview: ',
    '引用：': 'Reference: ',
    '；右键重新选择成员': '; right-click to choose a different member',
    '右键可选择 env 的字段。': 'Right-click to select env fields.',
    '返回：': 'Returns: ',
    '工程外部接口（用户自行声明，非 Valve 官方 API）': 'External project API (declared by the user, not official Valve API)',
    '已保存到 ': 'Saved to ',
    ' 右键可选择 env 的字段。': ' Right-click to select env fields.',
})
