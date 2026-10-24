from pathlib import Path
import unittest


class SpaceInputTests(unittest.TestCase):
    def test_canvas_does_not_intercept_space(self):
        src = (Path(__file__).resolve().parents[1] / 'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        self.assertNotIn('Qt.Key_Space', src)
        self.assertNotIn('_space_held', src)
        self.assertIn('super().keyPressEvent(event)', src)
        self.assertIn('super().keyReleaseEvent(event)', src)


if __name__ == '__main__':
    unittest.main()
