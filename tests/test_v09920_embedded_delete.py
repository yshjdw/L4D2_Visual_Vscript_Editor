import unittest
from pathlib import Path
from l4visual.models import Block, Section, ScriptDocument
from l4visual.block_reorder import remove_block

ROOT=Path(__file__).resolve().parents[1]

class NestedDeleteTests(unittest.TestCase):
    def test_menu_has_single_delete_in_both_widget_types(self):
        source=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        nested=source[source.index('class EmbeddedExpressionWidget('):source.index('class ExpressionSlot(')]
        block=source[source.index('    def menu_actions(self,position=None):',source.index('class BlockWidget(')):source.index('class DragTitle(')]
        self.assertIn("menu.addAction(translated_text('Delete'))", nested)
        self.assertIn("menu.addAction(translated_text('Delete'))", block)
        self.assertIn("self.socket.replace('null')", nested)
        self.assertIn('self.collection.remove(self.block)', block)
        self.assertNotIn('remove_wrapper_preserve_children(', block)
        self.assertNotIn('delete_all=menu.addAction', block)
        self.assertIn('pill.bind_menu_target(op_label)', source)

    def test_deleting_inner_statement_keeps_outer_and_siblings(self):
        left=Block('raw', {'source':'printl(1);'})
        right=Block('raw', {'source':'printl(2);'})
        nested=Block('if', {'condition':'true'}, {'body':[left,right]})
        doc=ScriptDocument('a.nut',[Section('function','demo',[nested])])
        self.assertTrue(remove_block(doc,left.id))
        self.assertEqual(doc.sections[0].blocks[0].id,nested.id)
        self.assertEqual([b.id for b in nested.branches['body']],[right.id])
        self.assertTrue(remove_block(doc,nested.id))
        self.assertEqual(doc.sections[0].blocks,[])

    def test_variable_default_auto_and_include_roottable(self):
        dialog=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf-8')
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        file_drop=(ROOT/'l4visual/ui/file_drop.py').read_text(encoding='utf-8')
        self.assertIn("'scope':'auto'",dialog)
        self.assertIn("socket.replace(json.dumps(name.removesuffix('.nut'), ensure_ascii=False))",canvas)
        self.assertIn("self.setText(stem)",file_drop)

if __name__=='__main__':unittest.main()
