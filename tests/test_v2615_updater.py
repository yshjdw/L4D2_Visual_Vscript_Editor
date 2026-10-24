from __future__ import annotations
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from l4visual.update_service import (APP_VERSION, UpdateError, is_newer,
    parse_version, trusted_download_url, release_from_json, validate_update_archive,
    list_install_files)
from l4visual.updater_worker import install_archive


class UpdateTests(unittest.TestCase):
    def test_ordering_numerical_not_alphabetic(self):
        self.assertTrue(is_newer('v26.15', '26.9'))
        self.assertFalse(is_newer('v26.9','26.14'))
        self.assertFalse(is_newer('26.15','v26.15'))
        self.assertEqual(parse_version('v26.15.0'),parse_version('26.15'))
        with self.assertRaises(UpdateError): parse_version('very-new-release')

    def test_metadata_release_asset(self):
        raw = {'tag_name':'v26.16', 'body':'Fixes', 'draft':False, 'prerelease':False,
               'html_url':'https://github.com/yshjdw/L4D2_Visual_Vscript_Editor/releases/tag/v26.16',
               'assets':[{'name':'source.zip','browser_download_url':'https://github.com/foo/bar'},
                         {'name':'L4D2_VScript_Visual_Prototype_v26.16.zip',
                          'browser_download_url':'https://github.com/yshjdw/L4D2_Visual_Vscript_Editor/releases/download/v26.16/L4D2_VScript_Visual_Prototype_v26.16.zip',
                          'size':200, 'digest':'sha256:'+'a'*64}]}
        info=release_from_json(raw)
        self.assertEqual(info.version,'26.16')
        self.assertEqual(info.asset_size,200)
        self.assertEqual(info.sha256,'a'*64)
        self.assertIn('Prototype',info.asset_name)
        self.assertTrue(trusted_download_url(info.asset_url))
        self.assertFalse(trusted_download_url('http://github.com/unsafe'))
        self.assertFalse(trusted_download_url('https://github.com.evil.net/unsafe'))

    def _archive(self,path,files):
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name, content in files.items(): z.writestr(name,content)

    def test_validation_rejects_traversal_and_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            zip_path=Path(directory)/'test.zip'
            self._archive(zip_path,{'app.py':'new', 'l4visual/ui/main_window.py':'new',
                                    'l4visual/codegen.py':'new','../../bad':'malicious'})
            with self.assertRaises(UpdateError):validate_update_archive(zip_path)
            self._archive(zip_path,{'app.py':'new'})
            with self.assertRaises(UpdateError):validate_update_archive(zip_path)

    def test_install_preserves_l4vp_project_and_unknown_files(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            root=folder/'app';root.mkdir()
            (root/'app.py').write_text('old')
            (root/'l4visual/ui').mkdir(parents=True)
            (root/'l4visual/ui/main_window.py').write_text('old')
            (root/'My_Story.l4vp').write_text('personal work')
            (root/'custom_notes.txt').write_text('notes')
            zip_path=folder/'update.zip'
            self._archive(zip_path,{
                'L4D2_VScript_Visual_Prototype/app.py':'new',
                'L4D2_VScript_Visual_Prototype/l4visual/codegen.py':'generator',
                'L4D2_VScript_Visual_Prototype/l4visual/ui/main_window.py':'new ui',
                'L4D2_VScript_Visual_Prototype/l4visual/version.py':"APP_VERSION = '26.15'",
                'L4D2_VScript_Visual_Prototype/Project_X.l4vp':'dont copy me',
                'L4D2_VScript_Visual_Prototype/examples/custom.l4vp':'also protected',
            })
            count=install_archive(zip_path,root,folder/'working','26.15')
            self.assertEqual(count,4)
            self.assertEqual((root/'app.py').read_text(),'new')
            self.assertEqual((root/'l4visual/ui/main_window.py').read_text(),'new ui')
            self.assertEqual((root/'My_Story.l4vp').read_text(),'personal work')
            self.assertFalse((root/'Project_X.l4vp').exists())
            self.assertFalse((root/'examples/custom.l4vp').exists())
            self.assertEqual((root/'custom_notes.txt').read_text(),'notes')

    def test_validation_current_distribution(self):
        # Ensures packaged editor layout remains recognizable.
        root=Path(__file__).resolve().parents[1]
        self.assertTrue((root/'l4visual/version.py').exists())
        self.assertIn('Update', (root/'l4visual/ui/main_window.py').read_text('utf-8'))

if __name__=='__main__':unittest.main()
