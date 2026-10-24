import unittest
from pathlib import Path
from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.validation import Validator
from l4visual.scene_geometry import MIN_SCENE, include_rect, content_scene_rect
from l4visual.data_definitions import prune_empty_orphan_data


class FakeCatalog:
    def events(self, query=''):
        return [{'name':name} for name in ('weapon_fire','weapon_reload')]
    def methods(self, search='', owner=None):
        return []


class DataScopeValidationTests(unittest.TestCase):
    def make_project(self, bad_reference=False):
        weapon=Block('var',{'name':'weapon','value':'player.GetActiveWeapon()','scope':'local','container_type':'普通'})
        value=Block('var',{'name':'value','container_type':'ScriptScope','scope':'local',
                           'value':{'kind':'variable_ref','symbol_id':weapon.id,'path':'weapon','name':'weapon'}})
        nested=Block('var',{'name':'ammo_keep','value':{'kind':'variable_ref','symbol_id':weapon.id,
                                   'path':'weapon','name':'weapon'},'init_mode':'once'})
        first=Block('event',{'event':'weapon_fire','env':'env'}, {'body':[weapon,value]})
        other=Block('event',{'event':'weapon_reload','env':'env'},{'body':[]})
        if bad_reference:
            first.branches['body'].remove(weapon)
            other.branches['body'].append(weapon)
        event_section=Section('events','OnGameEvent',[first,other])
        data=Section('data','value',[nested],{'source_id':value.id,'container':'Table'})
        doc=ScriptDocument('director_base_addon.nut',[event_section,data])
        return Project(documents=[doc]),doc

    def test_script_scope_data_member_uses_owner_lexical_context(self):
        project,doc=self.make_project()
        issues=Validator(FakeCatalog()).check(project,doc)
        self.assertFalse([x for x in issues if '跨函数' in x.text],issues)

    def test_actual_foreign_event_variable_still_errors(self):
        project,doc=self.make_project(bad_reference=True)
        issues=Validator(FakeCatalog()).check(project,doc)
        self.assertTrue(any(x.level=='错误' and '跨函数' in x.text and x.section=='value' for x in issues),issues)

    def test_unused_empty_workspace_is_info_not_error(self):
        plain=Block('var',{'name':'weapon','scope':'local','container_type':'普通','value':'null'})
        func=Section('function','Sample',[plain],{'params':[]})
        ghost=Section('data','weapon',[],{'source_id':plain.id,'container':'Table'})
        doc=ScriptDocument('director_base_addon.nut',[func,ghost])
        issues=Validator(FakeCatalog()).check(Project(documents=[doc]),doc)
        self.assertTrue(any(x.level=='提示' and '空数据工作区' in x.text for x in issues),issues)
        self.assertFalse(any(x.level=='错误' and '类型不一致' in x.text for x in issues),issues)

    def test_empty_stale_linked_workspace_pruned_on_load(self):
        plain=Block('var',{'name':'weapon','scope':'local','container_type':'普通','value':'null'})
        func=Section('function','Sample',[plain],{'params':[]})
        ghost=Section('data','weapon',[],{'source_id':plain.id,'container':'Table','fallback_expression':''})
        doc=ScriptDocument('director_base_addon.nut',[func,ghost])
        removed=prune_empty_orphan_data(doc)
        self.assertEqual(removed,[ghost.id])
        self.assertNotIn(ghost,doc.sections)

    def test_nonempty_mismatched_workspace_still_errors(self):
        plain=Block('var',{'name':'weapon','scope':'local','container_type':'普通','value':'null'})
        func=Section('function','Sample',[plain],{'params':[]})
        invalid=Section('data','weapon',[Block('var',{'name':'x','value':'3'})],
                        {'source_id':plain.id,'container':'Table'})
        doc=ScriptDocument('director_base_addon.nut',[func,invalid])
        issues=Validator(FakeCatalog()).check(Project(documents=[doc]),doc)
        self.assertTrue(any(x.level=='错误' and '类型不一致' in x.text for x in issues),issues)

    def test_wrong_env_userid_method_warned(self):
        src=Block('method',{'method':'GetPlayerUserId','owner':'CTerrorPlayer',
                            'target':{'kind':'variable_ref','name':'env','path':'env.userid'},'parameters':[]})
        e=Block('event',{'event':'weapon_fire','env':'env'},{'body':[src]})
        doc=ScriptDocument('director_base_addon.nut',[Section('events','OnGameEvent',[e])])
        issues=Validator(FakeCatalog()).check(Project(documents=[doc]),doc)
        self.assertTrue(any(x.level=='警告' and 'GetPlayerFromUserID' in x.text for x in issues),issues)


class DynamicSceneMathTests(unittest.TestCase):
    def test_minimum_retained_for_small_content(self):
        self.assertEqual(content_scene_rect([(0,0,100,100)]),MIN_SCENE)
    def test_expand_beyond_right_and_bottom(self):
        x,y,w,h=content_scene_rect([(4550,3650,900,700)])
        self.assertEqual((x,y),MIN_SCENE[:2])
        self.assertGreaterEqual(x+w,4550+900+360)
        self.assertGreaterEqual(y+h,3650+700+360)
    def test_expand_in_negative_directions(self):
        x,y,w,h=content_scene_rect([(-5000,-3300,500,300)])
        self.assertLessEqual(x,-5360)
        self.assertLessEqual(y,-3660)
        self.assertGreaterEqual(x+w,4600)
        self.assertGreaterEqual(y+h,3700)
    def test_add_existing_rect_never_shrinks(self):
        rect=include_rect(MIN_SCENE,(-10,-10,10,10))
        self.assertEqual(rect,MIN_SCENE)
        self.assertEqual(include_rect(rect,(9000,12000,0,0))[0],-2400)
    def test_negative_sizes_rejected(self):
        with self.assertRaises(ValueError):include_rect(MIN_SCENE,(1,1,-3,4))
    def test_gui_wires_dynamic_extent_into_operations(self):
        src=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        for phrase in ('def recalculate_bounds(', 'def ensure_position(', 'def expand_at_edges(',
                       'self.recalculate_bounds(expand_only=True)', 'self.board.ensure_position(point)',
                       'self._grow_for_scroll('):
            self.assertIn(phrase,src)


if __name__=='__main__':
    unittest.main()
