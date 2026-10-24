import unittest
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.data_definitions import create_definition
from l4visual.variable_paths import reference_for_symbol
from l4visual.array_ops import new_array_operation, change_array_operation, array_call
from l4visual.codegen import expression, SquirrelGenerator
from l4visual.expressions import can_embed, as_embedded
from l4visual.storage import save_project, load_project
from tempfile import TemporaryDirectory
from pathlib import Path

class DataInteractionTests(unittest.TestCase):
    def make(self):
        entry=Block('var', {'name':'data','container_type':'Table','value':'{}'})
        ns=Section('namespace','MyScript',[entry])
        doc=ScriptDocument('main.nut',[ns])
        root=create_definition(doc,ns,entry)
        array=Block('var',{'name':'items','container_type':'Set','value':'[10, 20]'})
        root.blocks.append(array)
        sub=create_definition(doc,root,array)
        return doc,root,sub,entry,array
    def test_variable_paths(self):
        doc,root,sub,entry,array=self.make()
        self.assertEqual(reference_for_symbol(doc,entry.id),'::MyScript.data')
        self.assertEqual(reference_for_symbol(doc,array.id),'::MyScript.data.items')
        self.assertEqual(reference_for_symbol(doc,sub.blocks[0].id),'::MyScript.data.items[0]')
    def test_renamed_path_without_stale_string(self):
        doc,root,sub,entry,array=self.make()
        entry.args['name']='Config'
        array.args['name']='Ammo'
        self.assertEqual(reference_for_symbol(doc,array.id),'::MyScript.Config.Ammo')
    def test_array_ops_signature(self):
        operation=new_array_operation('insert','items')
        self.assertEqual(len(operation.args['parameters']),2)
        change_array_operation(operation,'pop')
        self.assertEqual(len(operation.args['parameters']),0)
        self.assertTrue(can_embed(operation))
        self.assertEqual(expression(as_embedded(operation)),'items.pop()')
        change_array_operation(operation,'append')
        self.assertFalse(can_embed(operation))
    def test_array_data_post_init(self):
        doc,root,sub,entry,array=self.make()
        op=new_array_operation('append')
        op.args['parameters']=['30']
        sub.blocks.append(op)
        codegen=SquirrelGenerator()
        text=codegen.compile(Project(documents=[doc]),doc)
        self.assertFalse(codegen.errors,codegen.errors)
        self.assertIn('::MyScript.data.items.append(30);',text)
        self.assertIn('items = [10, 20]',text)
        self.assertLess(text.index('items = [10, 20]'),text.index('::MyScript.data.items.append(30);'))
    def test_array_ops_restricted_to_array_root(self):
        from l4visual.block_reorder import accepts_block
        doc,root,sub,entry,array=self.make()
        self.assertFalse(accepts_block(root,root.blocks,'array_op'))
        self.assertTrue(accepts_block(sub,sub.blocks,'array_op'))

    def test_roundtrip_data_ops(self):
        doc,root,sub,entry,array=self.make()
        sub.blocks.append(new_array_operation('append'))
        proj=Project(documents=[doc])
        with TemporaryDirectory() as temp:
            p=Path(temp)/'test.l4vp';save_project(p,proj)
            restored=load_project(p)
            self.assertEqual(restored.documents[0].sections[-1].blocks[-1].kind,'array_op')

if __name__=='__main__': unittest.main()
