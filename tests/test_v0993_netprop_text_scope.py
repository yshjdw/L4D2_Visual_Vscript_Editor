"""Regressions for the user-supplied 2024 L4D2 SendTable and Squirrel scope."""
import unittest
from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.netprop_catalog import list_properties, resolve_property, runtime_property_name
from l4visual.netprop_method import set_selected_property
from l4visual.codegen import expression, SquirrelGenerator
from l4visual.expressions import method_call_expression
from l4visual.data_definitions import prune_empty_orphan_data
from l4visual.validation import Validator


class NetPropSourceRegressions(unittest.TestCase):
    def test_m_i_ammo_is_a_documented_array_container(self):
        row=resolve_property('CBasePlayer','m_iAmmo')
        self.assertEqual(row['type'],'array')
        self.assertEqual(row['length'],32)
        self.assertEqual(row['name'],'m_iAmmo')
        self.assertEqual(row['document_path'],'localdata.m_iAmmo')

    def test_ammo_inherited_by_terror_player(self):
        row=resolve_property('CTerrorPlayer','m_iAmmo')
        self.assertEqual(row['declaring_class'],'CBasePlayer')

    def test_legacy_wrapper_path_is_accepted(self):
        row=resolve_property('CTerrorWeapon','LocalWeaponData.m_iPrimaryAmmoType')
        self.assertEqual(row['name'],'m_iPrimaryAmmoType')
        self.assertEqual(runtime_property_name('LocalWeaponData.m_iPrimaryAmmoType'),'m_iPrimaryAmmoType')

    def test_real_nested_path_is_preserved(self):
        self.assertEqual(runtime_property_name('m_Collision.m_vecMins'),'m_Collision.m_vecMins')

    def test_picker_changes_scalar_getter_to_typed_int_array(self):
        b=Block('method',{'owner':'CNetPropManager','target':'NetProps',
                          'method':'GetPropFloat','parameters':['player','"m_iHealth"'],
                          'parameter_specs':[{'name':'entity','type':'CBaseEntity'},
                                             {'name':'propertyName','type':'string'}]})
        row=resolve_property('CTerrorPlayer','m_iAmmo')
        set_selected_property(b,1,{'table':'CTerrorPlayer','property':row['name'],
                                   'array':True,'prop_type':'Int'})
        self.assertEqual(b.args['method'],'GetPropIntArray')
        self.assertEqual(len(b.args['parameters']),3)
        self.assertEqual(b.args['parameters'][2],'0')
        self.assertEqual(method_call_expression(b,expression),
                         'NetProps.GetPropIntArray(player, "m_iAmmo", 0)')

    def test_picker_changes_wrong_float_scalar_to_int(self):
        b=Block('method',{'owner':'CNetPropManager','target':'NetProps',
                          'method':'GetPropFloat','parameters':['weapon','"m_iClip1"']})
        set_selected_property(b,1,{'table':'CTerrorWeapon','property':'m_iClip1',
                                   'array':False,'prop_type':'Int'})
        self.assertEqual(b.args['method'],'GetPropInt')
        self.assertEqual(method_call_expression(b,expression),
                         'NetProps.GetPropInt(weapon, "m_iClip1")')

    def test_set_prop_array_places_value_before_index(self):
        b=Block('method',{'owner':'CNetPropManager','target':'NetProps',
                          'method':'SetPropFloat','parameters':['player','"m_iHealth"','100'],
                          'parameter_specs':[{'name':'entity','type':'CBaseEntity'},
                                             {'name':'propertyName','type':'string'},
                                             {'name':'value','type':'float'}]})
        set_selected_property(b,1,{'table':'CTerrorPlayer','property':'m_iAmmo',
                                   'array':True,'prop_type':'Int'})
        self.assertEqual(b.args['method'],'SetPropIntArray')
        self.assertEqual(method_call_expression(b,expression),
                         'NetProps.SetPropIntArray(player, "m_iAmmo", 100, 0)')

    def test_saved_wrong_scalar_type_is_repaired_during_codegen(self):
        b=Block('method',{'owner':'CNetPropManager','target':'NetProps',
            'method':'GetPropFloat','netprop_class':'CBaseRifle',
            'netprop_selected_type':'Int','parameters':['weapon',{'kind':'literal','value':'m_iClip1'}],
            'parameter_specs':[{'name':'entity','type':'CBaseEntity'},{'name':'propertyName','type':'string'}]})
        self.assertEqual(method_call_expression(b,expression),
                         'NetProps.GetPropInt(weapon, "m_iClip1")')

    def test_old_netprop_block_uses_runtime_key(self):
        b=Block('netprop', {'mode':'get','target':'weapon',
                            'property':'LocalWeaponData.m_iPrimaryAmmoType','prop_type':'Int'})
        self.assertEqual(method_call_expression(b,expression),
                         'NetProps.GetPropInt(weapon, "m_iPrimaryAmmoType")')

    def test_array_block_code_generator(self):
        b=Block('netprop',{'mode':'get','target':'player','property':'m_iAmmo',
                           'table':'CTerrorPlayer','array':True,'prop_type':'Int','index':'ammoType'})
        self.assertEqual(method_call_expression(b,expression),
                         'NetProps.GetPropIntArray(player, "m_iAmmo", ammoType)')


