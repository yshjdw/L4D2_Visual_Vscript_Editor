import unittest
from pathlib import Path
from l4visual.display_profile import (DisplayProfile, current_profile, use_profile,
    event_caption, method_caption, block_caption, method_field_order, parameter_caption)
from l4visual.codegen import SquirrelGenerator
from l4visual.models import Project, ScriptDocument, Section, Block

ROOT=Path(__file__).resolve().parents[1]

class DisplayProfileTests(unittest.TestCase):
    def tearDown(self):
        use_profile('zh','professional')

    def test_four_modes_have_distinct_wording(self):
        p1=DisplayProfile('zh','professional')
        p2=DisplayProfile('en','professional')
        p3=DisplayProfile('zh','general')
        p4=DisplayProfile('en','general')
        self.assertEqual(method_caption('GetActiveWeapon',p1),'GetActiveWeapon')
        self.assertEqual(method_caption('GetActiveWeapon',p2),'GetActiveWeapon')
        self.assertIn('武器',method_caption('GetActiveWeapon',p3))
        self.assertIn('weapon',method_caption('GetActiveWeapon',p4).lower())
        self.assertEqual(event_caption('weapon_reload',p1),'weapon_reload')
        self.assertIn('换弹',event_caption('weapon_reload',p3))
        self.assertIn('reload',event_caption('weapon_reload',p4))

    def test_parameter_and_receiver_order(self):
        self.assertEqual(method_field_order(DisplayProfile('zh','general'))[0],'target')
        self.assertEqual(method_field_order(DisplayProfile('en','general'))[0],'method')
        self.assertEqual(parameter_caption('amount',DisplayProfile('zh','general')),'数量')
        self.assertEqual(parameter_caption('amount',DisplayProfile('en','professional')),'amount')

    def test_invalid_modes_rejected(self):
        with self.assertRaises(ValueError): DisplayProfile('fr','general')
        with self.assertRaises(ValueError): DisplayProfile('en','simple')

    def test_switching_style_does_not_mutate_ast_or_generated_script(self):
        method=Block('method',{'target':'weapon','method':'SetClip1','parameters':['30'],
             'parameter_specs':[{'name':'amount','type':'int'}],'owner':'CTerrorWeapon','return_type':'void','output':''})
        section=Section('function','Fire',[method],{'owner':'Custom'})
        doc=ScriptDocument('test.nut',[section])
        project=Project('demo',documents=[doc])
        before=doc.to_dict()
        outputs=[]
        for language in ('zh','en'):
            for style in ('professional','general'):
                use_profile(language,style)
                outputs.append(SquirrelGenerator().compile(project,doc))
        self.assertEqual(len(set(outputs)),1)
        self.assertEqual(doc.to_dict(),before)
        self.assertIn('weapon.SetClip1(30);',outputs[0])

    def test_source_routes_changes_to_gui_widgets(self):
        main=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        palette=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        self.assertIn("self.preferences.setValue('display/language',language)",main)
        self.assertIn('self.canvas.board.refresh_sections()',main)
        self.assertIn('method_field_order(profile)',canvas)
        self.assertIn('method_caption(str(value),profile,block.args.get(',canvas)
        self.assertIn('event_caption(str(value),profile)',canvas)
        self.assertIn('event_caption(self.record[\'name\'])',palette)
        self.assertIn('method_caption(self.record[\'name\'],owner=',palette)

    def test_wrapping_reserves_measured_height_in_parent(self):
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        self.assertIn('self._fields_host.setFixedHeight',canvas)
        self.assertIn('heightForWidth(width)',canvas)
        self.assertIn('schedule_geometry_update()',canvas)
        self.assertIn('row.addWidget(socket)',canvas)
        self.assertIn('fields.addWidget(pair)',canvas)
        self.assertIn('panel.adjustSize()',canvas)

if __name__=='__main__':unittest.main()
