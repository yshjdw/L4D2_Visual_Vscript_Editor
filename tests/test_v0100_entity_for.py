"""Entity For selector, Squirrel code generation and legacy project compatibility."""
import unittest

from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.codegen import SquirrelGenerator
from l4visual.entity_search import (
    ENTITY_SEARCH_MODES, ENTITY_FIELD_DEFAULTS,
    search_fields, normalize_entity_search,
)


class EntityForTests(unittest.TestCase):
    def render(self, block):
        doc=ScriptDocument('sample.nut',[Section('function','Run',[block],{'owner':'Main','params':[]})])
        gen=SquirrelGenerator()
        code=gen.compile(Project(documents=[doc]),doc)
        self.assertEqual(gen.errors,[],gen.errors)
        return code

    def test_dropdown_modes_have_distinct_fields(self):
        self.assertEqual(search_fields('FindByClassname'),('filter',))
        self.assertEqual(search_fields('FindByClassnameWithin'),('filter','origin','radius'))
        self.assertEqual(search_fields('FindInSphere'),('origin','radius'))
        self.assertEqual(search_fields('AllEntities'),())
        self.assertEqual(search_fields('FindByNameWithin'),('filter','origin','radius'))
        self.assertEqual(len(ENTITY_SEARCH_MODES),8)

    def test_legacy_entity_for_generates_identically(self):
        b=Block('entity_for',{'variable':'ent','search':'FindByClassname','filter':'"infected"'},{'body':[]})
        code=self.render(b)
        self.assertIn('local ent = null;',code)
        self.assertIn('while ((ent = Entities.FindByClassname(ent, "infected")) != null)',code)
        self.assertNotIn('FindByClassnameWithin',code)

    def test_classname_search(self):
        b=Block('entity_for',{'variable':'e','search':'FindByName','filter':'"target*"'},{'body':[]})
        self.assertIn('Entities.FindByName(e, "target*")',self.render(b))

    def test_model_search(self):
        b=Block('entity_for',{'variable':'weapon','search':'FindByModel','filter':'"models/w_models/weapons/w_rifle_m16a2.mdl"'},{'body':[]})
        self.assertIn('Entities.FindByModel(weapon, "models/w_models/weapons/w_rifle_m16a2.mdl")',self.render(b))

    def test_target_search(self):
        b=Block('entity_for',{'variable':'x','search':'FindByTarget','filter':'"trigger01"'},{'body':[]})
        self.assertIn('Entities.FindByTarget(x, "trigger01")',self.render(b))

    def test_classname_within_uses_three_user_arguments(self):
        b=Block('entity_for',{'variable':'e','search':'FindByClassnameWithin','filter':'"player"','origin':'Vector(1, 2, 3)','radius':'350'},{'body':[]})
        self.assertIn('Entities.FindByClassnameWithin(e, "player", Vector(1, 2, 3), 350)',self.render(b))

    def test_name_within_uses_correct_order(self):
        b=Block('entity_for',{'variable':'e','search':'FindByNameWithin','filter':'"door"','origin':'center','radius':'radius'},{'body':[]})
        self.assertIn('Entities.FindByNameWithin(e, "door", center, radius)',self.render(b))

    def test_sphere_has_no_name_parameter(self):
        b=Block('entity_for',{'variable':'ent','search':'FindInSphere','filter':'"should_not_appear"','origin':'pos','radius':'512'},{'body':[]})
        self.assertIn('Entities.FindInSphere(ent, pos, 512)',self.render(b))
        self.assertNotIn('should_not_appear',self.render(b))

    def test_all_entities_for_loop_continue_advances(self):
        b=Block('entity_for',{'variable':'ent','search':'AllEntities','filter':'"old"'},{'body':[Block('continue',{})]})
        code=self.render(b)
        self.assertIn('for (local ent = Entities.First(); ent != null; ent = Entities.Next(ent))',code)
        self.assertIn('continue;',code)
        self.assertNotIn('"old"',code)

    def test_switch_keeps_old_inputs_and_adds_missing(self):
        b=Block('entity_for',{'variable':'e','search':'FindByClassname','filter':'"weapon_*"'},{'body':[]})
        normalize_entity_search(b,'FindByClassnameWithin')
        self.assertEqual(b.args['filter'],'"weapon_*"')
        self.assertEqual(b.args['origin'],ENTITY_FIELD_DEFAULTS['origin'])
        self.assertEqual(b.args['radius'],ENTITY_FIELD_DEFAULTS['radius'])
        normalize_entity_search(b,'FindInSphere')
        self.assertEqual(b.args['filter'],'"weapon_*"')
        self.assertNotIn('weapon_',self.render(b))
        normalize_entity_search(b,'FindByClassname')
        self.assertIn('"weapon_*"',self.render(b))

    def test_invalid_method_does_not_generate_unsafe_call(self):
        b=Block('entity_for',{'variable':'e','search':'FindByImaginary','filter':'"player"'},{'body':[]})
        doc=ScriptDocument('main.nut',[Section('function','Run',[b])])
        gen=SquirrelGenerator(); gen.compile(Project(documents=[doc]),doc)
        self.assertTrue(gen.errors)
        with self.assertRaises(ValueError):normalize_entity_search(b,'FindByClassnameNearest')

    def test_negative_radius_is_rejected(self):
        b=Block('entity_for',{'variable':'e','search':'FindInSphere','origin':'pos','radius':'-1'},{'body':[]})
        gen=SquirrelGenerator();doc=ScriptDocument('main.nut',[Section('function','Run',[b])])
        gen.compile(Project(documents=[doc]),doc)
        self.assertTrue(any('半径' in x for x in gen.errors))

    def test_embedded_entity_filter_expression(self):
        ref={'kind':'variable_ref','name':'classname','path':'classname','symbol_id':'abc'}
        b=Block('entity_for',{'variable':'e','search':'FindByClassname','filter':ref},{'body':[]})
        self.assertIn('Entities.FindByClassname(e, classname)',self.render(b))

    def test_json_round_trip(self):
        b=Block('entity_for',{'variable':'e','search':'FindInSphere','origin':'center','radius':'120'},{'body':[]})
        doc=ScriptDocument('m.nut',[Section('function','Main',[b])])
        back=ScriptDocument.from_dict(doc.to_dict())
        self.assertIn('Entities.FindInSphere(e, center, 120)',self.render(back.sections[0].blocks[0]))


if __name__=='__main__': unittest.main()
