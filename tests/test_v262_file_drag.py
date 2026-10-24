import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class FileDragTests(unittest.TestCase):
    def test_canvas_embeds_only_filename_literal(self):
        text=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        self.assertIn('socket.replace(json.dumps(name.removesuffix(\'.nut\'), ensure_ascii=False))',text)
        self.assertNotIn("socket.replace('IncludeScript('",text)
    def test_line_edit_uses_stem_only(self):
        text=(ROOT/'l4visual/ui/file_drop.py').read_text(encoding='utf-8')
        self.assertIn('self.setText(stem)',text)
    def test_window_version(self):
        text=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        self.assertNotIn('0.9.9.47',text)
        self.assertIn('APP_VERSION',text)

if __name__=='__main__': unittest.main()
