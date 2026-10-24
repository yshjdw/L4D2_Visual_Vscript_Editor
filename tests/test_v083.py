import unittest
from pathlib import Path

class TestSceneLifetimeFix(unittest.TestCase):
    def test_load_invalidates_cached_connection_items_before_scene_clear(self):
        source=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        method=source.split('    def load(self,document):',1)[1].split('\nclass Canvas(',1)[0]
        self.assertLess(method.index('self._links=[]'),method.index('self.clear()'))
        self.assertLess(method.index('self.items_by_id={}'),method.index('self.clear()'))
    def test_connection_cache_detaches_prior_to_removal(self):
        source=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        method=source.split('    def update_connections(self):',1)[1].split('    def raise_item(',1)[0]
        self.assertLess(method.index('self._links=[]'),method.index('self.removeItem(link)'))

if __name__=='__main__':unittest.main()
