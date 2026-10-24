import tempfile
import unittest
from pathlib import Path

from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.codegen import SquirrelGenerator
from l4visual.data_definitions import repair_orphan_workspaces
from l4visual.storage import save_project, load_project


class AutomaticOrphanCleanupTests(unittest.TestCase):
    def test_unique_nonempty_workspace_deleted_even_without_namespace(self):
        orphan = Section('data', 'pills_cache', [
            Block('var', {'name': 'custom_counter', 'value': '123'})
        ], {'source_id': 'deleted-owner', 'container': 'Table'})
        doc = ScriptDocument('director_base_addon.nut', [orphan])
        project = Project(documents=[doc])
        source = SquirrelGenerator().compile(project, doc)
        self.assertEqual(repair_orphan_workspaces(project),
                         [(doc.name, orphan.id, 'missing_owner')])
        self.assertEqual(SquirrelGenerator().compile(project, doc), source)
        self.assertEqual(project.recovered_workspaces[0]['section'], orphan.to_dict())
        self.assertEqual(repair_orphan_workspaces(project), [])

    def test_nested_data_children_are_removed_and_archived(self):
        child_variable = Block('var', {'name': 'nested', 'value': '{}', 'container_type': 'Table'})
        parent = Section('data', 'orphan', [child_variable],
                         {'source_id': 'deleted', 'container': 'Table'})
        child = Section('data', 'nested', [Block('var', {'name': 'important', 'value': '42'})],
                        {'source_id': child_variable.id, 'parent_section_id': parent.id,
                         'container': 'Table'})
        doc = ScriptDocument('main.nut', [child, parent])
        project = Project(documents=[doc])
        result = repair_orphan_workspaces(project)
        self.assertEqual({sid for _,sid,_ in result}, {parent.id, child.id})
        self.assertEqual(len(project.recovered_workspaces), 2)
        self.assertEqual({e['section']['id'] for e in project.recovered_workspaces},
                         {parent.id, child.id})
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'project.l4vp'
            save_project(destination, project)
            loaded = load_project(destination)
            self.assertEqual(loaded.recovered_workspaces, project.recovered_workspaces)

    def test_fallback_only_orphan_is_preserved_in_recovery(self):
        orphan = Section('data', 'fallback', [], {
            'source_id': 'deleted', 'container': 'Table',
            'fallback_expression': '{ member = custom_function(5) }',
        })
        doc = ScriptDocument('main.nut', [orphan])
        project = Project(documents=[doc])
        self.assertEqual(repair_orphan_workspaces(project),
                         [(doc.name, orphan.id, 'missing_owner')])
        self.assertEqual(project.recovered_workspaces[0]['section']['args']['fallback_expression'],
                         '{ member = custom_function(5) }')

    def test_intentional_standalone_data_is_preserved(self):
        orphan = Section('data', 'no_link', [Block('var', {'name': 'x', 'value': '5'})],
                         {'container': 'Table'})
        doc = ScriptDocument('main.nut', [orphan])
        project = Project(documents=[doc])
        before = SquirrelGenerator().compile(project, doc)
        self.assertIn('::no_link <-', before)
        self.assertEqual(repair_orphan_workspaces(project), [])
        self.assertIn(orphan, doc.sections)
        self.assertEqual(SquirrelGenerator().compile(project, doc), before)

    def test_legitimate_separate_data_workspace_is_not_removed(self):
        variable = Block('var', {'name': 'data', 'value': '{}', 'container_type': 'Table'})
        namespace = Section('namespace', 'Global', [variable])
        section = Section('data', 'data', [Block('var', {'name': 'count', 'value': '3'})],
                          {'source_id': variable.id, 'container': 'Table'})
        document = ScriptDocument('main.nut', [namespace, section])
        project = Project(documents=[document])
        before = SquirrelGenerator().compile(project, document)
        self.assertEqual(repair_orphan_workspaces(project), [])
        self.assertIn(section, document.sections)
        self.assertEqual(SquirrelGenerator().compile(project, document), before)

    def test_nonempty_mismatched_but_existing_source_not_silently_removed(self):
        variable = Block('var', {'name': 'data', 'value': '0', 'container_type': '普通'})
        namespace = Section('namespace', 'Global', [variable])
        section = Section('data', 'data', [Block('var', {'name': 'count', 'value': '3'})],
                          {'source_id': variable.id, 'container': 'Table'})
        document = ScriptDocument('main.nut', [namespace, section])
        project = Project(documents=[document])
        self.assertEqual(repair_orphan_workspaces(project), [])
        self.assertIn(section, document.sections)


if __name__ == '__main__':
    unittest.main()
