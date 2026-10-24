import unittest
from pathlib import Path
from l4visual.models import ScriptDocument, Section, Block
from l4visual.storage import load_project

class DataWorkspaceIsolationTests(unittest.TestCase):
    def test_uploaded_project_data_is_preserved(self):
        path=Path('/mnt/data/keep_ammo_on_relaod.l4vp')
        if not path.exists():self.skipTest('sample not mounted')
        project=load_project(path)
        doc=project.documents[0]
        data=[s for s in doc.sections if s.kind=='data']
        self.assertEqual(len(data),1)
        self.assertEqual(data[0].name,'value')
        self.assertEqual(data[0].blocks[0].args['name'],'ammo')

    def test_main_canvas_filters_data_and_popup_explicitly_shows_it(self):
        canvas=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text()
        self.assertIn('if section.kind == "data" and not self.show_data_sections:',canvas)
        self.assertIn('show_data_sections=True',canvas)
        self.assertIn('self.board.show_data_sections=show_data_sections',canvas)

if __name__=='__main__':unittest.main()
