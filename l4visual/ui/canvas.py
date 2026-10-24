from __future__ import annotations
import json
from copy import deepcopy
from PySide6.QtCore import Qt, Signal, QMimeData, QPointF, QPoint, QEvent, QTimer, QSize, QSizeF, QRect, QRectF
from PySide6.QtGui import QColor, QPainter, QDrag, QFont, QPainterPath, QPen, QCursor, QMouseEvent, QContextMenuEvent
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QGraphicsItem, QGraphicsPathItem,
    QWidget, QFrame, QLabel, QLineEdit, QComboBox, QTextEdit, QHBoxLayout, QVBoxLayout,
    QPushButton, QMenu, QInputDialog, QMessageBox, QScrollArea, QDialog, QSlider, QToolButton, QApplication, QLayout, QSizePolicy)
from .dialogs import BLOCK_NAMES, DEFAULT_ARGS, new_block, new_block_payload, SectionEditor
from ..display_profile import current_profile, block_caption, method_caption, event_caption, parameter_caption, field_caption, method_field_order
from ..flow_geometry import plan_flow
from ..scene_geometry import MIN_SCENE, content_scene_rect, include_rect
from ..raw_editor_geometry import raw_editor_height
from ..models import clone_block, Block
from ..complex_copy import clone_with_definitions
from ..expressions import block_from_method, can_embed, as_embedded, is_embedded, unpack_embedded, embedded_ids, is_boolean_return, repair_documented_method_parameters
from ..symbols import rename_references
from ..data_definitions import DATA_BLOCKS, container_kind, create_definition, synchronize_symbol
from ..variable_types import change_variable_type
from ..variable_paths import reference_for_symbol
from ..reference_members import reference_root
from ..array_ops import ARRAY_OPERATIONS, change_array_operation
from ..event_metadata import event_tip
from ..netprop_method import property_parameter_index, selected_property, set_selected_property, repair_saved_netprop_selection
from ..scope_visibility import visible_local, resolve_socket_statement
from ..entity_search import ENTITY_SEARCH_MODES, ENTITY_FIELD_LABELS, search_fields, normalize_entity_search
from .localization import localize_widget_tree, translated_text

MIME_BLOCK = 'application/x-l4dv-block'
MIME_EXPR = 'application/x-l4dv-variable'
MIME_MOVE = 'application/x-l4dv-existing-block'
MIME_METHOD = 'application/x-l4dv-official-method'
MIME_EVENT = 'application/x-l4dv-official-event'
MIME_FUNCTION_CALL = 'application/x-l4dv-user-function-call'
MIME_EMBEDDED_COPY = 'application/x-l4dv-embedded-copy'
MIME_EMBEDDED_MOVE = 'application/x-l4dv-embedded-move'
MIME_SCOPE_MEMBER = 'application/x-l4dv-scope-member'
from .file_drop import MIME_PROJECT_FILE, project_drag_payload
from ..block_reorder import accepts_block, move_block, remove_block, locate_block, remove_wrapper_preserve_children
COLORS = {'var':'#aa7430','assign':'#aa7430','member':'#aa7430','method':'#367c64',
 'call':'#326d9a','string_call':'#367d93','netprop':'#426a8a','event':'#ab6840','if':'#ab792a','while':'#ab792a',
 'for':'#ab792a','entity_for':'#ab792a','foreach':'#ab792a','try':'#90639b','return':'#6a57a8',
 'break':'#985938','continue':'#985938','throw':'#985938','raw':'#596173','expr':'#6a57a8','array_op':'#367c64','summon':'#3d7d84','zspawn':'#3d7d84','trace_line':'#3d7d84','operator':'#5b86a9','math_call':'#528fa4','rawin':'#34847d','utility':'#528fa4'}
BRANCH_NAMES = {'body':'执行','else':'否则','catch':'捕获'}

DISPLAY = {'target':'对象/目标','value':'值','condition':'条件','source':'集合/range','variable':'变量',
 'function':'函数','method':'方法','event':'事件','env':'env','property':'属性','filter':'实体名称',
 'search':'查找','output':'结果变量','name':'变量','container_type':'类型','mode':'模式','error':'异常变量',
 'infected_type':'感染者种类','pos':'生成位置 Vector', 'origin':'中心 Vector','radius':'半径 u','assignment':'赋值方式','left':'左值','right':'右值','operator':'运算符','key':'索引 / 键名（可选）','index':'索引','prop_type':'属性类型','table':'SendTable','owner':'所属类','scope':'作用域'}
FIELD_ORDER = {
 'var':['name','container_type','value','scope'], 'assign':['target','assignment','value'], 'member':['target','assignment','value'],
 'call':['function','parameters','output'],'string_call':['function','parameters'],'array_op':['target','operation','parameters','output'],'method':['target','method','parameters','output'],
 'netprop':['mode','target','property','prop_type','value','output','index'],
 'if':['condition'],'while':['condition'],'for':['variable','source'],
 'foreach':['variable','key','source'],'entity_for':['variable','search','filter','origin','radius'],
 'event':['event','env'],'try':['error'],'return':['value'],'throw':['value'],
 'raw':['source'],'expr':['value'],'utility':['operation','value','parameters'],'summon':['classname','output'],'zspawn':['infected_type','pos'],'trace_line':['start','end','ignore','mask','output'],
 'operator':['left','operator','right'],'math_call':['function','parameters'],'rawin':['target','key']}

class WrappingFields(QLayout):
    """Keep full sockets visible; wrap the next control instead of shrinking it."""
    def __init__(self, parent=None, spacing=5):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def addStretch(self, stretch=0):
        # A trailing stretch has no meaning in a wrapping field layout.
        pass

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._layout(QRect(0, 0, max(1,width),0),False)

    def _size(self, item):
        return item.sizeHint().expandedTo(item.minimumSize())

    def _layout(self, rect, place):
        left,top,right,bottom=self.getContentsMargins()
        usable=max(1,rect.width()-left-right)
        present=[item for item in self._items if not item.isEmpty()]
        sizes=[(self._size(item).width(),self._size(item).height()) for item in present]
        content_height,rectangles=plan_flow(sizes,usable,self.spacing())
        if place:
            for item,(x,y,w,h) in zip(present,rectangles):
                item.setGeometry(QRect(rect.x()+left+x,rect.y()+top+y,w,h))
        return top+content_height+bottom

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._layout(rect, True)

    def minimumSize(self):
        margins=self.getContentsMargins()
        width=max((self._size(item).width() for item in self._items if not item.isEmpty()),default=0)
        # The width is a single whole control, NOT the sum of all controls.
        # Height is computed separately from the parent widget's real width.
        return QSize(width+margins[0]+margins[2],38+margins[1]+margins[3])

    def sizeHint(self):
        width = max(520, self.minimumSize().width())
        width = max(self.minimumSize().width(), min(width, 960))
        return QSize(width, self.heightForWidth(width))


def _row_minimum_width(layout):
    """Measure one unwrapped Qt row from its actual child widgets.

    Qt's cached QWidgetItem size hints can be smaller than a just-created
    embedded expression. Use every child's declared minimum and preferred
    width, not the old allocated width of its parent proxy widget.
    """
    left, top, right, bottom = layout.getContentsMargins()
    widths=[]
    for index in range(layout.count()):
        item=layout.itemAt(index)
        if item is None:
            continue
        child=item.widget()
        if child is not None:
            width=max(child.minimumWidth(), child.minimumSizeHint().width(),
                      child.sizeHint().width(), item.minimumSize().width(),
                      item.sizeHint().width())
        elif item.layout() is not None:
            width=max(item.layout().minimumSize().width(), item.layout().sizeHint().width())
        else:
            width=max(item.minimumSize().width(), item.sizeHint().width())
        widths.append(max(0,width))
    return left+right+sum(widths)+max(0,len(widths)-1)*max(0,layout.spacing())


def _row_minimum_height(layout):
    """Minimum height of an unwrapped expression, including nested controls."""
    left,top,right,bottom=layout.getContentsMargins()
    height=0
    for i in range(layout.count()):
        item=layout.itemAt(i)
        if item is None:continue
        child=item.widget()
        if child is not None:
            extent=max(child.minimumHeight(),child.minimumSizeHint().height(),
                       child.sizeHint().height(),item.minimumSize().height(),
                       item.sizeHint().height())
        elif item.layout() is not None:
            extent=max(item.layout().minimumSize().height(),item.layout().sizeHint().height())
        else:
            extent=max(item.minimumSize().height(),item.sizeHint().height())
        height=max(height,extent)
    return top+bottom+height


def _reflow_expression_widgets(panel):
    """Expand each shell/slot from the deepest nested expression outward.

    The entire row (including its final close/delete control) is indivisible.
    A string_call nested inside DoEntFire must never be sized to the old
    QGraphicsProxyWidget width and then clip its descendants.
    """
    slots=panel.findChildren(ExpressionSlot)
    def nesting(slot):
        depth=0
        parent=slot.parentWidget()
        while parent is not None:
            if isinstance(parent,ExpressionSlot):depth+=1
            parent=parent.parentWidget()
        return depth
    for slot in sorted(slots,key=nesting,reverse=True):
        row=slot.layout()
        if row is None:continue
        for i in range(row.count()):
            item=row.itemAt(i)
            child=item.widget() if item is not None else None
            if isinstance(child,EmbeddedExpressionWidget):
                inner=child.layout()
                inner.invalidate()
                margin=child.contentsMargins()
                required=_row_minimum_width(inner)+margin.left()+margin.right()
                height=_row_minimum_height(inner)+margin.top()+margin.bottom()
                if child.minimumWidth()!=required:child.setMinimumWidth(required)
                if child.minimumHeight()!=height:child.setMinimumHeight(height)
                child.updateGeometry()
        row.invalidate()
        # Four pixels protect the 2px socket border around nested rounded
        # shells; without this the last pixels can be painted outside the slot.
        required=_row_minimum_width(row)+4
        height=_row_minimum_height(row)+4
        if slot.minimumWidth()!=required:slot.setMinimumWidth(required)
        if slot.minimumHeight()!=height:slot.setMinimumHeight(height)
        slot.updateGeometry()

def _section_required_geometry(panel, layout):
    """Intrinsic section extent, independent of previously allocated geometry.

    An expanded heading/block is laid out to fill its parent. Mapping its
    *allocated* far edge back to the section and adding margins again creates
    a positive feedback loop (one resize makes the next resize even larger).
    Bottom-up socket and BlockWidget measurement already propagates intrinsic
    minimum widths to the section layout; that is the sole width authority.
    """
    minimum=layout.minimumSize()
    return QSize(max(490,minimum.width()),max(1,minimum.height()))



def _deepest_visible_widget(root, point):
    """Return the deepest visible child at a root-local position.

    QWidget.childAt() stops descending when an intermediate layout still has
    an outdated rectangle.  Expression sockets can be painted further right
    than that rectangle after an asynchronous QGraphicsProxyWidget relayout.
    Resolve every descendant in the common root coordinate system instead;
    this deliberately does not depend on any intermediate widget's bounds.
    """
    best=None
    best_depth=-1
    for widget in root.findChildren(QWidget):
        if not widget.isVisible():
            continue
        local=widget.mapFrom(root,point)
        if not widget.rect().contains(local):
            continue
        depth=0
        parent=widget.parentWidget()
        while parent is not None:
            depth+=1
            if parent is root:
                break
            parent=parent.parentWidget()
        if depth>best_depth or depth==best_depth:
            best=widget
            best_depth=depth
    return best


def _precise_control_at(root,point,types):
    """Hit interactive descendants without trusting a stale ancestor rectangle.

    A very wide expression may be rendered outside a parent widget's obsolete
    geometry; QWidget.childAt and QGraphicsProxyWidget mouse dispatch cannot
    reach the visible editor/reference in that case. Evaluate each candidate
    in root-local coordinates, independently of intermediate container bounds.
    """
    best=None
    best_depth=-1
    for widget in root.findChildren(QWidget):
        if not isinstance(widget,types) or not widget.isVisible() or not widget.isEnabled():
            continue
        if not widget.rect().contains(widget.mapFrom(root,point)):
            continue
        depth=0
        parent=widget.parentWidget()
        while parent is not None:
            depth+=1
            if parent is root:break
            parent=parent.parentWidget()
        if depth>=best_depth:
            best=widget;best_depth=depth
    return best


def _local_pointer_pos(target, canvas, position):
    """Resolve the mouse point using scene-to-proxy coordinates.

    A QGraphicsProxyWidget's nested QLineEdit does not share ordinary desktop
    widget geometry with the viewport.  mapFromGlobal() can map every click to
    outside the text field, making QLineEdit place the caret at the end.
    """
    scene_position = canvas.mapToScene(position.toPoint() if hasattr(position, 'toPoint') else position)
    for section in canvas.board.items_by_id.values():
        root = section.widget()
        if root is None or (target is not root and not root.isAncestorOf(target)):
            continue
        root_point = section.mapFromScene(scene_position).toPoint()
        return target.mapFrom(root, root_point)
    return target.mapFromGlobal(canvas.viewport().mapToGlobal(position.toPoint()))


def _nearest_embedded_expression(widget, root):
    """Find the precise innermost expression owning a hit QWidget."""
    while widget is not None and widget is not root:
        if isinstance(widget, EmbeddedExpressionWidget):
            return widget
        widget=widget.parentWidget()
    return None


class VariableToken(QLabel):
    def __init__(self,section,block,key,changed):
        super().__init__('● '+str(block.args.get(key,'')))
        self.section=section;self.block=block;self.key=key;self.changed=changed
        self.reference_path=None
        self.setStyleSheet('QLabel{background:#e9c17b;color:#4b3115;border-radius:13px;padding:5px 9px;font-weight:bold;}')
        self.setToolTip('左键拖出变量引用；右键可以修改名称或选择 Table / Set 成员')
    def rename_variable(self):
        text,ok=QInputDialog.getText(None,'重命名变量','名称',text=str(self.block.args.get(self.key,'')))
        if not ok or text==self.block.args.get(self.key,''):
            return
        from ..codegen import IDENT
        if not IDENT.fullmatch(text):
            QMessageBox.warning(None,'名称非法','请输入合法的 Squirrel 标识符')
            return
        self.block.args[self.key]=text
        self.reference_path=None
        sc=self.section.scene()
        if sc and getattr(sc,'document',None):
            owner=getattr(sc,'owner_document',None) or sc.document
            rename_references(owner,self.block.id,text)
            synchronize_symbol(owner,self.block.id,text)
        self.setText('● '+text)
        self.changed()

    def mouseDoubleClickEvent(self,event):
        if event.button()==Qt.LeftButton:
            self.rename_variable()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self,event):
        if event.button()==Qt.RightButton:
            menu=QMenu(None)
            rename=menu.addAction('重命名变量')
            copy=menu.addAction('复制变量引用')
            standalone=menu.addAction('仅执行方法，不生成结果变量') if self.key=='output' else None
            open_workspace=None
            pick_member=menu.addAction('选择成员变量…') if (self.block.kind=='event' and self.key=='env') or (self.block.kind=='var' and container_kind(self.block)) else None
            if container_kind(self.block):
                menu.addSeparator()
                open_workspace=menu.addAction('打开独立复杂变量工作区')
            chosen=menu.exec(QCursor.pos())
            if chosen==rename:
                self.rename_variable()
            elif chosen==copy:
                QApplication.clipboard().setText(str(self.block.args.get(self.key,'')))
            elif chosen==standalone and standalone is not None:
                self.block.args[self.key]=''
                self.changed()
                self.section.refresh()
            elif chosen==pick_member and pick_member is not None:
                from .member_picker import MemberPicker
                scene=self.section.scene()
                document=(getattr(scene,'owner_document',None) or getattr(scene,'document',None)) if scene else None
                base=(reference_for_symbol(document,self.block.id) if self.block.kind=='var' else None) or str(self.block.args.get(self.key,''))
                picker=MemberPicker(document,self.block,base,selected_path=self.reference_path)
                if picker.exec() and picker.value:
                    # A member selection changes this draggable reference only.
                    # It must NOT rename the source declaration.
                    self.reference_path=picker.value
                    self.setText('● '+picker.value)
            elif chosen==open_workspace:
                owner=self.parentWidget()
                while owner is not None and not isinstance(owner,BlockWidget):
                    owner=owner.parentWidget()
                if owner is not None:owner.open_definition()
            event.accept()
            return
        if event.button()==Qt.LeftButton:
            payload={'name':self.block.args.get(self.key,''),'id':self.block.id,'scope':('local' if self.block.args.get('scope','auto')=='auto' and self.section.model.kind in ('function','think','events') else self.block.args.get('scope','auto')) if self.block.kind=='var' else 'local' if self.key=='env' else 'auto','section_id':self.section.model.id,'path':self.reference_path}
            drag=QDrag(self);mime=QMimeData();mime.setData(MIME_EXPR,json.dumps(payload).encode());drag.setMimeData(mime)
            drag.exec(Qt.CopyAction);event.accept();return
        super().mousePressEvent(event)

