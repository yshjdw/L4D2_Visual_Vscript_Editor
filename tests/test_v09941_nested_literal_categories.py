import json
import re
import unittest
from pathlib import Path

from l4visual.literal_subgroups import literal_subgroups
from l4visual.quick_literals import LITERAL_GROUPS, lookup_literal, new_literal_block, literal_tooltip, literal_label
from l4visual.expressions import as_embedded
from l4visual.codegen import expression

ROOT=Path(__file__).resolve().parents[1]


class NestedLiteralCategoryTests(unittest.TestCase):
    def test_every_legacy_classname_has_exactly_one_category(self):
        groups=literal_subgroups('classname')
        categorized=[(source,value) for subgroup in groups for source,value in subgroup['entries']]
        original={value for value,_,_ in LITERAL_GROUPS['classname']['entries']}
        self.assertEqual(len(categorized),len(original))
        self.assertEqual({value for _,value in categorized},original)
        self.assertEqual(len({value for _,value in categorized}),len(categorized))
        self.assertTrue(all(source=='classname' for source,_ in categorized))
        self.assertTrue(any(group['id']=='spawners' for group in groups))
        self.assertTrue(any(group['id']=='effects' for group in groups))

    def test_items_include_melee_and_mission_items_without_duplicates(self):
        groups=literal_subgroups('item')
        found=[(source,value) for group in groups for source,value in group['entries']]
        original={value for source in ('item','item_melee','item_world')
                  for value,_,_ in LITERAL_GROUPS[source]['entries']}
        self.assertEqual({value for _,value in found},original)
        self.assertEqual(len(found),len(original))
        self.assertIn(('item','katana'),found)
        self.assertIn(('item_world','gascan'),found)

    def test_category_localization_and_existing_literals_are_unchanged(self):
        for parent in ('classname','item'):
            groups=literal_subgroups(parent)
            self.assertGreater(len(groups),4)
            for sub in groups:
                self.assertTrue(sub['zh'] and sub['en'])
                self.assertTrue(sub['description_zh'] and sub['description_en'])
                self.assertNotRegex(sub['en']+sub['description_en'],r'[\u3400-\u9fff]')
                for source,value in sub['entries']:
                    self.assertEqual(lookup_literal(source,value)[0],value)
                    for language in ('zh','en'):
                        for style in ('general','professional'):
                            self.assertTrue(literal_label(source,value,language,style))
                            self.assertTrue(literal_tooltip(source,value,language,style))
                    self.assertEqual(expression(as_embedded(new_literal_block(source,value))),json.dumps(value,ensure_ascii=False))

    def test_nested_palette_render_refresh_and_search_lifecycle(self):
        source=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf8')
        self.assertIn('self.nested_literal_groups=[]',source)
        self.assertIn("if group in ('classname','item','spawn_classname'):",source)
        self.assertIn('for subgroup in literal_subgroups(group):',source)
        self.assertIn("sub['en' if language=='en' else 'zh']",source)
        self.assertIn("sub['description_en' if language=='en' else 'description_zh']",source)
        self.assertIn("for parent in self.nested_literal_groups:",source)
        self.assertIn("yield child['toggle']",source)
        self.assertIn('self._search_expansion_snapshot={toggle:toggle.isChecked()',source)
        self.assertIn('toggle.setChecked(was_open)',source)
        self.assertIn('self.search.returnPressed.connect(self.apply_search)',source)
        self.assertIn('self.search.textChanged.connect(self._on_search_text_changed)',source)
        self.assertIn("if not text.strip() and self._applied_search:",source)
        self.assertIn("self.filter('')",source)
        self.assertNotIn('self.search.textChanged.connect(self.apply_search)',source)


if __name__=='__main__':
    unittest.main()
