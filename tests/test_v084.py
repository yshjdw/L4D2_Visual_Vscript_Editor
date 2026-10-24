import unittest
from l4visual.models import Block, Section, ScriptDocument
from l4visual.reference_members import find_reference_source, reference_root


class ReferenceMembersTests(unittest.TestCase):
    def test_nested_event_reference_finds_source(self):
        event = Block('event', {'event': 'weapon_reload', 'env': 'env'}, {'body': [Block('var', {'name': 'value', 'scope': 'local', 'value': {'kind':'embedded_block', 'block':{'kind':'call','args':{'function':'GetPlayerFromUserID','parameters':[{'kind':'variable_ref','path':'env.userid','symbol_id':'a'}]},'branches':{},'id':'b'}}})]})
        doc = ScriptDocument('x.nut', [Section('events','MyEvents',[event])])
        source, path = reference_root(doc, {'kind':'variable_ref','path':'env.userid','symbol_id':event.id})
        self.assertIs(source,event)
        self.assertEqual(path,'env')

    def test_normal_var_root(self):
        var=Block('var', {'name':'inventory','container_type':'Table','value':'{}'})
        doc=ScriptDocument('x.nut',[Section('function','Test',[var])])
        source,path=reference_root(doc,{'kind':'variable_ref','path':'inventory.item','symbol_id':var.id})
        self.assertIs(source,var)
        self.assertEqual(path,'inventory')

    def test_deleted_source(self):
        doc=ScriptDocument('x.nut',[])
        self.assertEqual(reference_root(doc,{'kind':'variable_ref','symbol_id':'missing'}),(None,None))
