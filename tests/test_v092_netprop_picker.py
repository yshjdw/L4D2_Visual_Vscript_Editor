import unittest
from l4visual.models import Block
from l4visual.netprop_method import property_parameter_index, selected_property, set_selected_property
from l4visual.expressions import method_call_expression,as_embedded,unpack_embedded
from l4visual.codegen import expression

class NetPropMethodTests(unittest.TestCase):
    def method(self):
        return Block('method',{'owner':'CNetPropManager','target':'NetProps','method':'GetPropFloat','parameters':['player','"m_iHealth"'],'parameter_specs':[{'name':'entity','type':'handle'},{'name':'propName','type':'string'}]})
    def test_property_slot(self):
        b=self.method()
        self.assertEqual(property_parameter_index(b),1)
        self.assertEqual(selected_property(b,1),'m_iHealth')
    def test_selected_property_generates_quoted_string(self):
        b=self.method()
        set_selected_property(b,1,{'table':'CBasePlayer','property':'m_iHealth','prop_type':'Int'})
        self.assertEqual(method_call_expression(b,expression),'NetProps.GetPropInt(player, "m_iHealth")')
        self.assertEqual(b.args['netprop_class'],'CBasePlayer')
    def test_nested_method_retains_selection(self):
        b=self.method()
        set_selected_property(b,1,{'table':'CBaseEntity','property':'m_Collision.m_vecMins','prop_type':'Vector'})
        child=unpack_embedded(as_embedded(b))
        self.assertEqual(selected_property(child,1),'m_Collision.m_vecMins')
    def test_unrelated_method_unchanged(self):
        other=Block('method',{'owner':'CBaseEntity','target':'ent','method':'GetOrigin','parameters':[]})
        self.assertIsNone(property_parameter_index(other))
    def test_incorrect_owner_not_modified(self):
        b=Block('method',{'owner':'Other','target':'ent','method':'GetPropFloat','parameters':['ent','"x"']})
        self.assertIsNone(property_parameter_index(b))

if __name__=='__main__': unittest.main()
