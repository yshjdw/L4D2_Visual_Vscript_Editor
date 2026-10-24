import unittest
import json
from pathlib import Path
from l4visual.catalog import Catalog
from l4visual.official_docs import official_events, event_field_help, event_field_translations
from l4visual.diagnostic_navigation import find_block, issue_target, viewport_focus_center
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.validation import Validator

ROOT=Path(__file__).resolve().parents[1]

class EventFieldLocalizationTests(unittest.TestCase):
    def test_reparsed_source_keeps_every_real_event(self):
        docs=official_events()
        self.assertEqual(len(docs),301)
        self.assertEqual(sum(len(v['fields']) for v in docs.values()),620)
        for name in ('player_activate','survival_round_start','scavenge_gas_can_destroyed','entity_killed','player_say'):
            self.assertIn(name,docs)
        self.assertEqual([f['name'] for f in docs['set_instructor_group_enabled']['fields']], ['group','enabled'])
        self.assertEqual([f['name'] for f in docs['player_hurt']['fields']].count('userid'),1)

    def test_event_database_contains_documented_events(self):
        cat=Catalog()
        try:
            names={r['name'] for r in cat.events()}
            self.assertTrue(set(official_events()).issubset(names))
            self.assertIn('player_spawn',names)  # backward compatibility
        finally:cat.close()

    def test_all_fields_have_chinese_english_and_provenance(self):
        translations=event_field_translations()
        self.assertEqual(set(translations),set(official_events()))
        for name,doc in official_events().items():
            self.assertEqual(set(translations[name]),{item['name'] for item in doc['fields']})
            for field in doc['fields']:
                entry=translations[name][field['name']]
                self.assertTrue(entry['zh'],(name,field))
                self.assertIn(entry['source'],('documented','inferred','source_inferred'))
                cn=event_field_help(name,field['name'],'zh')
                en=event_field_help(name,field['name'],'en')
                self.assertIn(name+'.env.'+field['name'],cn)
                self.assertIn(name+'.env.'+field['name'],en)
                if field['description']:
                    self.assertIn(field['description'].strip(),en)
                else:
                    self.assertIn('推断',cn)
                    self.assertIn('Inferred',en)

    def test_event_scoped_semantics_and_missing_docs(self):
        self.assertIn('换弹',event_field_help('weapon_reload','manual','zh'))
        self.assertIn('受到伤害',event_field_help('player_hurt','userid','zh'))
        self.assertIn('击杀者',event_field_help('player_death','attacker','zh'))
        self.assertIn('投票',event_field_help('vote_started','issue','zh'))
        self.assertIn('原始文档未说明',event_field_help('vote_started','issue','zh'))
        self.assertIn('没有收录',event_field_help('weapon_reload','made_up_field','zh'))

class DiagnosticNavigationTests(unittest.TestCase):
    def test_nested_block_id_persisted_in_diagnostic(self):
        invalid=Block('break')
        branch=Block('if',{'condition':'true'},{'body':[invalid]})
        doc=ScriptDocument('director_base_addon.nut',[Section('function','do_it',[branch],{'owner':''})])
        cat=Catalog()
        try:
            found=[x for x in Validator(cat).check(Project(documents=[doc]),doc)
                   if '循环内部' in x.text]
        finally:cat.close()
        self.assertEqual(len(found),1)
        self.assertEqual(found[0].block_id,invalid.id)
        self.assertEqual(found[0].section_id,doc.sections[0].id)
        sec,block=issue_target(doc,found[0].section_id,found[0].block_id)
        self.assertIs(sec,doc.sections[0])
        self.assertIs(block,invalid)

    def test_navigation_keeps_same_named_sections_distinct(self):
        a=Block('raw',{'code':'a'})
        b=Block('raw',{'code':'b'})
        one=Section('function','duplicate',[a])
        two=Section('function','duplicate',[b])
        doc=ScriptDocument('example.nut',[one,two])
        sec,block=issue_target(doc,two.id,b.id,'duplicate')
        self.assertIs(sec,two)
        self.assertIs(block,b)
        self.assertIsNone(find_block(one.blocks,b.id))

    def test_focus_math_uses_top_alignment_and_center(self):
        x,y=viewport_focus_center(600,410,800,2,40)
        self.assertEqual(x,600)
        self.assertAlmostEqual(y,590)
        self.assertAlmostEqual(410-(y-800/(2*2)),40/2)
        with self.assertRaises(ValueError):viewport_focus_center(100,100,800,0)

    def test_gui_wires_click_to_block(self):
        text=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf8')
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf8')
        self.assertIn('self.issues.itemClicked.connect(self.jump_to_issue)',text)
        self.assertIn("row.setData(Qt.UserRole,{'document_id':self.current_doc.id,",text)
        self.assertIn('self.canvas.focus_diagnostic(section_id,block_id)',text)
        self.assertIn('panel.findChildren(BlockWidget)',canvas)
        self.assertIn('self.centerOn(QPointF(center_x,center_y))',canvas)

if __name__=='__main__':unittest.main()
