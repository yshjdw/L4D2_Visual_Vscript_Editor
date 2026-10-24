import unittest
from l4visual.netprop_catalog import list_classes,list_properties,api_type
from l4visual.models import Block
from l4visual.expressions import method_call_expression
from l4visual.codegen import expression

class TestNetPropCatalog(unittest.TestCase):
    def test_full_source(self):
        self.assertGreaterEqual(len(list_classes()),275)
    def test_property(self):
        rows=list_properties('CBasePlayer','m_iHealth')
        self.assertTrue(rows)
        self.assertEqual(api_type(rows[0]),'Int')
    def test_inherited_property(self):
        self.assertTrue(list_properties('CTerrorPlayer','m_iHealth'))
    def test_nested(self):
        self.assertTrue(list_properties('CBaseEntity','m_Collision.m_vecMins'))
    def test_codegen_string_literal(self):
        b=Block('netprop',{'mode':'get','target':'player','property':'m_iHealth','prop_type':'Int','array':False})
        self.assertEqual(method_call_expression(b,expression),'NetProps.GetPropInt(player, "m_iHealth")')

if __name__=='__main__':unittest.main()
