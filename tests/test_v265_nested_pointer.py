"""Regression for deep pointer hit-testing when Qt parent geometry is stale."""
import ast
import unittest
from pathlib import Path

SOURCE=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf8')
MODULE=ast.parse(SOURCE)

class Point:
    def __init__(self,x,y):self.x,self.y=x,y
class Rect:
    def __init__(self,w,h):self.w,self.h=w,h
    def contains(self,p):return 0 <= p.x < self.w and 0 <= p.y < self.h
class QWidget:
    def __init__(self,parent=None,x=0,y=0,w=100,h=25,visible=True):
        self.parent=parent;self.x=x;self.y=y;self.w=w;self.h=h;self.visible=visible
        if parent is not None:parent.children.append(self)
        self.children=[]
    def isVisible(self):return self.visible
    def parentWidget(self):return self.parent
    def rect(self):return Rect(self.w,self.h)
    def findChildren(self,kind):
        out=[]
        def collect(parent):
            for child in parent.children:
                if isinstance(child,kind):out.append(child)
                collect(child)
        collect(self)
        return out
    def mapFrom(self,root,p):
        def position(obj):
            x=y=0
            while obj is not None:
                x+=obj.x;y+=obj.y
                obj=obj.parent
            return x,y
        rx,ry=position(root);sx,sy=position(self)
        return Point(p.x+rx-sx,p.y+ry-sy)
class EmbeddedExpressionWidget(QWidget):pass

namespace={'QWidget':QWidget,'EmbeddedExpressionWidget':EmbeddedExpressionWidget}
for name in ('_deepest_visible_widget','_nearest_embedded_expression'):
    fn=next(node for node in MODULE.body if isinstance(node,ast.FunctionDef) and node.name==name)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'canvas.py','exec'),namespace)

class TestDeepHit(unittest.TestCase):
    def test_detect_min_beyond_old_parent_rect(self):
        root=QWidget(w=1000,h=150)
        stale_parent=QWidget(root,x=20,w=160,h=100)
        outer=EmbeddedExpressionWidget(stale_parent,x=35,w=680,h=65)
        inner=EmbeddedExpressionWidget(outer,x=410,w=240,h=42)
        grip=QWidget(inner,x=5,w=20)
        point=Point(20+35+410+8,5)
        hit=namespace['_deepest_visible_widget'](root,point)
        self.assertIs(hit,grip)
        self.assertIs(namespace['_nearest_embedded_expression'](hit,root),inner)
        self.assertGreater(point.x,stale_parent.x+stale_parent.w)
    def test_rightmost_min_and_convar_separate(self):
        root=QWidget(w=1400,h=150)
        outer=EmbeddedExpressionWidget(root,x=10,w=1100,h=40)
        minimum=EmbeddedExpressionWidget(outer,x=550,w=480,h=40)
        getter=EmbeddedExpressionWidget(minimum,x=220,w=245,h=40)
        hit=namespace['_deepest_visible_widget'](root,Point(10+550+250,5))
        self.assertIs(namespace['_nearest_embedded_expression'](hit,root),getter)
        hit=namespace['_deepest_visible_widget'](root,Point(10+550+40,5))
        self.assertIs(namespace['_nearest_embedded_expression'](hit,root),minimum)
    def test_hidden_children_do_not_capture(self):
        root=QWidget(w=500,h=100)
        shown=EmbeddedExpressionWidget(root,x=20,w=220,h=40)
        QWidget(shown,x=3,w=40,visible=False)
        hit=namespace['_deepest_visible_widget'](root,Point(25,3))
        self.assertIs(hit,shown)
    def test_mouse_routing_and_drop_use_shared_hit(self):
        canvas=SOURCE[SOURCE.index('class Canvas(QGraphicsView):'):]
        self.assertIn('def _precise_widget_at(',canvas)
        self.assertIn('def _expression_at_viewport(',canvas)
        self.assertIn('root,hit=self._precise_widget_at(viewport_pos)',canvas)
        self.assertIn('event.type()==QEvent.ContextMenu',canvas)
        self.assertIn('shell.show_menu(event.globalPos())',canvas)
        self.assertIn('direct.start_expression_drag()',canvas)
        self.assertIn('self._nested_press_point',canvas)
    def test_no_recursive_section_size_feedback(self):
        geometry=SOURCE[SOURCE.index('    def _finish_geometry(self):'):SOURCE.index('    def refresh(self):',SOURCE.index('class SectionItem'))]
        self.assertNotIn('mapTo(',geometry)
        self.assertIn('_section_required_geometry(panel,panel_layout)',geometry)

if __name__=='__main__':unittest.main()
