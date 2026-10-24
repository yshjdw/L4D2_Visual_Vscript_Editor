import struct
import tempfile
import unittest
from pathlib import Path
from l4visual.vpk_export import package_scripts, author_credit, MAGIC, addoninfo
from l4visual.models import Block
from l4visual.data_definitions import container_kind

class V098Tests(unittest.TestCase):
    def test_plain_variable_is_not_container(self):
        self.assertIsNone(container_kind(Block('var', {'name':'player','value':'null','container_type':'普通'})))
    def test_table_and_scope_remain_containers(self):
        self.assertEqual(container_kind(Block('var',{'name':'t','container_type':'Table'})),'Table')
        self.assertEqual(container_kind(Block('var',{'name':'scope','container_type':'ScriptScope','value':'ent'})),'Table')
    def test_author_suffix_once(self):
        self.assertEqual(author_credit('Alice'),'Alice/Vscript Visual Maker')
        self.assertEqual(author_credit('Alice/Vscript Visual Maker'),'Alice/Vscript Visual Maker')
    def test_vpk_header_tree_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'addon.vpk'
            package_scripts(path,{'director_base_addon.nut':'printl("x");','utils/helper.nut':'printl("y");'},title='Test',author='Alice',version='2',description='Sample')
            raw=path.read_bytes()
            sig,ver,size=struct.unpack_from('<III',raw,0)
            self.assertEqual((sig,ver),(MAGIC,1))
            tree=raw[12:12+size]
            self.assertIn(b'addoninfo\0',tree)
            self.assertIn(b'director_base_addon\0',tree)
            self.assertIn(b'helper\0',tree)
            self.assertIn(b'scripts/vscripts/utils\0',tree)
            self.assertIn(b'Alice/Vscript Visual Maker',raw)
            self.assertIn(b'printl("x");',raw)
    def test_vpk_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                package_scripts(Path(tmp)/'bad.vpk',{'../evil.nut':'x'},title='Bad',author='')
    def test_kv_escapes_quotes(self):
        info=addoninfo('Test "quoted"','Bob','1','line\n2')
        self.assertIn('\\"quoted\\"',info)
        self.assertIn('line\\n2',info)

if __name__=='__main__':unittest.main()
