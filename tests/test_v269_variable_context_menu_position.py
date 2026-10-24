from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "l4visual" / "ui" / "canvas.py"


class VariableMenuPositionTests(unittest.TestCase):
    def test_variable_popup_has_no_proxy_widget_parent(self):
        code = SOURCE.read_text(encoding="utf-8")
        section = code.split("    def show_reference_menu(self,global_pos=None):", 1)[1].split("    def contextMenuEvent(self,event):", 1)[0]
        self.assertIn("menu=QMenu(None)", section)
        self.assertNotIn("menu=QMenu(self)", section)
        self.assertIn("menu.exec(QCursor.pos() if global_pos is None else global_pos)", section)

    def test_native_right_click_uses_actual_screen_cursor(self):
        code=SOURCE.read_text(encoding="utf-8")
        section=code.split("class EmbeddedVariableReference(QLabel):",1)[1].split("class EmbeddedExpressionDragHandle",1)[0]
        self.assertIn("self.show_reference_menu(QCursor.pos())",section)

    def test_viewport_right_click_maps_viewport_point_to_screen(self):
        code=SOURCE.read_text(encoding="utf-8")
        self.assertIn("token.show_reference_menu(self.viewport().mapToGlobal(event.pos()))",code)


if __name__ == "__main__":
    unittest.main()