class EmbeddedVariableReference(QLabel):
    """A live reference token, not a passive label: edit nested members in place."""
    def __init__(self, socket, reference):
        super().__init__('● '+str(reference.get('path') or reference.get('name') or 'null'))
        self.socket=socket
        self.reference=reference
        self.setObjectName('variableReference')
        self.setStyleSheet('QLabel#variableReference{background:#e9c17b;color:#4b3115;border-radius:12px;padding:5px 9px;font-weight:bold;}')
        self.setToolTip('拖动以复制引用；Table、Array 和事件 env 可以右键选择成员。普通变量不支持成员访问。')
        try:
            from ..official_docs import event_field_help
            scene=socket.owner.root_section.scene()
            document=(getattr(scene,'owner_document',None) or getattr(scene,'document',None)) if scene else None
            source,_=reference_root(document,reference)
            if source is not None and source.kind=='event':
                full=str(reference.get('path') or '')
                field=full.split('.',1)[1].split('.',1)[0] if '.' in full else ''
                if field:self.setToolTip(event_field_help(source.args.get('event',''),field))
        except (AttributeError,TypeError,ValueError):
            pass
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._drag_origin=None
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._drag_origin=event.position()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        if self._drag_origin is None or not (event.buttons() & Qt.LeftButton):
            return super().mouseMoveEvent(event)
        if (event.position()-self._drag_origin).manhattanLength()<QApplication.startDragDistance():
            return
        self._drag_origin=None
        self.start_reference_drag()
        event.accept()

    def start_reference_drag(self):
        """Use the same variable-reference MIME for native and canvas-routed drags."""
        mime=QMimeData()
        payload={"name":self.reference.get("name", ""),
                 "id":self.reference.get("symbol_id"),
                 "section_id":self.reference.get("section_id"),
                 "path":self.reference.get("path"),
                 "scope":self.reference.get("scope", "auto")}
        # A reference already in a socket is copied, never removed.
        document=getattr(self.socket.owner.root_section.scene(), "owner_document", None)
        if document is None:
            document=getattr(self.socket.owner.root_section.scene(), "document", None)
        if payload["id"] and document:
            source,_=reference_root(document,self.reference)
            if source is not None and source.kind=="event":payload["scope"]="local"
            elif source is not None and source.kind=="var":
                payload["scope"]=source.args.get("scope", "auto")
                if payload["scope"]=="auto" and self.socket.owner.root_section.model.kind in ("events","function","think"):
                    payload["scope"]="local"
        mime.setData(MIME_EXPR,json.dumps(payload,ensure_ascii=False).encode("utf-8"))
        drag=QDrag(self);drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

    def mouseReleaseEvent(self,event):
        self._drag_origin=None
        super().mouseReleaseEvent(event)

    def open_members(self):
        from .member_picker import MemberPicker
        from ..data_definitions import container_kind
        scene=self.socket.owner.root_section.scene()
        document=(getattr(scene,'owner_document',None) or getattr(scene,'document',None)) if scene else None
        source,root=reference_root(document,self.reference)
        if source is None:
            QMessageBox.information(self,'引用已失效','找不到原始变量声明，可能已经被删除。')
            return
        if source.kind!='event' and not container_kind(source):
            QMessageBox.information(self,'普通变量','该变量不是 Table / Set，没有已登记的成员。')
            return
        picker=MemberPicker(document,source,root,selected_path=self.reference.get('path'))
        if picker.exec() and picker.value is not None:
            updated=dict(self.reference)
            updated['path']=picker.value
            self.socket.replace(updated)

    def show_reference_menu(self,global_pos=None):
        scene=self.socket.owner.root_section.scene()
        doc=(getattr(scene,'owner_document',None) or getattr(scene,'document',None)) if scene else None
        source,_=reference_root(doc,self.reference)
        # This token lives inside a QGraphicsProxyWidget.  A child QMenu
        # can inherit the proxy's transformed coordinate space and open away
        # from the actual click.  Use a top-level popup and a screen point.
        menu=QMenu(None)
        copy=menu.addAction(translated_text('复制变量引用'))
        choose=(menu.addAction(translated_text('选择成员变量 / 返回根变量…'))
                if source is not None and (source.kind=='event' or container_kind(source)) else None)
        menu.addSeparator()
        delete=menu.addAction(translated_text('Delete'))
        chosen=menu.exec(QCursor.pos() if global_pos is None else global_pos)
        if chosen==copy:
            QApplication.clipboard().setText(str(self.reference.get('path') or self.reference.get('name') or ''))
        elif choose is not None and chosen==choose:
            self.open_members()
        elif chosen==delete:
            self.socket.replace('null')

    def contextMenuEvent(self,event):
        # QGraphicsProxyWidget may synthesize globalPos in the wrong
        # coordinate system; the hardware cursor is always screen-global.
        self.show_reference_menu(QCursor.pos())
        event.accept()

    def mouseDoubleClickEvent(self,event):
        if event.button()==Qt.LeftButton:
            scene=self.socket.owner.root_section.scene()
            doc=(getattr(scene,'owner_document',None) or getattr(scene,'document',None)) if scene else None
            source,_=reference_root(doc,self.reference)
            if source is not None and (source.kind=='event' or container_kind(source)):
                self.open_members()
                event.accept()
                return
        super().mouseDoubleClickEvent(event)


class EmbeddedExpressionDragHandle(QLabel):
    """Copies an already embedded oval/hexagonal expression without moving its source."""
    def __init__(self, socket):
        super().__init__('⠿')
        self.socket=socket
        self._drag_origin=None
        self.setToolTip('拖动复制已嵌入的表达式；原位置保持不变')
        self.setCursor(Qt.OpenHandCursor)
        self.setStyleSheet('color:white;font-size:16px;font-weight:bold;')

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._drag_origin=event.position()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        if self._drag_origin is None or not (event.buttons() & Qt.LeftButton):return
        if (event.position()-self._drag_origin).manhattanLength()<8:return
        self._drag_origin=None
        self.start_expression_drag()
        event.accept()

    def start_expression_drag(self):
        value=self.socket.value()
        if not is_embedded(value):return
        mime=QMimeData()
        mime.setData(MIME_EMBEDDED_COPY,json.dumps(value,ensure_ascii=False).encode('utf-8'))
        nested=unpack_embedded(value)
        mime.setData(MIME_EMBEDDED_MOVE,nested.id.encode('utf-8'))
        drag=QDrag(self);drag.setMimeData(mime)
        drag.exec(Qt.CopyAction | Qt.MoveAction,Qt.CopyAction)

    def mouseReleaseEvent(self,event):
        self._drag_origin=None
        super().mouseReleaseEvent(event)


class BlockDragHandle(QLabel):
    """Drag a statement block from its grip; do not consume normal field edits."""
    def __init__(self, widget):
        super().__init__('⠿')
        self.owner=widget
        self._origin=None
        self.setToolTip('拖动重排积木、移动至其他分支或分区；Ctrl 拖动复制')
        self.setCursor(Qt.OpenHandCursor)
        self.setStyleSheet('color:white;font-size:18px;min-width:18px;')
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            scene=self.owner.section.scene()
            if scene:scene.raise_item(self.owner.section)
            self.owner.raise_()
            self._origin=event.position()
            event.accept();return
        super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        if self._origin is None or (event.position()-self._origin).manhattanLength()<8:
            return
        self._origin=None
        scene=self.owner.section.scene()
        if scene is None or scene.document is None:return
        mime=QMimeData();mime.setData(MIME_MOVE,self.owner.block.id.encode('utf-8'))
        drag=QDrag(self);drag.setMimeData(mime)
        self.setCursor(Qt.ClosedHandCursor)
        drag.exec(Qt.MoveAction | Qt.CopyAction,Qt.CopyAction if event.modifiers() & Qt.ControlModifier else Qt.MoveAction)
        self.setCursor(Qt.OpenHandCursor)
        event.accept()
    def mouseReleaseEvent(self,event):
        self._origin=None
        super().mouseReleaseEvent(event)

class NestedExpressionShape(QFrame):
    """Round value outputs, hexagonal boolean predicates; never statement tabs."""
    def __init__(self, boolean=False, parent=None):
        super().__init__(parent)
        self.boolean=bool(boolean)
        self.setStyleSheet('QFrame{background:transparent;border:0;}')
        self.setContentsMargins(8 if boolean else 4,2,8 if boolean else 4,2)
        self.setToolTip('布尔条件表达式' if boolean else '可作为返回值的表达式')

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        w=max(12,self.width()-1);h=max(12,self.height()-1)
        path=QPainterPath()
        if self.boolean:
            cut=min(17,w/6)
            path.moveTo(cut,1);path.lineTo(w-cut,1);path.lineTo(w,h/2)
            path.lineTo(w-cut,h-1);path.lineTo(cut,h-1);path.lineTo(1,h/2);path.closeSubpath()
        else:path.addRoundedRect(1,1,w-1,h-1,h/2,h/2)
        p.setPen(QPen(QColor('#b9eadb'),1.6));p.setBrush(QColor('#387d79' if self.boolean else '#399678'))
        p.drawPath(path)
        p.end()


class EmbeddedExpressionWidget(NestedExpressionShape):
    """A nested expression shell with its own precise context menu.

    Right-clicking a green/teal embedded expression must target that specific
    expression block rather than bubbling to the outer statement block.
    """
    def __init__(self, socket, nested, parent=None):
        super().__init__(is_boolean_return(nested), parent)
        self.socket=socket
        self.nested=nested
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda point:self.show_menu(QCursor.pos()))

    def sizeHint(self):
        layout=self.layout()
        if layout is not None:
            return layout.sizeHint().expandedTo(layout.minimumSize())
        return super().sizeHint()

    def minimumSizeHint(self):
        layout=self.layout()
        if layout is not None:
            return layout.minimumSize()
        return super().minimumSizeHint()

    def bind_menu_target(self, widget):
        if widget is None:
            return None
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda point,w=widget:self.show_menu(QCursor.pos()))
        return widget

    def show_menu(self, global_pos=None):
        menu=QMenu(None)
        switch={}
        if self.nested.kind=='operator':
            from ..math_blocks import OPERATORS
            current=str(self.nested.args.get('operator','+'))
            group=next((values for values in OPERATORS.values() if current in values),())
            sub=menu.addMenu('切换运算符 / Switch operator')
            for value in group:
                action=sub.addAction(value)
                switch[action]=value
        elif self.nested.kind=='math_call':
            from ..math_blocks import MATH_FUNCTIONS
            sub=menu.addMenu('切换 Math 函数 / Switch Math')
            for value in MATH_FUNCTIONS:
                switch[sub.addAction(value)]=value
        edit_args=menu.addAction('编辑参数槽 / Edit arguments…') if self.nested.kind in ('call','string_call') else None
        trace_config=menu.addAction(translated_text('TraceLine 配置工作区...')) if self.nested.kind=='utility' and self.nested.args.get('operation')=='trace_ray' else None
        delete=menu.addAction(translated_text('Delete'))
        chosen=menu.exec(global_pos or QCursor.pos())
        if trace_config and chosen==trace_config:
            from .trace_dialog import TraceLineConfigDialog
            dialog=TraceLineConfigDialog(self.nested,None)
            if dialog.exec():
                self.socket.replace({'kind':'embedded_block','block':self.nested.to_dict()})
            return
        if edit_args and chosen==edit_args:
            values=list(self.nested.args.get('parameters',[]))
            amount,ok=QInputDialog.getInt(None,'调用参数 / Arguments','参数槽数量 / Number of slots',len(values),0,64)
            if ok:
                specs=list(self.nested.args.get('parameter_specs',[]))
                self.nested.args['parameters']=(values+['null']*amount)[:amount]
                self.nested.args['parameter_specs']=(specs+[{'name':f'arg{i+1}','type':'auto'} for i in range(len(specs),amount)])[:amount]
                self.socket.replace({'kind':'embedded_block','block':self.nested.to_dict()})
            return
        if chosen==delete:self.socket.replace('null')
        elif chosen in switch:
            value=switch[chosen]
            if self.nested.kind=='operator':
                self.nested.args['operator']=value
            else:
                from ..math_blocks import MATH_FUNCTIONS
                self.nested.args['function']=value
                params=self.nested.args.setdefault('parameters',[])
                count=MATH_FUNCTIONS[value]
                self.nested.args['parameters']=(params+['0']*count)[:count]
            self.socket.replace({'kind':'embedded_block','block':self.nested.to_dict()})


