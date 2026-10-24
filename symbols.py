"""引用由唯一节点 ID 绑定，不通过同名字串决定引用身份。"""
from .models import ScriptDocument


def rename_references(document: ScriptDocument, symbol_id: str, new_name: str):
    count=0
    def visit(value):
        nonlocal count
        if isinstance(value,dict):
            if value.get('symbol_id')==symbol_id and value.get('kind') in ('variable','variable_ref'):
                if value.get('kind')=='variable':
                    value['value']=new_name
                else:
                    old=str(value.get('name',''))
                    path=str(value.get('path',''))
                    if path==old:
                        value['path']=new_name
                    elif old and path.endswith('.'+old):
                        value['path']=path[:-len(old)]+new_name
                    value['name']=new_name
                count+=1
            for child in value.values():visit(child)
        elif isinstance(value,list):
            for child in value:visit(child)
    for section in document.sections:
        for block in section.blocks:
            visit(block.args)
            def nested(b):
                for children in b.branches.values():
                    for child in children:
                        visit(child.args)
                        nested(child)
            nested(block)
    return count
