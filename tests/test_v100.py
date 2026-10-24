import unittest
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.expressions import can_embed, method_call_expression
from l4visual.validation import Validator
from l4visual.catalog import Catalog

class V100Tests(unittest.TestCase):
    def test_global_function_compilation(self):
        fn=Section('function','DetectWeapon',args={'owner':'','params':['weapon','aaa']})
        document=ScriptDocument('test.nut',[fn])
        project=Project(documents=[document])
        compiled=SquirrelGenerator().compile(project,document)
        self.assertIn('::DetectWeapon <- function(weapon, aaa)',compiled)
    def test_rawin_expression(self):
        block=Block('rawin',{'target':{'kind':'variable_ref','path':'scope'},'key':'"ammo_keep"'})
        self.assertTrue(can_embed(block))
        self.assertEqual(method_call_expression(block,expression),'scope.rawin("ammo_keep")')
    def test_local_rebinding_copy_in_event(self):
        x=Block('var',{'name':'player','scope':'auto','value':'null'})
        src=Block('event',{'event':'weapon_fire','env':'env'},{'body':[x]})
        y=Block('var',{'name':'player','scope':'auto','value':'null'})
        copied=Block('assign',{'target':{'kind':'variable_ref','name':'player','path':'player','symbol_id':x.id},'value':'1'})
        dst=Block('event',{'event':'weapon_reload','env':'env'},{'body':[y,copied]})
        document=ScriptDocument('test.nut',[Section('events','MyEvents',[src,dst])])
        project=Project(documents=[document])
        messages=[issue.text for issue in Validator(Catalog()).check(project,document)]
        self.assertFalse(any('跨函数' in t and 'player' in t for t in messages),messages)
    def test_local_rebinding_requires_prior_declaration(self):
        x=Block('var',{'name':'player','scope':'auto','value':'null'})
        src=Block('event',{'event':'weapon_fire','env':'env'},{'body':[x]})
        y=Block('var',{'name':'player','scope':'auto','value':'null'})
        copied=Block('assign',{'target':{'kind':'variable_ref','name':'player','path':'player','symbol_id':x.id},'value':'1'})
        dst=Block('event',{'event':'weapon_reload','env':'env'},{'body':[copied,y]})
        document=ScriptDocument('test.nut',[Section('events','MyEvents',[src,dst])])
        project=Project(documents=[document])
        messages=[issue.text for issue in Validator(Catalog()).check(project,document)]
        self.assertTrue(any('跨函数' in t and 'player' in t for t in messages),messages)

if __name__=='__main__':unittest.main()
