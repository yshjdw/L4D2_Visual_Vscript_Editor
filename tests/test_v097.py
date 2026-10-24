import unittest
from l4visual.models import Block, Section, ScriptDocument
from l4visual.scope_members import scope_binding, member_sources, copy_scope_reference
from l4visual.data_definitions import find_source
from l4visual.variable_paths import reference_for_symbol

class NestedScopeTests(unittest.TestCase):
    def setUp(self):
        self.source=Block('var', {'name':'value','container_type':'ScriptScope','value':'player'})
        self.target=Block('var', {'name':'scope','container_type':'ScriptScope','value':'player'})
        self.branch=Block('if', {'condition':'true'}, {'then':[self.source]})
        self.event1=Section('events','OnGameEvent',blocks=[self.branch])
        self.event2=Section('events','OnGameEvent_2',blocks=[Block('if',{'condition':'true'},{'then':[self.target]})])
        self.ammo=Block('var',{'name':'ammo_keep','value':'0','init_mode':'once'})
        self.data1=Section('data','value',blocks=[self.ammo],args={'container':'Table','source_id':self.source.id,'parent_section_id':self.event1.id})
        self.data2=Section('data','scope',blocks=[],args={'container':'Table','source_id':self.target.id,'parent_section_id':self.event2.id})
        self.doc=ScriptDocument('test',[self.event1,self.event2,self.data1,self.data2])
    def test_nested_source_discovered(self):
        self.assertIs(find_source(self.doc,self.data1)[1],self.source)
        self.assertEqual(scope_binding(self.doc,self.data1),'player')
    def test_member_visible(self):
        self.assertEqual([b.args['name'] for _,b in member_sources(self.doc,self.data2)],['ammo_keep'])
        self.assertEqual([b.args['name'] for _,b in member_sources(self.doc,self.data1)],['ammo_keep'])
    def test_cross_window_reference(self):
        payload={'source_section_id':self.data1.id,'member_id':self.ammo.id,'name':'ammo_keep'}
        created=copy_scope_reference(self.doc,payload,self.data2)
        self.assertEqual(created.args['init_mode'],'reference')
        self.assertEqual(created.args['reference_source_id'],self.ammo.id)
        self.data2.blocks.append(created)
        self.assertEqual(reference_for_symbol(self.doc,self.ammo.id),'value.ammo_keep')
        self.assertEqual(reference_for_symbol(self.doc,created.id),'scope.ammo_keep')
    def test_same_scope_cannot_copy(self):
        payload={'source_section_id':self.data1.id,'member_id':self.ammo.id,'name':'ammo_keep'}
        with self.assertRaises(ValueError):copy_scope_reference(self.doc,payload,self.data1)
    def test_embedded_variable_ref_binding(self):
        self.source.args['value']={'kind':'variable_ref','name':'player','path':'player','symbol_id':'p1'}
        self.target.args['value']={'kind':'variable_ref','name':'player','path':'player','symbol_id':'p1'}
        self.assertEqual(scope_binding(self.doc,self.data1),'player')
        self.assertEqual([b.args['name'] for _,b in member_sources(self.doc,self.data2)],['ammo_keep'])
    def test_source_is_not_duplicate(self):
        self.data2.blocks.append(copy_scope_reference(self.doc,{'source_section_id':self.data1.id,'member_id':self.ammo.id,'name':'ammo_keep'},self.data2))
        self.assertEqual(len(list(member_sources(self.doc))),1)

if __name__=='__main__':unittest.main()
