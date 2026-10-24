import unittest
from l4visual.models import Block
from l4visual.codegen import SquirrelGenerator
from l4visual.spawn_catalog import SPAWN_GROUPS,enabled_config

class Test078(unittest.TestCase):
    def test_default_summon_no_config(self):
        self.assertEqual(SquirrelGenerator().emit_block(Block('summon',{'classname':'info_target','config':{},'output':''})),['    SpawnEntityFromTable("info_target", {});'])
    def test_select_config(self):
        b=Block('summon',{'classname':'info_target','config':{'origin':'Vector(1, 2, 3)','targetname':'"test"'},'output':'thinker'})
        self.assertEqual(SquirrelGenerator().emit_block(b),['    local thinker = SpawnEntityFromTable("info_target", {origin = Vector(1, 2, 3), targetname = "test"});'])
    def test_unknown_config_excluded(self):
        self.assertEqual(enabled_config({'bogus':'1','count':'5'}),{'count':'5'})
    def test_entity_catalog(self):
        self.assertIn('weapon_rifle_ak47_spawn',SPAWN_GROUPS['武器生成点'])
        self.assertIn('weapon_defibrillator_spawn',SPAWN_GROUPS['物品生成点'])
    def test_bad_entity(self):
        with self.assertRaises(ValueError):
            SquirrelGenerator().emit_block(Block('summon',{'classname':'bad;cmd','config':{}}))

if __name__=='__main__':unittest.main()

class ExternalAPI078(unittest.TestCase):
    def test_external_owner_is_receiver(self):
        from l4visual.expressions import block_from_method
        b=block_from_method({'external':True,'owner':'ArmorSystem','name':'LoadArmor','parameters':'name:any','returns':'table'})
        self.assertEqual(b.args['target'],'ArmorSystem')
        self.assertEqual(b.args['method'],'LoadArmor')
