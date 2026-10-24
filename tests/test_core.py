import tempfile
import unittest
from pathlib import Path
from l4visual.catalog import Catalog
from l4visual.codegen import SquirrelGenerator,expression
from l4visual.models import default_project,Project,ScriptDocument,Section,Block,clone_block
from l4visual.storage import save_project,load_project
from l4visual.symbols import rename_references
from l4visual.validation import Validator

class StorageTests(unittest.TestCase):
    def test_round_trip_and_magic(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'sample.l4vp';source=default_project()
            save_project(file,source)
            self.assertTrue(file.read_bytes().startswith(b'L4DVPROJ'))
            self.assertEqual(load_project(file).to_dict(),source.to_dict())
    def test_invalid_and_corrupt(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'bad.l4vp';file.write_bytes(b'{"name":"ordinary json"}')
            with self.assertRaises(ValueError):load_project(file)
            save_project(file,default_project())
            damaged=bytearray(file.read_bytes());damaged[-2]^=0xF0;file.write_bytes(damaged)
            with self.assertRaises((ValueError,Exception)):load_project(file)

class ReferenceCloneTests(unittest.TestCase):
    def test_copied_nested_blocks_receive_distinct_ids(self):
        source=Block('if',{'condition':'ready'},{'body':[Block('var',{'name':'x','value':'1'})]})
        duplicated=clone_block(source)
        self.assertNotEqual(source.id,duplicated.id)
        self.assertNotEqual(source.branches['body'][0].id,duplicated.branches['body'][0].id)
        duplicated.branches['body'][0].args['name']='y'
        self.assertEqual(source.branches['body'][0].args['name'],'x')

class CatalogTests(unittest.TestCase):
    def setUp(self):self.cat=Catalog()
    def tearDown(self):self.cat.close()
    def test_event_and_method(self):
        self.assertGreater(len(self.cat.events()),250)
        self.assertEqual([x['name'] for x in self.cat.events('player_death')],['player_death'])
        self.assertTrue(any(x['name']=='GetOrigin' for x in self.cat.methods(owner='CBaseEntity')))
    def test_netprop_inheritance(self):
        names={p['name'] for p in self.cat.props('DT_TerrorPlayer')}
        self.assertIn('m_iHealth',names)
        self.assertIn('m_isIncapacitated',names)
        self.assertIn('m_vecOrigin',names)
        self.assertIn('m_iClip1',{p['name'] for p in self.cat.props('DT_TerrorWeapon')})

class CompilerTests(unittest.TestCase):
    def test_default(self):
        proj=default_project();gen=SquirrelGenerator();code=gen.compile(proj,proj.documents[0])
        self.assertFalse(gen.errors,gen.errors)
        self.assertIn('::MyScript <- {};',code)
        self.assertIn('::MyScript.Start <- function()',code)
        self.assertIn('OnGameEvent_round_start <- function(env)',code)
        self.assertIn('__CollectGameEventCallbacks(::MyEvents);',code)
        self.assertIn('local position = player.GetOrigin();',code)
    def test_flow_and_netprop(self):
        doc=ScriptDocument('test.nut',[
            Section('function','Function',[Block('netprop',{'mode':'get','target':'weapon','property':'m_iClip1','prop_type':'Int','output':'clip'}),
            Block('netprop',{'mode':'set','target':'weapon','property':'m_iClip1','prop_type':'Int','value':'30'}),
            Block('for',{'variable':'i','start':'0','stop':'3','step':'1'},{'body':[Block('continue')]}),
            Block('try',{'error':'e'},{'body':[Block('throw',{'value':'"err"'})], 'catch':[Block('return',{'value':'false'})]})])])
        result=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('NetProps.GetPropInt(weapon, "m_iClip1")',result)
        self.assertIn('NetProps.SetPropInt(weapon, "m_iClip1", 30)',result)
        self.assertIn('for (local i = 0; i < 3; i += 1)',result)
        self.assertIn('catch (e)',result)
    def test_expression_and_symbol_id(self):
        doc=ScriptDocument('t.nut',[Section('function','Test',[Block('var',{'name':'foo','value':'4'},id='ABC'),
                  Block('return',{'value':{'kind':'variable','symbol_id':'ABC','value':'foo'}})])])
        self.assertEqual(rename_references(doc,'ABC','bar'),1)
        self.assertEqual(expression(doc.sections[0].blocks[1].args['value']),'bar')
    def test_validator_rejects_event_in_regular_section(self):
        cat=Catalog()
        doc=ScriptDocument('a.nut',[Section('function','Fn',[Block('event',{'event':'player_hurt'})])])
        problems=Validator(cat).check(Project(documents=[doc]),doc)
        self.assertTrue(any('事件只能' in p.text for p in problems))
        cat.close()

if __name__=='__main__':unittest.main()