class ExpressionSlot(QFrame):
    """A real socket: text is editable, expression blocks can replace its content."""
    def __init__(self, owner, key, index=None, depth=0, hint=''):
        super().__init__(owner if isinstance(owner,QWidget) else None)
        self.owner=owner;self.key=key;self.index=index;self.depth=depth
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred)
        self.setObjectName('expressionSocket')
        self.setStyleSheet('QFrame#expressionSocket{background:#eceddc;border:2px solid #c4d1e0;border-radius:14px;} QFrame#expressionSocket[dragHover="true"]{border:3px solid #60ddb1;background:#ffffff;}')
        self.row=QHBoxLayout(self);self.row.setContentsMargins(5,2,5,2);self.row.setSpacing(3)
        self.render(hint)

    def value(self):
        val=self.owner.block.args.get(self.key,'')
        if self.index is not None:
            return val[self.index] if isinstance(val,list) and self.index<len(val) else ''
        return val

    def set_value(self, val):
        if self.index is not None:
            arr=self.owner.block.args.setdefault(self.key,[])
            while len(arr)<=self.index:arr.append('null')
            arr[self.index]=val
        else:self.owner.block.args[self.key]=val
        if self.key=='value' and self.index is None and self.owner.block.kind=='var':
            from ..variable_types import sync_active_variable_value
            sync_active_variable_value(self.owner.block)
        self.owner.changed()

    def render(self,hint=''):
        while self.row.count():
            item=self.row.takeAt(0)
            w=item.widget()
            if w:w.deleteLater()
        val=self.value()
        if isinstance(val,dict) and val.get('kind')=='variable_ref':
            # Keep a proper variable-reference widget in the value socket.
            # The declaration remains untouched; this socket contains a reference.
            path=str(val.get('path') or val.get('name') or 'null')
            token=EmbeddedVariableReference(self,val)
            self.row.addWidget(token)
            remove=QPushButton('×')
            remove.setFixedSize(20,21)
            remove.setToolTip('移除变量引用，恢复文本输入')
            remove.setStyleSheet('QPushButton{background:#f4f0df;color:#000000;border:1px solid #a5acb4;border-radius:7px;font-weight:bold;} QPushButton:hover{background:#fff3d0;color:#000000;}')
            remove.clicked.connect(lambda:self.replace('null'))
            self.row.addWidget(remove)
        elif is_embedded(val):
            nested=unpack_embedded(val)
            repair_documented_method_parameters(nested)
            repair_saved_netprop_selection(nested)
            pill=EmbeddedExpressionWidget(self,nested,self)
            lay=QHBoxLayout(pill);lay.setContentsMargins(8,3,6,3);lay.setSpacing(4)
            handle=EmbeddedExpressionDragHandle(self)
            pill.bind_menu_target(handle)
            lay.addWidget(handle)
            name=nested.args.get('method',nested.args.get('function',nested.args.get('operation',nested.kind)))
            if nested.kind=='utility':
                from ..utility_blocks import UTILITY_BLOCKS, utility_caption
                info=UTILITY_BLOCKS.get(nested.args.get('operation'),{})
                label=utility_caption(info,current_profile().language,current_profile().style) if info else 'Utility'
            else:
                label=method_caption(str(name)) if nested.kind=='method' else str(name)
            if nested.kind=='expr' and nested.args.get('literal_group'):
                from ..quick_literals import literal_label, literal_tooltip
                group=nested.args['literal_group'];value=nested.args['literal_name']
                label=literal_label(group,value,current_profile().language,current_profile().style)
            lab=QLabel(label+('(' if nested.kind in ('method','call','string_call') and current_profile().style=='professional' else ''))
            if nested.kind=='expr' and nested.args.get('literal_group'):
                lab.setToolTip(literal_tooltip(group,value,current_profile().language,current_profile().style))
                lab.setWordWrap(True)
                lab.setMaximumWidth(240)
            if nested.kind=='utility':
                lab.setToolTip(info.get('description_en' if current_profile().language=='en' else 'description',''))
                lab.setWordWrap(True)
                lab.setMaximumWidth(200)
            lab.setStyleSheet('color:white;font-weight:bold;')
            pill.bind_menu_target(lab)
            receiver_first=(nested.kind=='method' and current_profile().style=='general'
                            and current_profile().language=='zh')
            if nested.kind=='math_call':
                from ..math_blocks import MATH_FUNCTIONS
                picker=QComboBox(pill)
                picker.addItems(list(MATH_FUNCTIONS))
                picker.setCurrentText(str(nested.args.get('function','sqrt')))
                picker.setMinimumWidth(90)
                def select_math(name,n=nested):
                    if name==n.args.get('function'):return
                    count=MATH_FUNCTIONS[name]
                    params=list(n.args.get('parameters',[]))
                    n.args['function']=name
                    n.args['parameters']=(params+['0']*count)[:count]
                    self.replace({'kind':'embedded_block','block':n.to_dict()})
                picker.currentTextChanged.connect(select_math)
                lay.addWidget(picker)
            elif not receiver_first:lay.addWidget(lab)
            if self.depth<7 and nested.kind in ('method','call','string_call','array_op','operator','math_call','rawin','utility'):
                if nested.kind in ('method','array_op'):
                    child=ExpressionSlot(EmbeddedOwner(self.owner,nested,self), 'target', depth=self.depth+1,hint='对象')
                    lay.addWidget(child)
                if receiver_first:lay.addWidget(lab)
                if nested.kind=='utility':
                    lay.addWidget(ExpressionSlot(EmbeddedOwner(self.owner,nested,self),'value',depth=self.depth+1,
                                                 hint=('Start Vector' if current_profile().language=='en' else '起点 Vector')
                                                 if nested.args.get('operation')=='trace_ray' else ('Value' if current_profile().language=='en' else '值')))
                if nested.kind=='rawin':
                    lay.addWidget(ExpressionSlot(EmbeddedOwner(self.owner,nested,self), 'target', depth=self.depth+1, hint='Table / Scope'))
                    key_label=QLabel(translated_text('包含键'))
                    key_label.setStyleSheet('color:white;')
                    pill.bind_menu_target(key_label)
                    lay.addWidget(key_label)
                    lay.addWidget(ExpressionSlot(EmbeddedOwner(self.owner,nested,self), 'key', depth=self.depth+1, hint='"ammo_keep"'))
                if nested.kind=='operator':
                    unary=nested.args.get('operator')=='!'
                    op_label=QLabel(str(nested.args.get('operator','+')))
                    pill.bind_menu_target(op_label)
                    if unary:lay.addWidget(op_label)
                    lay.addWidget(ExpressionSlot(EmbeddedOwner(self.owner,nested,self), 'left', depth=self.depth+1,hint='布尔值' if unary else '左值'))
                    if not unary:
                        lay.addWidget(op_label)
                        lay.addWidget(ExpressionSlot(EmbeddedOwner(self.owner,nested,self), 'right', depth=self.depth+1,hint='右值'))
                params=nested.args.get('parameters',[])
                for i in range(len(params)):
                    spec=nested.args.get('parameter_specs',[])
                    title=(spec[i].get('en' if current_profile().language=='en' else 'zh') or spec[i]['name']) if i<len(spec) and nested.kind=='utility' else (spec[i]['name'] if i<len(spec) else f'arg{i+1}')
                    if nested.kind=='utility':
                        param_label=QLabel(title);param_label.setStyleSheet('color:white;')
                        lay.addWidget(param_label)
                    if i==property_parameter_index(nested):
                        btn=QPushButton('NetProp：'+(selected_property(nested,i) or '选择属性'))
                        btn.setToolTip('点击选择 NetProp 属性')
                        def pick_nested(checked=False,n=nested,index=i):
                            from .netprop_picker import NetPropPicker
                            dialog=NetPropPicker(n.args.get('netprop_class',''),selected_property(n,index))
                            if dialog.exec() and dialog.selection:
                                set_selected_property(n,index,dialog.selection)
                                self.set_value({'kind':'embedded_block','block':n.to_dict()})
                                self.owner.root_refresh()
                        btn.clicked.connect(pick_nested);lay.addWidget(btn)
                    else:
                        if nested.kind=='string_call':
                            cb=QComboBox()
                            cb.addItems(['auto','int','float','bool','string','handle','Vector'])
                            cb.setCurrentText(str(spec[i].get('type','auto')) if i<len(spec) else 'auto')
                            def change_nested_type(value,n=nested,index=i):
                                specs=n.args.setdefault('parameter_specs',[])
                                while len(specs)<=index:specs.append({'name':f'arg{len(specs)+1}','type':'auto'})
                                specs[index]['type']=value
                                self.set_value({'kind':'embedded_block','block':n.to_dict()})
                                QTimer.singleShot(0,self.owner.root_refresh)
                            cb.currentTextChanged.connect(change_nested_type)
                            lay.addWidget(cb)
                        child=ExpressionSlot(EmbeddedOwner(self.owner,nested,self), 'parameters',i,self.depth+1,title)
                        child.setToolTip(title);lay.addWidget(child)
            remove=QPushButton('×');remove.setToolTip('移除嵌套积木，恢复文字输入');remove.setFixedSize(20,21)
            remove.setStyleSheet('QPushButton{background:#f4f0df;color:#000000;border:1px solid #a5acb4;border-radius:7px;font-weight:bold;} QPushButton:hover{background:#fff3d0;color:#000000;}')
            remove.clicked.connect(lambda:self.replace('null'))
            pill.bind_menu_target(remove)
            lay.addWidget(remove)
            self.row.addWidget(pill)
        elif isinstance(val,dict):
            editor=QLineEdit('null');editor.setToolTip('复合表达式：请在生成器检查后手动修改')
            editor.textEdited.connect(self.set_value);self.row.addWidget(editor)
        else:
            editor=QLineEdit(str(val) if val is not None else '')
            editor.setPlaceholderText(hint or DISPLAY.get(self.key,self.key))
            editor.setAcceptDrops(False)
            editor.textEdited.connect(self.set_value)
            self.row.addWidget(editor)
            def autosize(*args):
                value=editor.text() or editor.placeholderText() or ' '
                width=max(75,min(900,editor.fontMetrics().horizontalAdvance(value)+30))
                changed_width=editor.width()!=width
                editor.setFixedWidth(width)
                editor.updateGeometry()
                section=self.owner.root_section
                if changed_width and section is not None and section.widget() is not None:
                    section.schedule_geometry_update()
            editor.textChanged.connect(autosize);autosize()
        # The section runs one bottom-up geometry pass after all descendants
        # have been inserted. Measuring here would cache a partly built row.
        self.updateGeometry()

    def sync_content_width(self):
        # Public compatibility helper for callers refreshing a single socket.
        root=self.owner.root_section
        panel=root.widget() if root is not None else None
        if panel is not None:
            _reflow_expression_widgets(panel)
        return self.minimumWidth()

    def replace(self,value):
        self.set_value(value)
        QTimer.singleShot(0,self.owner.root_refresh)

    def dragEnterEvent(self,event):
        mime=event.mimeData()
        if any(mime.hasFormat(x) for x in (MIME_METHOD,MIME_MOVE,MIME_BLOCK,MIME_EXPR,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
            self.setProperty('dragHover','true');self.style().unpolish(self);self.style().polish(self)
            event.acceptProposedAction();return
        super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        if any(event.mimeData().hasFormat(x) for x in (MIME_METHOD,MIME_MOVE,MIME_BLOCK,MIME_EXPR,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
            event.acceptProposedAction();return
        super().dragMoveEvent(event)
    def dragLeaveEvent(self,event):
        self.setProperty('dragHover','false');self.style().unpolish(self);self.style().polish(self)
        super().dragLeaveEvent(event)

    def dropEvent(self,event):
        self.setProperty('dragHover','false');self.style().unpolish(self);self.style().polish(self)
        scene=self.owner.root_section.scene()
        if scene and scene.views():
            canvas=scene.views()[0]
            if hasattr(canvas,'embed_in_socket') and canvas.embed_in_socket(event.mimeData(),self,event.keyboardModifiers()):
                event.acceptProposedAction();return
        event.ignore()


class EmbeddedOwner:
    """Adapter so recursive parameter slots update their owning expression AST."""
    def __init__(self,outer,nested,socket):
        self.outer=outer;self.block=nested;self.socket=socket
        self.root_section=outer.root_section
        self.changed=self.commit
    def commit(self):
        self.socket.set_value({'kind':'embedded_block','block':self.block.to_dict()})
    def root_refresh(self):self.outer.root_refresh()

class BlockWidget(QFrame):
    def __init__(self,section,block,collection,changed,refresh,depth=0):
        super().__init__();repair_documented_method_parameters(block)
        if block.kind=='entity_for' and block.args.get('search','FindByClassname') in ENTITY_SEARCH_MODES:
            normalize_entity_search(block,block.args.get('search','FindByClassname'))
        self.section=section;self.block=block;self.collection=collection
        self.changed=changed;self.refresh=refresh;self.depth=depth;self.root_section=section
        self.root_refresh=refresh
        self.setObjectName('block')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda point:self.menu_actions(QCursor.pos()))
        color=COLORS.get(block.kind,'#596173')
        self.setStyleSheet('QFrame#block{background:%s;border-radius:8px;border:1px solid #ffffff25;} QLineEdit{background:#f4f0df;color:#242c37;border:0;border-radius:5px;padding:4px;min-height:23px;} QComboBox{background:#f4f0df;color:#000000;padding:3px;} QComboBox QAbstractItemView{background:#ffffff;color:#000000;selection-background-color:#b9d6f4;selection-color:#000000;}'%color)
        self.setMinimumWidth(295)
        self.setSizePolicy(__import__('PySide6.QtWidgets',fromlist=['QSizePolicy']).QSizePolicy.Preferred,__import__('PySide6.QtWidgets',fromlist=['QSizePolicy']).QSizePolicy.Preferred)
        outer=QVBoxLayout(self);outer.setContentsMargins(7,5,7,6);outer.setSpacing(3)
        head=QHBoxLayout();head.setSpacing(4);outer.addLayout(head)
        head.addWidget(BlockDragHandle(self))
        label=QLabel(block_caption(block.kind));label.setStyleSheet('color:white;font-weight:600;');head.addWidget(label)
        if block.kind=='event':
            from ..event_metadata import event_tip
            label.setToolTip(event_tip(block.args.get('event','')))

        head.addStretch(1)
        action=QPushButton('⋯');action.setFixedSize(24,24);action.setToolTip('复制 / 删除 / 移动积木')
        action.clicked.connect(lambda:self.menu_actions());head.addWidget(action)
        if block.kind=='zspawn':self.setToolTip('Native ZSpawn(table) for common and special infected.' if current_profile().language=='en' else '原生 ZSpawn(table)，用于生成普通与特殊感染者。')
        if block.kind=='summon':self.setToolTip(translated_text('根据 classname 与勾选的 KeyValues 创建实体。右键 -> Summon 配置工作区。请检查实体是否可由该 API 创建。'))
        if block.kind=='trace_line':self.setToolTip(translated_text('TraceLine 语句块：设置 start/end/ignore/mask，追踪结果写入 output Table；右键打开配置。'))
        if block.kind=='event':self.setStyleSheet(self.styleSheet()+ 'QFrame#block{border-top-left-radius:30px;border-top-right-radius:30px;}')
        # Height-for-width QLayouts embedded directly in a QVBoxLayout were given
        # a fixed 38px minimum. Their second line painted under the next block.
        # A widget owns the flow layout and reports its actual wrapped height.
        self._fields_host=QWidget(self)
        self._fields_host.setObjectName('fieldsHost')
        self._fields_host.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        fields=WrappingFields(self._fields_host,spacing=5)
        self._flow_fields=fields
        outer.addWidget(self._fields_host)
        self._field_editors=[]
        if block.kind=='method':repair_saved_netprop_selection(block)
        profile=current_profile()
        keys=method_field_order(profile) if block.kind=='method' else FIELD_ORDER.get(block.kind,[])
        for key in keys:
            if block.kind=='entity_for' and key in ('filter','origin','radius') and key not in ENTITY_SEARCH_MODES.get(block.args.get('search','FindByClassname'),ENTITY_SEARCH_MODES['FindByClassname'])['fields']:continue
            if key not in block.args:continue
            if block.kind=='operator' and block.args.get('operator')=='!' and key=='right':continue
            if key=='value' and block.kind=='netprop' and block.args.get('mode')!='set':continue
            if key=='output' and block.kind=='netprop' and block.args.get('mode')!='get':continue
            if key=='parameters':
                parameters=block.args.get('parameters',[])
                specs=block.args.get('parameter_specs',[])
                for idx in range(len(parameters)):
                    spec=specs[idx] if idx<len(specs) else {}
                    label=(spec.get('en' if profile.language=='en' else 'zh') or spec.get('name',f'arg{idx+1}')) if block.kind=='utility' else spec.get('name',f'arg{idx+1}')
                    pair=QWidget(self)
                    row=QHBoxLayout(pair)
                    row.setContentsMargins(0,0,0,0);row.setSpacing(4)
                    name=QLabel(parameter_caption(label,profile)+(': ' if profile.language=='en' else '：'))
                    name.setStyleSheet('color:#fff;')
                    if profile.style=='general':
                        name.setToolTip(label+' : '+str(spec.get('type','unknown')))
                    row.addWidget(name)
                    if block.kind=='string_call':
                        cb=QComboBox()
                        cb.addItems(['auto','int','float','bool','string','handle','Vector'])
                        cb.setCurrentText(str(spec.get('type','auto')))
                        cb.setToolTip(('String arguments use simple quote concatenation; arbitrary runtime strings containing quotes/backslashes need extra escaping.' if profile.language=='en' else 'string 参数现在使用简单引号拼接；若运行时字符串含有引号或反斜杠，需要自行转义。'))
                        def change_string_type(value,b=block,i=idx):
                            specs=b.args.setdefault('parameter_specs',[])
                            while len(specs)<=i:specs.append({'name':f'arg{len(specs)+1}','type':'auto'})
                            specs[i]['type']=value
                            self.changed()
                        cb.currentTextChanged.connect(change_string_type)
                        row.addWidget(cb)
                    if idx==property_parameter_index(block):
                        btn=QPushButton('选择 NetProp：'+(selected_property(block,idx) or '未选择'))
                        btn.setToolTip('先选择实体网络类，再选择属性。属性会被保存为字符串字面量，不再允许自由输入。')
                        btn.clicked.connect(lambda checked=False,b=block,i=idx:self.choose_method_netprop(b,i))
                        row.addWidget(btn)
                    else:
                        socket=ExpressionSlot(self,'parameters',idx,hint=parameter_caption(label,profile))
                        socket.setToolTip(label+' : '+str(spec.get('type','unknown')))
                        row.addWidget(socket)
                    pair.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)
                    fields.addWidget(pair)
                if not parameters and block.kind in ('call','method','string_call'):
                    noargs=QLabel('()');noargs.setStyleSheet('color:#e5f2e6');fields.addWidget(noargs)
                continue
            if key in ('output','variable','env','error','name') and block.args.get(key) and (key!='name' or block.kind=='var'):
                token=VariableToken(section,block,key,changed)
                if block.kind=='event' and key=='env':token.setToolTip(event_tip(block.args.get('event',''))+'\n'+translated_text('右键可选择 env 的字段。'))
                if block.kind=='foreach' and key=='variable':token.setToolTip('当前元素的值。Table 是成员值；Array 是元素值。')
                if block.kind=='foreach' and key=='key':token.setToolTip('可选：Array 为从 0 开始的索引；Table 为成员键名。')
                fields.addWidget(token);continue
            value=block.args.get(key)
            if key=='event' and block.kind=='event' and profile.style=='general':
                caption=QLabel(event_caption(str(value),profile))
                caption.setToolTip(event_tip(str(value)))
                caption.setStyleSheet('color:white;font-weight:bold;padding:5px;')
                fields.addWidget(caption)
                continue
            if key=='method' and block.kind=='method' and profile.style=='general':
                caption=QLabel(method_caption(str(value),profile,block.args.get('owner','')))
                caption.setStyleSheet('color:white;font-weight:bold;padding:5px;')
                caption.setToolTip('API: '+str(block.args.get('owner',''))+'.'+str(value))
                fields.addWidget(caption)
                continue
            if key=='infected_type' and block.kind=='zspawn':
                from ..spawn_catalog import INFECTED_TYPES
                editor=QComboBox()
                for species,zh,en in INFECTED_TYPES:
                    caption=en if profile.language=='en' else zh
                    editor.addItem(caption+' ('+str(species)+')',species)
                editor.setCurrentIndex(max(0,editor.findData(int(value))))
                editor.setToolTip('Select the infected type for native ZSpawn(table); location uses a Vector.' if profile.language=='en' else '选择原生 ZSpawn(table) 感染者类型；生成位置需要 Vector。')
                editor.currentIndexChanged.connect(lambda i,b=block,c=editor:self._type_or_mode_changed(b,'infected_type',c.itemData(i)) if i>=0 else None)
                fields.addWidget(editor)
            elif key=='search' and block.kind=='entity_for':
                editor=QComboBox()
                editor.setMinimumWidth(250)
                for method,spec in ENTITY_SEARCH_MODES.items():editor.addItem(translated_text(spec['label']),method)
                editor.setCurrentIndex(max(0,editor.findData(str(value))))
                editor.setToolTip(translated_text(ENTITY_SEARCH_MODES.get(str(value),ENTITY_SEARCH_MODES['FindByClassname'])['hint']))
                editor.currentIndexChanged.connect(lambda i,b=block,c=editor:self._type_or_mode_changed(b,'search',c.itemData(i)) if i>=0 else None)
                fields.addWidget(editor)
            elif key in ('mode','container_type','operation','scope','assignment','operator','function') and (key!='function' or block.kind=='math_call'):
                editor=QComboBox();vals=['auto','=','<-','+=','-=','*=','/=','%='] if key=='assignment' else ['+','-','*','/','%','>','<','>=','<=','==','!=','&&','||','!','&','|','^','<<','>>'] if key=='operator' else list(__import__('l4visual.math_blocks',fromlist=['MATH_FUNCTIONS']).MATH_FUNCTIONS) if key=='function' else ['get','set'] if key=='mode' else list(ARRAY_OPERATIONS) if key=='operation' else ['root','auto','local','无','static'] if key=='scope' else ['普通','Table','Set','ScriptScope']
                if key=='operation' and block.kind=='utility':
                    from ..utility_blocks import UTILITY_BLOCKS
                    for option,info in UTILITY_BLOCKS.items():
                        editor.addItem(info['en'] if profile.language=='en' else info['zh'],option)
                    editor.setCurrentIndex(max(0,editor.findData(str(value))))
                    editor.currentIndexChanged.connect(lambda index,b=block,c=editor:self._type_or_mode_changed(b,'operation',c.itemData(index)) if index>=0 else None)
                elif key in ('container_type','scope'):
                    # The visible language must not alter the persisted Squirrel
                    # type/scope enum used by code generation and validation.
                    for option in vals:
                        editor.addItem(translated_text(option),option)
                    editor.setCurrentIndex(max(0,editor.findData(str(value))))
                    editor.currentIndexChanged.connect(
                        lambda index,b=block,k=key,c=editor:self._type_or_mode_changed(b,k,c.itemData(index)) if index>=0 else None)
                else:
                    editor.addItems(vals);editor.setCurrentText(str(value))
                    editor.currentTextChanged.connect(lambda v,b=block,k=key:self._type_or_mode_changed(b,k,v))
                editor.setMinimumWidth(76)
                if key=='container_type':editor.setToolTip('ScriptScope：Value 填实体表达式，打开 Table 数据窗口定义其成员；普通 Table 的 GetScriptScope() 返回值也会推断为 Table。')
                if key=='scope':editor.setToolTip('root: 根作用域全局变量；auto: 函数中 local、根位置全局；local: 仅当前作用域；无: 不声明，只对已有变量赋值；static: 仅合法 Squirrel class 静态成员可用。')
                fields.addWidget(editor)
            elif key=='property' and block.kind=='netprop':
                btn=QPushButton('选择属性：'+str(value or '未选择'))
                btn.setToolTip('选择实体类与属性。m_iAmmo 等数组自动打开索引槽；LocalWeaponData 等资料分组不会被误加到运行时键名中。')
                btn.clicked.connect(self.choose_netprop)
                fields.addWidget(btn)
            elif key=='source' and block.kind=='raw':
                from PySide6.QtWidgets import QPlainTextEdit
                editor=QPlainTextEdit(str(value or ''))
                editor.setObjectName('squirrelSourceEditor')
                editor.setPlaceholderText('输入 Squirrel 脚本；Enter 换行，支持多行')
                editor.setMinimumWidth(420)
                editor.setFixedWidth(540)
                editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
                editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                editor.setStyleSheet('QPlainTextEdit{background:#f4f0df;color:#242c37;border:1px solid #9eb1bc;border-radius:5px;padding:5px;}')
                def source_updated(b=block,control=editor,emit=True):
                    text=control.toPlainText()
                    b.args['source']=text
                    lines=text.split('\n')
                    metrics=control.fontMetrics()
                    # Count both real line breaks and automatic soft wrapping.
                    # No 390px cap: long code must expand rather than be hidden.
                    widths=[metrics.horizontalAdvance(line) for line in lines]
                    inner_width=max(90,control.width()-32)
                    desired=raw_editor_height(text,widths,inner_width,metrics.lineSpacing(),padding=28)
                    if desired!=control.height():
                        control.setFixedHeight(desired)
                        control.updateGeometry()
                        # Resized child -> new WrappingFields height -> parent
                        # branch/section/QGraphicsProxyWidget height.
                        timer=getattr(self,'_layout_timer',None)
                        if timer is not None:timer.start(0)
                        if self.section is not None:self.section.schedule_geometry_update()
                    if emit:changed()
                editor.textChanged.connect(source_updated)
                source_updated(emit=False)
                fields.addWidget(editor)
            elif key in ('target','source','condition','value','filter','origin','radius','index','left','right','classname','start','end','ignore','mask') or (block.kind=='rawin' and key=='key'):
                socket=ExpressionSlot(self,key,hint=('成员键 / key' if block.kind=='rawin' and key=='key' else
                                    ('Start Vector' if profile.language=='en' else '起点 Vector')
                                    if block.kind=='utility' and key=='value' and block.args.get('operation')=='trace_ray' else
                                    field_caption(key,profile) if profile.style=='general' else DISPLAY.get(key,key)))
                if block.kind=='entity_for' and key in ENTITY_FIELD_LABELS:
                    socket.setToolTip(translated_text(ENTITY_FIELD_LABELS[key])+'; '+translated_text(ENTITY_SEARCH_MODES[block.args.get('search','FindByClassname')]['hint']) if current_profile().language=='en' else ENTITY_FIELD_LABELS[key]+'；'+ENTITY_SEARCH_MODES[block.args.get('search','FindByClassname')]['hint'])
                fields.addWidget(socket)
            else:
                editor=QLineEdit(str(value) if value is not None else '')
                editor.setPlaceholderText(field_caption(key,profile) if profile.style=='general' else DISPLAY.get(key,key))
                if block.kind=='foreach' and key=='key':editor.setToolTip('可选。Array：索引 0、1、2…；Table：成员键名。留空只遍历值。')
                editor.textEdited.connect(lambda t,b=block,k=key:(b.args.__setitem__(k,t),changed()))
                if key=='method' and block.kind=='method':
                    editor.editingFinished.connect(self.resolve_method_signature)
                def fit(*args,control=editor):
                    content=control.text() or control.placeholderText() or ' '
                    width=max(60,min(450,control.fontMetrics().horizontalAdvance(content)+32))
                    changed_width=control.width()!=width
                    control.setFixedWidth(width)
                    control.updateGeometry()
                    if changed_width and self.section is not None and self.section.widget() is not None:
                        self.section.schedule_geometry_update()
                editor.textChanged.connect(fit);fit()
                fields.addWidget(editor)
            if block.kind=='event' and key=='event':
                self.setToolTip(event_tip(str(value)))
            if key=='method' and block.kind=='method':
                tip=QLabel('●' if block.args.get('return_type','') not in ('void','none') else '■')
                tip.setToolTip('圆形=可放入表达式插槽；方形=仅执行')
                fields.addWidget(tip)
        fields.addStretch(1)
        self._fields_host.setMinimumWidth(fields.minimumSize().width())
        self.setMinimumWidth(max(295,fields.minimumSize().width()+18))
        self._fields_host.setFixedHeight(max(38,fields.heightForWidth(690)))
        self._layout_timer=QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.timeout.connect(self._recalculate_field_height)
        self._layout_timer.start(0)
        if block.kind == 'var' and section.model.kind == 'data' and section.model.args.get('container','Table') == 'Table':
            mode_row = QHBoxLayout()
            mode_label = QLabel('ScriptScope 成员初始化：')
            mode_label.setStyleSheet('color:white;')
            mode_row.addWidget(mode_label)
            mode_combo = QComboBox()
            mode_combo.setStyleSheet('QComboBox{color:#111111;background:#f4f0df;} QComboBox QAbstractItemView{color:#111111;background:#ffffff;}')
            mode_combo.addItem('仅首次创建（推荐）', 'once')
            mode_combo.addItem('每次覆盖', 'overwrite')
            mode_combo.addItem('仅修改已有成员', 'existing')
            mode_combo.addItem('仅引用（不生成初始化代码）', 'reference')
            mode_combo.setCurrentIndex(max(0,mode_combo.findData(block.args.get('init_mode','once'))))
            mode_combo.setToolTip('仅当该数据分区属于 ScriptScope 时生效。普通 Table 构造器保持原样。')
            mode_combo.currentIndexChanged.connect(lambda i, b=block, c=mode_combo: (b.args.__setitem__('init_mode',c.itemData(i)),changed()))
            mode_row.addWidget(mode_combo)
            mode_row.addStretch(1)
            outer.addLayout(mode_row)
        if block.kind=='if' and 'else' not in block.branches:
            # Legacy single-branch blocks and new blocks use the same persistent model.
            block.branches.setdefault('body', [])
        for branch_name,children in block.branches.items():
            wrapper=QFrame();wrapper._branch_target=(block,branch_name);wrapper.setObjectName('branch_drop_zone')
            wrapper.setStyleSheet('QFrame{background:#161e2b;border-left:5px solid #e0ae55;border-radius:4px;}')
            l=QVBoxLayout(wrapper);l.setContentsMargins(11,6,4,7);l.setSpacing(4)
            if block.kind=='if' and branch_name.startswith('elif__'):
                header=QHBoxLayout()
                header.addWidget(QLabel('否则如果 / else if'))
                cond=ExpressionSlot(self, 'elif_condition_'+branch_name, hint='条件')
                block.args.setdefault('elif_condition_'+branch_name,'true')
                header.addWidget(cond)
                remove=QPushButton('−');remove.setFixedSize(24,24)
                remove.setToolTip('删除此 else if 分支及其内部的全部积木')
                remove.clicked.connect(lambda checked=False,key=branch_name:self._remove_elif(key))
                header.addWidget(remove)
                l.addLayout(header)
            else:
                branch_title=BRANCH_NAMES.get(branch_name,branch_name) if current_profile().language=='zh' else {
                    'body':'Execute','else':'Else','catch':'Catch'}.get(branch_name,branch_name)
                tip=QLabel(branch_title+('  ─ 拖入积木' if current_profile().language=='zh' else '  ─ drop blocks here'));tip.setStyleSheet('color:#abbcd0;font-size:11px;');l.addWidget(tip)
            for child in children:l.addWidget(BlockWidget(section,child,children,changed,refresh,depth+1))
            if not children:
                placeholder=QLabel(translated_text('将积木拖放到这里'));placeholder.setMinimumHeight(31)
                placeholder.setStyleSheet('color:#6f86a2;');l.addWidget(placeholder)
            outer.addWidget(wrapper)
        if block.kind=='if':
            add=QPushButton('＋ 添加 else if / else' if current_profile().language=='zh' else '＋ Add else if / else')
            add.setToolTip('首次添加 else；已有 else 时在它前面插入 else if。')
            add.clicked.connect(self._add_if_branch)
            outer.addWidget(add)
        if block.kind=='var' and container_kind(block):
            b=QPushButton('打开数据定义分区');b.clicked.connect(self.open_definition);outer.addWidget(b)
        localize_widget_tree(self)
    def _recalculate_field_height(self):
        host=getattr(self,'_fields_host',None)
        if host is None:
            return
        # Each field is indivisible; recompute QHBoxLayout-backed parameter
        # containers after every nested expression has reported its real width.
        for index in range(self._flow_fields.count()):
            item=self._flow_fields.itemAt(index)
            child=item.widget() if item is not None else None
            if child is not None and child.layout() is not None and isinstance(child.layout(),QHBoxLayout):
                row=child.layout()
                row.invalidate()
                required_pair=_row_minimum_width(row)
                if required_pair!=child.minimumWidth():child.setMinimumWidth(required_pair)
                child.updateGeometry()
        self._flow_fields.invalidate()
        required=self._flow_fields.minimumSize().width()
        changed=False
        if host.minimumWidth()!=required:
            host.setMinimumWidth(required)
            changed=True
        block_layout=self.layout()
        block_layout.invalidate()
        # Include branches and their child statement blocks, not just the
        # parameter row. This is essential for C-shaped if/while/event blocks.
        required_block=max(295, required+18,block_layout.minimumSize().width())
        if self.minimumWidth()!=required_block:
            self.setMinimumWidth(required_block)
            changed=True
        width=max(required,host.width() or self.contentsRect().width()-14)
        wanted=max(38,self._flow_fields.heightForWidth(width))
        if host.height()!=wanted or host.minimumHeight()!=wanted:
            host.setFixedHeight(wanted)
            changed=True
        if changed:
            host.updateGeometry()
            block_layout.invalidate()
            self.updateGeometry()
            parent=self.parentWidget()
            while parent is not None:
                layout=parent.layout()
                if layout is not None:layout.invalidate()
                parent.updateGeometry()
                parent=parent.parentWidget()
            if self.section is not None and self.section.widget() is not None:
                self.section.schedule_geometry_update()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._layout_timer.start(0)

    def _add_if_branch(self):
        branches=self.block.branches
        if 'else' not in branches:
            branches['else']=[]
        else:
            from uuid import uuid4
            key='elif__'+uuid4().hex[:8]
            old_else=branches.pop('else')
            branches[key]=[]
            self.block.args['elif_condition_'+key]='true'
            branches['else']=old_else
        self.changed();QTimer.singleShot(0,self.root_refresh)

    def _remove_elif(self,key):
        self.block.branches.pop(key,None)
        self.block.args.pop('elif_condition_'+key,None)
        self.changed();QTimer.singleShot(0,self.root_refresh)

    def choose_method_netprop(self,block,index):
        from .netprop_picker import NetPropPicker
        picker=NetPropPicker(block.args.get('netprop_class',''),selected_property(block,index))
        if picker.exec() and picker.selection:
            set_selected_property(block,index,picker.selection)
            self.changed()
            self.root_refresh()

    def choose_netprop(self):
        from .netprop_picker import NetPropPicker
        picker=NetPropPicker(self.block.args.get('table',''),self.block.args.get('property',''))
        if picker.exec() and picker.selection:
            self.block.args.update(picker.selection)
            self.changed()
            self.root_refresh()

    def _type_or_mode_changed(self, block, key, value):
        if key=='function' and block.kind=='math_call':
            from ..math_blocks import MATH_FUNCTIONS
            if value not in MATH_FUNCTIONS or block.args.get('function')==value:return
            params=list(block.args.get('parameters',[]))
            count=MATH_FUNCTIONS[value]
            block.args['function']=value
            block.args['parameters']=(params+['0']*count)[:count]
            self.changed();QTimer.singleShot(0,self.root_refresh)
            return
        if key == 'search' and block.kind == 'entity_for':
            if value not in ENTITY_SEARCH_MODES or value == block.args.get('search'):return
            normalize_entity_search(block,value)
            self.changed()
            QTimer.singleShot(0,self.root_refresh)
            return
        if key == 'operation' and block.kind == 'array_op':
            if block.args.get('operation') != value:
                change_array_operation(block,value)
                self.root_refresh()
            return
        if key=='operation' and block.kind=='utility':
            if block.args.get('operation')==value:return
            from ..utility_blocks import change_utility_operation
            change_utility_operation(block,value)
            self.changed()
            QTimer.singleShot(0,self.root_refresh)
            return
        if key == 'container_type' and block.kind == 'var':
            scene=self.section.scene()
            document=(getattr(scene,'owner_document',None) or getattr(scene,'document',None)) if scene else None
            if not change_variable_type(document,block,value):return
        else:
            if block.args.get(key)==value:return
            block.args[key]=value
        self.changed()
        # Rebuilding a proxy while its own combo emits currentTextChanged can
        # invalidate the native popup. Queue the rebuild after the signal ends.
        QTimer.singleShot(0,self.root_refresh)

    def resolve_method_signature(self):
        if self.block.kind!='method':return
        catalog=self.section.catalog
        row=catalog.method(self.block.args.get('owner',''),self.block.args.get('method',''))
        if row is None:return
        old=self.block.args.get('parameters',[])
        new=block_from_method(row)
        for i in range(min(len(old),len(new.args['parameters']))):
            new.args['parameters'][i]=old[i]
        self.block.args.update({k:v for k,v in new.args.items() if k in ('parameters','parameter_specs','return_type')})
        if str(row.get('returns','unknown')).lower() in ('void','none'):self.block.args['output']=''
        elif not self.block.args.get('output'):self.block.args['output']='result_'+self.block.id[:5]
        self.root_refresh()

    def open_definition(self):
        doc=getattr(self.section.scene(),'owner_document',None) or getattr(self.section.scene(),'document',None)
        if not doc:return
        try:sec=create_definition(doc,self.section.model,self.block)
        except ValueError as exc:
            self.setToolTip(str(exc))
            return
        # Never parent a top-level window to a widget inside QGraphicsProxyWidget.
        # Qt may embed child popups in the graphics scene and cover the whole canvas.
        dialog=DefinitionWorkspace(doc,sec,self.section.catalog,None)
        dialog.setAttribute(Qt.WA_DeleteOnClose,True)
        windows=getattr(QApplication.instance(),'_l4_data_windows',None)
        if windows is None:
            windows=[]
            QApplication.instance()._l4_data_windows=windows
        windows.append(dialog)
        dialog.destroyed.connect(lambda *_,w=dialog,store=windows:store.remove(w) if w in store else None)
        dialog.canvas.edited.connect(self.changed)
        # Update all open reference trays when a declaration is edited in any Data window.
        def refresh_open_trays():
            for window in tuple(windows):
                if hasattr(window,'scope_palette'):
                    window.scope_palette.reload()
        dialog.canvas.edited.connect(refresh_open_trays)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
    def edit_argument_slots(self):
        args=list(self.block.args.get('parameters',[]))
        amount,ok=QInputDialog.getInt(None,'调用参数 / Arguments','参数槽数量 / Number of slots',len(args),0,64)
        if not ok:return
        args=(args+['null']*amount)[:amount]
        specs=list(self.block.args.get('parameter_specs',[]))
        specs=(specs+[{'name':f'arg{i+1}','type':'auto'} for i in range(len(specs),amount)])[:amount]
        self.block.args['parameters']=args
        self.block.args['parameter_specs']=specs
        self.changed();QTimer.singleShot(0,self.root_refresh)

    def menu_actions(self,position=None):
        menu=QMenu(None)
        menu.setAttribute(Qt.WA_DeleteOnClose,False)
        if self.block.kind=='var' and container_kind(self.block):
            define=menu.addAction(translated_text('打开独立数据工作区'))
            menu.addSeparator()
        else:define=None
        spawn_config=menu.addAction(translated_text('Summon 配置工作区...')) if self.block.kind=='summon' else None
        trace_config=menu.addAction(translated_text('TraceLine 配置工作区...')) if self.block.kind=='trace_line' or (self.block.kind=='utility' and self.block.args.get('operation')=='trace_ray') else None
        edit_args=menu.addAction('编辑参数槽 / Edit arguments…') if self.block.kind in ('call','string_call') else None
        switch_actions={}
        if self.block.kind=='operator':
            from ..math_blocks import OPERATORS
            group=next((values for values in OPERATORS.values() if self.block.args.get('operator','+') in values),())
            sub=menu.addMenu('切换运算符 / Switch operator')
            for value in group:switch_actions[sub.addAction(value)]=value
        dup=menu.addAction(translated_text('复制积木'))
        up=menu.addAction(translated_text('上移'))
        down=menu.addAction(translated_text('下移'))
        menu.addSeparator()
        delete=menu.addAction(translated_text('Delete'))
        chosen=menu.exec(position or QCursor.pos())
        if chosen==define:self.open_definition();return
        if edit_args and chosen==edit_args:
            self.edit_argument_slots()
            return
        if chosen in switch_actions:
            self.block.args['operator']=switch_actions[chosen]
            self.changed();QTimer.singleShot(0,self.root_refresh)
            return
        if trace_config and chosen==trace_config:
            from .trace_dialog import TraceLineConfigDialog
            dialog=TraceLineConfigDialog(self.block,None)
            if dialog.exec():self.changed();QTimer.singleShot(0,self.root_refresh)
            return
        if spawn_config and chosen==spawn_config:
            from .spawn_dialog import SpawnConfigDialog
            dialog=SpawnConfigDialog(self.block,None)
            if dialog.exec():self.changed();QTimer.singleShot(0,self.root_refresh)
            return
        if self.block not in self.collection:return
        if chosen==dup:
            self.collection.insert(self.collection.index(self.block)+1,clone_with_definitions((getattr(self.section.scene(),'owner_document',None) or getattr(self.section.scene(),'document',None)),self.block))
        elif chosen==delete:
            self.collection.remove(self.block)
        elif chosen in (up,down):
            idx=self.collection.index(self.block);pos=idx+(-1 if chosen==up else 1)
            if 0<=pos<len(self.collection):self.collection[idx],self.collection[pos]=self.collection[pos],self.collection[idx]
        else:return
        self.changed()
        QTimer.singleShot(0,self.root_refresh)

class DragTitle(QLabel):
    def __init__(self,text,section):
        super().__init__(text)
        self.section=section
        self._press_scene=None
        self._start_scene_pos=None
        self.setCursor(Qt.OpenHandCursor)

    def _scene_position_from_mouse(self,event):
        scene=self.section.scene()
        if scene is None or not scene.views():return None
        view=scene.views()[0]
        # Qt synthetic mouse events from QGraphicsProxyWidget may have local
        # positions already transformed. Use one consistent global -> viewport
        # -> scene mapping, rather than mixing global pixels with scene units.
        vp=view.viewport().mapFromGlobal(QCursor.pos())
        return view.mapToScene(vp)

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._press_scene=self._scene_position_from_mouse(event)
            self._start_scene_pos=QPointF(self.section.pos())
            scene=self.section.scene()
            if scene and hasattr(scene,'raise_item'):scene.raise_item(self.section)
            self.setCursor(Qt.ClosedHandCursor)
            event.accept();return
        super().mousePressEvent(event)

    def show_actions(self, global_pos=None):
        menu=QMenu(self)
        edit=menu.addAction('编辑分区属性')
        delete=menu.addAction('删除分区及内部积木') if self.section.model.kind not in ('init','data') else None
        action=menu.exec(global_pos or QCursor.pos())
        if action==edit:self.section.edit_section()
        elif delete is not None and action==delete:self.section.delete_section()

    def contextMenuEvent(self,event):
        self.show_actions(event.globalPos())
        event.accept()

    def mouseMoveEvent(self,event):
        if self._press_scene is not None:
            scene=self.section.scene()
            if not scene or not scene.views():return
            view=scene.views()[0]
            current=self._scene_position_from_mouse(event)
            if current is None:return
            target=self._start_scene_pos+(current-self._press_scene)
            self.section.move_from_user(view.clamp_section_position(target))
            if scene:scene.update_connections()
            event.accept();return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self,event):
        if self._press_scene is not None:
            self._press_scene=None;self._start_scene_pos=None
            self.setCursor(Qt.OpenHandCursor)
            self.section.model.x=self.section.pos().x()
            self.section.model.y=self.section.pos().y()
            self.section.moved.emit()
            scene=self.section.scene()
            if scene and hasattr(scene, "update_connections"):scene.update_connections()
            event.accept();return
        super().mouseReleaseEvent(event)

class FunctionParameterToken(QLabel):
    """Drag a declared function argument; references are tied to the function section."""
    def __init__(self, section, name):
        super().__init__('● '+name)
        self.section=section
        self.name=name
        self.setCursor(Qt.OpenHandCursor)
        self.setStyleSheet('QLabel{background:#e9c17b;color:#4b3115;border-radius:13px;padding:5px 9px;font-weight:bold;}')
        self.setToolTip('形参属于此函数作用域；拖入函数内部槽位，不会重新声明形参。')

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            payload={'name':self.name,'id':'parameter:'+self.section.model.id+':'+self.name,
                     'scope':'local','section_id':self.section.model.id,
                     'path':getattr(self,'_selected_path',self.name),'parameter':True}
            mime=QMimeData();mime.setData(MIME_EXPR,json.dumps(payload,ensure_ascii=False).encode())
            drag=QDrag(self);drag.setMimeData(mime);drag.exec(Qt.CopyAction)
            event.accept();return
        if event.button()==Qt.RightButton:
            from .function_parameters import FunctionParameterEditor
            dialog=FunctionParameterEditor(self.section.model,self.name)
            if dialog.exec():
                self._selected_path=dialog.selected_path
                self.setText('● '+self._selected_path)
                self.setToolTip(translated_text('引用：')+self._selected_path+translated_text('；右键重新选择成员'))
                self.section.changed.emit()
            event.accept();return
        super().mousePressEvent(event)

class FunctionCallHandle(QLabel):
    """Palette-like drag source for a user-defined function; never moves its definition."""
    def __init__(self, section, as_string=False):
        super().__init__('⠿ 字符串调用' if as_string else '⠿ 调用')
        self.as_string=as_string
        self.section=section
        self._origin=None
        self.setCursor(Qt.OpenHandCursor)
        self.setToolTip('生成可嵌入 RunScriptCode 的调用字符串' if as_string else '向工作区拖出此函数的调用积木，原函数分区保持不变')
        self.setStyleSheet('QLabel{background:#367bb5;color:white;padding:9px;border-radius:6px;font-weight:bold;}')

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._origin=event.position()
            event.accept();return
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        if self._origin is None or (event.position()-self._origin).manhattanLength()<8:return
        self._origin=None
        section=self.section.model
        owner=section.args.get('owner','')
        parameters=section.args.get('params',[])
        if isinstance(parameters,str):parameters=[x.strip() for x in parameters.split(',') if x.strip()]
        name=(owner+'.' if owner else '')+section.name
        payload={'id':section.id,'function':name,'parameters':parameters,'parameter_types':section.args.get('param_types',[]),'return_type':section.args.get('return_type','unknown'),'as_string':self.as_string}
        mime=QMimeData();mime.setData(MIME_FUNCTION_CALL,json.dumps(payload,ensure_ascii=False).encode('utf-8'))
        drag=QDrag(self);drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)
        event.accept()

    def mouseReleaseEvent(self,event):
        self._origin=None
        super().mouseReleaseEvent(event)


