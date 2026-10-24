"""Windows smoke test for a PySide6 installation. No game installation needed.

Run: py -3 tools/gui_smoke.py
Qt should be present. This test does not simulate real touch hardware.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication
from l4visual.ui.main_window import MainWindow
from l4visual.models import Block, Section
from l4visual.expressions import block_from_method

app=QApplication.instance() or QApplication([])
window=MainWindow()
app.processEvents()
canvas=window.canvas
section=window.current_doc.sections[0]
item=canvas.board.items_by_id[section.id]
original=(section.x,section.y)
item.update_size();app.processEvents()
assert (item.pos().x(),item.pos().y())==original, 'Resize moved an existing section'
section.blocks.append(Block('assign',{'target':'test_pos','value':'100'}))
canvas.board.refresh_sections([section.id]);app.processEvents()
assert (section.x,section.y)==original, 'Adding blocks changed an existing section origin'
assert (item.pos().x(),item.pos().y())==original, 'Adding blocks visually moved section'
new=Section('function','SmokeSection',x=500,y=600)
window.current_doc.sections.append(new)
canvas.board.add_section_item(new);app.processEvents()
assert (item.pos().x(),item.pos().y())==original, 'Adding section repositioned old section'
row=window.catalog.method('CBaseEntity','SetOrigin')
assert row
block=block_from_method(row)
assert len(block.args['parameters'])==1
item2=canvas.board.items_by_id[new.id]
new.blocks.append(block)
item2.update_size();app.processEvents()
assert (item.pos().x(),item.pos().y())==original
window.catalog.close()
print('GUI smoke test PASS — section origins stable, method slots generated')

# v0.7.1: an oval method must land inside the declaration's value socket,
# including when the cursor is above the socket's QLineEdit child.
import json
from PySide6.QtCore import QMimeData,Qt
from l4visual.ui.canvas import BlockWidget,ExpressionSlot,MIME_METHOD
from l4visual.variable_types import change_variable_type
sample_var=Block('var',{'name':'position','container_type':'普通','value':'0','scope':'local'})
new.blocks.append(sample_var)
item2.update_size();app.processEvents()
widgets=item2.widget().findChildren(BlockWidget)
var_widget=next(w for w in widgets if w.block is sample_var)
value_slot=next(s for s in var_widget.findChildren(ExpressionSlot) if s.key=='value')
from PySide6.QtCore import QPointF
scene_point=item2.mapToScene(QPointF(value_slot.mapTo(item2.widget(),value_slot.rect().center())))
viewport_point=canvas.mapFromScene(scene_point)
assert canvas.socket_at_viewport(viewport_point) is value_slot, 'Value slot is not hit-testable through proxy widget'
record=window.catalog.method('CBaseEntity','GetOrigin')
mime=QMimeData();mime.setData(MIME_METHOD,json.dumps(record).encode('utf-8'))
assert canvas.embed_in_socket(mime,value_slot,Qt.NoModifier), 'Official method cannot be dropped into value'
app.processEvents()
assert sample_var.args['value']['kind']=='embedded_block', 'Embedding did not update the AST'

# Changing the variable's kind must replace its template and visible editor.
change_variable_type(window.current_doc,sample_var,'Table')
item2.update_size();app.processEvents()
assert sample_var.args['value']=='{}', 'Table template not applied'
var_widget=next(w for w in item2.widget().findChildren(BlockWidget) if w.block is sample_var)
assert any('打开数据定义' in b.text() for b in var_widget.findChildren(__import__('PySide6.QtWidgets',fromlist=['QPushButton']).QPushButton)), 'Data workspace action missing after switch'
change_variable_type(window.current_doc,sample_var,'Set')
item2.update_size();app.processEvents()
assert sample_var.args['value']=='[]', 'Set template not applied'
assert (item2.pos().x(),item2.pos().y())==(500,600), 'Variable type refresh moved section'
assert (item.pos().x(),item.pos().y())==original, 'Variable type refresh moved another section'
print('v0.7.1 GUI checks PASS — value sockets, method embeddings, type templates')

# v0.7.2: ownership links do not alter section coordinates.
from l4visual.ui.dialogs import SectionEditor
from PySide6.QtWidgets import QComboBox
new.args['owner']='MyScript'
canvas.board.update_connections()
assert len(canvas.board._links)>=1, 'Function to Namespace link not created'
editor=SectionEditor(new,None,document=window.current_doc)
assert editor.owner.currentData()=='MyScript'
assert editor.owner.findData('Unregistered')<0
editor.type.setCurrentIndex(editor.type.findData('events'))
assert not editor.owner.isEnabled() and not editor.owner.currentData(), 'Unused namespace field not cleared'
assert not editor.params.isEnabled() and not editor.params.text(), 'Unused parameters not cleared'
assert (item.pos().x(),item.pos().y())==original
print('v0.7.2 GUI checks PASS — namespace link, owner selector, inactive fields')
