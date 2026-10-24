from __future__ import annotations
from PySide6.QtCore import Qt, QSize, QPoint, QMimeData, Signal, QEvent, QRect
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QDrag, QFont, QFontMetrics
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLineEdit, QLabel, QSizePolicy, QToolButton
from .dialogs import BLOCK_CATEGORIES, BLOCK_NAMES, DEFAULT_ARGS, BRANCHES
from ..display_profile import block_caption,method_caption,event_caption,current_profile,category_caption
from .canvas import MIME_BLOCK, MIME_METHOD, MIME_EVENT, MIME_MOVE, MIME_EMBEDDED_MOVE, COLORS
from .localization import localize_widget_tree, translated_text
from ..string_search import kmp_contains
import json

# A preview is also the drag source. It never creates a node until the canvas accepts the drop.
class PaletteBlock(QWidget):
    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind=kind
        self._press=None
        self.setCursor(Qt.OpenHandCursor)
        self.setMinimumHeight(92 if kind in BRANCHES else 44)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setToolTip(self._tooltip())
    def _tooltip(self):
        if self.kind == 'trace_line':
            if current_profile().language == 'en':
                return ('Drag to the source-block workspace. Right-click the TraceLine block '
                        'to configure start/end Vectors, ignored entity, collision mask and result-table variable. '
                        'Native TraceLine(table) writes collision fields into the table.')
            return ('拖入源码积木工作区。右键 TraceLine 积木，可配置起点/终点 Vector、'
                    '忽略实体、碰撞掩码和结果 Table 变量。原生 TraceLine(table) 将碰撞字段写入 Table。')
        return translated_text('拖入工作区：') + translated_text(BLOCK_NAMES.get(self.kind, self.kind))

    def sizeHint(self):
        return QSize(255, max(self.minimumHeight(), 92 if self.kind in BRANCHES else 44))

    def _text_width(self):
        return max(80, self.width()-32)

    def _wrapped_height(self, label, font=None):
        metrics=QFontMetrics(font or self.font())
        bounds=metrics.boundingRect(QRect(0,0,self._text_width(),100000),
                                    Qt.TextWordWrap|Qt.AlignLeft, str(label))
        return max(metrics.height(),bounds.height())

    def _set_card_height(self, height):
        height=max(44,int(height))
        if self.minimumHeight()!=height or self.maximumHeight()!=height:
            self.setMinimumHeight(height)
            self.setMaximumHeight(height)
            self.updateGeometry()

    def refresh_description(self):
        self.setToolTip(self._tooltip())
        self._resize_description()
        self.update()

    def _resize_description(self):
        font=QFont(self.font());font.setPointSize(9);font.setBold(True)
        height=max(44,92 if self.kind in BRANCHES else 44)
        if self.kind not in BRANCHES:
            height=max(height,18+QFontMetrics(font).boundingRect(QRect(0,0,max(65,self.width()-150),100000),Qt.TextWordWrap|Qt.AlignLeft,block_caption(self.kind)).height()+12)
        self._set_card_height(height)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._resize_description()

    def _shape(self):
        w=max(130,self.width()-8); h=self.height()-4
        c=self.kind in BRANCHES
        path=QPainterPath()
        # Expression outputs have oval/hexagonal connectors instead of the
        # top/bottom tabs used by independent statements.
        expression = self.kind in ('expr','operator','math_call','rawin','utility') or (self.kind == 'method' and
            hasattr(self,'record') and str(self.record.get('returns','')).lower() not in ('void','none'))
        if expression:
            if hasattr(self,'record') and str(self.record.get('returns','')).lower()=='bool':
                cut=min(h/2,19)
                path.moveTo(cut,2);path.lineTo(w-cut,2);path.lineTo(w-2,h/2)
                path.lineTo(w-cut,h-2);path.lineTo(cut,h-2);path.lineTo(2,h/2);path.closeSubpath()
            else:path.addRoundedRect(2,2,w-4,h-4,min(h/2,24),min(h/2,24))
            return path
        # Statement connector: notch on top, tab at bottom.
        path.moveTo(8,2);path.lineTo(24,2);path.lineTo(30,7);path.lineTo(51,7);path.lineTo(57,2)
        path.lineTo(w-9,2);path.quadTo(w-2,2,w-2,10)
        if c:
            path.lineTo(w-2,h-10);path.quadTo(w-2,h-4,w-9,h-4)
            path.lineTo(57,h-4);path.lineTo(51,h);path.lineTo(30,h);path.lineTo(24,h-4)
            path.lineTo(8,h-4);path.quadTo(2,h-4,2,h-10)
            path.lineTo(2,h-29);path.lineTo(23,h-29);path.lineTo(29,h-24)
            path.lineTo(51,h-24);path.lineTo(57,h-29);path.lineTo(w-21,h-29)
            path.lineTo(w-21,35);path.lineTo(2,35)
        else:
            path.lineTo(w-2,h-10);path.quadTo(w-2,h-4,w-9,h-4)
            path.lineTo(57,h-4);path.lineTo(51,h);path.lineTo(30,h);path.lineTo(24,h-4)
            path.lineTo(8,h-4);path.quadTo(2,h-4,2,h-10)
        path.lineTo(2,10);path.quadTo(2,2,8,2);path.closeSubpath()
        return path
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor('#ffffff55'),1))
        p.setBrush(QColor(COLORS.get(self.kind,'#596173')))
        p.drawPath(self._shape())
        p.setPen(QColor('#ffffff'))
        font=QFont(self.font());font.setPointSize(9);font.setBold(True);p.setFont(font)
        title=block_caption(self.kind)
        short={'method':block_caption('method'),'netprop':'NetProps','entity_for':block_caption('entity_for'),'foreach':block_caption('foreach')}
        if self.kind in BRANCHES:
            p.drawText(13,23,short.get(self.kind,title))
        else:
            p.drawText(QRect(13,8,max(65,self.width()-136),max(25,self.height()-12)),
                       Qt.AlignVCenter|Qt.TextWordWrap,short.get(self.kind,title))
        if self.kind in BRANCHES:
            p.setPen(QColor('#b8c7d9'));font.setBold(False);font.setPointSize(8);p.setFont(font)
            p.drawText(32,55,translated_text('将积木放入此处'))
        else:
            # Visually embedded input slot, not an editable field in the palette.
            vals=DEFAULT_ARGS.get(self.kind,{})
            label=str(next(iter(vals.values()),''))[:14]
            if label:
                p.setPen(Qt.NoPen);p.setBrush(QColor('#f3ebd9'))
                width=min(110,max(45,p.fontMetrics().horizontalAdvance(label)+16))
                x=max(108,self.width()-width-19)
                p.drawRoundedRect(x,10,width,24,7,7)
                p.setPen(QColor('#243246'));p.drawText(x+7,26,label)
        p.end()
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._press=event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData();mime.setData(MIME_BLOCK,self.kind.encode('utf-8'))
        drag.setMimeData(mime)
        pix=self.grab();drag.setPixmap(pix);drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)
    def mouseReleaseEvent(self,event):
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        event.accept()

