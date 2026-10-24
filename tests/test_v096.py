import unittest
from l4visual.models import Section,Block,ScriptDocument
from l4visual.data_definitions import dynamic_table_assignments,render_definition
from l4visual.scope_members import scope_binding,member_sources,copy_scope_reference,scope_member_path
from l4visual.codegen import expression

class ScopeMemberTests(unittest.TestCase):
    def setUp(self):
        self.a=Block('var',{'name':'value','container_type':'ScriptScope','value':'player'})
        self.b=Block('var',{'name':'scope','container_type':'ScriptScope','value':'player'})
        self.a_sec=Section('events','weapon_fire',blocks=[self.a])
        self.b_sec=Section('events','weapon_reload',blocks=[self.b])
        self.entry=Block('var',{'name':'ammo_keep','value':'0','init_mode':'once'})
        self.adata=Section('data','value',blocks=[self.entry],args={'container':'Table','source_id':self.a.id})
        self.bdata=Section('data','scope',blocks=[],args={'container':'Table','source_id':self.b.id})
        self.doc=ScriptDocument('test',[self.a_sec,self.b_sec,self.adata,self.bdata])
    def test_bindings_and_inventory(self):
        self.assertEqual(scope_binding(self.doc,self.adata),'player')
        self.assertEqual([b.args['name'] for _,b in member_sources(self.doc)],['ammo_keep'])
    def test_copy_is_reference_only(self):
        p={'source_section_id':self.adata.id,'member_id':self.entry.id,'name':'ammo_keep'}
        copied=copy_scope_reference(self.doc,p,self.bdata)
        self.assertEqual(copied.args['init_mode'],'reference')
        self.bdata.blocks.append(copied)
        self.assertEqual(dynamic_table_assignments(self.doc,self.bdata,'scope',render_definition),[])
        self.assertEqual(len(list(member_sources(self.doc))),1)
    def test_source_does_initialize(self):
        self.assertIn('rawin',dynamic_table_assignments(self.doc,self.adata,'value',render_definition)[0])
    def test_different_scope_alias_allowed_as_reference_only(self):
        self.b.args['value']='other'
        p={'source_section_id':self.adata.id,'member_id':self.entry.id,'name':'ammo_keep'}
        self.assertEqual([b.args['name'] for _,b in member_sources(self.doc,self.bdata)],['ammo_keep'])
        ref=copy_scope_reference(self.doc,p,self.bdata)
        self.assertEqual(ref.args['init_mode'],'reference')
        self.assertEqual(ref.args['reference_source_section_id'],self.adata.id)
        self.assertEqual(scope_member_path(self.doc,p,self.bdata),'scope.ammo_keep')
    def test_reference_mode_no_initialization(self):
        self.entry.args['init_mode']='reference'
        self.assertEqual(dynamic_table_assignments(self.doc,self.adata,'value',render_definition),[])
    def test_missing_source_rejected(self):
        with self.assertRaises(ValueError):copy_scope_reference(self.doc,{'source_section_id':'no','member_id':'no','name':'x'},self.bdata)

if __name__=='__main__':unittest.main()
