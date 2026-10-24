import json
import unittest
from pathlib import Path
from l4visual.quick_literals import LITERAL_GROUPS, lookup_literal, literal_label, literal_tooltip, new_literal_block
from l4visual.expressions import as_embedded
from l4visual.codegen import expression

ROOT=Path(__file__).resolve().parents[1]

class DragLiteralTests(unittest.TestCase):
    def test_three_groups_are_present_and_unique(self):
        self.assertTrue({'classname','item','model','model_world','model_view','model_melee','model_melee_view','model_survivor','model_infected','model_common'} <= set(LITERAL_GROUPS))
        for key,data in LITERAL_GROUPS.items():
            values=[v for v,*_ in data['entries']]
            self.assertEqual(len(values),len(set(values)),key)
            for value in values:
                self.assertEqual(lookup_literal(key,value)[0],value)

    def test_quoted_string_not_identifier(self):
        for key,value in [('classname','weapon_pain_pills'),('item','pain_pills'),('model','models/w_models/weapons/w_eq_painpills.mdl')]:
            block=new_literal_block(key,value)
            self.assertEqual(expression(as_embedded(block)),json.dumps(value))
            self.assertEqual(block.args['literal_name'],value)
            self.assertEqual(block.args['return_type'],'string')

    def test_localized_style_and_tooltip(self):
        value='weapon_pain_pills'
        self.assertIn('止痛药',literal_label('classname',value,'zh','general'))
        self.assertIn('Pain pills',literal_label('classname',value,'en','general'))
        self.assertEqual(literal_label('classname',value,'en','professional'),value)
        self.assertNotIn('止痛药',literal_tooltip('classname',value,'en','general'))
        self.assertIn('Squirrel string literal:',literal_tooltip('classname',value,'en','general'))

    def test_unknown_value_cannot_be_injected(self):
        with self.assertRaises(ValueError):new_literal_block('item','bad_string\\"')
        with self.assertRaises(ValueError):new_literal_block('bad','pain_pills')

    def test_drag_palette_and_search_state_wiring(self):
        code=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf8')
        dialogs=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf8')
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf8')
        self.assertIn('class LiteralPaletteBlock(PaletteBlock)',code)
        self.assertIn("'literal:'+self.group+':'+self.value",code)
        self.assertIn("if payload.startswith('literal:')",dialogs)
        self.assertIn('new_literal_block(group,value)',dialogs)
        self.assertIn('literal_label(group,value,current_profile().language,current_profile().style)',canvas)
        self.assertIn('self.search.returnPressed.connect(self.apply_search)',code)
        self.assertIn('self.search.textChanged.connect(self._on_search_text_changed)',code)
        self.assertIn('self._search_expansion_snapshot={toggle:toggle.isChecked()',code)
        self.assertIn('toggle.setChecked(was_open)',code)
        self.assertIn('self._search_expansion_snapshot=None',code)
        self.assertNotIn('self.search.textChanged.connect(self.apply_search)',code)

if __name__=='__main__':unittest.main()
