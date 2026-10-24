import unittest
from types import SimpleNamespace
from pathlib import Path
from l4visual.models import Section, Block
from l4visual.scope_visibility import visible_local, resolve_socket_statement

class TestNestedVariableDrop(unittest.TestCase):
    def test_nested_operators_resolve_real_statement(self):
        section=Section('function','main',blocks=[Block('var',{'name':'count'}),Block('assign',{'target':'result'})])
        root=SimpleNamespace(root_section=SimpleNamespace(model=section),block=section.blocks[1])
        nested=SimpleNamespace(outer=SimpleNamespace(outer=root,block=Block('operator')),block=Block('operator'))
        target_section,block_id=resolve_socket_statement(nested)
        self.assertIs(target_section.model,section)
        self.assertEqual(block_id,section.blocks[1].id)
        self.assertTrue(visible_local(section,section.blocks[0].id,block_id))
    def test_scope_still_rejects_cross_section(self):
        first=Section('function','a',blocks=[Block('var',{'name':'x'}),Block('assign',{'target':'y'})])
        second=Section('function','b',blocks=[Block('assign',{'target':'y'})])
        self.assertFalse(visible_local(second,first.blocks[0].id,second.blocks[0].id))
    def test_delete_buttons_have_explicit_black_color(self):
        source=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        self.assertEqual(source.count("remove.setStyleSheet('QPushButton{background:#f4f0df;color:#000000;"),2)
