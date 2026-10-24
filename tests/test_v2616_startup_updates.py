from __future__ import annotations
import ast
import unittest
from pathlib import Path
from l4visual.update_service import is_newer, release_from_json, UpdateError
from l4visual.version import APP_VERSION


class StartupUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.app = (cls.root/'app.py').read_text(encoding='utf-8')
        cls.startup = (cls.root/'l4visual/ui/startup_updates.py').read_text(encoding='utf-8')
        cls.main_window = (cls.root/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        ast.parse(cls.app)
        ast.parse(cls.startup)

    def test_prelaunch_dialog_runs_before_main_window(self):
        self.assertLess(self.app.index('dialog.exec()'), self.app.index('window = MainWindow('))
        self.assertIn('MainWindow(startup_checked=True)', self.app)
        self.assertIn('if not startup_checked', self.main_window)

    def test_user_can_skip_without_network(self):
        self.assertIn('self.enter.clicked.connect(self.enter_editor)', self.startup)
        self.assertIn('def enter_editor(self):', self.startup)
        self.assertIn('self.accept()', self.startup)
        self.assertIn('def reject(self):', self.startup)
        self.assertIn('self.enter_editor()', self.startup)

    def test_visible_states_and_language_variants(self):
        for phrase in ('正在连接 GitHub', '检查更新失败', '当前已是最新版本', '发现新版本',
                       '重新检查', '取消下载', '进入编辑器', '下载更新'):
            self.assertIn(phrase, self.startup)
        for phrase in ('Unable to check', 'latest version', 'newer version',
                       'Cancel download', 'Enter editor', 'Download update'):
            self.assertIn(phrase, self.startup)

    def test_download_before_install_and_delayed_external_worker(self):
        self.assertIn('ReleaseDownloadTask', self.startup)
        self.assertIn('self._download_task.cancel()', self.startup)
        self.assertIn('self.install_requested = True', self.startup)
        self.assertLess(self.app.index('if dialog.install_requested'), self.app.index('window = MainWindow('))
        self.assertIn('start_detached_install(archive, folder, tag)', self.app)
        self.assertIn("'--parent-pid'", self.startup)
        self.assertIn("'--version'", self.startup)

    def test_same_version_does_not_prompt_for_download(self):
        self.assertFalse(is_newer('v26.16', '26.16'))
        data={'tag_name':'v26.16','draft':False,'prerelease':False,'assets':[]}
        info=release_from_json(data)
        self.assertFalse(is_newer(info.version, APP_VERSION))
        self.assertFalse(info.asset_url)
        self.assertTrue(is_newer('v26.18', APP_VERSION))

if __name__ == '__main__':
    unittest.main()
