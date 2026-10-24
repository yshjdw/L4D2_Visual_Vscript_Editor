"""Bilingual, sectioned guide to the visual VScript editor."""
from PySide6.QtWidgets import QDialog,QVBoxLayout,QTextBrowser,QPushButton,QComboBox,QHBoxLayout
from ..display_profile import current_profile

SECTIONS={
 'zh':[
 ('快速开始','创建工程后，在工程栏建立或双击 .nut 文件；通过「可视化 → 新增分区」添加 Function、Think 或 Events。将左侧积木拖进分区；F5 预览和检查；Ctrl+S 保存 .l4vp，Ctrl+E 导出当前 .nut。'),
 ('工程栏与文件夹','工程栏映射 scripts/vscripts。右键新建、重命名、删除文件和文件夹；拖动文件或文件夹到另一文件夹可移动，不能移动到自身/子文件夹；同名冲突会被阻止。拖动 .nut 文件到参数表达式槽可填入文件名字符串。'),
 ('分区类型','Function：定义可调用函数；Think：定时执行，可在设置中配置间隔及自动绑定；Events：创建游戏事件回调；Namespace：组织全局成员。文件初始化分区由程序维护，复杂数据工作区从 Table/Set 变量打开。'),
 ('积木编辑与嵌套','矩形积木用于执行语句，圆形/六角形积木可以放到参数、条件和值的槽中。用左侧积木库拖放、直接编辑浅色输入框；拖动手柄移动积木，Ctrl 拖动复制。右键外层语句与内层表达式时应分别出现对应菜单。'),
 ('变量与作用域','新建变量默认是 auto：在函数中声明 local，根位置声明全局变量。root 显式生成根表全局变量（::name <- value）；local 仅在当前作用域声明；无表示赋值而不声明。作用域决定变量可见性与生命周期。'),
 ('事件、env 与 ScriptScope','在 Events 分区选择事件后从 env 引用具体字段。常用例子：GetPlayerFromUserID(env.userid)。访问玩家/武器成员前检查实体不为 null 且 IsValid()。ScriptScope 绑定到实体，创建成员前先 ValidateScriptScope()。'),
 ('IncludeScript 与文件依赖','把工程栏中的 .nut 文件拖入调用积木的字符串/表达式参数槽，会填写文件名字符串（不包含 .nut），而非整条 IncludeScript 调用。也可以在文件右键菜单使用「编辑 IncludeScript 依赖」添加工程级依赖；两种机制用途不同。避免文件递归相互包含。'),
 ('代码预览与错误定位','F5 或点击「预览 / 检查」生成 Squirrel 预览并检查常见结构问题。点击静态检查中的错误可定位相关分区/模块。设置中可启用「忽略静态检查，允许导出」，但不能绕过真正的代码生成错误。'),
 ('保存与导出','Ctrl+S 保存工程（.l4vp），Ctrl+E 导出当前 .nut；文件菜单可批量导出 .nut 或打包 VPK。导出前检查 IncludeScript 路径和 addoninfo 信息，并在游戏中实际测试。'),
 ('实体与 Think 示例','获取玩家：GetPlayerFromUserID(env.userid)。获取当前武器：player.GetActiveWeapon()；调用前检查 null/IsValid()。Think 分区内写需要循环执行的行为，并返回执行间隔（例如 0.1）；自动绑定需选择有效实体。'),
 ],
 'en':[
 ('Getting started','Create a project and open a .nut file in the Project tree. Add Function, Think, or Events using Visual → Add section. Drag blocks into sections. Press F5 to preview/validate, Ctrl+S to save .l4vp, and Ctrl+E to export the current .nut.'),
 ('Project tree and folders','The tree represents scripts/vscripts. Right-click to create, rename or delete files/folders. Drag a file or folder into another folder to move it; self/descendant moves and name collisions are blocked. Drag a .nut file onto an expression socket to insert the filename string (without .nut).'),
 ('Section types','Function defines callable functions; Think runs repeatedly with an interval and optional automatic binding; Events defines game event callbacks; Namespace groups global members. Initialization is managed automatically, while complex data workspaces open from Table/Set variables.'),
 ('Blocks and nesting','Statement blocks execute commands; rounded/hexagonal expression blocks fit into value, argument, and condition sockets. Edit the light input controls, drag grips to move blocks, and Ctrl-drag to copy. Right-click the precise outer statement or inner expression for its own menu.'),
 ('Variables and scope','New variables default to auto: local inside functions and global at the root. root explicitly declares a global ::name <- value; local declares in the current scope; None assigns without declaring. Scope affects lifetime and visibility.'),
 ('Events, env and ScriptScope','Select an event in the Events section and reference its env fields. Example: GetPlayerFromUserID(env.userid). Check entity handles for null and IsValid() before using methods. ValidateScriptScope() before populating entity-scoped members.'),
 ('IncludeScript and dependencies','Drag a .nut file from the Project tree into a call/expression socket to insert only the filename string (without .nut), not a complete IncludeScript call. Or right-click a project file to edit its IncludeScript dependency list; these are separate workflows. Avoid recursive includes.'),
 ('Preview and diagnostics','Press F5 to generate a Squirrel preview and run structural checks. Click a validation issue to navigate to the related block. Settings can bypass static validation for export, but not code generation failures.'),
 ('Saving and exporting','Ctrl+S saves the .l4vp project; Ctrl+E exports the current .nut. File menu can export all .nut files or package a VPK. Review IncludeScript paths, addon metadata and in-game behavior.'),
 ('Entities and Think example','Get player: GetPlayerFromUserID(env.userid). Get held weapon: player.GetActiveWeapon(); check null/IsValid(). Put recurring actions in a Think section and return an interval such as 0.1; automatic binding requires a valid entity.'),
 ]}

class EntityHelpDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('编辑器使用指南 / Editor User Guide')
        self.resize(850,720)
        lay=QVBoxLayout(self)
        toolbar=QHBoxLayout();lay.addLayout(toolbar)
        self.language=QComboBox()
        self.language.addItem('简体中文','zh');self.language.addItem('English','en')
        self.language.setCurrentIndex(1 if current_profile().language=='en' else 0)
        toolbar.addWidget(self.language);toolbar.addStretch()
        self.viewer=QTextBrowser();self.viewer.setOpenExternalLinks(False)
        lay.addWidget(self.viewer)
        self.close_button=QPushButton('关闭');self.close_button.clicked.connect(self.accept);lay.addWidget(self.close_button)
        self.language.currentIndexChanged.connect(self.update_guide)
        self.update_guide()

    def update_guide(self):
        import html
        lang=self.language.currentData()
        self.close_button.setText('Close' if lang=='en' else '关闭')
        title='L4D2 可视化 VScript 编辑器：使用指南' if lang=='zh' else 'L4D2 Visual VScript Editor: User Guide'
        sections=SECTIONS[lang]
        toc=' · '.join(f'<a href="#s{i}">{i+1}. {html.escape(label)}</a>' for i,(label,_) in enumerate(sections))
        body=''.join(f'<h2 id="s{i}">{i+1}. {html.escape(label)}</h2><p>{html.escape(paragraph)}</p>' for i,(label,paragraph) in enumerate(sections))
        self.viewer.setHtml(f'<html><head><style>body{{font-family:Segoe UI,Microsoft YaHei;color:#e8edf7;background:#192232;padding:20px;line-height:1.6}}h1{{color:#a5d7ef}}h2{{color:#b5e5cd;border-bottom:1px solid #49606f;padding-top:12px}}p{{font-size:13px}}a{{color:#8cc9f6}}</style></head><body><h1>{title}</h1><p>{toc}</p>{body}</body></html>')