class BooleanPaletteBlock(PaletteBlock):
    def __init__(self, value, parent=None):
        super().__init__('expr',parent)
        self.literal=value
        self.setToolTip(('Boolean constant: ' if current_profile().language=='en' else '布尔常量：')+value)
    def refresh_description(self):
        self.setToolTip(('Boolean constant: ' if current_profile().language=='en' else '布尔常量：')+self.literal)
        self.update()
    def _shape(self):
        w=max(130,self.width()-8);h=self.height()-4
        path=QPainterPath();cut=min(h/2,19)
        path.moveTo(cut,2);path.lineTo(w-cut,2);path.lineTo(w-2,h/2)
        path.lineTo(w-cut,h-2);path.lineTo(cut,h-2);path.lineTo(2,h/2);path.closeSubpath()
        return path
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor('#ffffff55'),1))
        painter.setBrush(QColor('#387d79'));painter.drawPath(self._shape())
        painter.setPen(QColor('white'));painter.drawText(18,27,self.literal)
        painter.end()
    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_BLOCK,('boolean:'+self.literal).encode())
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)

class OperatorPaletteBlock(PaletteBlock):
    def __init__(self,operator,parent=None):
        super().__init__('operator',parent)
        self.operator=operator
        self.setToolTip(translated_text('Squirrel 运算符 ')+operator+translated_text('；拖入 Value 或 If 条件槽，可修改左右操作数。'))
    def refresh_description(self):
        self.setToolTip(translated_text('Squirrel 运算符 ')+self.operator+translated_text('；拖入 Value 或 If 条件槽，可修改左右操作数。'))
        self.update()
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor('#ffffff55'),1));painter.setBrush(QColor(COLORS['operator']))
        painter.drawPath(self._shape());painter.setPen(QColor('white'))
        painter.drawText(16,27, ('! ( value )' if current_profile().language=='en' else '! ( 布尔值 )') if self.operator=='!' else (' ( left ' if current_profile().language=='en' else '( 左值  ')+self.operator+(' right )' if current_profile().language=='en' else '  右值 )'))
        painter.end()
    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_BLOCK,('operator:'+self.operator).encode())
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)

