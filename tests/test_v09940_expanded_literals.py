import json
import re
import unittest
from l4visual.quick_literals import (LITERAL_GROUPS, new_literal_block, literal_tooltip,
    literal_label, corresponding_view_or_world_model)
from l4visual.expressions import as_embedded
from l4visual.codegen import expression
from l4visual.spawn_catalog import SPAWN_GROUPS

class ExpandedLiteralTests(unittest.TestCase):
    def test_weapon_and_supply_classname_coverage(self):
        names={v for v,_,_ in LITERAL_GROUPS['classname']['entries']}
        for value in ('weapon_rifle_m60','weapon_pistol_magnum','weapon_defibrillator',
                      'weapon_cola_bottles','weapon_upgradepack_explosive',
                      'weapon_fireworkcrate','weapon_melee','weapon_item_spawn',
                      'logic_relay','prop_physics','infected','tank_rock'):
            self.assertIn(value,names)
        for kind in ('武器生成点','物品生成点'):
            for value in SPAWN_GROUPS[kind]:
                self.assertIn(value,names)

    def test_give_items_and_melee_names_are_separate_from_entity_classnames(self):
        regular={v for v,_,_ in LITERAL_GROUPS['item']['entries']}
        melee={v for v,_,_ in LITERAL_GROUPS['item_melee']['entries']}
        for value in ('rifle_ak47','rifle_m60','pain_pills','defibrillator','grenade_launcher'):
            self.assertIn(value,regular)
        for value in ('katana','fireaxe','pitchfork','shovel','knife'):
            self.assertIn(value,regular)
            self.assertIn(value,melee)
        self.assertIn('gascan', {v for v,_,_ in LITERAL_GROUPS['item_world']['entries']})
        self.assertNotIn('weapon_katana',{v for v,_,_ in LITERAL_GROUPS['classname_weapons']['entries']})

    def test_item_vw_pairs_and_absence_of_invented_props_pairs(self):
        for name in ('medkit','defibrillator','painpills','adrenaline','molotov','pipebomb',
                     'bile_flask','incendiary_ammopack','explosive_ammopack','cola'):
            self.assertIn('models/v_models/v_'+name+'.mdl',
                {v for v,_,_ in LITERAL_GROUPS['model_equipment_view']['entries']})
        self.assertEqual(
            corresponding_view_or_world_model('model_equipment_view','models/v_models/v_medkit.mdl'),
            'models/w_models/weapons/w_eq_medkit.mdl')
        self.assertEqual(
            corresponding_view_or_world_model('model_melee_view','models/weapons/melee/v_katana.mdl'),
            'models/weapons/melee/w_katana.mdl')
        self.assertIsNone(corresponding_view_or_world_model('model_props','models/props_junk/gascan001a.mdl'))
        self.assertEqual(
            corresponding_view_or_world_model('model_melee_view','models/weapons/melee/v_chainsaw.mdl'),
            'models/weapons/melee/w_chainsaw.mdl')
        self.assertEqual(
            corresponding_view_or_world_model('model_view','models/v_models/v_M60.mdl'),
            'models/w_models/weapons/w_m60.mdl')

    def test_names_no_duplicates_and_stable_squirrel(self):
        for group,data in LITERAL_GROUPS.items():
            values=[e[0] for e in data['entries']]
            self.assertEqual(len(values),len(set(values)),group)
            self.assertTrue(data['description_en'] and data['description_zh'])
            for value in values:
                block=new_literal_block(group,value)
                self.assertEqual(expression(as_embedded(block)), value if group=='trace_mask' else json.dumps(value,ensure_ascii=False))

    def test_languages_and_styles(self):
        for group,data in LITERAL_GROUPS.items():
            value=data['entries'][0][0]
            for language in ('en','zh'):
                for style in ('general','professional'):
                    label=literal_label(group,value,language,style)
                    tooltip=literal_tooltip(group,value,language,style)
                    self.assertTrue(label and tooltip)
                    if style=='professional':self.assertEqual(label,value)
                    if language=='en':
                        self.assertNotRegex(tooltip,r'[\u3400-\u9fff]',msg=group)
                    else:
                        self.assertIn('生成 Squirrel 整数' if group=='trace_mask' else '生成 Squirrel 字符串',tooltip)
        self.assertIn('V/W counterpart:',literal_tooltip('model_equipment_view','models/v_models/v_medkit.mdl','en'))
        self.assertIn('对应 V/W 模型',literal_tooltip('model_equipment_view','models/v_models/v_medkit.mdl','zh'))

if __name__=='__main__':unittest.main()
