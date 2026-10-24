"""Project-zone trash targets for QDrag statement blocks."""
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtWidgets import QTreeWidget, QLabel
from PySide6.QtGui import QDrag
from .file_drop import MIME_PROJECT_FILE
from .localization import translated_text
from .canvas import MIME_MOVE, MIME_EMBEDDED_MOVE

class ProjectTrashMixin:
    def _accepts(self,event):
        if event.mimeData().hasFormat(MIME_MOVE) or event.mimeData().hasFormat(MIME_EMBEDDED_MOVE):
            event.acceptProposedAction();return True
        return False
    def dragEnterEvent(self,event):
        if not self._accepts(event):super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        if not self._accepts(event):super().dragMoveEvent(event)
    def dropEvent(self,event):
        if self._accepts(event):
            if event.mimeData().hasFormat(MIME_EMBEDDED_MOVE):
                self.embeddedDropped.emit(bytes(event.mimeData().data(MIME_EMBEDDED_MOVE)).decode('utf-8'))
            else:
                self.blockDropped.emit(bytes(event.mimeData().data(MIME_MOVE)).decode('utf-8'))
        else:super().dropEvent(event)

class ProjectTree(ProjectTrashMixin,QTreeWidget):
    blockDropped=Signal(str)
    embeddedDropped=Signal(str)
    fileMoved=Signal(str,str)
    folderMoved=Signal(str,str)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDrop)
        self.setDragEnabled(True)
    def dragEnterEvent(self,event):
        if event.mimeData().hasFormat(MIME_PROJECT_FILE):
            event.acceptProposedAction();return
        super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        if event.mimeData().hasFormat(MIME_PROJECT_FILE):
            target=self.itemAt(event.position().toPoint())
            meta=target.data(0,Qt.UserRole) if target else None
            if isinstance(meta,tuple) and meta[0] in ("folder","root"):
                event.acceptProposedAction();return
            event.ignore();return
        super().dragMoveEvent(event)
    def dropEvent(self,event):
        if event.mimeData().hasFormat(MIME_PROJECT_FILE):
            target=self.itemAt(event.position().toPoint())
            meta=target.data(0,Qt.UserRole) if target else None
            if isinstance(meta,tuple) and meta[0] in ("folder","root"):
                import json
                data=json.loads(bytes(event.mimeData().data(MIME_PROJECT_FILE)).decode("utf-8"))
                if isinstance(data,dict) and data.get("kind")=="folder":
                    src=data.get("folder","");dest=meta[1] if meta[0]=="folder" else ""
                    if src and dest!=src and not dest.startswith(src+"/"):
                        self.folderMoved.emit(src,dest)
                        event.acceptProposedAction();return
                if isinstance(data,dict) and data.get("file_id"):
                    self.fileMoved.emit(data["file_id"],meta[1] if meta[0]=="folder" else "")
                    event.acceptProposedAction();return
            event.ignore();return
        super().dropEvent(event)
    def startDrag(self,supportedActions):
        item=self.currentItem()
        if item is None:return
        name=item.data(0,Qt.UserRole+1)
        import json
        meta=item.data(0,Qt.UserRole)
        if not isinstance(meta,tuple):return
        if meta[0]=='folder' and meta[1]:
            data={'kind':'folder','folder':meta[1]}
        elif meta[0]=='file' and isinstance(name,str) and name.endswith('.nut'):
            data={'kind':'file','name':name,'file_id':meta[1]}
        else:return
        mime=QMimeData();mime.setData(MIME_PROJECT_FILE,json.dumps(data).encode('utf-8'))
        drag=QDrag(self);drag.setMimeData(mime);drag.exec(Qt.CopyAction|Qt.MoveAction)
        self.setToolTip(translated_text('可将 .nut 文件拖入 IncludeScript 参数槽，也可将文件和文件夹移动至其他文件夹'))

class TrashZone(ProjectTrashMixin,QLabel):
    blockDropped=Signal(str)
    embeddedDropped=Signal(str)
    def __init__(self,parent=None):
        super().__init__('  ⌫  拖动已有积木到这里快速删除  ',parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(44)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('QLabel{background:#42282e;color:#ffd1ca;border:2px dashed #bb6573;border-radius:9px;font-weight:bold;}')
