"""Nested expression geometry regression without a desktop Qt installation."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'l4visual/ui/canvas.py').read_text(encoding='utf-8')

class _Size:
    def __init__(self, width):
        self._width=width
    def width(self):
        return self._width

class _Widget:
    def __init__(self, minimum, preferred):
        self._minimum=minimum
        self._preferred=preferred
    def minimumWidth(self):
        return self._minimum
    def minimumSizeHint(self):
        return _Size(self._minimum)
    def sizeHint(self):
        return _Size(self._preferred)

class _Item:
    def __init__(self, widget):
        self._widget=widget
    def widget(self):
        return self._widget
    def minimumSize(self):
        return _Size(self._widget.minimumWidth())
    def sizeHint(self):
        return self._widget.sizeHint()
    def layout(self):
        return None

class _Row:
    def __init__(self, widths, spacing=4, margins=(8,3,6,3)):
        self.items=[_Item(_Widget(w,w)) for w in widths]
        self.space=spacing
        self.margins=margins
    def getContentsMargins(self):
        return self.margins
    def count(self):
        return len(self.items)
    def itemAt(self, index):
        return self.items[index]
    def spacing(self):
        return self.space

# Exercise the exact Qt-independent measuring routine from the editor source.
module=ast.parse(SOURCE)
helper=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='_row_minimum_width')
context={}
exec(compile(ast.Module(body=[helper],type_ignores=[]),str(ROOT/'l4visual/ui/canvas.py'),'exec'),context)
row_width=context['_row_minimum_width']

class NestedWidthTests(unittest.TestCase):
    def test_nested_slots_add_all_children_and_margins(self):
        inner=row_width(_Row([24,96,32,135,24]))
        middle=row_width(_Row([24,125,75,inner,78,128,24]))
        outer=row_width(_Row([110,60,middle,88,24]))
        self.assertEqual(inner,8+6+24+96+32+135+24+4*4)
        self.assertEqual(middle,8+6+24+125+75+inner+78+128+24+6*4)
        self.assertGreater(outer,900)

    def test_round_shapes_have_independent_height_guards(self):
        self.assertIn('height=_row_minimum_height(inner)+margin.top()+margin.bottom()', SOURCE)
        self.assertIn('if child.minimumHeight()!=height:child.setMinimumHeight(height)', SOURCE)
        self.assertIn('height=_row_minimum_height(row)+4', SOURCE)
        self.assertIn('if slot.minimumHeight()!=height:slot.setMinimumHeight(height)', SOURCE)

    def test_render_and_reflow_include_nested_shells(self):
        self.assertIn('inner.invalidate()', SOURCE)
        self.assertIn('required=_row_minimum_width(inner)', SOURCE)
        self.assertIn('required=_row_minimum_width(row)', SOURCE)
        self.assertIn('_reflow_expression_widgets(panel)', SOURCE)
        self.assertIn('required_block=max(295, required+18,block_layout.minimumSize().width())', SOURCE)
        self.assertIn('size=_section_required_geometry(panel,panel_layout)', SOURCE)

    def test_input_changes_request_new_layout(self):
        self.assertIn('section.schedule_geometry_update()', SOURCE)
        self.assertIn('self.section.schedule_geometry_update()', SOURCE)

if __name__=='__main__':
    unittest.main()
