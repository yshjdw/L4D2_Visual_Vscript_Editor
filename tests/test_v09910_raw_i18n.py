import unittest
from pathlib import Path
from l4visual.raw_editor_geometry import count_visual_lines, raw_editor_height
from l4visual.display_profile import use_profile
from l4visual.ui.localization import UI_EN, translated_text
from l4visual.models import Project, ScriptDocument, Section, Block
from l4visual.codegen import SquirrelGenerator

ROOT=Path(__file__).resolve().parents[1]


class RawEditorHeightTests(unittest.TestCase):
    def test_expands_on_return_and_shrinks_after_deletion(self):
        a=raw_editor_height('x',[10],420,18)
        b=raw_editor_height('x\n' * 25,[10]*25+[0],420,18)
        self.assertGreater(b,390)
        self.assertGreater(b,a)
        self.assertEqual(a,raw_editor_height('x',[10],420,18))

    def test_soft_wrapped_long_single_line_is_tall(self):
        self.assertEqual(count_visual_lines('x'*100,[1000],100),10)
        self.assertGreater(raw_editor_height('x'*100,[1000],100,20),raw_editor_height('short',[20],100,20))

    def test_trailing_newline_creates_visible_line(self):
        self.assertEqual(count_visual_lines('one\n',[25,0],100),2)
        self.assertEqual(count_visual_lines('',[0],100),1)

    def test_rejects_mismatched_measurements(self):
        with self.assertRaises(ValueError):count_visual_lines('a\nb',[7],50)

    def test_raw_source_resize_wires_to_parent_layout(self):
        code=(ROOT/'l4visual/ui/canvas.py').read_text()
        self.assertIn('raw_editor_height(text,widths,inner_width',code)
        self.assertNotIn('min(390,control.fontMetrics()',code)
        self.assertIn('self.section.schedule_geometry_update()',code)
        self.assertIn('editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)',code)


class InterfaceEnglishTests(unittest.TestCase):
    def tearDown(self):use_profile('zh','professional')

    def test_translate_static_ui_both_directions(self):
        use_profile('en','general')
        self.assertEqual(translated_text('打开数据定义分区'),'Open data workspace')
        self.assertEqual(translated_text('将积木拖放到这里'),'Drop blocks here')
        self.assertEqual(translated_text('ScriptScope 成员初始化：'),'ScriptScope member initialization:')
        use_profile('zh','professional')
        self.assertEqual(translated_text('打开数据定义分区'),'打开数据定义分区')

    def test_dynamic_captions(self):
        use_profile('en','professional')
        self.assertEqual(translated_text('选择成员变量 · env'),'Choose member · env')
        self.assertEqual(translated_text('选择属性：m_iAmmo'),'Select property: m_iAmmo')

    def test_do_not_translate_program_text(self):
        use_profile('en','general')
        for text in ('scope.ammo_keep <- 30;', 'player', 'weapon_reload', 'm_iAmmo'):
            self.assertEqual(translated_text(text),text)
        self.assertGreater(len(UI_EN),120)

    def test_codegen_does_not_depend_on_display_language(self):
        doc=ScriptDocument('test.nut',[Section('init','init',[Block('raw',{'source':'local name = "hello world";\nprintl(name);'})])])
        project=Project('demo',documents=[doc])
        before=doc.to_dict()
        outputs=[]
        for language in ('zh','en'):
            for style in ('general','professional'):
                use_profile(language,style)
                outputs.append(SquirrelGenerator().compile(project,doc))
        self.assertEqual(len(set(outputs)),1)
        self.assertEqual(before,doc.to_dict())


if __name__=='__main__':unittest.main()

class DocumentedTooltipLanguageTests(unittest.TestCase):
    def tearDown(self):use_profile('zh','professional')

    def test_event_tooltip_and_env_tip_use_english(self):
        from l4visual.api_docs import event_tooltip
        from l4visual.event_metadata import event_tip
        use_profile('en','general')
        result=event_tooltip({'name':'weapon_reload','source':'L4D2','fields':'userid,manual'})
        self.assertIn('env is a Squirrel Table',result)
        self.assertNotIn('易懂说法',result)
        self.assertIn('Known fields:',event_tip('weapon_reload'))

    def test_method_tooltip_use_english(self):
        from l4visual.api_docs import method_tooltip
        use_profile('en','professional')
        text=method_tooltip({'owner':'CTerrorWeapon','name':'SetClip1','parameters':'amount:int','returns':'void','source':'L4D2'})
        self.assertIn('Source:',text)
        self.assertNotIn('说明：',text)

class ValidationPresentationLanguageTests(unittest.TestCase):
    def tearDown(self):use_profile('zh','professional')

    def test_error_text_translates_but_keeps_section(self):
        from l4visual.ui.localization import localized_issue
        use_profile('en','general')
        result=localized_issue('错误','局部变量 / env 跨函数、事件或分支引用：player',section='MyEvents')
        self.assertIn('[Error] MyEvents',result)
        self.assertIn('Local variable / env',result)
        self.assertIn('player',result)
        use_profile('zh','professional')
        self.assertIn('[错误] MyEvents',localized_issue('错误','局部变量 / env 跨函数、事件或分支引用：player',section='MyEvents'))
