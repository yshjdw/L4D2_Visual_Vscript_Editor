import unittest
from l4visual.models import Project, ScriptDocument, Section, Block
from l4visual.project_files import list_folders, rename_prefix, remove_prefix
from l4visual.expressions import method_call_expression
from l4visual.codegen import expression, SquirrelGenerator

class TestProjectFiles(unittest.TestCase):
    def setUp(self):
        self.p=Project(documents=[ScriptDocument('main.nut',includes=['lib/utils.nut']), ScriptDocument('lib/utils.nut')],library={'project_folders':['empty']})
    def test_dirs(self):
        self.assertEqual(list_folders(self.p),{'lib','empty'})
    def test_rename_folder_updates_includes(self):
        rename_prefix(self.p,'lib','scripts')
        self.assertEqual(self.p.documents[1].name,'scripts/utils.nut')
        self.assertEqual(self.p.documents[0].includes,['scripts/utils.nut'])
    def test_remove_folder_updates_includes(self):
        remove_prefix(self.p,'lib')
        self.assertEqual(len(self.p.documents),1)
        self.assertEqual(self.p.documents[0].includes,[])
    def test_root_undeletable(self):
        with self.assertRaises(ValueError):remove_prefix(self.p,'')

class TestMath(unittest.TestCase):
    def test_operator_statement(self):
        value=Block('operator',{'left':'health','operator':'>=','right':'25'})
        self.assertEqual(method_call_expression(value, expression),'(health >= 25)')
    def test_math_two_parameters(self):
        value=Block('math_call',{'function':'pow','parameters':['2','3']})
        self.assertEqual(method_call_expression(value,expression),'pow(2, 3)')
    def test_math_bad_count(self):
        with self.assertRaises(ValueError):method_call_expression(Block('math_call',{'function':'pow','parameters':['2']}),expression)
    def test_nested_expression(self):
        from l4visual.expressions import as_embedded
        inner=Block('operator',{'left':'1','operator':'+','right':'2'})
        outer=Block('assign',{'target':'x','value':as_embedded(inner)})
        self.assertEqual(SquirrelGenerator().emit_block(outer),['    x = (1 + 2);'])
