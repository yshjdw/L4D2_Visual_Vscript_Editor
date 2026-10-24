import unittest
from l4visual.official_docs import event_field_help
from l4visual.project_files import norm_path

class ProjectTreeRegressionTests(unittest.TestCase):
    def test_event_specific_field(self):
        self.assertIn('换弹',event_field_help('weapon_reload','manual','zh'))
        self.assertIn('manually',event_field_help('weapon_reload','manual','en'))
        self.assertIn('开火',event_field_help('weapon_fire','userid','zh'))
        self.assertIn('受到伤害',event_field_help('player_hurt','userid','zh'))
    def test_nested_member_description_remains_event_scoped(self):
        from l4visual.official_docs import official_events
        for name,doc in official_events().items():
            for field in doc['fields']:
                self.assertTrue(event_field_help(name,field['name'],'en'))
    def test_safe_folder_path(self):
        self.assertEqual(norm_path('sub\\file.nut'),'sub/file.nut')

if __name__=='__main__':unittest.main()
