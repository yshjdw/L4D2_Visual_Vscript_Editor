"""Regression tests for v0.7.1 variable templates and method->value embeddings."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from l4visual.catalog import Catalog
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.expressions import block_from_method, as_embedded, is_embedded, can_embed
from l4visual.variable_types import change_variable_type
from l4visual.data_definitions import create_definition, linked_definition, container_kind
from l4visual.codegen import SquirrelGenerator
from l4visual.storage import save_project, load_project


class VariableTemplateTests(unittest.TestCase):
    def make(self):
        var=Block('var',{'name':'Something','container_type':'普通','value':'123','scope':'local'})
        sec=Section('function','Test',[var],x=177.25,y=-443.75)
        doc=ScriptDocument('main.nut',[sec])
        return var,sec,doc

    def test_switch_changes_value_template(self):
        var,sec,doc=self.make()
        self.assertTrue(change_variable_type(doc,var,'Table'))
        self.assertEqual(var.args['value'],'{}')
        self.assertTrue(change_variable_type(doc,var,'Set'))
        self.assertEqual(var.args['value'],'[]')
        self.assertTrue(change_variable_type(doc,var,'普通'))
        self.assertEqual(var.args['value'],'123')
        self.assertEqual((sec.x,sec.y),(177.25,-443.75))

    def test_switch_preserves_separate_container_values(self):
        var,sec,doc=self.make()
        change_variable_type(doc,var,'Table')
        var.args['value']='{armor=100}'
        change_variable_type(doc,var,'Set')
        var.args['value']='[25,50]'
        change_variable_type(doc,var,'Table')
        self.assertEqual(var.args['value'],'{armor=100}')
        change_variable_type(doc,var,'Set')
        self.assertEqual(var.args['value'],'[25,50]')

    def test_linked_complex_is_disabled_for_simple(self):
        var,sec,doc=self.make()
        change_variable_type(doc,var,'Table')
        var.args['value']='{hp=100}'
        data=create_definition(doc,sec,var)
        project=Project(documents=[doc])
        out=SquirrelGenerator().compile(project,doc)
        self.assertIn('local Something = {hp = 100};',out)
        change_variable_type(doc,var,'普通')
        self.assertIsNotNone(linked_definition(doc,var.id))
        out=SquirrelGenerator().compile(project,doc)
        self.assertIn('local Something = 123;',out)
        self.assertNotIn('local Something = {hp = 100};',out)
        change_variable_type(doc,var,'Set')
        self.assertEqual(data.args['container'],'Set')
        self.assertEqual((sec.x,sec.y),(177.25,-443.75))

    def test_simple_switch_in_namespace_and_init(self):
        for kind in ('namespace','init'):
            var=Block('var',{'name':'HP','value':'0','container_type':'普通','scope':'auto'})
            sec=Section(kind,'Stats' if kind=='namespace' else '初始化',[var])
            doc=ScriptDocument('main.nut',[sec])
            change_variable_type(doc,var,'Table')
            var.args['value']='{n=1}'
            create_definition(doc,sec,var)
            change_variable_type(doc,var,'普通')
            code=SquirrelGenerator().compile(Project(documents=[doc]),doc)
            self.assertNotIn('{n = 1}',code)

    def test_ordinary_expression_is_restored_after_switching(self):
        var,sec,doc=self.make()
        inner={'kind':'embedded_block','block':Block('method',{'target':'player','method':'GetOrigin','parameters':[],'return_type':'Vector'}).to_dict()}
        var.args['value']=inner
        change_variable_type(doc,var,'Table')
        self.assertEqual(var.args['value'],'{}')
        change_variable_type(doc,var,'普通')
        self.assertEqual(var.args['value'],inner)

    def test_explicit_ordinary_type_not_mistaken_for_table(self):
        var,sec,doc=self.make()
        var.args['value']='{}'
        self.assertIsNone(container_kind(var))

    def test_invalid_type_fails(self):
        var,sec,doc=self.make()
        with self.assertRaises(ValueError):change_variable_type(doc,var,'Dictionary')
        with self.assertRaises(ValueError):change_variable_type(doc,Block('assign',{}),'Table')


class SocketEmbeddingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.db=Catalog()
    @classmethod
    def tearDownClass(cls):cls.db.close()

    def test_variable_declaration_value_accepts_official_method(self):
        record=self.db.method('CBaseEntity','GetOrigin')
        self.assertIsNotNone(record)
        method=block_from_method(record)
        method.args['target']='player'
        self.assertTrue(can_embed(method))
        result=as_embedded(method)
        var=Block('var',{'name':'position','value':result,'container_type':'普通','scope':'local'})
        doc=ScriptDocument('m.nut',[Section('function','Test',[var])])
        code=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('local position = player.GetOrigin();',code)
        self.assertTrue(is_embedded(var.args['value']))

    def test_nested_method_parameter_round_trip(self):
        get_origin=block_from_method(self.db.method('CBaseEntity','GetOrigin'))
        get_origin.args['target']='player'
        set_origin=block_from_method(self.db.method('CBaseEntity','SetOrigin'))
        set_origin.args['target']='player'
        set_origin.args['parameters'][0]=as_embedded(get_origin)
        doc=ScriptDocument('m.nut',[Section('function','Test',[set_origin])])
        code=SquirrelGenerator().compile(Project(documents=[doc]),doc)
        self.assertIn('player.SetOrigin(player.GetOrigin());',code)
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'test.l4vp'
            save_project(path,Project(documents=[doc]))
            result=load_project(path)
            self.assertTrue(is_embedded(result.documents[0].sections[0].blocks[0].args['parameters'][0]))


if __name__=='__main__':unittest.main()
