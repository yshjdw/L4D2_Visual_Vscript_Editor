import unittest
from l4visual.event_metadata import EVENT_FIELDS, event_group, event_tip
from l4visual.codegen import SquirrelGenerator
from l4visual.models import Block,ScriptDocument,Section,Project
from l4visual.catalog import Catalog

class V074Tests(unittest.TestCase):
    def test_event_grouping(self):
        self.assertEqual(event_group('player_hurt'), '伤害与死亡')
        self.assertEqual(event_group('ammo_pickup'), '物品、武器与补给')
        self.assertEqual(event_group('tank_spawn'), '特殊感染者与感染者')
    def test_event_tip(self):
        self.assertIn('userid',event_tip('player_hurt'))
        self.assertIn('table',event_tip('round_start'))
    def test_all_named_events_in_database(self):
        names={r['name'] for r in Catalog().events()}
        self.assertTrue('player_hurt' in names and 'player_death' in names)
        self.assertTrue(set(EVENT_FIELDS).issubset(names))
    def test_scope_modes(self):
        b=Block('var',{'name':'a','value':'5','scope':'local'})
        doc=ScriptDocument('demo.nut',[Section('function','Start',[b],{'owner':'Demo'})])
        project=Project('demo',documents=[doc])
        generator=SquirrelGenerator()
        code=generator.compile(project,doc)
        self.assertIn('local a = 5;',code)
        b.args['scope']='static'
        code=generator.compile(project,doc)
        self.assertTrue(any('static' in e for e in generator.errors))
        b.args['scope']='无'
        code=generator.compile(project,doc)
        self.assertIn('a = 5;',code)
        self.assertNotIn('local a =',code)

if __name__ == '__main__':unittest.main()

class ScopeVisibilityTests(unittest.TestCase):
    def test_event_env_does_not_escape_to_other_event(self):
        from l4visual.scope_visibility import visible_local
        a=Block('event',{'event':'player_hurt','env':'env'}, {'body':[Block('call',{'function':'printl'})]})
        b=Block('event',{'event':'round_start','env':'env'}, {'body':[Block('call',{'function':'printl'})]})
        section=Section('events','Events',[a,b])
        self.assertTrue(visible_local(section,a.id,a.branches['body'][0].id))
        self.assertFalse(visible_local(section,a.id,b.branches['body'][0].id))
    def test_local_branch_visibility(self):
        from l4visual.scope_visibility import visible_local
        declare=Block('var',{'name':'x','scope':'local','value':'1'})
        nested=Block('if',{'condition':'true'},{'body':[declare,Block('call',{})]})
        later=Block('call',{})
        section=Section('function','F',[nested,later])
        self.assertTrue(visible_local(section,declare.id,nested.branches['body'][1].id))
        self.assertFalse(visible_local(section,declare.id,later.id))
    def test_local_declared_after_use_is_invisible(self):
        from l4visual.scope_visibility import visible_local
        first=Block('call',{})
        declare=Block('var',{'name':'x','scope':'local','value':'1'})
        section=Section('function','F',[first,declare])
        self.assertFalse(visible_local(section,declare.id,first.id))
