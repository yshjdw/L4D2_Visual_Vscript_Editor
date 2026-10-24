import unittest
from l4visual.catalog import Catalog
from l4visual.official_docs import official_events,official_functions,event_field_help
from l4visual.event_metadata import EVENT_FIELDS,event_tip
from l4visual.api_docs import method_tooltip,event_tooltip
from l4visual.expressions import block_from_method, method_call_expression
from l4visual.codegen import expression

class OfficialDocsTests(unittest.TestCase):
 def setUp(self):self.catalog=Catalog()
 def tearDown(self):self.catalog.close()
 def test_event_parsing(self):
  self.assertIn('userid',EVENT_FIELDS['ability_use'])
  self.assertIn('ability',EVENT_FIELDS['ability_use'])
  self.assertIn('context',EVENT_FIELDS['ability_use'])
  self.assertIn('attackerentid',EVENT_FIELDS['player_hurt'])
  self.assertIn('headshot',EVENT_FIELDS['player_death'])
  self.assertIn('short',event_field_help('ability_use','userid'))
 def test_no_false_metadata_fields(self):
  self.assertNotIn('local',EVENT_FIELDS['player_hurt'])
 def test_event_details(self):
  rec=next(x for x in self.catalog.events('ability_use') if x['name']=='ability_use')
  tooltip=event_tooltip(rec)
  self.assertIn('env.ability (string)',tooltip)
  self.assertIn('jockey',tooltip)
  self.assertIn('table',event_tip('ability_use'))
 def test_method_examples(self):
  self.assertIn('Math.sqrt',official_functions())
  rec=self.catalog.method('Math','sqrt')
  self.assertIsNotNone(rec)
  tooltip=method_tooltip(rec)
  self.assertIn('square root',tooltip)
  call=block_from_method(rec)
  self.assertEqual(method_call_expression(call,expression),'sqrt(0.0)')
 def test_global_method_no_fake_owner(self):
  record=self.catalog.method('Globals','IncludeScript')
  self.assertIsNotNone(record)
  block=block_from_method(record)
  self.assertEqual(block.kind,'call')
  self.assertTrue(method_call_expression(block,expression).startswith('IncludeScript('))
 def test_representative_counts(self):
  self.assertGreaterEqual(len(official_events()),280)
  self.assertGreaterEqual(len(official_functions()),600)
  self.assertGreaterEqual(self.catalog.stats()['methods'],600)