class CustomMathPaletteBlock(PaletteBlock):
    """Immediately draggable two-socket max/min expression."""
    def __init__(self, function, parent=None):
        super().__init__('math_call', parent)
        if function not in ('max', 'min'):
            raise ValueError('Unsupported custom math function')
        self.function=function
        self.refresh_description()

    def refresh_description(self):
        english=current_profile().language=='en'
        professional=current_profile().style=='professional'
        label='max(a, b)' if self.function=='max' else 'min(a, b)'
        meaning=(('Larger of two values' if self.function=='max' else 'Smaller of two values') if english else
                 ('返回两个值中的较大值' if self.function=='max' else '返回两个值中的较小值'))
        if professional:
            self.caption=label
        else:
            friendly=(('Maximum' if self.function=='max' else 'Minimum') if english else
                      ('较大值' if self.function=='max' else '较小值'))
            self.caption=friendly+' · '+label
        extra=('Two expression inputs; uses an automatically generated named Squirrel helper (not a built-in math function).' if english else
               '两个表达式参数；自动生成具名 Squirrel 辅助函数，不依赖原版 Math 内置函数。')
        self.setToolTip(self.caption+'\n'+meaning+'\n'+extra)
        self._resize_description()
        self.update()

    def _resize_description(self):
        font=QFont(self.font());font.setPointSize(9);font.setBold(True)
        self._set_card_height(max(44,self._wrapped_height(getattr(self,'caption','max(a, b)'),font)+20))

    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor('#ffffff55'),1))
        painter.setBrush(QColor(COLORS['math_call']));painter.drawPath(self._shape())
        painter.setPen(QColor('white'))
        font=QFont(self.font());font.setPointSize(9);font.setBold(True);painter.setFont(font)
        painter.drawText(QRect(15,7,max(55,self.width()-28),self.height()-12),Qt.AlignVCenter|Qt.TextWordWrap,self.caption)
        painter.end()

    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_BLOCK,('math:'+self.function).encode('utf-8'))
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)


class UtilityPaletteBlock(PaletteBlock):
    def __init__(self,operation,parent=None):
        super().__init__('utility',parent)
        from ..utility_blocks import UTILITY_BLOCKS
        self.operation=operation
        self.refresh_description()

    def refresh_description(self):
        from ..utility_blocks import UTILITY_BLOCKS
        info=UTILITY_BLOCKS[self.operation]
        from ..utility_blocks import utility_caption
        english=current_profile().language=='en'
        description=info.get('description_en') if english else info.get('description')
        # Never fall back from English to Chinese when a description is absent.
        if not description:
            description='No English description is available.' if english else '暂无中文说明。'
        self.setToolTip(utility_caption(info,current_profile().language,current_profile().style)+'\n'+description)
        self._resize_description()
        self.update()

    def _resize_description(self):
        from ..utility_blocks import UTILITY_BLOCKS
        font=QFont(self.font());font.setPointSize(9)
        info=UTILITY_BLOCKS[self.operation]
        from ..utility_blocks import utility_caption
        label=utility_caption(info,current_profile().language,current_profile().style)
        self._set_card_height(max(44,self._wrapped_height(label,font)+22))

    def paintEvent(self,event):
        from ..utility_blocks import UTILITY_BLOCKS
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(COLORS['utility']));painter.setPen(QPen(QColor('#ffffff55'),1))
        painter.drawPath(self._shape());painter.setPen(QColor('white'))
        info=UTILITY_BLOCKS[self.operation]
        from ..utility_blocks import utility_caption
        label=utility_caption(info,current_profile().language,current_profile().style)
        painter.drawText(self.rect().adjusted(14,6,-14,-6),Qt.AlignVCenter|Qt.AlignLeft|Qt.TextWordWrap,label)
        painter.end()
    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_BLOCK,('utility:'+self.operation).encode())
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)

class LiteralPaletteBlock(PaletteBlock):
    """Draggable quoted string constant, with language/style-specific caption."""
    def __init__(self, group, value, parent=None):
        super().__init__('expr',parent)
        self.group=group
        self.value=value
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.refresh_description()

    def refresh_description(self):
        from ..quick_literals import literal_tooltip
        p=current_profile()
        self.setToolTip(literal_tooltip(self.group,self.value,p.language,p.style))
        self._resize_description()
        self.update()

    def _resize_description(self):
        from ..quick_literals import literal_label
        p=current_profile()
        name=literal_label(self.group,self.value,p.language,p.style)
        font=QFont(self.font());font.setPointSize(9)
        self._set_card_height(max(44,20+self._wrapped_height(name,font)))

    def paintEvent(self,event):
        from ..quick_literals import literal_label
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor('#f2dba1'),1.2))
        painter.setBrush(QColor('#806536'))
        painter.drawPath(self._shape())
        painter.setPen(QColor('white'))
        p=current_profile()
        caption=literal_label(self.group,self.value,p.language,p.style)
        painter.drawText(self.rect().adjusted(14,5,-14,-5),Qt.AlignVCenter|Qt.AlignLeft|Qt.TextWordWrap,caption)
        painter.end()

    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_BLOCK,('literal:'+self.group+':'+self.value).encode('utf-8'))
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)


