import re
import unittest
from pathlib import Path

from l4visual.models import Block, Project, Section, ScriptDocument
from l4visual.expressions import as_embedded, can_embed
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.utility_blocks import (UTILITY_BLOCKS, UTILITY_GROUPS,
                                     create_utility_args, utility_caption, change_utility_operation)

ROOT=Path(__file__).resolve().parents[1]

class EntityIndexUtilityTests(unittest.TestCase):
    def test_metadata_and_bilingual_tooltips(self):
        meta=UTILITY_BLOCKS['entity_from_index']
        self.assertEqual(meta['group'],'entities')
        self.assertEqual(meta['return_type'],'handle')
        self.assertEqual(meta['default'],'env.weaponentid')
        self.assertIn('实体索引',meta['description'])
        self.assertIn('weaponentid',meta['description_en'])
        self.assertIn('userid',meta['description_en'])
        self.assertIn('weapon-type ID',meta['description_en'])
        self.assertFalse(re.search(r'[\u3400-\u9fff]',meta['description_en']))
        self.assertIn(meta['group'],UTILITY_GROUPS)
        self.assertEqual(utility_caption(meta,'en','professional'),'EntIndexToHScript(entindex)')
        self.assertEqual(utility_caption(meta,'zh','general'),'根据实体索引获取实体句柄')
        self.assertEqual(utility_caption(meta,'en','general'),'Entity from entity index')

    def test_direct_native_call_and_nesting(self):
        data=create_utility_args('entity_from_index')
        block=Block('utility',data)
        self.assertTrue(can_embed(block))
        self.assertEqual(expression(as_embedded(block)), 'EntIndexToHScript(env.weaponentid)')
        for event_field in ('env.entityid','env.propid','env.attackerentid','env.entindex','env.weaponentid'):
            with self.subTest(event_field=event_field):
                data['value']=event_field
                self.assertEqual(expression(as_embedded(block)),f'EntIndexToHScript({event_field})')
        data['value']='env.weaponentid'
        weapon=Block('var',{'name':'weapon','value':as_embedded(block),'scope':'local'})
        document=ScriptDocument('test.nut',[Section('function','GetWeapon',[weapon])])
        gen=SquirrelGenerator()
        output=gen.compile(Project('test',documents=[document]),document)
        self.assertEqual(gen.errors,[])
        self.assertIn('EntIndexToHScript(env.weaponentid)',output)
        self.assertNotIn('::L4VP_Utils.EntityFromIndex',output)
        self.assertNotIn('(function(',output)

    def test_other_wrappers_unchanged(self):
        op=create_utility_args('player_from_userid')
        self.assertEqual(expression(as_embedded(Block('utility',op))),'GetPlayerFromUserID(env.userid)')
        b=Block('utility',create_utility_args('entity_from_index'))
        b.args['value']='env.entityid'
        change_utility_operation(b,'entity_valid')
        self.assertEqual(b.args['value'],'env.entityid')
        self.assertEqual(b.args['return_type'],'bool')

    def test_ui_palette_supported_and_versioned(self):
        palette=(ROOT/'l4visual/ui/palette.py').read_text('utf-8')
        self.assertIn('for operation,info in UTILITY_BLOCKS.items()',palette)
        self.assertIn('utility_caption(info,current_profile().language,current_profile().style)',palette)
        self.assertIn("description=info.get('description_en') if english else info.get('description')",palette)
        self.assertIn('APP_VERSION',(ROOT/'l4visual/ui/main_window.py').read_text('utf-8'))

if __name__=='__main__':
    unittest.main()
