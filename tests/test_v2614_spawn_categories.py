import unittest
from pathlib import Path
from l4visual.quick_literals import LITERAL_GROUPS, new_literal_block, literal_tooltip
from l4visual.literal_subgroups import literal_subgroups
from l4visual.spawn_catalog import SPAWN_GROUPS, SPAWN_GROUP_META, INFECTED_TYPES, spawn_category
from l4visual.models import Block, Project, Section, ScriptDocument
from l4visual.expressions import as_embedded
from l4visual.codegen import SquirrelGenerator
from l4visual.display_profile import DisplayProfile, block_caption

ROOT=Path(__file__).resolve().parents[1]
class SpawnCategoriesV2614Tests(unittest.TestCase):
    def test_subgroups_unique_complete_and_bilingual(self):
        cats=literal_subgroups('spawn_classname')
        values=[v for group in cats for source,v in group['entries']]
        self.assertGreaterEqual(len(cats),7)
        self.assertGreaterEqual(len(values),75)
        self.assertEqual(len(values),len(set(values)))
        self.assertEqual(set(values),{v for v,*_ in LITERAL_GROUPS['spawn_classname']['entries']})
        self.assertTrue({'weapon_rifle_ak47','weapon_pain_pills','weapon_molotov','weapon_melee','weapon_melee_spawn','witch','infected'}.issubset(values))
        for cat in cats:
            self.assertTrue(cat['zh'] and cat['en'] and cat['description_zh'] and cat['description_en'])
            self.assertNotRegex(cat['en']+cat['description_en'],r'[\u3400-\u9fff]')
        self.assertEqual(spawn_category('weapon_rifle_ak47'),'主武器实体')
        self.assertEqual(spawn_category('weapon_pain_pills'),'医疗与补给实体')
    def test_spawn_literal_quoted_and_no_nested_spawn(self):
        for value in ('weapon_rifle_ak47','weapon_first_aid_kit','weapon_molotov','weapon_melee_spawn'):
            lit=new_literal_block('spawn_classname',value)
            b=Block('summon',{'classname':as_embedded(lit),'config':{'origin':'Vector(2, 3, 4)'},'output':'created'})
            doc=ScriptDocument('spawn.nut',[Section('function','Spawn',[b])]);g=SquirrelGenerator()
            text=g.compile(Project('p',documents=[doc]),doc)
            self.assertFalse(g.errors)
            self.assertIn('SpawnEntityFromTable("'+value+'", {origin = Vector(2, 3, 4)})',text)
            self.assertEqual(text.count('SpawnEntityFromTable('),1)
            for lang in ('zh','en'):
                for style in ('general','professional'):
                    tip=literal_tooltip('spawn_classname',value,lang,style)
                    self.assertIn(value,tip)
                    if lang=='en':self.assertNotRegex(tip,r'[\u3400-\u9fff]')
    def test_zspawn_types_and_codegen(self):
        self.assertEqual([x[0] for x in INFECTED_TYPES],list(range(9)))
        blocks=[Block('zspawn',{'infected_type':species,'pos':'Vector(1, 2, 3)'}) for species,_,_ in INFECTED_TYPES]
        doc=ScriptDocument('zspawn.nut',[Section('function','SpawnInfected',blocks)])
        g=SquirrelGenerator();text=g.compile(Project('p',documents=[doc]),doc)
        self.assertFalse(g.errors)
        for species,_,_ in INFECTED_TYPES:
            self.assertIn('ZSpawn({type = '+str(species)+', pos = Vector(1, 2, 3)});',text)
        self.assertNotIn('SpawnEntityFromTable(',text)
        self.assertEqual(block_caption('zspawn',DisplayProfile('en','professional')),'ZSpawn(table)')
        self.assertEqual(block_caption('zspawn',DisplayProfile('zh','general')),'生成感染者')
        doc.sections[0].blocks=[Block('zspawn',{'infected_type':99,'pos':'Vector(0,0,0)'})]
        g.compile(Project('p',documents=[doc]),doc)
        self.assertTrue(g.errors)
    def test_qt_ui_wiring_and_nested_search(self):
        palette=(ROOT/'l4visual/ui/palette.py').read_text('utf-8')
        self.assertIn("if group in ('classname','item','spawn_classname'):",palette)
        self.assertIn('for subgroup in literal_subgroups(group)',palette)
        self.assertIn('self._search_expansion_snapshot',palette)
        dialog=(ROOT/'l4visual/ui/spawn_dialog.py').read_text('utf-8')
        self.assertIn('QTreeWidget',dialog)
        self.assertIn('SPAWN_GROUP_META',dialog)
        self.assertIn('current_profile().language',dialog)
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text('utf-8')
        self.assertIn("key=='infected_type' and block.kind=='zspawn'",canvas)
        self.assertIn('INFECTED_TYPES',canvas)
if __name__=='__main__':unittest.main()
