"""Drag a project .nut file as a script-name string."""
from PySide6.QtCore import Qt,QMimeData
from PySide6.QtWidgets import QTreeWidget,QLineEdit
MIME_PROJECT_FILE='application/x-l4dv-project-nut'

def project_drag_payload(mime):
    import json
    raw=bytes(mime.data(MIME_PROJECT_FILE)).decode('utf-8')
    try:
        value=json.loads(raw)
    except ValueError:
        return {'name':raw,'kind':'file'}
    return value if isinstance(value,dict) else {'name':raw,'kind':'file'}
class IncludeFileLineEdit(QLineEdit):
    def __init__(self,project,parent=None):
        super().__init__(parent);self.project=project;self.setAcceptDrops(True)
        self.setToolTip('Drop a .nut file to insert its script name (without .nut).')
    def dragEnterEvent(self,event):
        if event.mimeData().hasFormat(MIME_PROJECT_FILE):event.acceptProposedAction()
        else:super().dragEnterEvent(event)
    def dropEvent(self,event):
        if not event.mimeData().hasFormat(MIME_PROJECT_FILE):return super().dropEvent(event)
        filename=project_drag_payload(event.mimeData()).get('name','')
        if filename in [d.name for d in self.project.documents]:
            stem=filename[:-4] if filename.endswith('.nut') else filename
            self.setText(stem)
            event.acceptProposedAction()