class OfficialMethodBlock(PaletteBlock):
    def __init__(self,record,parent=None):
        super().__init__('method',parent)
        self.record=record
        self.refresh_description()
        self._resize_description()

    def refresh_description(self):
        from ..api_docs import method_tooltip
        self.setToolTip(method_tooltip(self.record))
        self._resize_description()
        self.update()

    def _resize_description(self):
        from PySide6.QtGui import QFontMetrics
        width=max(180,self.width() or self.sizeHint().width())-28
        font=QFont(self.font());font.setPointSize(9)
        metrics=QFontMetrics(font)
        description=method_caption(self.record['name'],owner=self.record.get('owner',''))
        title=metrics.boundingRect(QRect(0,0,width,10000),Qt.TextWordWrap|Qt.AlignLeft,description)
        detail='('+str(self.record.get('parameters',''))+') → '+str(self.record.get('returns',''))
        detail_height=metrics.boundingRect(QRect(0,0,width,10000),Qt.TextWordWrap|Qt.AlignLeft,detail).height()
        target=max(54,14+title.height()+8+detail_height+12)
        if self.minimumHeight()!=target:
            self.setMinimumHeight(target)
            self.setMaximumHeight(target)
            self.updateGeometry()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._resize_description()

    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor('#ffffff55'),1));painter.setBrush(QColor(COLORS['method']))
        painter.drawPath(self._shape())
        painter.setPen(QColor('white'))
        font=QFont(self.font());font.setPointSize(9);painter.setFont(font)
        display=method_caption(self.record['name'],owner=self.record.get('owner',''))
        available=max(50,self.width()-28)
        title_rect=painter.fontMetrics().boundingRect(QRect(0,0,available,10000),Qt.TextWordWrap|Qt.AlignLeft,display)
        painter.drawText(QRect(13,9,available,title_rect.height()+3),Qt.TextWordWrap|Qt.AlignLeft,display)
        painter.setPen(QColor('#e0f8ed'))
        detail='('+str(self.record.get('parameters',''))+') → '+str(self.record.get('returns',''))
        painter.drawText(QRect(13,12+title_rect.height()+5,available,max(22,self.height()-title_rect.height()-17)),Qt.TextWordWrap|Qt.AlignLeft,detail)
        painter.end()
    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_METHOD,json.dumps(self.record,ensure_ascii=False).encode('utf-8'))
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14))
        drag.exec(Qt.CopyAction)

class ExternalMethodBlock(OfficialMethodBlock):
    def __init__(self, record, parent=None):
        normalized=dict(record)
        args=normalized.get('params',[])
        if not isinstance(args,list):args=[]
        normalized['parameters']=','.join(str(x)+':any' for x in args)
        normalized.setdefault('returns','unknown')
        normalized.setdefault('owner','ExternalAPI')
        normalized['external']=True
        normalized.setdefault('name','Unnamed')
        super().__init__(normalized,parent)
        self.refresh_description()

    def refresh_description(self):
        record=self.record
        self.setToolTip(translated_text('工程外部接口（用户自行声明，非 Valve 官方 API）')+'\n'+record['owner']+'.'+record['name']+'('+record['parameters']+')\n'+translated_text('返回：')+record['returns'])
        self._resize_description()
        self.update()

class EventPaletteBlock(PaletteBlock):
    def __init__(self,record,parent=None):
        super().__init__('event',parent)
        self.record=record
        from ..api_docs import event_tooltip
        self.refresh_description()

    def refresh_description(self):
        from ..api_docs import event_tooltip
        self.setToolTip(event_tooltip(self.record))
        self._resize_description()
        self.update()

    def _resize_description(self):
        font=QFont(self.font());font.setPointSize(9)
        self._set_card_height(max(44,self._wrapped_height(event_caption(self.record['name']),font)+22))

    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(COLORS['event']));painter.setPen(QPen(QColor('#eac59a'),1))
        path=QPainterPath();w=self.width()-6;h=self.height()-3
        path.moveTo(3,h-2);path.lineTo(3,24);path.cubicTo(3,2,20,2,42,2)
        path.lineTo(w-16,2);path.quadTo(w-2,2,w-2,18)
        path.lineTo(w-2,h-2);path.closeSubpath()
        painter.drawPath(path);painter.setPen(QColor('white'))
        display=event_caption(self.record['name'])
        painter.drawText(QRect(13,7,max(55,self.width()-28),self.height()-13),Qt.AlignVCenter|Qt.AlignLeft|Qt.TextWordWrap,display);painter.end()
    def mouseMoveEvent(self,event):
        if self._press is None:return
        if (event.position().toPoint()-self._press).manhattanLength()<8:return
        self._press=None;self.setCursor(Qt.OpenHandCursor)
        drag=QDrag(self);mime=QMimeData()
        mime.setData(MIME_EVENT,json.dumps(self.record,ensure_ascii=False).encode())
        drag.setMimeData(mime);drag.setPixmap(self.grab());drag.setHotSpot(QPoint(12,14));drag.exec(Qt.CopyAction)


