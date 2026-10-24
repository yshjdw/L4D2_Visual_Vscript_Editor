import unittest
from pathlib import Path
from l4visual.models import Block
from l4visual.expressions import method_call_expression
from l4visual.codegen import expression

class RawinViewTests(unittest.TestCase):
    def test_standalone_rawin_has_two_expression_sockets(self):
        s=(Path(__file__).resolve().parents[1]/"l4visual/ui/canvas.py").read_text()
        self.assertIn("(block.kind=='rawin' and key=='key')",s)
        self.assertIn("'rawin':['target','key']",s)
    def test_embedded_rawin_has_target_and_key(self):
        s=(Path(__file__).resolve().parents[1]/"l4visual/ui/canvas.py").read_text()
        self.assertIn("'math_call','rawin','utility')",s)
        self.assertIn("nested.kind=='rawin'",s)
        self.assertIn("'key', depth=self.depth+1",s)
    def test_expression_remains_correct(self):
        b=Block('rawin',{'target':'scope','key':'"ammo_keep"'})
        self.assertEqual(method_call_expression(b,expression),'scope.rawin("ammo_keep")')
