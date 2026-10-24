"""Version 26.9: overlapped sections must share the same paint/hit stacking."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf8')
MODULE=ast.parse(SOURCE)


def method(cls, name):
    owner=next(node for node in MODULE.body if isinstance(node,ast.ClassDef) and node.name==cls)
    return next(node for node in owner.body if isinstance(node,ast.FunctionDef) and node.name==name)

class Point:
    def __init__(self,x,y): self.x,self.y=x,y
    def toPoint(self):return self
class Rect:
    def __init__(self,w,h): self.w,self.h=w,h
    def contains(self,p):return 0<=p.x<self.w and 0<=p.y<self.h
class QWidget:
    def __init__(self,parent=None,x=0,y=0,w=600,h=200,visible=True,enabled=True):
        self.parent=parent;self.x=x;self.y=y;self.w=w;self.h=h
        self.visible=visible;self.enabled=enabled;self.children=[]
        if parent is not None:parent.children.append(self)
    def isVisible(self):return self.visible
    def isEnabled(self):return self.enabled
    def rect(self):return Rect(self.w,self.h)
    def parentWidget(self):return self.parent
    def findChildren(self,klass):
        result=[]
        def walk(p):
            for child in p.children:
                if isinstance(child,klass):result.append(child)
                walk(child)
        walk(self)
        return result
    def mapFrom(self,root,point):
        def xy(item):
            x=y=0
            while item:
                x+=item.x;y+=item.y;item=item.parent
            return x,y
        sx,sy=xy(self);rx,ry=xy(root)
        return Point(point.x+rx-sx,point.y+ry-sy)
class QLineEdit(QWidget):pass
class QTextEdit(QWidget):pass
class EmbeddedVariableReference(QWidget):pass

class Section:
    def __init__(self,root,z,x=0,y=0,visible=True):
        self.root=root;self.z=z;self.x=x;self.y=y;self.visible=visible
    def scene(self):return self.board
    def widget(self):return self.root
    def isVisible(self):return self.visible
    def zValue(self):return self.z
    def mapFromScene(self,point):return Point(point.x-self.x,point.y-self.y)
    def boundingRect(self):return self.root.rect()

names={'QWidget':QWidget,'QLineEdit':QLineEdit,'QTextEdit':QTextEdit,
       'EmbeddedVariableReference':EmbeddedVariableReference}
for fn_name in ('_deepest_visible_widget','_precise_control_at'):
    fn=next(node for node in MODULE.body if isinstance(node,ast.FunctionDef) and node.name==fn_name)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'canvas.py','exec'),names)
exec(compile(ast.Module(body=[method('Canvas','_precise_widget_at')],type_ignores=[]),'canvas.py','exec'),names)

class TestOverlappingSections(unittest.TestCase):
    def make_canvas(self,*sections):
        board=SimpleNamespace(items_by_id={str(i):s for i,s in enumerate(sections)})
        for s in sections:s.board=board
        return SimpleNamespace(board=board,mapToScene=lambda p:p)

    def test_front_panel_background_blocks_covered_editor(self):
        lower=QWidget(); editor=QLineEdit(lower,x=70,y=10,w=200,h=40)
        upper=QWidget() # Upper panel has NO child at the clicked point
        back_item=Section(lower,1);front_item=Section(upper,3)
        canvas=self.make_canvas(back_item,front_item)
        root,widget=names['_precise_widget_at'](canvas,Point(90,20))
        self.assertIs(root,upper)
        self.assertIsNone(widget)

    def test_front_editor_receives_click_when_back_has_same_position(self):
        bottom=QWidget();old_editor=QLineEdit(bottom,x=70,y=10,w=200,h=40)
        top=QWidget();new_editor=QLineEdit(top,x=70,y=10,w=200,h=40)
        canvas=self.make_canvas(Section(bottom,1),Section(top,3))
        root,hit=names['_precise_widget_at'](canvas,Point(95,22))
        self.assertIs(root,top)
        self.assertIs(hit,new_editor)
        self.assertIsNot(hit,old_editor)

    def test_equal_z_follows_qt_later_added_stacking_order(self):
        bottom=QWidget();QLineEdit(bottom,x=0,w=100)
        top=QWidget();target=EmbeddedVariableReference(top,x=0,w=100)
        canvas=self.make_canvas(Section(bottom,1),Section(top,1))
        root,hit=names['_precise_widget_at'](canvas,Point(10,10))
        self.assertIs(root,top)
        self.assertIs(hit,target)

    def test_only_bottom_section_hit_outside_front_bounds(self):
        bottom=QWidget();editor=QLineEdit(bottom,x=250,w=100)
        top=QWidget(w=180,h=120)
        canvas=self.make_canvas(Section(bottom,1),Section(top,4))
        root,hit=names['_precise_widget_at'](canvas,Point(260,5))
        self.assertIs(root,bottom)
        self.assertIs(hit,editor)

    def test_project_reload_assigns_distinct_z_values(self):
        source=ast.get_source_segment(SOURCE,method('VisualScene','load'))
        self.assertIn('self._z_counter=20',source)
        self.assertIn('self.raise_item(item)',source)
        self.assertIn('size=_section_required_geometry(panel,panel_layout)',ast.get_source_segment(SOURCE,method('SectionItem','_finish_geometry')))

if __name__=='__main__':unittest.main()
