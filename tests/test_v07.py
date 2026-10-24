import unittest
from l4visual.models import Block, Section, ScriptDocument, Project, clone_block
from l4visual.catalog import Catalog
from l4visual.block_reorder import remove_block, move_block
from l4visual.expressions import block_from_method, parse_signature, as_embedded, is_embedded, can_embed, embedded_ids, is_boolean_return
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.data_definitions import create_definition

class MethodShapesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.db=Catalog()
    @classmethod
    def tearDownClass(cls):cls.db.close()

    def method(self,owner,name):
        row=self.db.method(owner,name)
        self.assertIsNotNone(row,(owner,name))
        return block_from_method(row)

    def test_get_origin_and_set_origin_have_different_slots(self):
        read=self.method('CBaseEntity','GetOrigin')
        write=self.method('CBaseEntity','SetOrigin')
        self.assertEqual(len(read.args['parameters']),0)
        self.assertEqual(len(write.args['parameters']),1)
        self.assertEqual(write.args['parameter_specs'][0]['type'],'Vector')
        self.assertTrue(can_embed(read))
        self.assertFalse(can_embed(write))
        self.assertTrue(read.args['output'].startswith('result_'))
        self.assertEqual(write.args['output'],'')

    def test_entity_lookup_receiver_and_named_slots(self):
        block=self.method('CEntities','FindByClassname')
        self.assertEqual(block.args['target'],'Entities')
        self.assertEqual(len(block.args['parameter_specs']),2)
        self.assertEqual([x['name'] for x in block.args['parameter_specs']],['previous','classname'])
        self.assertEqual(block.args['parameters'],['null','""'])

    def test_three_slot_method_and_typed_boolean(self):
        block=self.method('CBaseEntity','TakeDamage')
        self.assertEqual(len(block.args['parameters']),3)
        self.assertFalse(can_embed(block))
        is_player=self.method('CBaseEntity','IsPlayer')
        self.assertTrue(is_boolean_return(is_player))
        self.assertTrue(can_embed(is_player))

    def test_nested_method_source_generates_expression(self):
        block=self.method('CBaseEntity','GetOrigin')
        block.args['target']='player'
        inner=as_embedded(block)
        self.assertTrue(is_embedded(inner))
        doc=ScriptDocument('main.nut',[Section('function','Test',[
            Block('assign',{'target':'point','value':inner})
        ])])
        out=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('point = player.GetOrigin();',out)

    def test_void_cannot_embed(self):
        with self.assertRaises(ValueError):as_embedded(self.method('CBaseEntity','SetHealth'))

    def test_output_variables_have_distinct_ids(self):
        a=self.method('CBaseEntity','GetHealth')
        b=self.method('CBaseEntity','GetHealth')
        self.assertNotEqual(a.args['output'],b.args['output'])

class CoreDropTests(unittest.TestCase):
    def test_trash_removes_only_the_target(self):
        target=Block('assign',{'target':'one','value':'1'})
        survivor=Block('return',{'value':'true'})
        doc=ScriptDocument('m.nut',[Section('function','Main',[Block('if',{'condition':'true'},{'body':[target,survivor]})],x=300,y=-100)])
        self.assertTrue(remove_block(doc,target.id))
        self.assertEqual(len(doc.sections[0].blocks[0].branches['body']),1)
        self.assertEqual((doc.sections[0].x,doc.sections[0].y),(300,-100))
        self.assertFalse(remove_block(doc,target.id))

    def test_copy_embedded_references_receive_new_id(self):
        inner=Block('method',{'target':'player','method':'GetHealth','parameters':[],'return_type':'int'})
        original=Block('assign',{'target':'hp','value':as_embedded(inner)})
        replica=clone_block(original)
        self.assertNotEqual(original.id,replica.id)
        self.assertTrue(embedded_ids(original).isdisjoint(embedded_ids(replica)))

    def test_reordering_does_not_mutate_sections_positions(self):
        a=Block('assign',{'target':'a','value':'0'})
        source=Section('function','A',[a],x=-500.75,y=810.25)
        target=Section('function','B',[],x=999.1,y=-212.0)
        doc=ScriptDocument('main.nut',[source,target])
        self.assertTrue(move_block(doc,a.id,target,target.blocks,0))
        self.assertEqual((source.x,source.y),(-500.75,810.25))
        self.assertEqual((target.x,target.y),(999.1,-212.0))

    def test_complex_definition_from_local_function(self):
        table=Block('var',{'name':'Config','container_type':'Table','value':'{hp=100}'})
        section=Section('function','Fn',[table])
        doc=ScriptDocument('main.nut',[section])
        create_definition(doc,section,table)
        generated=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('local Config = {hp = 100};',generated)

if __name__=='__main__':unittest.main()
