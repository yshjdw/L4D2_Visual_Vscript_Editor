import ast
import re
import unittest
from pathlib import Path
from l4visual.ui.localization import UI_EN, translated_text
from l4visual.display_profile import DisplayProfile, category_caption, menu_caption, use_profile, current_profile
from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.codegen import SquirrelGenerator

ROOT=Path(__file__).resolve().parents[1]

class EnglishUIMissingStringsTests(unittest.TestCase):
    def test_all_static_widget_labels_in_registry(self):
        src=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf8')
        tree=ast.parse(src)
        kinds=next(ast.literal_eval(n.value) for n in tree.body
             if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BLOCK_NAMES' for t in n.targets))
        categories=next(ast.literal_eval(n.value) for n in tree.body
             if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BLOCK_CATEGORIES' for t in n.targets))
        from l4visual.display_profile import _CATEGORY_EN
        for value in kinds.values():
            if re.search('[\u4e00-\u9fff]',value):
                self.assertFalse(re.search('[\u4e00-\u9fff]',translated_text(value,'en')),value)
        for value in categories:
            self.assertIn(value,_CATEGORY_EN)
            self.assertFalse(re.search('[\u4e00-\u9fff]',category_caption(value,DisplayProfile('en','general'))))

    def test_updated_ui_labels_translate_both_ways(self):
        source_strings=[
            '通用工具','字符串调用参数类型（逗号隔开）',
            '与形参依次对应。支持 auto/int/float/bool/string；handle 和 Vector 不可直接字符串调用。',
            '可将 .nut 文件拖入 IncludeScript 参数槽，也可将文件和文件夹移动至其他文件夹',
            '点击错误信息，定位到对应积木 / Click an issue to focus its block',
            '＋复杂变量','＋函数','编辑参数槽 / Edit arguments…',
            'root: 根作用域全局变量；auto: 函数中 local、根位置全局；local: 仅当前作用域；无: 不声明，只对已有变量赋值；static: 仅合法 Squirrel class 静态成员可用。',
            '自动创建 / 绑定 info_target','固定根容器不能删除；在这里添加 Table/Array 成员。ScriptScope 的成员在获取实体作用域后用 <- 创建；Array 的 append 等操作在初始化完成后执行。',
            '从积木库拖出添加积木；将已有积木拖回积木库可删除',
            '右键可选择 env 的字段。','当前数据结构：','生成：',
            '双击末级属性选择；数组属性（如 m_iAmmo）会启用 Array 模式和索引槽。\n资料分组名不等于运行时属性名，保存时自动使用可调用的属性键。',
        ]
        for chinese in source_strings:
            with self.subTest(chinese=chinese):
                self.assertEqual(translated_text(chinese,'zh'),chinese)
                self.assertFalse(re.search('[\u4e00-\u9fff]',translated_text(chinese,'en')))

    def test_existing_translations_contain_no_cjk(self):
        for k,v in UI_EN.items():
            self.assertFalse(re.search('[\u4e00-\u9fff]',v),(k,v))

    def test_api_and_source_code_are_invariant(self):
        original=current_profile()
        try:
            block=Block('call',{'function':'printl','parameters':['"Hello"'],'output':''})
            doc=ScriptDocument('test.nut',[Section('function','demo',[block],{'owner':''})])
            project=Project('demo',documents=[doc])
            a=[]
            for language in ('zh','en','zh'):
                use_profile(language,'general')
                category_caption('物品、武器与补给')
                translated_text('变量名称')
                a.append(SquirrelGenerator().compile(project,doc))
            self.assertEqual(len(set(a)),1)
        finally:
            use_profile(original.language,original.style)

    def test_editor_paths_use_dynamic_translation(self):
        source=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf8')
        self.assertIn("category_caption(row['category'])",source)
        self.assertIn("widget.objectName()=='qt_dockwidget_closebutton'",source)
        self.assertIn("self.api_browser.setHeaderLabels(['API',translated_text('返回类型')])",source)
        self.assertIn("L4D2 Visual VScript ",source)
        source=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf8')
        self.assertIn("translated_text('右键可选择 env 的字段。')",source)
        self.assertIn("translated_text('引用：')",source)
        help_source=(ROOT/'l4visual/ui/help_dialog.py').read_text(encoding='utf8')
        self.assertIn('新建变量默认是 auto',help_source)
        self.assertIn('New variables default to auto',help_source)

if __name__=='__main__':unittest.main()
