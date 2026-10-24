from pathlib import Path
import unittest
from l4visual.models import Block, ScriptDocument, Section, Project
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.expressions import as_embedded
from l4visual.utility_blocks import create_utility_args
from l4visual.trace_config import current_trace_values, update_trace_values

ROOT=Path(__file__).resolve().parents[1]

class TraceConfigTests(unittest.TestCase):
    def test_source_block_is_draggable_with_parameters(self):
        source=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf-8')
        self.assertIn("'射线追踪':['trace_line']",source)
        self.assertIn("'trace_line':{'start':",source)

    def test_native_statement_emits_table_then_trace(self):
        blk=Block('trace_line',dict(start='player.EyePosition()',
                                    end='player.EyePosition() + player.EyeAngles().Forward() * 1000',
                                    ignore='player',mask='33579137',output='ray'))
        doc=ScriptDocument('test.nut',[Section('function','Fire',[blk])]);gen=SquirrelGenerator()
        code=gen.compile(Project('Test',documents=[doc]),doc)
        self.assertEqual(gen.errors,[])
        self.assertIn('local ray = {start = player.EyePosition(), end = ',code)
        self.assertIn('ignore = player, mask = 33579137};',code)
        self.assertIn('TraceLine(ray);',code)
        self.assertNotIn('(function(',code)

    def test_native_statement_at_root_and_optional_output(self):
        blk=Block('trace_line',{'start':'Vector(0, 0, 0)','end':'Vector(1000, 0, 0)', 'ignore':'null','mask':'33579137','output':'trace'})
        gen=SquirrelGenerator()
        text='\n'.join(gen.emit_block(blk,0,'global'))
        self.assertIn('::trace <- {start',text)
        self.assertIn('TraceLine(::trace);',text)
        blk.args['output']=''
        text='\n'.join(gen.emit_block(blk,1,'function'))
        self.assertEqual(text.count('TraceLine('),1)
        self.assertNotIn('local ',text)

    def test_model_roundtrip_and_nested_mask(self):
        mask=Block('expr',{'value':'1174421507'})
        blk=Block('trace_line',{'start':'Vector(0, 0, 0)','end':'Vector(1000, 0, 0)', 'ignore':'null','mask':as_embedded(mask),'output':'trace'})
        self.assertEqual(Block.from_dict(blk.to_dict()).args,blk.args)
        emitted='\n'.join(SquirrelGenerator().emit_block(blk,1,'function'))
        self.assertIn('mask = 1174421507',emitted)

    def test_both_trace_forms_have_a_context_menu(self):
        code=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        self.assertIn("self.block.kind=='trace_line'",code)
        self.assertIn("self.nested.args.get('operation')=='trace_ray'",code)
        self.assertIn('TraceLineConfigDialog(self.block,None)',code)
        self.assertIn('TraceLineConfigDialog(self.nested,None)',code)

    def test_utility_config_keeps_nested_expression_ast(self):
        mask=Block('expr',{'value':'33579137'})
        args=create_utility_args('trace_ray')
        nested_mask=as_embedded(mask)
        args['parameters'][2]=nested_mask
        block=Block('utility',args)
        values=current_trace_values(block)
        self.assertEqual(values[3],nested_mask)
        values[0]='player.EyePosition()'
        update_trace_values(block,values)
        self.assertEqual(block.args['value'],'player.EyePosition()')
        self.assertEqual(block.args['parameters'][2],nested_mask)

    def test_statement_config_updates_all_fields(self):
        block=Block('trace_line',{'start':'a','end':'b','ignore':'null','mask':'-1','output':'tr'})
        update_trace_values(block,['a2','b2','player','1174421507'])
        self.assertEqual([block.args[k] for k in ('start','end','ignore','mask')],
                         ['a2','b2','player','1174421507'])
        self.assertEqual(block.args['output'],'tr')

    def test_translations_and_dual_display(self):
        from l4visual.display_profile import DisplayProfile, block_caption
        for l in ('zh','en'):
            for s in ('general','professional'):
                self.assertTrue(block_caption('trace_line',DisplayProfile(l,s)))
        self.assertEqual(block_caption('trace_line',DisplayProfile('en','general')),'Run TraceLine raycast')
        self.assertEqual(block_caption('trace_line',DisplayProfile('en','professional')),'TraceLine(table)')

if __name__ == '__main__':unittest.main()