class ScopeRegressions(unittest.TestCase):
    def test_remove_only_unlinked_empty_data(self):
        var=Block('var',{'name':'scope','value':'ent','container_type':'ScriptScope'})
        evt=Section('events','MyEvents',[Block('event',{'event':'weapon_reload','env':'env'},
                                               {'body':[var]})])
        valid=Section('data','scope',[],{'source_id':var.id,'container':'Table'})
        invalid=Section('data','scope',[],{'source_id':'nonexistent','container':'Table'})
        nonempty=Section('data','keep', [Block('var',{'name':'important','value':'10'})],
                         {'source_id':'nonexistent','container':'Table'})
        doc=ScriptDocument('director_base_addon.nut',[evt,valid,invalid,nonempty])
        self.assertEqual(prune_empty_orphan_data(doc),[invalid.id])
        self.assertIn(valid,doc.sections)
        self.assertIn(nonempty,doc.sections)

    def test_cross_event_local_reference_is_error(self):
        source=Block('var',{'name':'player','value':'null','scope':'auto'})
        ref={'kind':'variable_ref','symbol_id':source.id,'name':'player','path':'player'}
        one=Block('event',{'event':'weapon_fire','env':'env'},{'body':[source]})
        two=Block('event',{'event':'weapon_reload','env':'env'},{'body':[Block('var',{'name':'target','value':ref})]})
        doc=ScriptDocument('director_base_addon.nut',[Section('events','MyEvents',[one,two])])
        project=Project(documents=[doc])
        class Events:
            def events(self,*a):return [{'name':'weapon_fire'},{'name':'weapon_reload'}]
        problems=Validator(Events()).check(project,doc)
        self.assertTrue(any('跨函数' in p.text for p in problems))

    def test_different_event_env_copy_with_same_name_is_valid(self):
        event1=Block('event',{'event':'weapon_fire','env':'env'},{'body':[]})
        event2=Block('event',{'event':'weapon_reload','env':'env'},{'body':[
            Block('var',{'name':'uid','value':{'kind':'variable_ref','symbol_id':event1.id,
                                           'name':'env','path':'env.userid'}})]})
        doc=ScriptDocument('director_base_addon.nut',[Section('events','MyEvents',[event1,event2])])
        project=Project(documents=[doc])
        class Events:
            def events(self,*a):return [{'name':'weapon_fire'},{'name':'weapon_reload'}]
        errors=Validator(Events()).check(project,doc)
        self.assertFalse(any('跨函数' in p.text for p in errors),errors)


if __name__=='__main__':unittest.main()
