import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf8')

class DragRegressionTests(unittest.TestCase):
    def test_embedded_copy_protocol(self):
        self.assertIn("MIME_EMBEDDED_COPY = 'application/x-l4dv-embedded-copy'",SOURCE)
        self.assertIn('lay.addWidget(handle)',SOURCE)
        self.assertIn('handle=EmbeddedExpressionDragHandle(self)',SOURCE)
        self.assertIn('if not is_embedded(value):return False',SOURCE)
        self.assertIn('block=unpack_embedded(value)',SOURCE)
    def test_variable_token_can_be_copied(self):
        start=SOURCE.index('class EmbeddedVariableReference(')
        stop=SOURCE.index('class EmbeddedExpressionDragHandle(')
        body=SOURCE[start:stop]
        self.assertIn('def mouseMoveEvent(self,event):',body)
        self.assertIn('mime.setData(MIME_EXPR,',body)
        self.assertIn('drag.exec(Qt.CopyAction)',body)
    def test_auto_pan_timer(self):
        self.assertIn('self._drag_edge_timer.timeout.connect(self._auto_pan_during_drag)',SOURCE)
        self.assertIn('self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+dx)',SOURCE)
        self.assertIn('self.verticalScrollBar().setValue(self.verticalScrollBar().value()+dy)',SOURCE)
        self.assertIn('self._drag_edge_timer.stop()',SOURCE)

if __name__=='__main__':unittest.main()
