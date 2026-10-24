import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'l4visual' / 'ui' / 'main_window.py').read_text(encoding='utf-8')

class DockRestorationTests(unittest.TestCase):
    def test_dock_references_persist(self):
        for name in ('self.project_dock=dock', 'self.palette_dock=dock2', 'self.api_dock=dock3'):
            self.assertIn(name, SOURCE)

    def test_menu_recovery_actions(self):
        self.assertIn("view_menu=self.menuBar().addMenu('视图')", SOURCE)
        self.assertIn('dock_widget.toggleViewAction()', SOURCE)
        self.assertIn('self.restore_default_layout', SOURCE)

    def test_tabified_dock_can_be_raised(self):
        self.assertIn('dock.raise_()', SOURCE)
        self.assertIn('self.tabifyDockWidget(self.project_dock,self.palette_dock)', SOURCE)

if __name__ == '__main__':
    unittest.main()
