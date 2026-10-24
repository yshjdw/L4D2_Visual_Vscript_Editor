from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / 'l4visual/ui/canvas.py').read_text(encoding='utf-8')


class WrappingLayoutTests(unittest.TestCase):
    def test_fields_are_wrapping(self):
        self.assertIn('fields=WrappingFields(self._fields_host,spacing=5)', SOURCE)
        self.assertIn('self._fields_host.setFixedHeight', SOURCE)
        self.assertIn('def _recalculate_field_height(self):', SOURCE)

    def test_layout_does_not_shrink_widgets(self):
        self.assertIn('sizeHint().expandedTo(item.minimumSize())', SOURCE)
        self.assertIn('plan_flow(sizes,usable,self.spacing())', SOURCE)

    def test_nested_expression_minimum_size(self):
        self.assertIn('if slot.minimumWidth()!=required:slot.setMinimumWidth(required)', SOURCE)

    def test_supports_dynamic_geometry(self):
        self.assertIn('def hasHeightForWidth(self):', SOURCE)
        self.assertIn('def heightForWidth(self, width):', SOURCE)


if __name__ == '__main__':
    unittest.main()
