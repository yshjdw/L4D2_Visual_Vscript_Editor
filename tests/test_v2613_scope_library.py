import re
import unittest
from pathlib import Path
from l4visual.models import Section, Block, ScriptDocument
from l4visual.scope_members import (member_sources, copy_scope_reference,
                                    scope_member_candidates, scope_member_path)
from l4visual.data_definitions import dynamic_table_assignments, render_definition

ROOT=Path(__file__).resolve().parents[1]

class ScopeLibraryTests(unittest.TestCase):
    def setUp(self):
        self.a=Block('var',{'name':'pills_scope','container_type':'ScriptScope','value':'pills'})
        self.b=Block('var',{'name':'new_scope','container_type':'ScriptScope','value':'new_pills'})
        self.c=Block('var',{'name':'other_scope','container_type':'ScriptScope','value':'a_different_entity'})
        self.sa=Section('function','old_func',[self.a])
        self.sb=Section('function','new_func',[self.b])
        self.sc=Section('function','different_func',[self.c])
        self.ma=Block('var',{'name':'pills_used','value':'0','init_mode':'once'})
        self.mb=Block('var',{'name':'enabled','value':'true','init_mode':'once'})
        self.mc=Block('var',{'name':'pills_used','value':'99','init_mode':'once'})
        self.da=Section('data','pills_scope',[self.ma,self.mb],{'source_id':self.a.id,'container':'Table'})
        self.dc=Section('data','other_scope',[self.mc],{'source_id':self.c.id,'container':'Table'})
        self.db=Section('data','new_scope',[],{'source_id':self.b.id,'container':'Table'})
        self.doc=ScriptDocument('director_base_addon.nut',[self.sa,self.sb,self.sc,self.da,self.dc,self.db])
        self.pa={'source_section_id':self.da.id,'member_id':self.ma.id,'name':'pills_used'}

    def test_inventory_all_distinct_local_aliases_and_same_workspace(self):
        records=list(member_sources(self.doc,self.db))
        self.assertEqual([(s.name,b.args['name']) for s,b in records],
                         [('pills_scope','pills_used'),('pills_scope','enabled'),('other_scope','pills_used')])
        self.assertEqual(len(list(member_sources(self.doc,self.da))),3)
        self.assertEqual(len(list(member_sources(self.doc))),3)

    def test_copy_cross_alias_without_initialization(self):
        created=copy_scope_reference(self.doc,self.pa,self.db)
        self.assertEqual(created.args['name'],'pills_used')
        self.assertEqual(created.args['init_mode'],'reference')
        self.assertEqual(created.args['reference_source_id'],self.ma.id)
        self.assertEqual(scope_member_path(self.doc,self.pa,self.db),'new_scope.pills_used')
        self.db.blocks.append(created)
        self.assertEqual(dynamic_table_assignments(self.doc,self.db,'new_scope',render_definition),[])
        self.assertEqual(len(list(member_sources(self.doc))),3)  # references not duplicate sources
        with self.assertRaisesRegex(ValueError,'同名'):copy_scope_reference(self.doc,self.pa,self.db)

    def test_source_identity_not_spoofed_by_drag_payload(self):
        fake={**self.pa,'name':'hacked'}
        self.assertEqual(copy_scope_reference(self.doc,fake,self.db).args['name'],'pills_used')
        bad={**self.pa,'member_id':self.mc.id}
        self.assertIsNone(scope_member_path(self.doc,bad,self.db))
        with self.assertRaises(ValueError):copy_scope_reference(self.doc,bad,self.db)
        with self.assertRaises(ValueError):copy_scope_reference(self.doc,self.pa,self.da)

    def test_reference_in_other_function_uses_target_handle_not_source(self):
        self.assertEqual(scope_member_candidates(self.doc,self.pa,self.sb),['new_scope.pills_used'])
        self.assertEqual(scope_member_path(self.doc,self.pa,self.sb),'new_scope.pills_used')
        self.assertEqual(scope_member_path(self.doc,self.pa,self.sc),'other_scope.pills_used')
        # No ScriptScope variable: do not leak 'pills_scope' from the other function.
        dest=Section('function','empty',blocks=[])
        self.assertIsNone(scope_member_path(self.doc,self.pa,dest))

    def test_ambiguous_scope_requires_user_choice(self):
        sec=Section('function','multiple',[self.b,self.c])
        self.assertEqual(scope_member_candidates(self.doc,self.pa,sec),
                         ['new_scope.pills_used','other_scope.pills_used'])
        self.assertIsNone(scope_member_path(self.doc,self.pa,sec))

    def test_event_branch_lexical_visibility(self):
        declaration=Block('var',{'name':'event_scope','container_type':'ScriptScope','value':'pills'})
        previous=Block('call',{'function':'printl','parameters':['"ok"']})
        event=Block('event',{'event':'pills_used','env':'env'}, {'body':[declaration,previous]})
        section=Section('events','MyEvents',[event])
        self.assertEqual(scope_member_candidates(self.doc,self.pa,section,previous.id),
                         ['event_scope.pills_used'])
        other=Block('event',{'event':'weapon_fire','env':'env'}, {'body':[Block('call',{'function':'printl','parameters':['"a"']})]})
        section.blocks.append(other)
        self.assertEqual(scope_member_candidates(self.doc,self.pa,section,other.branches['body'][0].id),[])

    def test_ui_has_locales_modes_and_selection(self):
        ui=(ROOT/'l4visual/ui/scope_palette.py').read_text('utf-8')
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text('utf-8')
        self.assertIn("profile.style == 'general'",ui)
        self.assertIn("current_profile().language=='en'",ui)
        self.assertIn('reference-only', (ROOT/'CHANGELOGS/CHANGELOG_v26.13.md').read_text('utf-8'))
        self.assertIn('QInputDialog.getItem(self,heading,question,paths',canvas)
        self.assertIn('scope_member_candidates(doc,payload,target_section.model,target_block_id)',canvas)
        self.assertIn('APP_VERSION',(ROOT/'l4visual/ui/main_window.py').read_text('utf-8'))

if __name__=='__main__':unittest.main()
