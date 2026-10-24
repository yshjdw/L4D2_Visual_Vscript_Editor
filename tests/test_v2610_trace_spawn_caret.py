from pathlib import Path
import unittest
from l4visual.models import Block, Project, Section, ScriptDocument
from l4visual.quick_literals import LITERAL_GROUPS, new_literal_block, literal_label, literal_tooltip
from l4visual.expressions import as_embedded
from l4visual.codegen import expression, SquirrelGenerator
from l4visual.utility_blocks import UTILITY_BLOCKS, UTILITY_GROUPS, create_utility_args

ROOT=Path(__file__).resolve().parents[1]

class TraceAndSpawnTests(unittest.TestCase):
    def test_trace_group_is_draggable_and_multilingual(self):
        self.assertIn('trace',UTILITY_GROUPS)
        ops=[name for name,info in UTILITY_BLOCKS.items() if info['group']=='trace']
        self.assertEqual(len(ops),8)
        for op in ops:
            with self.subTest(op=op):
                info=UTILITY_BLOCKS[op]
                self.assertTrue(info['zh'] and info['en'] and info['description'] and info['description_en'])
                self.assertNotRegex(info['description_en'],r'[\u3400-\u9fff]')
                b=Block('utility',create_utility_args(op))
                self.assertEqual(b.kind,'utility')
                self.assertIn('::L4VP_Utils.',expression(as_embedded(b)))
        ray=Block('utility',create_utility_args('trace_ray'))
        self.assertEqual(ray.args['value'],'Vector(0, 0, 0)')
        self.assertEqual(ray.args['parameters'],['Vector(1000, 0, 0)','null','33579137'])

    def test_trace_helpers_do_not_emit_iife_and_are_single(self):
        a=Block('utility',create_utility_args('trace_ray'))
        b=Block('utility',dict(create_utility_args('trace_pos'),value='ray'))
        c=Block('utility',dict(create_utility_args('trace_hit'),value='ray'))
        blocks=[Block('var',{'name':'ray','value':as_embedded(a),'scope':'local'}),
                Block('var',{'name':'pos','value':as_embedded(b),'scope':'local'}),
                Block('return',{'value':as_embedded(c)})]
        d=ScriptDocument('trace.nut',[Section('function','TestTrace',blocks)])
        generator=SquirrelGenerator()
        text=generator.compile(Project('p',documents=[d]),d)
        self.assertEqual(generator.errors,[])
        self.assertEqual(text.count('::L4VP_Utils.TraceRay <- function'),1)
        self.assertEqual(text.count('::L4VP_Utils.TraceRead <- function'),1)
        self.assertIn('local tr = {start = start, end = finish, ignore = ignored, mask = mask};',text)
        self.assertIn('TraceLine(tr)',text)
        self.assertIn('::L4VP_Utils.TracePosition(ray)',text)
        self.assertIn('::L4VP_Utils.TraceHit(ray)',text)
        self.assertNotIn('(function(',text)

    def test_spawn_classname_works_in_summon_socket(self):
        candidates=LITERAL_GROUPS['spawn_classname']['entries']
        self.assertGreaterEqual(len(candidates),30)
        self.assertIn('info_target',[row[0] for row in candidates])
        for language in ('en','zh'):
            for style in ('general','professional'):
                tooltip=literal_tooltip('spawn_classname','info_target',language,style)
                self.assertTrue(tooltip)
                if language=='en':self.assertNotRegex(tooltip,r'[\u3400-\u9fff]')
        b=new_literal_block('spawn_classname','info_target')
        self.assertEqual(expression(as_embedded(b)),'"info_target"')
        spawn=Block('summon',{'classname':as_embedded(b),'config':{},'output':'ent'})
        d=ScriptDocument('spawn.nut',[Section('function','Spawn',[spawn])])
        code=SquirrelGenerator().compile(Project('p',documents=[d]),d)
        self.assertIn('SpawnEntityFromTable("info_target", {})',code)
        self.assertEqual(code.count('SpawnEntityFromTable('),1)

    def test_trace_mask_is_numeric_not_string(self):
        mask=new_literal_block('trace_mask','1174421507')
        self.assertEqual(mask.args['return_type'],'int')
        self.assertEqual(expression(as_embedded(mask)),'1174421507')
        self.assertIn('integer',literal_tooltip('trace_mask','1174421507','en'))

    def test_caret_maps_through_scene_not_global(self):
        src=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        fn=src.split('def _local_pointer_pos(',1)[1].split('\n\ndef ',1)[0]
        self.assertIn('canvas.mapToScene(',fn)
        self.assertIn('section.mapFromScene(',fn)
        self.assertIn('target.mapFrom(root, root_point)',fn)
        self.assertIn('_local_pointer_pos(widget,self,event.position())',src)
        self.assertIn('_local_pointer_pos(widget,self,event.pos())',src)
        self.assertNotIn('_local_pointer_pos(widget,vp,event.position())',src)

if __name__=='__main__':unittest.main()
