import unittest
from l4visual.codegen import expression
from l4visual.event_metadata import EVENT_FIELDS, event_tip

class Test076(unittest.TestCase):
    def test_variable_ref_roundtrip_codegen(self):
        value={'kind':'variable_ref','name':'env','path':'env.userid','symbol_id':'event-node'}
        self.assertEqual(expression(value),'env.userid')
    def test_nested_member_path(self):
        self.assertEqual(expression({'kind':'variable_ref','path':'::Data.Inventory[1].ammo'}),'::Data.Inventory[1].ammo')
    def test_ability_use_fields(self):
        self.assertEqual(EVENT_FIELDS['ability_use'],['userid','ability','context'])
        self.assertIn('ability',event_tip('ability_use'))
    def test_weapon_reload_fields(self):
        self.assertEqual(EVENT_FIELDS['weapon_reload'],['userid','manual'])

if __name__=='__main__':unittest.main()
