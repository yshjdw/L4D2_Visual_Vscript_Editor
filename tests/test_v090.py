import unittest
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.data_definitions import container_kind, is_script_scope, create_definition, linked_definition
from l4visual.variable_types import change_variable_type
from l4visual.codegen import SquirrelGenerator

class ScriptScopeTests(unittest.TestCase):
    def build(self, dtype='ScriptScope', value='ent'):
        var=Block('var',{'name':'scope','container_type':dtype,'value':value,'scope':'local'})
        fn=Section('function','Setup',[var],{'owner':'MyScript','params':[]})
        doc=ScriptDocument('director_base_addon.nut',[Section('namespace','MyScript'),fn])
        project=Project(documents=[doc])
        data=create_definition(doc,fn,var)
        data.blocks.append(Block('var',{'name':'hp','value':'100','container_type':'普通'}))
        nested=Block('var',{'name':'inventory','value':'{}','container_type':'Table'})
        data.blocks.append(nested)
        sub=create_definition(doc,data,nested)
        sub.blocks.append(Block('var',{'name':'ammo','value':'20','container_type':'普通'}))
        return project,doc,var,data

    def test_script_scope_nested_table_compilation(self):
        proj,doc,_,sec=self.build()
        generator=SquirrelGenerator(); code=generator.compile(proj,doc)
        self.assertFalse(generator.errors)
        self.assertIn('ent.ValidateScriptScope();',code)
        self.assertIn('local scope = ent.GetScriptScope();',code)
        self.assertIn('scope.hp <- 100;',code)
        self.assertIn('scope.inventory <- {ammo = 20};',code)
        self.assertEqual(sec.args['container'],'Table')

    def test_get_script_scope_automatically_table(self):
        proj,doc,var,_=self.build('普通','ent.GetScriptScope()')
        self.assertTrue(is_script_scope(var))
        self.assertEqual(container_kind(var),'Table')
        generator=SquirrelGenerator();code=generator.compile(proj,doc)
        self.assertIn('local scope = ent.GetScriptScope();',code)
        self.assertIn('scope.hp <- 100;',code)
        self.assertNotIn('local scope = {',code)
        self.assertFalse(generator.errors)

    def test_embedded_get_scope_returns_table(self):
        expr={'kind':'embedded_block','block':Block('method',{'target':'player','method':'GetScriptScope','parameters':[]}).to_dict()}
        var=Block('var',{'name':'scope','container_type':'普通','scope':'local','value':expr})
        self.assertEqual(container_kind(var),'Table')
        self.assertTrue(is_script_scope(var))

    def test_change_type(self):
        var=Block('var',{'name':'scope','container_type':'普通','scope':'local','value':'0'})
        self.assertTrue(change_variable_type(None,var,'ScriptScope'))
        self.assertEqual(var.args['value'],'ent')
        self.assertEqual(container_kind(var),'Table')
        self.assertTrue(change_variable_type(None,var,'Table'))
        self.assertEqual(var.args['value'],'ent')

    def test_assignment_modes(self):
        from l4visual.codegen import expression
        gen=SquirrelGenerator()
        self.assertEqual(gen.emit_block(Block('assign',{'target':'scope.hp','value':'12','assignment':'<-'}),1),['    scope.hp <- 12;'])
        self.assertEqual(gen.emit_block(Block('assign',{'target':'scope.hp','value':'12','assignment':'='}),1),['    scope.hp = 12;'])
        self.assertEqual(gen.emit_block(Block('assign',{'target':'hp','value':'12','assignment':'auto'}),1),['    hp = 12;'])
        with self.assertRaises(ValueError):gen.emit_block(Block('assign',{'target':'hp','value':'12','assignment':'<-'}))

if __name__=='__main__':unittest.main()
