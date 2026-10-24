import json
import unittest
from pathlib import Path
from l4visual.models import Block
from l4visual.codegen import SquirrelGenerator
from l4visual.netprop_catalog import list_properties,api_type

class Test0994(unittest.TestCase):
    def test_if_single_branch(self):
        b=Block('if',{'condition':'x > 0'},{'body':[Block('raw',{'source':'printl("yes");'})]})
        result='\n'.join(SquirrelGenerator().emit_block(b,0,'function'))
        self.assertIn('if (x > 0)',result)
        self.assertNotIn('else',result)
    def test_elseif_and_else_serialization(self):
        b=Block('if',{'condition':'a','elif_condition_elif__abc':'b'},{'body':[], 'elif__abc':[Block('raw',{'source':'printl("b");'})],'else':[Block('raw',{'source':'printl("c");'})]})
        rebuilt=Block.from_dict(b.to_dict())
        result='\n'.join(SquirrelGenerator().emit_block(rebuilt,0,'function'))
        self.assertIn('else if (b)',result)
        self.assertIn('else\n{',result)
        self.assertLess(result.index('else if'),result.rindex('else\n'))
    def test_array_ranges(self):
        props=list_properties('CBasePlayer')
        ammo=[p for p in props if p['name']=='m_iAmmo']
        self.assertEqual(ammo[0]['length'],32)
        self.assertEqual(ammo[0]['type'],'array')
        self.assertEqual(api_type(ammo[0]),'Int')
        weapons=[p for p in list_properties('CBaseCombatCharacter') if p['name']=='m_hMyWeapons']
        self.assertTrue(weapons)
        self.assertEqual(weapons[0]['length'],56)
    def test_many_arrays_imported(self):
        data=json.loads((Path(__file__).parents[1]/'resources/netprops_2024.json').read_text())
        count=sum(p['type']=='array' for c in data['classes'].values() for p in c['props'])
        self.assertGreaterEqual(count,100)
    def test_multiline_source_preserves_spaces(self):
        b=Block('raw',{'source':'local message = "hello world";\nprintl(message);'})
        text='\n'.join(SquirrelGenerator().emit_block(b,0,'function'))
        self.assertIn('"hello world"',text)
        self.assertIn('printl(message);',text)

if __name__=='__main__':unittest.main()