def call_block_from_section_payload(payload):
    """Generate independent call with parameter placeholders from a function signature."""
    params=payload.get('parameters',[])
    return Block('string_call' if payload.get('as_string') else 'call',{'function':payload['function'],
        'parameters':['null' for _ in params],
        'parameter_specs':[{'name':str(name),'type':(payload.get('parameter_types',[])[i] if i<len(payload.get('parameter_types',[])) else 'auto')} for i,name in enumerate(params)],
        'output':'', 'return_type':payload.get('return_type','unknown'),
        'source_function_id':payload.get('id','')})


class SectionItem(QGraphicsProxyWidget):
    moved=Signal();changed=Signal()
    def __init__(self,section,catalog):
        super().__init__();self.model=section;self.catalog=catalog
        self._authorized_position=True
        self.setFlag(QGraphicsItem.ItemIsMovable,False);self.setFlag(QGraphicsItem.ItemIsSelectable,True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setZValue(1)
        self.setPos(section.x,section.y)
        self._authorized_position=False
        self.update_size()
    def itemChange(self, change, value):
        if (change==QGraphicsItem.ItemPositionChange and not getattr(self,'_authorized_position',False)):
            return QPointF(self.model.x,self.model.y)
        return super().itemChange(change,value)

    def move_from_user(self, point):
        self._authorized_position=True
        try:self.setPos(point)
        finally:self._authorized_position=False
        scene=self.scene()
        if scene is not None and hasattr(scene,'recalculate_bounds'):
            scene.recalculate_bounds(expand_only=True)

    def update_size(self):
        fixed_position=QPointF(self.model.x,self.model.y)
        panel=QFrame();panel.setObjectName('panel')
        panel.setStyleSheet('QFrame#panel{background:#212b3e;border:2px solid #465b7b;border-radius:11px;}')
        panel.setMinimumWidth(490)
        panel.setSizePolicy(__import__('PySide6.QtWidgets',fromlist=['QSizePolicy']).QSizePolicy.MinimumExpanding,__import__('PySide6.QtWidgets',fromlist=['QSizePolicy']).QSizePolicy.Preferred)
        layout=QVBoxLayout(panel);layout.setContentsMargins(10,8,10,12);layout.setSpacing(5)
        heading=DragTitle('⠿  '+self.model.name+'   ['+self.model.kind+']',self)
        heading.setToolTip('抓取标题移动分区；双击修改分区属性')
        heading.setStyleSheet('background:#3b5274;color:#fff;padding:12px;border-radius:7px;font-size:14px;font-weight:bold;')
        heading.mouseDoubleClickEvent=lambda event:self.edit_section()
        if self.model.kind not in ('init','data'):
            title_row=QHBoxLayout();title_row.setContentsMargins(0,0,0,0)
            title_row.addWidget(heading,1)
            section_menu=QPushButton('⋯')
            section_menu.setToolTip('编辑 / 删除分区')
            section_menu.setFixedSize(28,28)
            section_menu.clicked.connect(lambda checked=False,h=heading:h.show_actions(QCursor.pos()))
            title_row.addWidget(section_menu,0)
            if self.model.kind=='function':
                title_row.addWidget(FunctionCallHandle(self),0)
                title_row.addWidget(FunctionCallHandle(self,as_string=True),0)
            layout.addLayout(title_row)
        else:
            layout.addWidget(heading)
        if self.model.kind=='function':
            params=self.model.args.get('params',[])
            if isinstance(params,str):params=[x.strip() for x in params.split(',') if x.strip()]
            if params:
                param_row=QHBoxLayout()
                caption=QLabel('形参 →');caption.setStyleSheet('color:#cad8e9;')
                param_row.addWidget(caption)
                for param in params:param_row.addWidget(FunctionParameterToken(self,str(param)))
                param_row.addStretch(1)
                layout.addLayout(param_row)
        container_layout=layout
        if self.model.kind=='data':
            root=QFrame();root.setObjectName('fixed_data_root')
            root.setStyleSheet('QFrame#fixed_data_root{background:#18283a;border-left:14px solid #d8a74a;border-top:9px solid #d8a74a;border-bottom:12px solid #d8a74a;border-right:0;border-top-left-radius:17px;border-bottom-left-radius:17px;}')
            container_layout=QVBoxLayout(root);container_layout.setContentsMargins(22,10,12,14);container_layout.setSpacing(5)
            root_title=('固定数据根容器（不可删除）' if current_profile().language=='zh' else 'Fixed data container (cannot be removed)')
            label=QLabel('⬟ '+ ('Table { }' if self.model.args.get('container')=='Table' else 'Set [ ]') +'  · '+root_title)
            label.setStyleSheet('color:#e8c27a;font-weight:bold;background:transparent;')
            container_layout.addWidget(label)
            layout.addWidget(root)
        for block in self.model.blocks:
            container_layout.addWidget(BlockWidget(self,block,self.model.blocks,self.changed.emit,self.refresh))
        if not self.model.blocks:
            empty=QLabel('将变量和数据操作积木拖入根容器内部' if current_profile().language=='zh' else 'Drop variable and data blocks into the root container');empty.setStyleSheet('color:#91a6c4;padding:18px;');container_layout.addWidget(empty)
        if self.widget() is not None:self.setWidget(None)
        localize_widget_tree(panel)
        panel.adjustSize()
        self.setWidget(panel)
        # Do not assume heightForWidth of the nested flow will be propagated
        # automatically by QGraphicsProxyWidget. Recompute once widget geometry
        # has been settled by Qt, then expand panel and proxy accordingly.
        QTimer.singleShot(0,self._finish_geometry)
        self.updateGeometry()
        # Resizing/rebuilding the proxy must never reposition its section.
        # Automatic layout may resize a section, but may not change its scene origin.
        if self.pos()!=fixed_position:
            self._authorized_position=True
            try:self.setPos(fixed_position)
            finally:self._authorized_position=False
    def schedule_geometry_update(self):
        if getattr(self,'_geometry_refresh_pending',False):return
        self._geometry_refresh_pending=True
        # Queued on the live proxy item; no stale Python reference to a
        # destroyed QGraphicsItem is kept in a separately running timer.
        if not hasattr(self,'_geometry_timer'):
            self._geometry_timer=QTimer()
            self._geometry_timer.setParent(self)
            self._geometry_timer.setSingleShot(True)
            self._geometry_timer.timeout.connect(self._run_geometry_update)
        self._geometry_timer.start(0)

    def _run_geometry_update(self):
        self._geometry_refresh_pending=False
        self._finish_geometry()

    def _finish_geometry(self):
        panel=self.widget()
        if panel is None or getattr(self,'_fitting_geometry',False):return
        self._fitting_geometry=True
        try:
            _reflow_expression_widgets(panel)
            blocks=panel.findChildren(BlockWidget)
            def ancestors(widget):
                depth=0
                parent=widget.parentWidget()
                while parent is not None:
                    if isinstance(parent,BlockWidget):depth+=1
                    parent=parent.parentWidget()
                return depth
            for block in sorted(blocks,key=ancestors,reverse=True):
                block._recalculate_field_height()

            panel_layout=panel.layout()
            # Qt's root minimum already contains every nested block's own
            # minimum.  Never use panel.width(), proxy.size(), or the actual
            # geometries of stretchable descendants as required dimensions:
            # they are *results* of the previous layout pass, not content.
            # Reset the previous minimum before measuring so shrink is legal.
            panel.setMinimumSize(490,0)
            panel_layout.invalidate()
            panel_layout.activate()
            size=_section_required_geometry(panel,panel_layout)
            width=size.width()
            # Qt can report a useful preferred height for wrapped rows only
            # after width assignment.  This height is recomputed, not cached.
            panel.resize(width,max(size.height(),panel_layout.sizeHint().height()))
            panel_layout.invalidate()
            panel_layout.activate()
            for block in sorted(blocks,key=ancestors,reverse=True):
                block._recalculate_field_height()
            panel_layout.invalidate()
            panel_layout.activate()
            size=_section_required_geometry(panel,panel_layout)
            width=size.width()
            height=max(size.height(),panel_layout.sizeHint().height())
            # Set both widgets to the same FINITE content extent, including
            # decreases.  Otherwise the proxy can stay huge after a block is
            # deleted and still steal clicks from sections behind it.
            panel.setMinimumSize(width,height)
            panel.resize(width,height)
            if self.widget() is panel:
                self.resize(width,height)
            self.updateGeometry()
            scene=self.scene()
            if scene is not None and hasattr(scene,'recalculate_bounds'):
                scene.recalculate_bounds()
        finally:
            self._fitting_geometry=False

    def refresh(self):
        self.update_size()
        if self.scene() and hasattr(self.scene(),'update_connections'):self.scene().update_connections()
        self.changed.emit()
    def delete_section(self):
        if self.model.kind in ('init','data'):
            QMessageBox.warning(None,'不可删除','初始化分区不可删除；Data 由所属变量管理。')
            return
        scene=self.scene()
        document=getattr(scene,'document',None)
        if document is None:return
        answer=QMessageBox.question(None,'确认删除分区',
            '删除 '+self.model.name+' 及其内部全部积木？',QMessageBox.Yes|QMessageBox.No)
        if answer!=QMessageBox.Yes:return
        section_id=self.model.id
        # A proxy widget cannot safely destroy itself in its own context-menu
        # callback. Remove from the document immediately and rebuild the scene
        # on the next event-loop iteration, after the QMenu has closed.
        document.sections[:]=[s for s in document.sections if s.id!=section_id]
        if scene:
            def finish_deletion(board=scene,doc=document):
                if board.document is not doc:return
                board.load(doc)
                board.updated.emit()
            QTimer.singleShot(0,finish_deletion)

    def edit_section(self):
        if self.model.kind=='init':
            QMessageBox.information(None,'固定初始化分区','初始化分区由文件自动维护，不可删除、转换或重复创建。')
            return
        scene=self.scene()
        document=getattr(scene,'document',None)
        before_name=self.model.name
        before_kind=self.model.kind
        dialog=SectionEditor(self.model,None,document=document)
        if dialog.exec():
            dialog.apply()
            if document and before_kind=='namespace' and self.model.kind=='namespace' and self.model.name!=before_name:
                for section in document.sections:
                    if section.kind=='function' and section.args.get('owner')==before_name:
                        section.args['owner']=self.model.name
            self.refresh()
            if scene and hasattr(scene,'refresh_sections'):scene.refresh_sections()
    def mouseReleaseEvent(self,event):
        super().mouseReleaseEvent(event)

class VisualScene(QGraphicsScene):
    updated=Signal()
    def __init__(self,catalog):
        super().__init__();self.catalog=catalog;self.document=None;self.items_by_id={}
        self.setSceneRect(*MIN_SCENE)
        self._z_counter=20
        self._links=[]
        self.show_data_sections=False
    def recalculate_bounds(self, expand_only=False):
        """Expand the workspace to fit sections, respecting its original minimum."""
        boxes=[]
        for item in self.items_by_id.values():
            if item.scene() is not self:
                continue
            rect=item.sceneBoundingRect()
            boxes.append((rect.left(),rect.top(),rect.width(),rect.height()))
        bounds=content_scene_rect(boxes,minimum=MIN_SCENE)
        if expand_only:
            present=self.sceneRect()
            bounds=include_rect(bounds,(present.left(),present.top(),present.width(),present.height()),0)
        self.setSceneRect(*bounds)

    def ensure_position(self,point, width=500, height=280):
        """Make it possible to drag a section outside all current boundaries."""
        rect=self.sceneRect()
        new=include_rect((rect.left(),rect.top(),rect.width(),rect.height()),
                         (point.x(),point.y(),width,height),320)
        if new!=(rect.left(),rect.top(),rect.width(),rect.height()):
            self.setSceneRect(*new)

    def expand_at_edges(self,left=False,top=False,right=False,bottom=False):
        if not any((left,top,right,bottom)):
            return
        rect=self.sceneRect()
        grow=950
        self.setSceneRect(rect.left()-(grow if left else 0),
                          rect.top()-(grow if top else 0),
                          rect.width()+grow*int(left)+grow*int(right),
                          rect.height()+grow*int(top)+grow*int(bottom))

    def drawBackground(self,p,rect):
        p.fillRect(rect,QColor('#131a27'))
        p.setPen(QColor('#243048'))
        from PySide6.QtCore import QLineF
        step=30
        xs=range(int(rect.left())//step*step,int(rect.right())+step,step)
        ys=range(int(rect.top())//step*step,int(rect.bottom())+step,step)
        p.drawLines([QLineF(x,rect.top(),x,rect.bottom()) for x in xs]+[QLineF(rect.left(),y,rect.right(),y) for y in ys])
    def update_connections(self):
        """Draw live dependency links without changing either section position."""
        from PySide6.QtGui import QPainterPath, QPen
        # Scene.clear() destroys the C++ graphics objects, so never reuse cached wrappers.
        old_links=self._links
        self._links=[]
        for link in old_links:
            if link.scene() is self:
                self.removeItem(link)
        if not self.document:return
        ns={item.model.name:item for item in self.items_by_id.values() if item.model.kind=='namespace'}
        for child in self.items_by_id.values():
            if child.model.kind!='function':continue
            owner=ns.get(child.model.args.get('owner',''))
            if owner is None:continue
            start=owner.sceneBoundingRect().center()
            end=child.sceneBoundingRect().center()
            start.setX(owner.sceneBoundingRect().right())
            end.setX(child.sceneBoundingRect().left())
            path=QPainterPath(start)
            middle=(start.x()+end.x())/2
            path.cubicTo(middle,start.y(),middle,end.y(),end.x(),end.y())
            link=QGraphicsPathItem(path)
            link.setPen(QPen(QColor('#89b6df'),2,Qt.DashLine))
            link.setZValue(-5)
            self.addItem(link)
            self._links.append(link)

    def raise_item(self,item):
        self._z_counter+=1
        item.setZValue(self._z_counter)

    def refresh_sections(self,ids=None):
        # Critical: never self.clear() or load() during block editing.
        for sid,item in tuple(self.items_by_id.items()):
            if ids is None or sid in ids:
                original=QPointF(item.model.x,item.model.y)
                item.update_size()
                if item.pos()!=original:
                    item._authorized_position=True
                    try:item.setPos(original)
                    finally:item._authorized_position=False
        self.update_connections()
        self.recalculate_bounds(expand_only=True)
        self.updated.emit()

    def add_section_item(self, section):
        if section.kind == "data" and not self.show_data_sections:
            return None
        if section.id in self.items_by_id:
            return self.items_by_id[section.id]
        item=SectionItem(section,self.catalog)
        self.addItem(item)
        item.changed.connect(self.updated.emit)
        item.moved.connect(self.updated.emit)
        self.items_by_id[section.id]=item
        # Sections created from the menu must be above already raised/selected
        # scene sections; otherwise the new section can be hidden underneath.
        self.raise_item(item)
        self.update_connections()
        self.recalculate_bounds(expand_only=True)
        self.updated.emit()
        return item

    def load(self,document):
        # Discard Python wrappers BEFORE Qt destroys their underlying C++ items.
        self._links=[]
        self.items_by_id={}
        self.document=None
        self.clear()
        self.document=document
        # Qt paints later-added graphics items above earlier ones when their Z
        # values are equal. Give every restored section an explicit unique Z so
        # the drawing order and all viewport hit tests always agree.
        self._z_counter=20
        if document:
            for section in document.sections:
                if section.kind == "data" and not self.show_data_sections:
                    continue
                item=SectionItem(section,self.catalog);self.addItem(item)
                item.changed.connect(self.updated.emit);item.moved.connect(self.updated.emit)
                self.items_by_id[section.id]=item
                self.raise_item(item)
        self.update_connections()
        self.recalculate_bounds()
        self.updated.emit()

class Canvas(QGraphicsView):
    edited=Signal()
    def __init__(self,catalog,parent=None):
        super().__init__(parent);self.catalog=catalog;self.current_document=None
        self.board=VisualScene(catalog);self.setScene(self.board);self.board.updated.connect(self.edited.emit)
        self.setRenderHint(QPainter.Antialiasing);self.setAcceptDrops(True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self._pan=False;self._last=None;self._pinch=1.0;self._hand_mode=False
        self.grabGesture(Qt.PinchGesture)
        self.viewport().setAttribute(Qt.WA_AcceptTouchEvents,True)
        self.viewport().installEventFilter(self)
        self._touch_points={};self._touch_distance=None;self._touch_center=None
        self._touch_section=None;self._touch_section_start=None;self._touch_start=None
        self._nested_press=None;self._nested_press_point=None
        self._variable_press=None;self._variable_press_point=None
        self._text_mouse_target=None
        self.setMouseTracking(True)
        self._drag_edge_timer=QTimer(self)
        self._drag_edge_timer.setInterval(35)
        self._drag_edge_timer.timeout.connect(self._auto_pan_during_drag)
        self._drag_edge_margin=65

    def _auto_pan_during_drag(self):
        point=self.viewport().mapFromGlobal(QCursor.pos())
        rect=self.viewport().rect()
        if not rect.contains(point) or not self._drag_edge_timer.isActive():
            return
        margin=self._drag_edge_margin
        def velocity(value,limit):
            if value<margin:return -max(2,round((margin-value)/margin*19))
            if value>limit-margin:return max(2,round((value-(limit-margin))/margin*19))
            return 0
        dx=velocity(point.x(),rect.width())
        dy=velocity(point.y(),rect.height())
        self._grow_for_scroll(dx,dy)
        if dx:self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+dx)
        if dy:self.verticalScrollBar().setValue(self.verticalScrollBar().value()+dy)

    def dragLeaveEvent(self,event):
        self._drag_edge_timer.stop()
        super().dragLeaveEvent(event)

    def load_document(self,document,show_data_sections=False):
        self.current_document=document
        self.board.show_data_sections=show_data_sections
        self.board.load(document)
    def focus_diagnostic(self, section_id, block_id=''):
        """Show the affected block centered horizontally, near the viewport top."""
        section=self.board.items_by_id.get(section_id)
        if section is None:
            return False
        target=section.sceneBoundingRect()
        if block_id:
            panel=section.widget()
            if panel is not None:
                for widget in panel.findChildren(BlockWidget):
                    if widget.block.id!=block_id:
                        continue
                    position=widget.mapTo(panel,QPoint(0,0))
                    corner=section.mapToScene(QPointF(position.x(),position.y()))
                    target=QRectF(corner,QSizeF(widget.width(),widget.height()))
                    # Keep the focus visible rather than just selecting the
                    # whole event/function container.
                    highlight='QFrame#block {border:3px solid #f6cb65;}'
                    if highlight not in widget.styleSheet():
                        widget.setStyleSheet(widget.styleSheet()+highlight)
                    break
        section.setSelected(True)
        from ..diagnostic_navigation import viewport_focus_center
        center_x,center_y=viewport_focus_center(target.center().x(),target.top(),
                                                self.viewport().height(),self.transform().m11())
        # A fixed scene rectangle otherwise prevents alignment for blocks
        # positioned very close to its bottom/right edge.
        scale=self.transform().m11()
        margin_x=self.viewport().width()/(2*scale)+60
        margin_y=self.viewport().height()/(2*scale)+60
        needed=QRectF(QPointF(center_x-margin_x,center_y-margin_y),
                      QPointF(center_x+margin_x,center_y+margin_y))
        self.board.setSceneRect(self.board.sceneRect().united(needed))
        self.centerOn(QPointF(center_x,center_y))
        return True

    def zoom(self,factor):
        current=self.transform().m11();factor=max(.25/current,min(3.0/current,factor))
        self.scale(factor,factor)
    def wheelEvent(self,event):
        if event.modifiers() & Qt.ControlModifier:
            self.zoom_at(1.12 if event.angleDelta().y()>0 else 1/1.12,event.position().toPoint())
            event.accept()
        else:
            delta=event.angleDelta()
            self._grow_for_scroll(-delta.x(),-delta.y())
            super().wheelEvent(event)
    def event(self,event):
        if event.type()==QEvent.Gesture:
            from PySide6.QtWidgets import QPinchGesture
            pinch=event.gesture(Qt.PinchGesture)
            if pinch:
                previous=pinch.lastScaleFactor()
                self.zoom(pinch.scaleFactor()/previous if previous else pinch.scaleFactor());return True
        return super().event(event)
    def clamp_section_position(self,point):
        # Scratch-like infinite workspace: enlarge instead of clamping titles
        # to the old fixed rectangle; works in all four directions.
        self.board.ensure_position(point)
        return point

    def _grow_for_scroll(self, dx=0, dy=0):
        h=self.horizontalScrollBar()
        v=self.verticalScrollBar()
        self.board.expand_at_edges(left=dx < 0 and h.value() <= h.minimum()+2,
                                   right=dx > 0 and h.value() >= h.maximum()-2,
                                   top=dy < 0 and v.value() <= v.minimum()+2,
                                   bottom=dy > 0 and v.value() >= v.maximum()-2)

    def _precise_widget_at(self, viewport_pos):
        """Hit test via scene coordinates without trusting QWidget.childAt().

        This is only used for interaction routing.  It never alters section
        dimensions, so it cannot reintroduce the 26.3 resize feedback loop.
        """
        scene_point=self.mapToScene(viewport_pos.toPoint() if hasattr(viewport_pos,'toPoint') else viewport_pos)
        # Reverse insertion order before sorting by Z: even if an older saved
        # scene happens to contain equal Z values, Qt puts the later-added item
        # on top, so our hit test must use that same order.
        sections=sorted(reversed(tuple(self.board.items_by_id.values())),
                        key=lambda item:item.zValue(), reverse=True)
        for section in sections:
            if section.scene() is not self.board or not section.isVisible():
                continue
            root=section.widget()
            if root is None or not root.isVisible():
                continue
            local=section.mapFromScene(scene_point).toPoint()
            hit=_deepest_visible_widget(root,local)
            # The section panel itself is opaque and receives clicks even when
            # the point isn't inside a child block.  An empty region of the
            # front panel must NOT let us select an editor on a covered section
            # behind it.  This was the overlap-dependent input failure.
            if hit is None and not (root.rect().contains(local) or
                                    section.boundingRect().contains(section.mapFromScene(scene_point))):
                continue
            control=_precise_control_at(root,local,(QLineEdit,QTextEdit,EmbeddedVariableReference))
            return root,control if control is not None else hit
        return None,None

    def _expression_at_viewport(self,viewport_pos):
        root,hit=self._precise_widget_at(viewport_pos)
        if root is None:return None,None
        return _nearest_embedded_expression(hit,root),hit

    def _text_editor_at_viewport(self,viewport_pos):
        root,hit=self._precise_widget_at(viewport_pos)
        while hit is not None and hit is not root:
            if isinstance(hit,(QLineEdit,QTextEdit)):
                return hit
            hit=hit.parentWidget()
        return None

    def _forward_text_mouse(self,widget,event):
        """Deliver mouse input to a clipped Qt text editor, preserving focus.

        The viewport is the source of mouse events even when QGraphicsProxyWidget
        fails to forward them past an out-of-date ancestor QRect. A single
        explicit delivery prevents the scene from also interpreting the press
        as canvas panning or an outer expression drag.
        """
        if widget is None or not widget.isVisible():return False
        vp=self.viewport()
        local=_local_pointer_pos(widget,self,event.position())
        global_pos=event.globalPosition()
        routed=QMouseEvent(event.type(),QPointF(local),global_pos,
                           event.button(),event.buttons(),event.modifiers())
        if event.type() in (QEvent.MouseButtonPress,QEvent.MouseButtonDblClick):
            # A QWidget hosted inside QGraphicsProxyWidget must have both
            # graphics-scene focus and ordinary QWidget keyboard focus.
            scene_point=self.mapToScene(event.position().toPoint())
            for item in sorted(self.board.items_by_id.values(),key=lambda x:x.zValue(),reverse=True):
                if item.scene() is self.board and item.widget() is not None:
                    root=item.widget()
                    if widget is root or root.isAncestorOf(widget):
                        self.board.setFocusItem(item,Qt.MouseFocusReason)
                        break
            widget.setFocus(Qt.MouseFocusReason)
        QApplication.sendEvent(widget,routed)
        event.accept()
        return True

    def _forward_text_context(self,widget,event):
        if isinstance(widget,QLineEdit):
            menu=widget.createStandardContextMenu()
            menu.exec(event.globalPos())
            return True
        if widget is not None:
            position=_local_pointer_pos(widget,self,event.pos())
            routed=QContextMenuEvent(QContextMenuEvent.Mouse,position,event.globalPos())
            QApplication.sendEvent(widget,routed)
            return True
        return False

    def _variable_reference_at_viewport(self,viewport_pos):
        """Find a nested variable token even beyond a stale parent widget rect."""
        root,hit=self._precise_widget_at(viewport_pos)
        while hit is not None and hit is not root:
            if isinstance(hit,EmbeddedVariableReference):return hit
            hit=hit.parentWidget()
        return None

    def _nested_press_target(self,viewport_pos):
        shell,hit=self._expression_at_viewport(viewport_pos)
        if shell is None:return None
        # Text editors, variable references and controls keep their native
        # handling.  Grip/background/labels may initiate a block drag.
        if isinstance(hit,(QLineEdit,QTextEdit,QComboBox,QPushButton,EmbeddedVariableReference)):
            return None
        return shell

    def _title_section_at(self,position):
        scene_pos=self.mapToScene(position.toPoint())
        for item in self.board.items(scene_pos):
            if not isinstance(item,SectionItem):continue
            widget=item.widget()
            if not widget:continue
            local=item.mapFromScene(scene_pos).toPoint()
            child=widget.childAt(local)
            while child is not None:
                if isinstance(child,DragTitle):return item
                child=child.parentWidget()
            return None
        return None

    def socket_at_viewport(self, viewport_pos):
        """Resolve deepest expression socket even when cursor is over its QLineEdit.

        QWidget children of a QGraphicsProxyWidget are not reliable recipients
        of every external drag/drop event. Hit-test explicitly in scene space.
        """
        root,hit=self._precise_widget_at(viewport_pos)
        while hit is not None and hit is not root:
            if isinstance(hit,ExpressionSlot):return hit
            hit=hit.parentWidget()
        return None

    def _drop_in_socket(self,event):
        mime=event.mimeData()
        if not any(mime.hasFormat(fmt) for fmt in (MIME_BLOCK,MIME_METHOD,MIME_MOVE,MIME_EXPR,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
            return False
        slot=self.socket_at_viewport(event.position())
        if slot is None:return False
        if self.embed_in_socket(mime,slot,event.keyboardModifiers()):
            self._drag_edge_timer.stop()
            event.acceptProposedAction()
            return True
        # A void/C-shaped/statement node can't enter a value socket.
        event.ignore()
        return True

    def eventFilter(self,obj,event):
        if obj is self.viewport():
            # Text editors have the same deep-hit problem as embedded blocks.
            # Route all phases of a single mouse gesture to one editor, even
            # if it lies outside an ancestor's stale input rectangle.
            if event.type()==QEvent.ContextMenu:
                editor=self._text_editor_at_viewport(event.pos())
                if editor is not None and self._forward_text_context(editor,event):
                    event.accept();return True
            if event.type()==QEvent.MouseButtonPress and event.button()==Qt.LeftButton:
                editor=self._text_editor_at_viewport(event.position())
                if editor is not None:
                    self._nested_press=None;self._nested_press_point=None
                    self._variable_press=None;self._variable_press_point=None
                    self._text_mouse_target=editor
                    return self._forward_text_mouse(editor,event)
                self._text_mouse_target=None
            if event.type() in (QEvent.MouseMove,QEvent.MouseButtonRelease,QEvent.MouseButtonDblClick):
                editor=self._text_mouse_target
                if editor is not None:
                    if event.type()==QEvent.MouseButtonDblClick or event.type()==QEvent.MouseMove and event.buttons() & Qt.LeftButton or event.type()==QEvent.MouseButtonRelease and event.button()==Qt.LeftButton:
                        handled=self._forward_text_mouse(editor,event)
                        if event.type()==QEvent.MouseButtonRelease:self._text_mouse_target=None
                        if handled:return True
            if event.type()==QEvent.ContextMenu:
                token=self._variable_reference_at_viewport(event.pos())
                if token is not None:
                    # Viewport context events carry a genuine global point;
                    # keep the same top-level popup path as native tokens.
                    token.show_reference_menu(self.viewport().mapToGlobal(event.pos()))
                    event.accept()
                    return True
                shell,hit=self._expression_at_viewport(event.pos())
                if shell is not None and not isinstance(hit,(QLineEdit,QTextEdit,EmbeddedVariableReference)):
                    shell.show_menu(event.globalPos())
                    event.accept()
                    return True
            if event.type()==QEvent.MouseButtonPress and event.button()==Qt.LeftButton:
                self._variable_press=None;self._variable_press_point=None
                token=self._variable_reference_at_viewport(event.position())
                if token is not None:
                    self._nested_press=None;self._nested_press_point=None
                    self._variable_press=token
                    self._variable_press_point=event.position()
                    event.accept()
                    return True
                shell=self._nested_press_target(event.position())
                if shell is not None:
                    self._nested_press=shell
                    self._nested_press_point=event.position()
                    event.accept()
                    return True
            if event.type()==QEvent.MouseMove and self._variable_press is not None:
                if not (event.buttons() & Qt.LeftButton):
                    self._variable_press=None;self._variable_press_point=None
                elif (event.position()-self._variable_press_point).manhattanLength()>=QApplication.startDragDistance():
                    token=self._variable_press
                    self._variable_press=None;self._variable_press_point=None
                    token.start_reference_drag()
                    event.accept()
                    return True
            if event.type()==QEvent.MouseButtonRelease and self._variable_press is not None:
                self._variable_press=None;self._variable_press_point=None
                event.accept()
                return True
            if event.type()==QEvent.MouseMove and self._nested_press is not None:
                if not (event.buttons() & Qt.LeftButton):
                    self._nested_press=None;self._nested_press_point=None
                elif (event.position()-self._nested_press_point).manhattanLength()>=QApplication.startDragDistance():
                    shell=self._nested_press
                    self._nested_press=None;self._nested_press_point=None
                    # Start the same QDrag used by the normal grip, but without
                    # relying on the clipped outer QWidget forwarding the event.
                    handles=shell.findChildren(EmbeddedExpressionDragHandle)
                    direct=next((h for h in handles if h.socket is shell.socket),None)
                    if direct is not None:direct.start_expression_drag()
                    event.accept()
                    return True
            if event.type()==QEvent.MouseButtonRelease and self._nested_press is not None:
                self._nested_press=None;self._nested_press_point=None
                event.accept()
                return True
        if obj is self.viewport() and event.type()==QEvent.Drop:
            self._drag_edge_timer.stop()
            if self._drop_in_socket(event):return True
        if obj is self.viewport() and event.type()==QEvent.DragLeave:
            self._drag_edge_timer.stop()
        if obj is self.viewport() and event.type()==QEvent.DragMove:
            if any(event.mimeData().hasFormat(fmt) for fmt in (MIME_BLOCK,MIME_EXPR,MIME_MOVE,MIME_METHOD,MIME_EVENT,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
                if not self._drag_edge_timer.isActive():self._drag_edge_timer.start()
            else:
                self._drag_edge_timer.stop()
            slot=self.socket_at_viewport(event.position())
            if slot is not None and any(event.mimeData().hasFormat(fmt) for fmt in (MIME_BLOCK,MIME_METHOD,MIME_MOVE,MIME_EXPR,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
                event.acceptProposedAction();return True
        if obj is self.viewport() and event.type() in (QEvent.TouchBegin,QEvent.TouchUpdate,QEvent.TouchEnd,QEvent.TouchCancel):
            points=event.points() if hasattr(event,'points') else []
            active=[p for p in points if getattr(p.state(), 'name', '') != 'Released']
            if event.type() in (QEvent.TouchEnd,QEvent.TouchCancel) or not active:
                if self._touch_section:
                    item=self._touch_section
                    item.model.x=item.pos().x();item.model.y=item.pos().y()
                    item.moved.emit()
                    self.board.update_connections()
                self._touch_section=None;self._touch_section_start=None;self._touch_start=None
                self._touch_center=None;self._touch_distance=None
                event.accept();return True
            if len(active)>=2:
                # A second finger always switches to canvas pinch/pan.
                self._touch_section=None;self._touch_section_start=None;self._touch_start=None
                a,b=active[0].position(),active[1].position()
                center=(a+b)/2
                from math import hypot
                distance=hypot(a.x()-b.x(),a.y()-b.y())
                if self._touch_distance and self._touch_distance>0:
                    self.zoom_at(distance/self._touch_distance,center.toPoint())
                if self._touch_center is not None:
                    delta=center-self._touch_center
                    self._grow_for_scroll(-round(delta.x()),-round(delta.y()))
                    self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-round(delta.x()))
                    self.verticalScrollBar().setValue(self.verticalScrollBar().value()-round(delta.y()))
                self._touch_distance=distance;self._touch_center=center
            else:
                pos=active[0].position()
                if event.type()==QEvent.TouchBegin or (self._touch_start is None and self._touch_center is None):
                    self._touch_start=pos
                    self._touch_section=self._title_section_at(pos)
                    self._touch_section_start=QPointF(self._touch_section.pos()) if self._touch_section else None
                if self._touch_section is not None and self._touch_start is not None:
                    # All distances are measured in viewport coordinates and converted
                    # into scene coordinates; global screen coordinates are unreliable
                    # for synthesized touch mouse events.
                    current_scene=self.mapToScene(pos.toPoint())
                    start_scene=self.mapToScene(self._touch_start.toPoint())
                    target=self._touch_section_start+(current_scene-start_scene)
                    self._touch_section.move_from_user(self.clamp_section_position(target))
                    self.board.update_connections()
                elif self._touch_center is not None and self._touch_distance is None:
                    delta=pos-self._touch_center
                    self._grow_for_scroll(-round(delta.x()),-round(delta.y()))
                    self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-round(delta.x()))
                    self.verticalScrollBar().setValue(self.verticalScrollBar().value()-round(delta.y()))
                self._touch_center=pos;self._touch_distance=None
            event.accept();return True
        return super().eventFilter(obj,event)
    def zoom_at(self,factor,position):
        before=self.mapToScene(position)
        self.zoom(factor)
        after=self.mapToScene(position)
        delta=after-before
        self.translate(delta.x(),delta.y())
    def _text_is_being_edited(self):
        from PySide6.QtWidgets import QPlainTextEdit
        widget=QApplication.focusWidget()
        if isinstance(widget, (QLineEdit,QTextEdit,QPlainTextEdit)):
            return not widget.isReadOnly()
        if isinstance(widget,QComboBox):
            return widget.isEditable()
        return False

    def keyPressEvent(self,event):
        # No Space shortcut: text fields and raw Squirrel editors own their keys.
        super().keyPressEvent(event)
    def keyReleaseEvent(self,event):
        super().keyReleaseEvent(event)
    def mousePressEvent(self,event):
        # Clicking outside a text editor commits the edit and clears its focus.
        empty=self.itemAt(event.position().toPoint()) is None
        if event.button()==Qt.LeftButton:
            # Clicking any non-text area (including another block/header) ends
            # editing; clicking *inside* the current editor keeps caret/selection.
            from PySide6.QtWidgets import QPlainTextEdit
            focused=QApplication.focusWidget()
            if isinstance(focused,(QLineEdit,QTextEdit,QPlainTextEdit)):
                point=focused.mapFromGlobal(self.viewport().mapToGlobal(event.position().toPoint()))
                if not focused.rect().contains(point):
                    focused.clearFocus()
        if event.button()==Qt.MiddleButton or event.button()==Qt.LeftButton and (self._hand_mode or empty):
            self._pan=True;self._last=event.position().toPoint();self.viewport().setCursor(Qt.ClosedHandCursor);event.accept();return
        super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        if self._pan and self._last is not None:
            pt=event.position().toPoint();delta=pt-self._last;self._last=pt
            self._grow_for_scroll(-delta.x(),-delta.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-delta.y())
            event.accept();return
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self,event):
        self._drag_edge_timer.stop()
        if self._pan:self._pan=False;self.viewport().unsetCursor();event.accept();return
        super().mouseReleaseEvent(event)
    def dragEnterEvent(self,event):
        if any(event.mimeData().hasFormat(fmt) for fmt in (MIME_BLOCK,MIME_EXPR,MIME_MOVE,MIME_METHOD,MIME_EVENT,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
            self._drag_edge_timer.start()
            event.acceptProposedAction()
        else:super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        if any(event.mimeData().hasFormat(fmt) for fmt in (MIME_BLOCK,MIME_EXPR,MIME_MOVE,MIME_METHOD,MIME_EVENT,MIME_FUNCTION_CALL,MIME_PROJECT_FILE,MIME_EMBEDDED_COPY,MIME_SCOPE_MEMBER)):
            if not self._drag_edge_timer.isActive():self._drag_edge_timer.start()
            event.acceptProposedAction()
        else:super().dragMoveEvent(event)
    def delete_existing_block(self,block_id):
        document=getattr(self.board,'owner_document',None) or self.current_document
        if not document or not remove_block(document,block_id):
            return False
        self.board.refresh_sections()
        self.edited.emit()
        return True

    def delete_embedded_block(self,expression_id):
        from ..expressions import remove_embedded_expression
        document=getattr(self.board,'owner_document',None) or self.current_document
        if not document or not remove_embedded_expression(document,expression_id):
            return False
        self.board.refresh_sections()
        self.edited.emit()
        return True

    def embed_in_socket(self,mime,socket,modifiers=Qt.NoModifier):
        """Embed an expression-capable block in a live argument slot.

        Statement/C-shaped/void blocks cannot be embedded. A moved expression is
        removed from its source only after the new target has been validated.
        """
        block=None
        moving=None
        if mime.hasFormat(MIME_SCOPE_MEMBER):
            payload=json.loads(bytes(mime.data(MIME_SCOPE_MEMBER)).decode('utf-8'))
            doc=getattr(self.board,'owner_document',None) or self.current_document
            target_section,target_block_id=resolve_socket_statement(socket.owner)
            if not target_section:return False
            from ..scope_members import scope_member_candidates
            paths=scope_member_candidates(doc,payload,target_section.model,target_block_id)
            if not paths:return False
            if len(paths)>1:
                from PySide6.QtWidgets import QInputDialog
                if current_profile().language=='zh':
                    heading,question='选择 ScriptScope','当前区域有多个 ScriptScope 变量，请选择成员的引用路径：'
                else:
                    heading,question='Select ScriptScope','Multiple ScriptScope variables are available. Select the reference path:'
                path,ok=QInputDialog.getItem(self,heading,question,paths,0,False)
                if not ok:return False
            else:
                path=paths[0]
            socket.replace({'kind':'variable_ref','path':path,'name':path.rsplit('.',1)[-1],
                            'symbol_id':payload['member_id'],'section_id':target_section.model.id})
            self.edited.emit()
            return True
        if mime.hasFormat(MIME_EXPR):
            param_payload=json.loads(bytes(mime.data(MIME_EXPR)).decode('utf-8'))
            if param_payload.get('parameter'):
                target_section,_=resolve_socket_statement(socket.owner)
                if not target_section or target_section.model.id!=param_payload.get('section_id'):
                    return False
                socket.replace({'kind':'variable_ref','name':param_payload['name'],
                                'path':param_payload.get('path') or param_payload['name'],
                                'section_id':param_payload['section_id'],
                                'symbol_id':param_payload['id']})
                self.edited.emit();return True
        if mime.hasFormat(MIME_PROJECT_FILE):
            name=project_drag_payload(mime).get('name','')
            scene=socket.owner.root_section.scene()
            project=getattr(getattr(scene,'views',lambda:[])()[0].window(),'project',None) if scene and scene.views() else None
            if project is None or name not in [d.name for d in project.documents]:return False
            socket.replace(json.dumps(name.removesuffix('.nut'), ensure_ascii=False))
            return True
        if mime.hasFormat(MIME_EMBEDDED_COPY):
            value=json.loads(bytes(mime.data(MIME_EMBEDDED_COPY)).decode("utf-8"))
            if not is_embedded(value):return False
            block=unpack_embedded(value)
        elif mime.hasFormat(MIME_FUNCTION_CALL):
            payload=json.loads(bytes(mime.data(MIME_FUNCTION_CALL)).decode("utf-8"))
            block=call_block_from_section_payload(payload)
        elif mime.hasFormat(MIME_METHOD):
            record=json.loads(bytes(mime.data(MIME_METHOD)).decode('utf-8'))
            block=block_from_method(record)
        elif mime.hasFormat(MIME_BLOCK):
            block=new_block_payload(bytes(mime.data(MIME_BLOCK)).decode('utf-8'))
        elif mime.hasFormat(MIME_MOVE):
            moving=bytes(mime.data(MIME_MOVE)).decode('utf-8')
            document=getattr(self.board,'owner_document',None) or self.current_document
            found=locate_block(document,moving)
            if found:block=found[2]
        elif mime.hasFormat(MIME_EXPR):
            payload=json.loads(bytes(mime.data(MIME_EXPR)).decode('utf-8'))
            doc=getattr(self.board,'owner_document',None) or self.current_document
            resolved=payload.get('path') or reference_for_symbol(doc,payload.get('id'))
            if payload.get('scope')=='local':
                # EmbeddedOwner is a recursive expression adapter, not a BlockWidget.
                # Resolve to the outermost real statement for lexical scope checks.
                section,destination=resolve_socket_statement(socket.owner)
                if section is None or payload.get('section_id')!=section.model.id:return False
                if not visible_local(section.model,payload.get('id'),destination):return False
            path=resolved or payload['name']
            socket.replace({'kind':'variable_ref','path':path,'name':payload.get('name',path),'symbol_id':payload.get('id'),'section_id':payload.get('section_id')})
            self.edited.emit()
            return True
        if block is None or not can_embed(block):return False
        # Do not move a statement into one of its own descendant sockets.
        if moving and moving in embedded_ids(socket.owner.block):return False
        if moving and moving==socket.owner.block.id:return False
        try:value=as_embedded(block)
        except ValueError:return False
        if moving and not (modifiers & Qt.ControlModifier):
            if not remove_block(document,moving):return False
        socket.replace(value)
        if moving:QTimer.singleShot(0,self.board.refresh_sections)
        self.edited.emit()
        return True

    def dropEvent(self,event):
        self._drag_edge_timer.stop()
        if self._drop_in_socket(event):return
        point=self.mapToScene(event.position().toPoint())
        section=next((i for i in self.board.items(point) if isinstance(i,SectionItem)),None)
        if section is None:
            event.ignore();return
        local=section.mapFromScene(point).toPoint()
        root=section.widget();child=root.childAt(local)
        target_list=section.model.blocks
        insert_index=len(target_list)
        # Header strip of any C-shaped branch is an insertion position before item 0.
        # childAt can hit the branch label instead of the first BlockWidget.
        branch_header=None
        probe=child
        while probe is not None and probe is not root:
            if hasattr(probe,'_branch_target'):
                branch_header=probe
                break
            probe=probe.parentWidget()
        if branch_header is not None:
            parent,key=branch_header._branch_target
            inner=branch_header.layout()
            first=next((inner.itemAt(i).widget() for i in range(inner.count()) if isinstance(inner.itemAt(i).widget(),BlockWidget)),None)
            if first is None or branch_header.mapFrom(root,local).y()<first.y()+min(first.height()*.25,16):
                target_list=parent.branches[key]
                insert_index=0
                child=branch_header
        # Find the innermost statement OR branch under the pointer.
        # A hovered block inserts before/after at its vertical midpoint.
        node=child
        while node is not None and node is not root:
            if isinstance(node,BlockWidget):
                target_list=node.collection
                insert_index=target_list.index(node.block)+(1 if node.mapFrom(root,local).y()>=node.height()/2 else 0)
                break
            if hasattr(node,'_branch_target'):
                parent,key=node._branch_target
                target_list=parent.branches[key]
                insert_index=0 if node is branch_header else len(target_list)
                break
            node=node.parentWidget()
        mime=event.mimeData()
        owning_document=getattr(self.board,'owner_document',None) or self.current_document
        if mime.hasFormat(MIME_SCOPE_MEMBER):
            from ..scope_members import copy_scope_reference
            payload=json.loads(bytes(mime.data(MIME_SCOPE_MEMBER)).decode('utf-8'))
            if section.model.kind!='data' or section.model.args.get('container')!='Table':
                event.ignore();return
            try:
                new_member=copy_scope_reference(owning_document,payload,section.model)
            except ValueError as exc:
                QMessageBox.warning(self,'ScriptScope 引用',str(exc));event.ignore();return
            target_list.insert(insert_index,new_member)
            QTimer.singleShot(0,self.board.refresh_sections)
        elif mime.hasFormat(MIME_EMBEDDED_COPY):
            event.ignore();return
        elif mime.hasFormat(MIME_MOVE):
            block_id=bytes(mime.data(MIME_MOVE)).decode('utf-8')
            from ..block_reorder import locate_block
            source=locate_block(owning_document,block_id)
            source_section=source[0] if source else None
            if (source and source_section.kind=='data' and section.model.kind=='data'
                    and source_section.id != section.model.id
                    and source[2].kind=='var'
                    and source[2].args.get('init_mode')!='reference'):
                from ..scope_members import copy_scope_reference
                payload={'source_section_id':source_section.id,'member_id':block_id,
                         'name':source[2].args.get('name','')}
                try:
                    new_member=copy_scope_reference(owning_document,payload,section.model)
                except ValueError as exc:
                    QMessageBox.warning(self,'ScriptScope 引用',str(exc));event.ignore();return
                target_list.insert(insert_index,new_member)
                QTimer.singleShot(0,self.board.refresh_sections)
                self.edited.emit()
                event.acceptProposedAction()
                return
            if event.keyboardModifiers() & Qt.ControlModifier:
                from ..block_reorder import locate_block
                found=locate_block(owning_document,block_id)
                if not found or not accepts_block(section.model,target_list,found[2].kind):
                    event.ignore();return
                target_list.insert(insert_index,clone_with_definitions(owning_document,found[2]))
            elif not move_block(owning_document,block_id,section.model,target_list,insert_index):
                event.ignore();return
            # Rebuild visible widgets only; never clear scene or reset section origins.
            QTimer.singleShot(0,self.board.refresh_sections)
        elif mime.hasFormat(MIME_FUNCTION_CALL):
            payload=json.loads(bytes(mime.data(MIME_FUNCTION_CALL)).decode('utf-8'))
            if not accepts_block(section.model,target_list,'string_call' if payload.get('as_string') else 'call'):
                event.ignore();return
            target_list.insert(insert_index,call_block_from_section_payload(payload))
            QTimer.singleShot(0,section.refresh)
        elif mime.hasFormat(MIME_METHOD):
            record=json.loads(bytes(mime.data(MIME_METHOD)).decode('utf-8'))
            if not accepts_block(section.model,target_list,'method'):
                event.ignore();return
            block=block_from_method(record)
            target_list.insert(insert_index,block)
            QTimer.singleShot(0,section.refresh)
        elif mime.hasFormat(MIME_EVENT):
            if section.model.kind!='events':event.ignore();return
            payload=json.loads(bytes(mime.data(MIME_EVENT)).decode('utf-8'))
            block=new_block('event');block.args['event']=payload['name'];block.args['env']='env'
            target_list.insert(insert_index,block)
            QTimer.singleShot(0,section.refresh)
        elif mime.hasFormat(MIME_BLOCK):
            kind=bytes(mime.data(MIME_BLOCK)).decode()
            actual_kind=kind.split(':',1)[0]
            if not accepts_block(section.model,target_list,actual_kind):
                event.ignore();return
            target_list.insert(insert_index,new_block_payload(kind))
            QTimer.singleShot(0,section.refresh)
        elif mime.hasFormat(MIME_EXPR):
            payload=json.loads(bytes(mime.data(MIME_EXPR)).decode())
            resolved=payload.get('path') or reference_for_symbol(owning_document,payload.get('id')) or payload['name']
            if payload.get('scope')=='local':
                destination=child
                while destination is not None and not isinstance(destination,BlockWidget):
                    destination=destination.parentWidget()
                valid=(payload.get('section_id')==section.model.id and
                       destination is not None and visible_local(section.model,payload.get('id'),destination.block.id))
                if not valid:
                    QMessageBox.warning(self,'局部变量作用域','local 变量不能拖出其词法作用域，或引用尚未声明的局部变量。')
                    event.ignore();return
            if isinstance(child,QLineEdit):
                child.setText(resolved);child.textEdited.emit(resolved)
            else:
                QMessageBox.information(self,'变量引用','请把圆形变量拖放到积木的浅色输入框。')
                event.ignore();return
        self.edited.emit();event.acceptProposedAction()


class DefinitionWorkspace(QDialog):
    """Independent visual workspace for a complex variable, with its own canvas."""
    def __init__(self,document,section,catalog,parent=None):
        super().__init__(parent)
        from ..models import ScriptDocument
        from .palette import BlockPalette
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('复杂变量工作区 · '+section.name+' ('+section.args.get('container','Table')+')')
        self.resize(1200,750)
        lay=QVBoxLayout(self)
        caption=QLabel('固定根容器不能删除；在这里添加 Table/Array 成员。ScriptScope 的成员在获取实体作用域后用 <- 创建；Array 的 append 等操作在初始化完成后执行。')
        caption.setWordWrap(True);lay.addWidget(caption)
        row=QHBoxLayout();lay.addLayout(row,1)
        palette_column=QWidget();palette_layout=QVBoxLayout(palette_column)
        palette_layout.setContentsMargins(0,0,0,0)
        palette=BlockPalette(catalog=catalog);palette_layout.addWidget(palette,1)
        palette_column.setFixedWidth(300);row.addWidget(palette_column)
        self.canvas=Canvas(catalog,self)
        self.canvas.load_document(ScriptDocument(document.name,[section]),show_data_sections=True)
        palette.blockDropped.connect(self.canvas.delete_existing_block)
        palette.embeddedDropped.connect(self.canvas.delete_embedded_block)
        self.canvas.board.owner_document=document
        row.addWidget(self.canvas,1)
        from .scope_palette import ScopeMemberPalette
        self.scope_palette=ScopeMemberPalette(document,section)
        lay.addWidget(self.scope_palette)
        self.canvas.edited.connect(self.scope_palette.reload)
        actions=QHBoxLayout();lay.addLayout(actions)
        minus=QPushButton('－');plus=QPushButton('＋');reset=QPushButton('100%');close=QPushButton('完成 / 返回主工作区')
        for button in (minus,reset,plus,close):actions.addWidget(button)
        minus.clicked.connect(lambda:self.canvas.zoom(.8))
        plus.clicked.connect(lambda:self.canvas.zoom(1.25))
        reset.clicked.connect(lambda:self.canvas.resetTransform())
        close.clicked.connect(self.accept)
