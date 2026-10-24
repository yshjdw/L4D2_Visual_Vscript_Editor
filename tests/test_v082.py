import unittest
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.expressions import method_call_expression
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.symbols import rename_references

class TestVariableArguments(unittest.TestCase):
    def test_netprop_property_variable(self):
        b=Block('netprop',{'mode':'get','target':'entity','property':{'kind':'variable_ref','path':'prop_name','name':'prop_name'},'prop_type':'Int'})
        self.assertEqual(method_call_expression(b,expression),'NetProps.GetPropInt(entity, prop_name)')
    def test_netprop_property_literal(self):
        b=Block('netprop',{'mode':'get','target':'entity','property':'m_iHealth','prop_type':'Int'})
        self.assertEqual(method_call_expression(b,expression),'NetProps.GetPropInt(entity, "m_iHealth")')
    def test_summon_dynamic_classname(self):
        b=Block('summon',{'classname':{'kind':'variable_ref','path':'requestedClass','name':'requestedClass'},'config':{},'output':''})
        result=SquirrelGenerator().emit_block(b,1,'function')
        self.assertIn('SpawnEntityFromTable(requestedClass, {})',result[0])
    def test_rename_direct_variable_ref(self):
        src=Block('var',{'name':'old','value':'4'})
        ref=Block('expr',{'value':{'kind':'variable_ref','symbol_id':src.id,'name':'old','path':'::Data.old'}})
        doc=ScriptDocument('main.nut',[Section('namespace','Data',[src,ref])])
        rename_references(doc,src.id,'new')
        self.assertEqual(ref.args['value']['path'],'::Data.new')
        self.assertEqual(ref.args['value']['name'],'new')
if __name__=='__main__':unittest.main()
