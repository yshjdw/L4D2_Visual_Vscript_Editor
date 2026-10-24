import tempfile
import unittest
from pathlib import Path

from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.storage import load_project, save_project
from l4visual.data_definitions import repair_orphan_workspaces
from l4visual.codegen import SquirrelGenerator
from l4visual.validation import Validator
from l4visual.catalog import Catalog


class OrphanDataRepairTests(unittest.TestCase):
    def test_matching_nonempty_orphan_is_removed_and_archived(self):
        namespace = Section('namespace', 'PillRelation', [
            Block('var', {'name': 'history', 'value': '{}', 'container_type': 'Table'}),
            Block('var', {'name': 'pending', 'value': '[]', 'container_type': 'Set'}),
        ])
        stale = Section('data', 'PillRelation', [
            Block('var', {'name': 'history', 'value': '{}', 'container_type': 'Table'}),
            Block('var', {'name': 'pending', 'value': '[]', 'container_type': 'Set'}),
        ], {'source_id': 'deleted12', 'container': 'Table', 'fallback_expression': ''})
        doc = ScriptDocument('director_base_addon.nut', [stale, namespace])
        project = Project(documents=[doc])
        before = SquirrelGenerator().compile(project, doc)
        changed = repair_orphan_workspaces(project)
        self.assertEqual(changed, [(doc.name, stale.id, 'duplicate_namespace')])
        self.assertNotIn(stale, doc.sections)
        self.assertEqual(before, SquirrelGenerator().compile(project, doc))
        self.assertEqual(project.recovered_workspaces[0]['section']['id'], stale.id)
        self.assertEqual(repair_orphan_workspaces(project), [])
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / 'test.l4vp'
            save_project(path, project)
            loaded = load_project(path)
            self.assertEqual(loaded.recovered_workspaces, project.recovered_workspaces)

    def test_nonduplicate_orphan_with_useful_content_is_archived(self):
        ns = Section('namespace', 'Example', [Block('var', {'name': 'history', 'value': '{}'})])
        orphan = Section('data', 'Example', [Block('var', {'name': 'new_data', 'value': '123'})],
                         {'source_id': 'missing_source', 'container': 'Table'})
        doc = ScriptDocument('main.nut', [ns, orphan])
        project = Project(documents=[doc])
        self.assertEqual(repair_orphan_workspaces(project), [(doc.name, orphan.id, 'missing_owner')])
        self.assertNotIn(orphan, doc.sections)
        self.assertEqual(project.recovered_workspaces[0]['section'], orphan.to_dict())

    def test_linked_source_and_nested_data_are_preserved(self):
        source = Block('var', {'name': 'relation', 'value': '{}', 'container_type': 'Table'})
        ns = Section('namespace', 'Example', [source])
        linked = Section('data', 'relation', [Block('var', {'name': 'n', 'value': '3'})],
                         {'source_id': source.id, 'container': 'Table'})
        doc = ScriptDocument('main.nut', [ns, linked])
        self.assertFalse(repair_orphan_workspaces(Project(documents=[doc])))
        self.assertIn(linked, doc.sections)

    def test_uploaded_pillrelation_project_keeps_output_exact(self):
        path = Path('/mnt/data/pills can used many times(5).l4vp')
        if not path.exists():
            self.skipTest('user project not mounted')
        project = load_project(path)
        doc = project.documents[0]
        before = SquirrelGenerator().compile(project, doc)
        changed = repair_orphan_workspaces(project)
        self.assertEqual([reason for _,_,reason in changed], ['duplicate_namespace'])
        after = SquirrelGenerator().compile(project, doc)
        self.assertEqual(before, after)
        issues = Validator(Catalog()).check(project, doc)
        self.assertFalse([issue for issue in issues if issue.level == '错误'])


if __name__ == '__main__':
    unittest.main()
