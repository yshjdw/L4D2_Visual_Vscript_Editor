"""Regression for 26.7: Qt editors at the right edge of long nested blocks."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf8')
MODULE=ast.parse(SOURCE)

class Point:
    def __init__(self,x,y=5):self.x,self.y=x,y
    def toPoint(self):return self
class Rect:
    def __init__(self,w,h):self.w,self.h=w,h
    def contains(self,p):return 0<=p.x<self.w and 0<=p.y<self.h
class QWidget:
    def __init__(self,parent=None,x=0,w=100,h=25,visible=True,enabled=True):
        self.parent=parent;self.x=x;self.w=w;self.h=h;self.visible=visible;self.enabled=enabled;self.children=[]
        if parent is not None:parent.children.append(self)
    def isVisible(self):return self.visible
    def isEnabled(self):return self.enabled
    def rect(self):return Rect(self.w,self.h)
    def parentWidget(self):return self.parent
    def findChildren(self,kind):
        result=[]
        def walk(node):
            for c in node.children:
                if isinstance(c,kind):result.append(c)
                walk(c)
        walk(self)
        return result
    def mapFrom(self,root,pos):
        def total(child):
            x=0
            while child:x+=child.x;child=child.parent
            return x
        return Point(pos.x+total(root)-total(self),pos.y)
class QLabel(QWidget):pass
class QLineEdit(QWidget):pass
class QTextEdit(QWidget):pass
class EmbeddedVariableReference(QWidget):pass


def get_function(name,parent=MODULE):
    return next(n for n in parent.body if isinstance(n,ast.FunctionDef) and n.name==name)

class TestRightEdgeControls(unittest.TestCase):
    def test_text_field_and_variable_accessible_outside_parent(self):
        names={'QWidget':QWidget,'QLineEdit':QLineEdit,'QTextEdit':QTextEdit,
               'EmbeddedVariableReference':EmbeddedVariableReference}
        fn=get_function('_precise_control_at')
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'canvas.py','exec'),names)
        root=QWidget(w=1800)
        stale=QWidget(root,x=20,w=150)
        expression=QWidget(stale,x=30,w=1350)
        math_min=QWidget(expression,x=600,w=650)
        variable=EmbeddedVariableReference(math_min,x=45,w=110)
        convar=QWidget(math_min,x=190,w=380)
        editor=QLineEdit(convar,x=30,w=250)
        # QLabel can have a stale overlapping rectangle and be deeper in the
        # QObject tree. It must not steal the control's explicit hit test.
        overlay=QWidget(editor,x=0,w=250)
        fake_text=QLabel(overlay,x=0,w=250)
        pvar=Point(20+30+600+45+10)
        pedit=Point(20+30+600+190+30+20)
        self.assertGreater(pvar.x,stale.x+stale.w)
        self.assertIs(names['_precise_control_at'](root,pvar,(QLineEdit,QTextEdit,EmbeddedVariableReference)),variable)
        self.assertIs(names['_precise_control_at'](root,pedit,(QLineEdit,QTextEdit,EmbeddedVariableReference)),editor)
        editor.enabled=False
        self.assertIsNone(names['_precise_control_at'](root,pedit,(QLineEdit,QTextEdit,EmbeddedVariableReference)))

    def test_canvas_text_control_resolution_and_forwarding_contract(self):
        canvas=next(n for n in MODULE.body if isinstance(n,ast.ClassDef) and n.name=='Canvas')
        method=get_function('_text_editor_at_viewport',canvas)
        names={'QLineEdit':QLineEdit,'QTextEdit':QTextEdit}
        exec(compile(ast.Module(body=[method],type_ignores=[]),'canvas.py','exec'),names)
        root=QWidget(w=1200)
        stale=QWidget(root,x=20,w=120)
        editor=QLineEdit(stale,x=560,w=150)
        dummy=SimpleNamespace(_precise_widget_at=lambda pos:(root,editor))
        self.assertIs(names['_text_editor_at_viewport'](dummy,Point(600)),editor)
        self.assertIn('QApplication.sendEvent(widget,routed)',SOURCE)
        self.assertIn('widget.setFocus(Qt.MouseFocusReason)',SOURCE)
        self.assertIn('self.board.setFocusItem(item,Qt.MouseFocusReason)',SOURCE)
        self.assertIn('self._text_mouse_target=editor',SOURCE)
        self.assertIn('self._forward_text_context(editor,event)',SOURCE)
        self.assertIn('return self._forward_text_mouse(editor,event)',SOURCE)
        self.assertIn('self._text_mouse_target=None',SOURCE)
        # No changes to 26.4's non-feedback section sizing.
        geometry=SOURCE[SOURCE.index('    def _finish_geometry(self):'):SOURCE.index('    def refresh(self):',SOURCE.index('class SectionItem'))]
        self.assertIn('_section_required_geometry(panel,panel_layout)',geometry)
        self.assertNotIn('mapTo(',geometry)

if __name__=='__main__':unittest.main()
