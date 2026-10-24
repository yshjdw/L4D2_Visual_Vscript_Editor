import unittest
import json
from pathlib import Path
from l4visual.quick_literals import LITERAL_GROUPS, lookup_literal, new_literal_block, literal_tooltip, literal_label
from l4visual.codegen import expression
from l4visual.expressions import as_embedded
from l4visual.display_profile import DisplayProfile, category_caption

ROOT=Path(__file__).resolve().parents[1]

class NewModelLibraryTests(unittest.TestCase):
    def test_view_world_and_melee_model_separation(self):
        pairs=[
            ('model_view','models/v_models/v_rifle_ak47.mdl'),
            ('model_world','models/w_models/weapons/w_rifle_ak47.mdl'),
            ('model_melee','models/weapons/melee/w_fireaxe.mdl'),
            ('model_equipment','models/w_models/weapons/w_eq_medkit.mdl'),
            ('model_props','models/props_junk/gascan001a.mdl'),
            ('model_melee_view','models/weapons/melee/v_fireaxe.mdl'),
            ('model_survivor','models/survivors/survivor_producer.mdl'),
            ('model_infected','models/infected/charger.mdl'),
            ('model_common','models/infected/common_male_ceda.mdl')]
        for group,path in pairs:
            self.assertEqual(lookup_literal(group,path)[0],path)
            self.assertEqual(expression(as_embedded(new_literal_block(group,path))),json.dumps(path))
        self.assertNotEqual(pairs[0][1],pairs[1][1])

    def test_complete_roster_and_groups(self):
        survivors=LITERAL_GROUPS['model_survivor']['entries']
        self.assertEqual(len(survivors),8)
        special=LITERAL_GROUPS['model_infected']['entries']
        self.assertGreaterEqual(len(special),9)
        self.assertGreater(sum(len(g['entries']) for g in LITERAL_GROUPS.values()),100)

    def test_i18n_and_style(self):
        value='models/survivors/survivor_producer.mdl'
        self.assertIn('罗雪儿',literal_label('model_survivor',value,'zh','general'))
        self.assertIn('Rochelle',literal_label('model_survivor',value,'en','general'))
        self.assertEqual(literal_label('model_survivor',value,'en','professional'),value)
        for group,data in LITERAL_GROUPS.items():
            self.assertNotIn('暂无',data['description_en'])
            for val,zh,en in data['entries']:
                self.assertNotIn('生成',literal_tooltip(group,val,'en','general'))

    def test_english_event_group_captions(self):
        self.assertEqual(category_caption('伤害与死亡',DisplayProfile('en','general')),'Damage & death')
        self.assertEqual(category_caption('伤害与死亡',DisplayProfile('zh','general')),'伤害与死亡')
        p=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        self.assertIn("toggle.setText(f'{category_caption(group)} ({len(records)})')",p)
        self.assertIn("toggle.setText(f'{category_caption(group)} ({len(items)})')",p)
        self.assertIn("group+' '+category_caption(group)",p)

    def test_startup_and_launcher(self):
        main=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        batch=(ROOT/'start_windows.bat').read_text(encoding='utf-8')
        self.assertIn('QTimer.singleShot(0,self.focus_starter_blocks)',main)
        self.assertIn('self.canvas.fitInView(bounds,Qt.KeepAspectRatio)',main)
        self.assertIn('exit /b 0',batch)
        self.assertTrue(batch.strip().endswith('exit /b 0'))

if __name__=='__main__':unittest.main()
