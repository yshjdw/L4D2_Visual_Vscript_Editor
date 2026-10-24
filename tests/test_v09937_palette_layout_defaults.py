import re
import unittest
from pathlib import Path
from l4visual.display_profile import DisplayProfile
from l4visual.utility_blocks import UTILITY_BLOCKS

ROOT=Path(__file__).resolve().parents[1]

class PaletteLayoutDefaultsTests(unittest.TestCase):
    def test_fresh_defaults_english_general(self):
        self.assertEqual((DisplayProfile().language,DisplayProfile().style),('en','general'))
        source=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        self.assertIn("self.preferences.value('display/language','en')",source)
        self.assertIn("self.preferences.value('display/style','general')",source)

    def test_utility_tooltips_have_english_descriptions(self):
        for key,info in UTILITY_BLOCKS.items():
            with self.subTest(key=key):
                self.assertTrue(info.get('description_en'))
                self.assertIsNone(re.search('[\u4e00-\u9fff]',info['description_en']))
        source=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        self.assertIn('widget.refresh_description()',source)
        self.assertIn('item.refresh_description()',source)

    def test_width_is_capped_and_descriptions_wrap(self):
        palette=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        window=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        self.assertIn('dock2.setMaximumWidth(420)',window)
        self.assertIn('Qt.TextWordWrap',palette)
        self.assertIn('self._set_card_height',palette)
        util=palette[palette.index('class UtilityPaletteBlock'):palette.index('class OfficialMethodBlock')]
        self.assertIn('Qt.AlignVCenter|Qt.AlignLeft|Qt.TextWordWrap',util)
        self.assertIn('def _resize_description(self):',util)

    def test_catalog_tooltips_are_english_end_to_end(self):
        from l4visual.catalog import Catalog
        from l4visual.api_docs import method_tooltip,event_tooltip
        from l4visual.display_profile import current_profile,use_profile
        original=current_profile()
        try:
            use_profile('en','general')
            catalog=Catalog()
            for method in catalog.methods():
                self.assertIsNone(re.search('[\u4e00-\u9fff]',method_tooltip(method)),method['name'])
            for event in catalog.events():
                self.assertIsNone(re.search('[\u4e00-\u9fff]',event_tooltip(event)),event['name'])
        finally:
            use_profile(original.language,original.style)

    def test_changelogs_are_consolidated(self):
        self.assertFalse(list(ROOT.glob('CHANGELOG_v*.md')))
        self.assertTrue((ROOT/'CHANGELOGS/CHANGELOG_v0.9.9.36.md').exists())
        self.assertTrue((ROOT/'CHANGELOGS/CHANGELOG_v0.9.9.37.md').exists())

if __name__=='__main__':unittest.main()
