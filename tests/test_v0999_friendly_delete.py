import unittest
from pathlib import Path
from l4visual.display_profile import DisplayProfile, method_caption, event_caption
from l4visual.official_docs import official_functions, official_events
from l4visual.models import ScriptDocument, Section, Project, Block
from l4visual.codegen import SquirrelGenerator

ROOT=Path(__file__).resolve().parents[1]

class HumanReadableLabelsTests(unittest.TestCase):
    def test_all_documented_methods_have_a_nonempty_plain_label(self):
        p=DisplayProfile('zh','general')
        for fullname,record in official_functions().items():
            label=method_caption(record['name'],p,record['owner'])
            self.assertTrue(label.strip(),fullname)
            self.assertFalse(label.startswith('调用 '),fullname)
            self.assertNotEqual(label,'调用 '+record['name'])

    def test_all_documented_events_have_a_nonempty_nontrivial_label(self):
        p=DisplayProfile('zh','general')
        for name in official_events():
            label=event_caption(name,p)
            self.assertTrue(label.strip(),name)
            self.assertNotIn(name+' 事件发生',label,name)

    def test_vetted_examples(self):
        p=DisplayProfile('zh','general')
        samples={
            'GetActiveWeapon':'武器',
            'GetScriptScope':'脚本数据',
            'SetClip1':'弹匣',
            'ReviveByDefib':'除颤器',
            'GetPropIntArray':'数组',
        }
        for name,fragment in samples.items():
            self.assertIn(fragment,method_caption(name,p))
        self.assertIn('换弹',event_caption('weapon_reload',p))
        self.assertIn('伤害',event_caption('player_hurt',p))
        self.assertIn('玩家',event_caption('player_connect',p))

    def test_pro_mode_remains_canonical(self):
        p=DisplayProfile('zh','professional')
        self.assertEqual(method_caption('SetClip1',p),'SetClip1')
        self.assertEqual(event_caption('weapon_reload',p),'weapon_reload')

    def test_ui_schedules_real_removal_instead_of_just_repainting(self):
        source=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        start=source.index('    def delete_section(self):',source.index('class SectionItem('))
        end=source.index('    def edit_section(self):',start)
        deletion=source[start:end]
        self.assertIn("self.model.kind in ('init','data')",deletion)
        self.assertIn('document.sections[:]',deletion)
        self.assertIn('board.load(doc)',deletion)
        self.assertIn('QTimer.singleShot(0,finish_deletion)',deletion)
        self.assertIn("section_menu.clicked.connect",source)


    def test_general_mode_rewrites_known_awkward_labels(self):
        p=DisplayProfile('zh','general')
        expected={
            ('CPointScriptUseTarget','SetProgressBarText'):'修改交互进度条上显示的文字',
            ('CCallChainer','Call'):'执行调用链里匹配到的目标函数',
            ('QAngle','Left'):'取得这个朝向的左侧方向向量',
            ('Globals','AddThinkToEnt'):'给实体绑定一个会持续重复运行的 Think 函数',
            ('Globals','DropFire'):'在指定位置生成一片火焰',
        }
        for (owner,name),label in expected.items():
            self.assertEqual(method_caption(name,p,owner),label)
        self.assertEqual(event_caption('round_end_message',p),'游戏准备显示本回合结束信息时')
        self.assertIn('操作提示',event_caption('explain_radio',p))

    def test_general_mode_has_no_mechanical_call_event_templates(self):
        p=DisplayProfile('zh','general')
        for fullname,record in official_functions().items():
            label=method_caption(record['name'],p,record.get('owner',''))
            self.assertFalse(label.startswith('调用'),fullname)
            self.assertNotIn('之后脚本执行',label,fullname)
        for name in official_events():
            label=event_caption(name,p)
            self.assertNotIn('事件发生',label,name)
            self.assertFalse(label.startswith('当'+name),name)

    def test_code_output_does_not_change_after_presentation(self):
        method=Block('method',{'target':'weapon','method':'SetClip1','parameters':['30'],
          'parameter_specs':[{'name':'amount','type':'int'}],'owner':'CTerrorWeapon',
          'return_type':'void','output':''})
        doc=ScriptDocument('director_base_addon.nut',[Section('function','demo',[method],{'owner':''})])
        project=Project('demo',documents=[doc])
        before=doc.to_dict()
        output=SquirrelGenerator().compile(project,doc)
        for language in ('zh','en'):
            for style in ('general','professional'):
                profile=DisplayProfile(language,style)
                for record in list(official_functions().values())[:50]:
                    method_caption(record['name'],profile,record['owner'])
                for event in list(official_events())[:50]:event_caption(event,profile)
                self.assertEqual(output,SquirrelGenerator().compile(project,doc))
                self.assertEqual(before,doc.to_dict())

if __name__=='__main__':unittest.main()
