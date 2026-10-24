"""Shared TraceLine configuration for statement and nestable ray blocks."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QLabel, QDialogButtonBox)
from ..display_profile import current_profile
from ..quick_literals import LITERAL_GROUPS
from ..codegen import expression


from ..trace_config import TRACE_DEFAULTS, current_trace_values, update_trace_values

class TraceLineConfigDialog(QDialog):
    def __init__(self, block, parent=None):
        super().__init__(parent, Qt.Dialog)
        self.block = block
        self.english = current_profile().language == 'en'
        self.setWindowTitle('TraceLine configuration' if self.english else 'TraceLine 配置工作区')
        self.resize(625, 340)
        main = QVBoxLayout(self)
        help_text = ('Set the trace parameters. TraceLine writes hit/pos/enthit/fraction etc. '
                     'into the result table. The ray expression returns a table or null.'
                     if self.english else
                     '设置射线参数。TraceLine 将 hit/pos/enthit/fraction 等结果写入 Table；射线表达式返回 Table 或 null。')
        header = QLabel(help_text)
        header.setWordWrap(True)
        main.addWidget(header)
        form = QFormLayout()
        main.addLayout(form)
        self.old_values = current_trace_values(block)
        texts = [expression(value) for value in self.old_values]
        names = (('Start position (Vector)', 'End position (Vector)', 'Ignored entity', 'Collision mask (integer)')
                 if self.english else
                 ('起点（Vector）', '终点（Vector）', '忽略的实体', '碰撞掩码（整数）'))
        hints = (('Ray starting point; e.g. player.EyePosition()',
                  'Ray destination, not direction; e.g. start + forward * 1000',
                  'Entity ignored for collision, or null',
                  'Select a mask preset or enter a Squirrel integer expression')
                 if self.english else
                 ('射线起点，例如 player.EyePosition()',
                  '射线终点（不是方向），例如 start + forward * 1000',
                  '忽略碰撞的实体，也可填 null',
                  '选择掩码预设，或者输入 Squirrel 整数表达式'))
        self.fields = []
        for i in range(3):
            field = QLineEdit(texts[i])
            field.setToolTip(hints[i])
            form.addRow(names[i], field)
            self.fields.append(field)
        mask = QComboBox()
        mask.setEditable(True)
        mask.setToolTip(hints[3])
        for value, zh, en in LITERAL_GROUPS['trace_mask']['entries']:
            mask.addItem(f'{value} — {en if self.english else zh}', value)
        found = mask.findData(texts[3])
        if found >= 0:
            mask.setCurrentIndex(found)
        else:
            mask.setEditText(texts[3])
        form.addRow(names[3], mask)
        self.fields.append(mask)
        self.output = None
        if block.kind == 'trace_line':
            self.output = QLineEdit(str(block.args.get('output', 'trace')))
            self.output.setToolTip('Name of the result table variable; blank discards the result.' if self.english
                                   else '保存追踪结果的 Table 变量名；留空则不保存结果。')
            form.addRow('Output variable' if self.english else '结果变量名', self.output)
        note = QLabel(('Existing nested input blocks stay intact unless you change their value here. '
                       'Use the canvas sockets to drag expressions into parameters.' if self.english else
                       '原有嵌套参数在未修改时保持不变；需要拖入表达式积木请使用画布上的参数槽。'))
        note.setWordWrap(True)
        main.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main.addWidget(buttons)

    def accept(self):
        values = []
        for i, field in enumerate(self.fields):
            if i == 3:
                selected = field.currentData() if field.currentIndex() >= 0 and field.currentText() == field.itemText(field.currentIndex()) else field.currentText().strip()
                entered = str(selected)
            else:
                entered = field.text().strip()
            if not entered:
                entered = TRACE_DEFAULTS[i]
            old_code = expression(self.old_values[i])
            values.append(self.old_values[i] if entered == old_code else entered)
        update_trace_values(self.block, values)
        if self.output is not None:
            self.block.args['output'] = self.output.text().strip()
        super().accept()
