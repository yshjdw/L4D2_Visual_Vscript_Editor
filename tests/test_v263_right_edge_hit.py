"""Regression: a wide section must be clickable without recursive size inflation."""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')

class Dim:
    def __init__(self,width,height=1):self.w,self.h=width,height
    def width(self):return self.w
    def height(self):return self.h

class Child:
    def __init__(self,x=0,width=400):self.x,self.w=x,width
    def minimumWidth(self):return 0
    def width(self):return self.w

class Panel:
    def __init__(self,children,width=490):self.children,self.w=children,width
    def width(self):return self.w
    def findChildren(self,cls):return self.children

class Layout:
    def __init__(self,width=490,height=120):self.w,self.h=width,height
    def minimumSize(self):return Dim(self.w,self.h)

code=ast.parse(SOURCE)
fn=next(node for node in code.body if isinstance(node,ast.FunctionDef) and node.name=='_section_required_geometry')
ns={'QSize':Dim}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(ROOT/'l4visual/ui/canvas.py'),'exec'),ns)
size=ns['_section_required_geometry']

class SectionGeometryRegressionTests(unittest.TestCase):
    def test_real_nested_width_is_preserved(self):
        # The bottom-up block measurement has propagated intrinsic width.
        panel=Panel([Child(400,2400)],width=490)
        measured=size(panel,Layout(2780,325))
        self.assertEqual((measured.width(),measured.height()),(2780,325))

    def test_stretched_child_geometry_cannot_create_feedback(self):
        # An expanding label near the right edge used to grow the section
        # by its margins on every update (even with no model changes).
        panel=Panel([Child(25,7000)],width=7025)
        layout=Layout(490,130)
        measured=size(panel,layout)
        self.assertEqual(measured.width(),490)
        self.assertEqual(size(panel,layout).width(),490)

    def test_previous_proxy_size_does_not_prevent_shrink(self):
        panel=Panel([],width=99000)
        self.assertEqual(size(panel,Layout(620,170)).width(),620)
        section=SOURCE[SOURCE.index('    def _finish_geometry(self):',SOURCE.index('class SectionItem(')):SOURCE.index('    def refresh(self):',SOURCE.index('class SectionItem('))]
        self.assertIn('panel.setMinimumSize(490,0)',section)
        self.assertIn('self.resize(width,height)',section)
        self.assertIn('panel.resize(width,height)',section)
        self.assertNotIn('width=max(size.width(),int(self.size().width()))',section)
        self.assertNotIn('height=max(size.height(),int(self.size().height()))',section)
        self.assertIn('scene.recalculate_bounds()',section)

    def test_measurement_stays_stable_for_repeated_large_sections(self):
        for width in (490,620,2100,6000):
            panel=Panel([Child(12,width)],width=width)
            layout=Layout(width,180)
            result=size(panel,layout)
            for i in range(100):
                result=size(panel,layout)
            self.assertEqual(result.width(),width)

if __name__=='__main__':unittest.main()
