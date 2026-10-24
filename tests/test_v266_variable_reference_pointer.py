"""Regression: a deeply nested variable reference is draggable even beyond stale parent geometry."""
import ast
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

SRC=(Path(__file__).resolve().parents[1]/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
MODULE=ast.parse(SRC)

def code_for_function(name, parent=MODULE):
    return next(node for node in parent.body if isinstance(node, ast.FunctionDef) and node.name == name)

class P:
    def __init__(self,x,y):self.x=x;self.y=y
class Rect:
    def __init__(self,w,h):self.w=w;self.h=h
    def contains(self,p):return 0<=p.x<self.w and 0<=p.y<self.h
class QWidget:
    def __init__(self,parent=None,x=0,w=100,h=25,visible=True):
        self.parent=parent;self.x=x;self.w=w;self.h=h;self.visible=visible;self.children=[]
        if parent:parent.children.append(self)
    def isVisible(self):return self.visible
    def parentWidget(self):return self.parent
    def rect(self):return Rect(self.w,self.h)
    def findChildren(self,cls):
        result=[]
        def traverse(node):
            for child in node.children:
                if isinstance(child,cls):result.append(child)
                traverse(child)
        traverse(self)
        return result
    def mapFrom(self,root,p):
        def total(node):
            x=0
            while node:
                x+=node.x;node=node.parent
            return x
        return P(p.x+total(root)-total(self),p.y)
class EmbeddedVariableReference(QWidget):pass
class EmbeddedExpressionWidget(QWidget):pass

class TestNestedVariableReference(unittest.TestCase):
    def test_precise_hit_can_reach_variable_reference_beyond_stale_parent(self):
        names={'QWidget':QWidget,'EmbeddedVariableReference':EmbeddedVariableReference}
        fn=code_for_function('_deepest_visible_widget')
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'canvas.py','exec'),names)
        canvas_class=next(node for node in MODULE.body if isinstance(node,ast.ClassDef) and node.name=='Canvas')
        method=code_for_function('_variable_reference_at_viewport',canvas_class)
        exec(compile(ast.Module(body=[method],type_ignores=[]),'canvas.py','exec'),names)
        root=QWidget(w=1500)
        stale=QWidget(root,x=20,w=120)
        outer=EmbeddedExpressionWidget(stale,x=10,w=1100)
        math_min=EmbeddedExpressionWidget(outer,x=480,w=460)
        socket=QWidget(math_min,x=45,w=160)
        origin=EmbeddedVariableReference(socket,x=3,w=115)
        # Deliberately outside stale parent's 120px width.
        point=P(20+10+480+45+3+40,5)
        self.assertGreater(point.x,stale.x+stale.w)
        self.assertIs(names['_deepest_visible_widget'](root,point),origin)
        obj=SimpleNamespace(_precise_widget_at=lambda pos:(root,names['_deepest_visible_widget'](root,pos)))
        self.assertIs(names['_variable_reference_at_viewport'](obj,point),origin)
    def test_drag_payload_is_a_copyable_variable_reference(self):
        var_class=next(n for n in MODULE.body if isinstance(n,ast.ClassDef) and n.name=='EmbeddedVariableReference')
        start=code_for_function('start_reference_drag',var_class)
        class Mime:
            def __init__(self):self.values={}
            def setData(self,mime,data):self.values[mime]=data
        class Drag:
            current=None
            def __init__(self,widget):self.widget=widget;self.mime=None;self.action=None;Drag.current=self
            def setMimeData(self,data):self.mime=data
            def exec(self,action):self.action=action
        names={'QMimeData':Mime,'QDrag':Drag,'MIME_EXPR':'application/x-l4dv-variable',
               'Qt':SimpleNamespace(CopyAction=100),'json':json,'reference_root':lambda doc,ref:(None,None)}
        exec(compile(ast.Module(body=[start],type_ignores=[]),'canvas.py','exec'),names)
        scene=SimpleNamespace(owner_document=None,document=None)
        widget=SimpleNamespace(reference={'name':'origin_value','symbol_id':'value42',
                                          'section_id':'s1','path':None,'scope':'local'},
                               socket=SimpleNamespace(owner=SimpleNamespace(root_section=SimpleNamespace(scene=lambda:scene))))
        names['start_reference_drag'](widget)
        self.assertEqual(Drag.current.action,100)
        self.assertIs(Drag.current.widget,widget)
        data=json.loads(Drag.current.mime.values['application/x-l4dv-variable'].decode())
        self.assertEqual(data['name'],'origin_value')
        self.assertEqual(data['id'],'value42')
        self.assertEqual(data['scope'],'local')
    def test_viewport_routes_token_before_outer_expression(self):
        canvas=SRC[SRC.index('class Canvas(QGraphicsView):'):]
        self.assertLess(canvas.index('token=self._variable_reference_at_viewport(event.pos())'),
                        canvas.index('shell,hit=self._expression_at_viewport(event.pos())'))
        self.assertLess(canvas.index('token=self._variable_reference_at_viewport(event.position())'),
                        canvas.index('shell=self._nested_press_target(event.position())'))
        self.assertIn('token.start_reference_drag()',canvas)
        self.assertIn('token.show_reference_menu(self.viewport().mapToGlobal(event.pos()))',canvas)
        self.assertIn('self._variable_press=None;self._variable_press_point=None',canvas)
        var_section=SRC[SRC.index('class EmbeddedVariableReference('):SRC.index('class EmbeddedExpressionDragHandle(')]
        self.assertIn("self.socket.replace('null')",var_section)
        self.assertIn("translated_text('复制变量引用')",var_section)
        self.assertIn("translated_text('Delete')",var_section)

if __name__=='__main__':unittest.main()
