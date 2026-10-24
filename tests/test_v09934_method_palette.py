import unittest
from pathlib import Path
from l4visual.display_profile import use_profile
from l4visual.api_docs import method_tooltip

ROOT=Path(__file__).resolve().parents[1]

class EnglishMethodPaletteTests(unittest.TestCase):
    def tearDown(self):
        use_profile('zh','professional')

    def test_english_tooltip_uses_english_labels(self):
        use_profile('en','general')
        description=method_tooltip({'owner':'CBaseEntity','name':'GetHealth','parameters':'','returns':'int','source':'test'})
        self.assertIn('Plain-language:',description)
        self.assertIn('Source description:',description)
        for label in ('易懂说法：','说明（文档原文）：','文档签名：','来源：','完整文档：'):
            self.assertNotIn(label,description)

    def test_cards_are_wrapped_not_elided_and_refresh_descriptions(self):
        code=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        a=code.index('class OfficialMethodBlock(')
        b=code.index('class ExternalMethodBlock(',a)
        block=code[a:b]
        self.assertIn('Qt.TextWordWrap',block)
        self.assertNotIn('Qt.ElideRight',block)
        self.assertIn('def resizeEvent(self,event):',block)
        self.assertIn('def refresh_description(self):',block)
        self.assertIn('for item in items:item.refresh_description()',code)

if __name__ == '__main__':unittest.main()
