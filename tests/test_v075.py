import ast
import unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/'l4visual'/'ui'/'canvas.py'

class Version075Tests(unittest.TestCase):
    def test_drag_title_release_has_defined_scene(self):
        tree=ast.parse(SOURCE.read_text(encoding='utf-8'))
        title=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='DragTitle')
        method=next(x for x in title.body if isinstance(x,ast.FunctionDef) and x.name=='mouseReleaseEvent')
        code=ast.unparse(method)
        self.assertIn('scene = self.section.scene()',code)

    def test_user_function_drag_payload_and_slot_support(self):
        source=SOURCE.read_text(encoding='utf-8')
        self.assertIn('class FunctionCallHandle(QLabel)',source)
        self.assertIn('MIME_FUNCTION_CALL',source)
        self.assertIn('call_block_from_section_payload(payload)',source)
        self.assertIn("self.model.kind=='function'",source)

if __name__=='__main__': unittest.main()