class BlockPalette(QWidget):
    blockDropped=Signal(str)
    embeddedDropped=Signal(str)
    def __init__(self,parent=None,catalog=None,library=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        outer=QVBoxLayout(self);outer.setContentsMargins(3,3,3,3);outer.setSpacing(7)
        self.search=QLineEdit();self.search.setPlaceholderText('Search blocks...' if current_profile().language=='en' else '搜索积木...')
        outer.addWidget(self.search)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QScrollArea.NoFrame)
        self.content=QWidget();self.content_lay=QVBoxLayout(self.content);self.content_lay.setContentsMargins(5,5,5,5)
        self.content_lay.setSpacing(8)
        self.entries=[]
        self.utility_groups=[]
        self.library=library or {}
        for category,kinds in BLOCK_CATEGORIES.items():
            head=QLabel(category_caption(category));head.setProperty('original_category',category);head.setStyleSheet('color:#a8bbd5;font-weight:700;padding-top:10px;')
            self.content_lay.addWidget(head);self.entries.append((head,category,None))
            for kind in kinds:
                if kind=='utility':
                    from ..utility_blocks import UTILITY_BLOCKS, UTILITY_GROUPS
                    for group,(zh,en) in UTILITY_GROUPS.items():
                        selected=[(operation,info) for operation,info in UTILITY_BLOCKS.items() if info['group']==group]
                        if not selected:continue
                        toggle=QToolButton()
                        toggle.setCheckable(True);toggle.setChecked(group=='players')
                        toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                        toggle.setArrowType(Qt.DownArrow if toggle.isChecked() else Qt.RightArrow)
                        toggle.setText((en if current_profile().language=='en' else zh)+' ('+str(len(selected))+')')
                        self.content_lay.addWidget(toggle)
                        holder=QWidget();sub_layout=QVBoxLayout(holder)
                        sub_layout.setContentsMargins(12,0,0,0);sub_layout.setSpacing(5)
                        items=[]
                        for operation,info in selected:
                            item=UtilityPaletteBlock(operation)
                            sub_layout.addWidget(item);items.append(item)
                            self.entries.append((item,category,kind+' '+operation+' '+info['zh']+' '+info['en']+' '+zh+' '+en))
                        self.content_lay.addWidget(holder)
                        holder.setVisible(toggle.isChecked())
                        toggle.toggled.connect(lambda checked,t=toggle,h=holder:(t.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),h.setVisible(checked)))
                        self.utility_groups.append((group,toggle,holder,items))
                    continue
                if kind=='math_call':
                    block=PaletteBlock(kind)
                    self.content_lay.addWidget(block);self.entries.append((block,category,kind+' sqrt pow atan2'))
                    for function in ('max','min'):
                        item=CustomMathPaletteBlock(function)
                        self.content_lay.addWidget(item)
                        self.entries.append((item,category,'math_call math:'+function+' '+('较大值 Maximum' if function=='max' else '较小值 Minimum')))
                    continue
                if kind=='boolean':
                    for literal in ('true','false'):
                        block=BooleanPaletteBlock(literal)
                        self.content_lay.addWidget(block)
                        self.entries.append((block,category,'boolean '+literal))
                    continue
                if kind=='operator':
                    from ..math_blocks import OPERATORS
                    for group,ops in OPERATORS.items():
                        caption=QLabel(category_caption(group));caption.setProperty('original_category',group);caption.setStyleSheet('color:#b4d4ef;padding-left:10px;')
                        self.content_lay.addWidget(caption)
                        self.entries.append((caption,category,None))
                        for op in ops:
                            block=OperatorPaletteBlock(op)
                            self.content_lay.addWidget(block)
                            self.entries.append((block,category,kind+' '+op))
                    continue
                block=PaletteBlock(kind)
                self.content_lay.addWidget(block);self.entries.append((block,category,kind))
        from ..quick_literals import LITERAL_GROUPS
        from ..literal_subgroups import literal_subgroups
        self.literal_groups=[]
        self.nested_literal_groups=[]
        for group,detail in LITERAL_GROUPS.items():
            if group in ('classname_weapons','classname_spawns','classname_entities','item_melee','item_world'):
                # These remain valid data IDs for older projects, but their
                # entries are displayed only once in the two-level library.
                continue
            if group in ('classname','item','spawn_classname'):
                top=QToolButton()
                top.setCheckable(True);top.setChecked(False)
                top.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                top.setArrowType(Qt.RightArrow)
                top.setText((detail['en'] if current_profile().language=='en' else detail['zh'])+' ('+str(sum(len(d['entries']) for d in literal_subgroups(group)))+')')
                top.setToolTip(detail['description_en' if current_profile().language=='en' else 'description_zh'])
                self.content_lay.addWidget(top)
                parent_holder=QWidget()
                parent_layout=QVBoxLayout(parent_holder)
                parent_layout.setContentsMargins(12,0,0,0);parent_layout.setSpacing(5)
                children=[]
                for subgroup in literal_subgroups(group):
                    child_toggle=QToolButton()
                    child_toggle.setCheckable(True);child_toggle.setChecked(False)
                    child_toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                    child_toggle.setArrowType(Qt.RightArrow)
                    caption=subgroup['en' if current_profile().language=='en' else 'zh']
                    child_toggle.setText(caption+' ('+str(len(subgroup['entries']))+')')
                    child_toggle.setToolTip(subgroup['description_en' if current_profile().language=='en' else 'description_zh'])
                    parent_layout.addWidget(child_toggle)
                    child_holder=QWidget();child_layout=QVBoxLayout(child_holder)
                    child_layout.setContentsMargins(12,0,0,0);child_layout.setSpacing(4)
                    items=[]
                    for source,value in subgroup['entries']:
                        block=LiteralPaletteBlock(source,value)
                        child_layout.addWidget(block);items.append(block)
                    parent_layout.addWidget(child_holder);child_holder.hide()
                    child_toggle.toggled.connect(lambda checked,t=child_toggle,h=child_holder:(t.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),h.setVisible(checked)))
                    children.append({'detail':subgroup,'toggle':child_toggle,'holder':child_holder,'items':items})
                parent_holder.hide();self.content_lay.addWidget(parent_holder)
                top.toggled.connect(lambda checked,t=top,h=parent_holder:(t.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),h.setVisible(checked)))
                self.nested_literal_groups.append({'group':group,'toggle':top,'holder':parent_holder,'children':children})
                continue
            toggle=QToolButton()
            toggle.setCheckable(True);toggle.setChecked(False)
            toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toggle.setArrowType(Qt.RightArrow)
            toggle.setText((detail['en'] if current_profile().language=='en' else detail['zh'])+' ('+str(len(detail['entries']))+')')
            toggle.setToolTip(detail['description_en' if current_profile().language=='en' else 'description_zh'])
            self.content_lay.addWidget(toggle)
            holder=QWidget();items=[]
            layout=QVBoxLayout(holder);layout.setContentsMargins(14,0,0,0);layout.setSpacing(4)
            for value,zh,en in detail['entries']:
                block=LiteralPaletteBlock(group,value)
                layout.addWidget(block);items.append(block)
            holder.hide();self.content_lay.addWidget(holder)
            toggle.toggled.connect(lambda checked,t=toggle,h=holder:(t.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),h.setVisible(checked)))
            self.literal_groups.append((group,toggle,holder,items))
        if catalog is not None:
            from collections import defaultdict
            by_owner=defaultdict(list)
            for record in catalog.methods():by_owner[record['owner']].append(record)
            group=QLabel(category_caption('官方方法 · 按类展开'));group.setProperty('original_category','官方方法 · 按类展开')
            group.setStyleSheet('color:#a8bbd5;font-weight:700;padding-top:12px;')
            self.content_lay.addWidget(group);self.entries.append((group,'官方方法',None))
            self.method_groups=[]
            for owner,records in sorted(by_owner.items()):
                toggle=QToolButton()
                toggle.setText(f'{owner} ({len(records)})')
                toggle.setCheckable(True);toggle.setChecked(False)
                toggle.setArrowType(Qt.RightArrow)
                toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                self.content_lay.addWidget(toggle)
                holder=QWidget();lay=QVBoxLayout(holder)
                lay.setContentsMargins(14,0,0,0);lay.setSpacing(4)
                method_items=[]
                for record in records:
                    item=OfficialMethodBlock(record)
                    lay.addWidget(item);method_items.append(item)
                holder.setVisible(False)
                self.content_lay.addWidget(holder)
                toggle.toggled.connect(lambda checked,t=toggle,h=holder:(t.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),h.setVisible(checked)))
                self.method_groups.append((owner,toggle,holder,method_items))
        if catalog is not None:
            from collections import defaultdict
            from ..event_metadata import event_group
            event_groups=defaultdict(list)
            for record in catalog.events():event_groups[event_group(record['name'],record.get('category',''))].append(record)
            self.event_groups=[]
            title=QLabel(category_caption('原版事件 · 按用途展开'));title.setProperty('original_category','原版事件 · 按用途展开');title.setStyleSheet('color:#a8bbd5;font-weight:700;')
            self.content_lay.addWidget(title)
            for group,records in sorted(event_groups.items()):
                toggle=QToolButton();toggle.setText(f'{category_caption(group)} ({len(records)})')
                toggle.setCheckable(True);toggle.setArrowType(Qt.RightArrow)
                toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);self.content_lay.addWidget(toggle)
                holder=QWidget();lay=QVBoxLayout(holder);lay.setContentsMargins(12,0,0,0)
                items=[]
                for record in records:
                    block=EventPaletteBlock(record);lay.addWidget(block);items.append(block)
                self.content_lay.addWidget(holder);holder.hide()
                toggle.toggled.connect(lambda checked,t=toggle,h=holder:(t.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),h.setVisible(checked)))
                self.event_groups.append((group,toggle,holder,items))
        self.external_groups=[]
        self.external_heading=QLabel(category_caption('外部 API · 工程自定义'));self.external_heading.setProperty('original_category','外部 API · 工程自定义')
        self.external_heading.setStyleSheet('color:#a8bbd5;font-weight:700;padding-top:10px;')
        self.content_lay.addWidget(self.external_heading)
        self.external_holder=QWidget()
        self.external_layout=QVBoxLayout(self.external_holder)
        self.external_layout.setContentsMargins(12,0,0,0)
        self.content_lay.addWidget(self.external_holder)
        self.reload_external(self.library)
        self.content_lay.addStretch()
        scroll.setWidget(self.content);outer.addWidget(scroll)
        self._applied_search=""
        self._search_expansion_snapshot=None
        self.search.returnPressed.connect(self.apply_search)
        self.search.textChanged.connect(self._on_search_text_changed)
        self._install_drop_targets()
    def _install_drop_targets(self):
        """The entire library, including its scrolling viewport and entries, is a drop target."""
        for widget in [self, *self.findChildren(QWidget)]:
            if widget.property('l4dv_library_drop_target'):
                continue
            widget.setProperty('l4dv_library_drop_target', True)
            widget.setAcceptDrops(True)
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if isinstance(watched, QWidget) and watched.property('l4dv_library_drop_target'):
            if event.type() in (QEvent.DragEnter, QEvent.DragMove, QEvent.Drop):
                mime=event.mimeData()
                if mime.hasFormat(MIME_EMBEDDED_MOVE):
                    if event.type()==QEvent.Drop:
                        expression_id=bytes(mime.data(MIME_EMBEDDED_MOVE)).decode('utf-8')
                        if expression_id:self.embeddedDropped.emit(expression_id)
                    event.setDropAction(Qt.MoveAction)
                    event.accept()
                    return True
                if mime.hasFormat(MIME_MOVE):
                    if event.type()==QEvent.Drop:
                        block_id=bytes(mime.data(MIME_MOVE)).decode('utf-8')
                        if block_id:
                            self.blockDropped.emit(block_id)
                    event.setDropAction(Qt.MoveAction)
                    event.accept()
                    return True
        return super().eventFilter(watched,event)

    def refresh_language(self):
        from PySide6.QtWidgets import QToolTip
        QToolTip.hideText()
        localize_widget_tree(self)
        self.search.setPlaceholderText('Search blocks...' if current_profile().language=='en' else '搜索积木...')
        for widget,category,kind in self.entries:
            original=widget.property('original_category')
            if original:
                widget.setText(category_caption(original))
            if isinstance(widget,PaletteBlock):
                widget.refresh_description()
            else:
                widget.update()
        from ..utility_blocks import UTILITY_GROUPS
        for group,toggle,holder,items in self.utility_groups:
            zh,en=UTILITY_GROUPS[group]
            toggle.setText((en if current_profile().language=='en' else zh)+' ('+str(len(items))+')')
        for _,toggle,holder,items in getattr(self,'method_groups',[]):
            for item in items:item.refresh_description()
        for group,toggle,holder,items in getattr(self,'event_groups',[]):
            toggle.setText(f'{category_caption(group)} ({len(items)})')
            for item in items:
                item.refresh_description()
        self.external_heading.setText(category_caption('外部 API · 工程自定义'))
        for item in self.external_groups:item.refresh_description()
        from ..quick_literals import LITERAL_GROUPS
        language=current_profile().language
        for group,toggle,holder,items in self.literal_groups:
            detail=LITERAL_GROUPS[group]
            toggle.setText((detail['en'] if language=='en' else detail['zh'])+' ('+str(len(items))+')')
            toggle.setToolTip(detail['description_en' if language=='en' else 'description_zh'])
            for item in items:item.refresh_description()
        for parent in self.nested_literal_groups:
            group=parent['group'];detail=LITERAL_GROUPS[group]
            count=sum(len(child['items']) for child in parent['children'])
            parent['toggle'].setText(detail['en' if language=='en' else 'zh']+' ('+str(count)+')')
            parent['toggle'].setToolTip(detail['description_en' if language=='en' else 'description_zh'])
            for child in parent['children']:
                sub=child['detail']
                child['toggle'].setText(sub['en' if language=='en' else 'zh']+' ('+str(len(child['items']))+')')
                child['toggle'].setToolTip(sub['description_en' if language=='en' else 'description_zh'])
                for item in child['items']:item.refresh_description()
        self.filter(self._applied_search)

    def reload_external(self,library):
        self.library=library or {}
        while self.external_layout.count():
            item=self.external_layout.takeAt(0)
            widget=item.widget()
            if widget:widget.deleteLater()
        self.external_groups=[]
        for record in self.library.get('functions',[]):
            if not isinstance(record,dict) or not record.get('name') or not record.get('owner'):continue
            item=ExternalMethodBlock(record)
            self.external_layout.addWidget(item)
            self.external_groups.append(item)
        self.external_heading.setVisible(bool(self.external_groups))
        self.external_holder.setVisible(bool(self.external_groups))
        self._install_drop_targets()

    def _on_search_text_changed(self,text):
        # Only an empty search resets immediately; other edits wait for Enter.
        if not text.strip() and self._applied_search:
            self.filter('')

    def _search_toggles(self):
        for _group,toggle,_holder,_items in self.utility_groups:
            yield toggle
        for parent in self.nested_literal_groups:
            yield parent['toggle']
            for child in parent['children']:
                yield child['toggle']
        for collection in (self.literal_groups, getattr(self,'method_groups',[]), getattr(self,'event_groups',[])):
            for _name,toggle,_holder,_items in collection:
                yield toggle

    def apply_search(self):
        self.filter(self.search.text())

    def filter(self,text):
        search=text.casefold().strip()
        if search and self._search_expansion_snapshot is None:
            self._search_expansion_snapshot={toggle:toggle.isChecked() for toggle in self._search_toggles()}
        self._applied_search=search
        shown={c for _,c,k in self.entries if k and (not search or kmp_contains(block_caption(k)+' '+BLOCK_NAMES.get(k,k)+' '+k+' '+c,search))}
        for widget,category,kind in self.entries:
            widget.setVisible(category in shown and (kind is None or not search or kmp_contains(block_caption(kind)+' '+BLOCK_NAMES.get(kind,kind)+' '+kind+' '+category,search)))
        for block in getattr(self,'external_groups',[]):
            block.setVisible(not search or kmp_contains(block.record['owner']+' '+block.record['name'],search))
        from ..utility_blocks import UTILITY_GROUPS, UTILITY_BLOCKS
        for group,toggle,holder,items in self.utility_groups:
            zh,en=UTILITY_GROUPS[group]
            group_match=bool(search and kmp_contains(group+' '+zh+' '+en,search))
            matching=[item for item in items if not search or group_match or
                kmp_contains(item.operation+' '+UTILITY_BLOCKS[item.operation]['zh']+' '+UTILITY_BLOCKS[item.operation]['en']+' '+UTILITY_BLOCKS[item.operation]['professional'],search)]
            for item in items:item.setVisible(item in matching)
            toggle.setVisible(bool(matching))
            if search and matching:toggle.setChecked(True)
            holder.setVisible(toggle.isChecked() and bool(matching))
        from ..quick_literals import LITERAL_GROUPS, lookup_literal
        for group,toggle,holder,items in self.literal_groups:
            detail=LITERAL_GROUPS[group]
            group_caption=detail['zh']+' '+detail['en']
            group_match=bool(search and kmp_contains(group_caption,search))
            matching=[item for item in items if not search or group_match or kmp_contains(' '.join(lookup_literal(group,item.value)),search)]
            for item in items:item.setVisible(item in matching)
            toggle.setVisible(bool(matching))
            if search and matching:toggle.setChecked(True)
            holder.setVisible(toggle.isChecked() and bool(matching))
        for parent in self.nested_literal_groups:
            group=parent['group'];detail=LITERAL_GROUPS[group]
            parent_match=bool(search and kmp_contains(detail['zh']+' '+detail['en']+' '+group,search))
            any_matching=False
            for child in parent['children']:
                sub=child['detail']
                subgroup_match=bool(search and kmp_contains(sub['zh']+' '+sub['en']+' '+sub['id'],search))
                matching=[item for item in child['items']
                          if not search or parent_match or subgroup_match or
                          kmp_contains(' '.join(lookup_literal(item.group,item.value)),search)]
                matchset=set(matching)
                for item in child['items']:item.setVisible(item in matchset)
                has_matches=bool(matching)
                any_matching |= has_matches
                child['toggle'].setVisible(has_matches)
                if search and has_matches:child['toggle'].setChecked(True)
                child['holder'].setVisible(child['toggle'].isChecked() and has_matches)
            parent['toggle'].setVisible(any_matching)
            if search and any_matching:parent['toggle'].setChecked(True)
            parent['holder'].setVisible(parent['toggle'].isChecked() and any_matching)
        for owner,toggle,holder,methods in getattr(self,'method_groups',[]):
            matching=[method for method in methods if not search or kmp_contains(owner+' '+method_caption(method.record['name'])+' '+method.record['name'],search)]
            for method in methods:method.setVisible(method in matching)
            toggle.setVisible(bool(matching))
            if search and matching:toggle.setChecked(True)
            holder.setVisible(toggle.isChecked() and bool(matching))
        for group,toggle,holder,items in getattr(self,'event_groups',[]):
            matching=[b for b in items if not search or kmp_contains(group+' '+category_caption(group)+' '+event_caption(b.record['name'])+' '+b.record['name'],search)]
            for b in items:b.setVisible(b in matching)
            toggle.setVisible(bool(matching))
            if search and matching:toggle.setChecked(True)
            holder.setVisible(toggle.isChecked() and bool(matching))
        if not search and self._search_expansion_snapshot is not None:
            for toggle,was_open in self._search_expansion_snapshot.items():
                toggle.setChecked(was_open)
            self._search_expansion_snapshot=None
