import unittest
from pathlib import Path

class PaletteSearchTests(unittest.TestCase):
    def test_kmp_matches_and_overlaps(self):
        from l4visual.string_search import kmp_contains
        for haystack,needle,expected in [
            ('GetPlayerFromUserID', 'player',True),
            ('ABABABAC','ABABAC',True),
            ('ABABABAC','ABABC',False),
            ('GetHealth','health',True),
            ('random','xyz',False),
            ('任何文字','',True),
        ]:self.assertEqual(kmp_contains(haystack,needle),expected)

    def test_search_only_on_enter(self):
        source=(Path(__file__).resolve().parents[1]/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        self.assertIn('self.search.returnPressed.connect(self.apply_search)',source)
        self.assertNotIn('self.search.textChanged.connect(self.filter)',source)

if __name__=='__main__':unittest.main()
