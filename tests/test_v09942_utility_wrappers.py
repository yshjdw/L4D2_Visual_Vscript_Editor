import re
import unittest
from pathlib import Path

from l4visual.codegen import SquirrelGenerator,expression
from l4visual.expressions import as_embedded,can_embed,unpack_embedded
from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.utility_blocks import (UTILITY_BLOCKS, UTILITY_GROUPS, create_utility_args,
                                     emit_utility, change_utility_operation, utility_caption)

ROOT=Path(__file__).resolve().parents[1]

class UtilityWrapperTests(unittest.TestCase):
    def make(self, operation, value=None, extra=None):
        data=create_utility_args(operation)
        if value is not None:data['value']=value
        if extra is not None:data['parameters']=extra
        return Block('utility',data)

    def test_every_utility_can_embed_and_generate_an_expression(self):
        self.assertGreaterEqual(len(UTILITY_BLOCKS),20)
        for op in UTILITY_BLOCKS:
            with self.subTest(op=op):
                block=self.make(op)
                self.assertTrue(can_embed(block))
                nested=as_embedded(block)
                self.assertEqual(unpack_embedded(nested).kind,'utility')
                self.assertEqual(unpack_embedded(nested).args['operation'],op)
                code=expression(nested)
                self.assertTrue(code)
                self.assertNotIn('ERROR',code)
                self.assertEqual(code,emit_utility(block.args,expression))

    def test_exact_slot4_and_generic_slot(self):
        for op in ('inventory_slot','inventory_slot4','inventory_has_slot','inventory_slot_classname'):
            with self.subTest(op=op):
                code=expression(as_embedded(self.make(op)))
                self.assertIn('::L4VP_Utils.Inventory',code)
                self.assertNotIn('(function(',code)
        self.assertEqual('::L4VP_Utils.InventorySlot(player, 4)',
                         expression(as_embedded(self.make('inventory_slot4'))))
        self.assertIn('InventorySlotClassname',expression(as_embedded(self.make('inventory_slot_classname'))))
        self.assertIn('InventoryHasSlot',expression(as_embedded(self.make('inventory_has_slot'))))

    def test_custom_slot_variable_or_nested_player(self):
        player=self.make('player_from_userid','env.userid')
        outer=self.make('inventory_slot',as_embedded(player),['slotNumber'])
        code=expression(as_embedded(outer))
        self.assertEqual('::L4VP_Utils.InventorySlot(GetPlayerFromUserID(env.userid), slotNumber)',code)

    def test_backward_compatibility_of_old_single_value_utility(self):
        for operation in ('player_from_userid','active_weapon','player_from_event',
                          'weapon_classname','remove_weapon_prefix'):
            old=Block('utility',{'operation':operation,'value':UTILITY_BLOCKS[operation]['default']})
            self.assertTrue(can_embed(old))
            self.assertTrue(expression(as_embedded(old)))

    def test_switching_operation_preserves_custom_inputs_and_matched_slot(self):
        block=self.make('inventory_slot','custom_player',['slotIndex'])
        change_utility_operation(block,'inventory_has_slot')
        self.assertEqual(block.args['value'],'custom_player')
        self.assertEqual(block.args['parameters'],['slotIndex'])
        self.assertEqual(block.args['return_type'],'bool')
        change_utility_operation(block,'entity_valid')
        self.assertEqual(block.args['value'],'custom_player')
        self.assertNotIn('parameters',block.args)

    def test_bilingual_display_is_code_neutral(self):
        for name,info in UTILITY_BLOCKS.items():
            with self.subTest(name=name):
                self.assertIn(info['group'],UTILITY_GROUPS)
                self.assertTrue(info['zh'] and info['en'] and info['professional'])
                self.assertIsNone(re.search('[\u4e00-\u9fff]',info['description_en']))
                self.assertIsNone(re.search('[\u4e00-\u9fff]',info['en']))
                self.assertEqual(utility_caption(info,'en','professional'),info['professional'])
                self.assertEqual(utility_caption(info,'en','general'),info['en'])
                self.assertEqual(utility_caption(info,'zh','general'),info['zh'])
                for param in info['params']:
                    self.assertTrue(param['en'] and param['zh'])
                    self.assertIsNone(re.search('[\u4e00-\u9fff]',param['en']))

    def test_no_changes_to_ordinary_script_generation(self):
        block=self.make('inventory_slot','player',['4'])
        doc=ScriptDocument('test.nut',[Section('function','get_slot4',[
            Block('var',{'name':'item','scope':'auto','container_type':'普通','value':as_embedded(block)})
        ],{'owner':''})])
        result=SquirrelGenerator().compile(Project('demo',documents=[doc]),doc)
        self.assertIn('GetInvTable(p, inv)',result)
        self.assertIn('::L4VP_Utils.InventorySlot(player, 4)',result)
        self.assertIn('local item =',result)

    def test_palette_canvas_wiring_and_search_restore(self):
        palette=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        dialogs=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf-8')
        expressions=(ROOT/'l4visual/expressions.py').read_text(encoding='utf-8')
        self.assertIn("'string_call','utility'",expressions)
        self.assertIn('create_utility_args(operation)',dialogs)
        self.assertIn("'utility':['operation','value','parameters']",canvas)
        self.assertIn('change_utility_operation(block,value)',canvas)
        self.assertIn('self.utility_groups',palette)
        self.assertIn('self._search_expansion_snapshot',palette)

if __name__=='__main__':unittest.main()
