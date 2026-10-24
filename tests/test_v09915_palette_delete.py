import unittest
from pathlib import Path
from l4visual.models import Block, Section, ScriptDocument
from l4visual.block_reorder import remove_block

ROOT=Path(__file__).resolve().parents[1]

class PaletteDropDeleteTests(unittest.TestCase):
    def test_nested_block_delete_removes_branch_and_contents(self):
        child=Block('raw',{'source':'printl("nested");'})
        parent=Block('if',{'condition':'true'},{'body':[child],'else':[]})
        doc=ScriptDocument('test.nut',[Section('function','f',[parent],{'owner':''})])
        self.assertTrue(remove_block(doc,parent.id))
        self.assertFalse(doc.sections[0].blocks)
        self.assertFalse(remove_block(doc,parent.id))

    def test_palette_itself_and_nested_widgets_receive_drop(self):
        source=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        self.assertIn('def _install_drop_targets(self):',source)
        self.assertIn('self.findChildren(QWidget)',source)
        self.assertIn('widget.setAcceptDrops(True)',source)
        self.assertIn('mime.hasFormat(MIME_MOVE)',source)
        self.assertIn('self.blockDropped.emit(block_id)',source)
        self.assertNotIn('self.trash=TrashZone()',source)
        self.assertIn('self._install_drop_targets()',source[source.index('def reload_external'):])

    def test_new_palette_blocks_cannot_be_deleted_as_existing(self):
        source=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        fragment=source[source.index('    def eventFilter(self, watched, event):'):source.index('    def refresh_language(self):')]
        self.assertNotIn('mime.hasFormat(MIME_BLOCK)',fragment)

if __name__=='__main__':unittest.main()
