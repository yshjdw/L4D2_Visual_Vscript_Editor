import tempfile
import unittest
from pathlib import Path
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.codegen import SquirrelGenerator,expression
from l4visual.data_definitions import (create_definition,render_definition,linked_definition,
                                       synchronize_symbol,container_kind,parse_simple_initializer)
from l4visual.symbols import rename_references
from l4visual.storage import save_project,load_project
from l4visual.validation import Validator
from l4visual.catalog import Catalog

class DataDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.namespace=Section('namespace','Data',[
            Block('var',{'name':'Inventory','value':'[10, 20]','container_type':'Set'}),
            Block('var',{'name':'Settings','value':'{}','container_type':'Table'}),
        ])
        self.doc=ScriptDocument('main.nut',[self.namespace])
        self.project=Project('linked',documents=[self.doc])

    def test_simple_array_initializer_is_preserved(self):
        inventory=self.namespace.blocks[0]
        d=create_definition(self.doc,self.namespace,inventory)
        self.assertEqual(len(d.blocks),2)
        self.assertEqual(expression(render_definition(self.doc,d)),'[10, 20]')
        self.assertIs(d,create_definition(self.doc,self.namespace,inventory))
        code=SquirrelGenerator().compile(self.project,self.doc)
        self.assertIn('::Data.Inventory <- [10, 20];',code)
        self.assertEqual(code.count('::Data.Inventory <-'),1)

    def test_recursive_nested_data(self):
        root=create_definition(self.doc,self.namespace,self.namespace.blocks[1])
        root.blocks.append(Block('var',{'name':'Health','value':'100'}))
        deep=Block('var',{'name':'Weights','value':'[]','container_type':'Set'})
        root.blocks.append(deep)
        items=create_definition(self.doc,root,deep)
        items.blocks.extend([Block('var',{'name':'0','value':'3'}),Block('var',{'name':'1','value':'5'})])
        actual=expression(render_definition(self.doc,root))
        self.assertEqual(actual,'{Health = 100, Weights = [3, 5]}')
        output=SquirrelGenerator().compile(self.project,self.doc)
        self.assertIn('::Data.Settings <- {Health = 100, Weights = [3, 5]};',output)
        self.assertNotIn('::Weights <-',output)
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'nested.l4vp';save_project(file,self.project)
            restored=load_project(file)
            self.assertEqual(SquirrelGenerator().compile(restored,restored.documents[0]),output)

    def test_rename_is_linked_by_id(self):
        block=self.namespace.blocks[1]
        section=create_definition(self.doc,self.namespace,block)
        ref=Block('assign',{'target':{'kind':'variable','value':'Settings','symbol_id':block.id},'value':'0'})
        self.namespace.blocks.append(ref)
        block.args['name']='NewSettings'
        synchronize_symbol(self.doc,block.id,'NewSettings')
        self.assertEqual(rename_references(self.doc,block.id,'NewSettings'),1)
        self.assertEqual(section.name,'NewSettings')
        self.assertEqual(expression(ref.args['target']),'NewSettings')

    def test_only_permitted_types(self):
        cat=Catalog()
        section=create_definition(self.doc,self.namespace,self.namespace.blocks[1])
        section.blocks.append(Block('for',{'variable':'x'}))
        errors=Validator(cat).check(self.project,self.doc)
        self.assertTrue(any('复杂数据定义分区' in x.text for x in errors))
        cat.close()

    def test_fallback_unrecognized_initializer(self):
        block=Block('var',{'name':'Values','value':'BuildList()','container_type':'Set'})
        self.namespace.blocks.append(block)
        section=create_definition(self.doc,self.namespace,block)
        self.assertEqual(expression(render_definition(self.doc,section)),'BuildList()')
        self.assertIn('::Data.Values <- BuildList();',SquirrelGenerator().compile(self.project,self.doc))

    def test_table_initializer_parser(self):
        parts=parse_simple_initializer('{health = 50, nested = [1, 2], name="A,B"}', 'Table')
        self.assertEqual(len(parts),3)
        self.assertEqual(parts[1].args['value'],'[1, 2]')

if __name__=='__main__':unittest.main()

class ForHelperTests(unittest.TestCase):
    def test_number_source(self):
        doc=ScriptDocument('loop.nut',[Section('function','Test',[Block('for',{'variable':'i','source':'5'},{'body':[]})])])
        text=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('for (local i = 0; i < 5; i += 1)',text)
    def test_range_source(self):
        doc=ScriptDocument('loop.nut',[Section('function','Test',[Block('for',{'variable':'i','source':'range(2, 10, 2)'},{'body':[]})])])
        text=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('for (local i = 2; i < 10; i += 2)',text)
    def test_zero_step_rejected(self):
        doc=ScriptDocument('loop.nut',[Section('function','Test',[Block('for',{'variable':'i','source':'range(2, 10, 0)'},{'body':[]})])])
        generator=SquirrelGenerator();generator.compile(Project(documents=[doc]),doc)
        self.assertTrue(any('step 不能为 0' in issue for issue in generator.errors))

class InitializationOrderTests(unittest.TestCase):
    def test_explicit_init_runs_before_think_attach(self):
        think=Section('think','Update',[Block('return',{'value':'0.5'})],
                      {'auto_attach':True,'entity_name':'vscript_timer'})
        init=Section('init','初始化',[Block('call',{'function':'InitializeData','parameters':[],'output':''})])
        doc=ScriptDocument('init.nut',[think,init])
        output=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertLess(output.index('InitializeData();'),output.index('AddThinkToEnt('))
