from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from uuid import uuid4


def uid() -> str:
    return uuid4().hex[:12]


@dataclass
class Block:
    kind: str
    args: dict = field(default_factory=dict)
    branches: dict[str, list['Block']] = field(default_factory=dict)
    id: str = field(default_factory=uid)

    def to_dict(self):
        return {"id": self.id, "kind": self.kind, "args": self.args,
                "branches": {key: [x.to_dict() for x in value] for key, value in self.branches.items()}}

    @classmethod
    def from_dict(cls, data):
        return cls(str(data['kind']), dict(data.get('args', {})),
                   {key: [cls.from_dict(x) for x in children] for key, children in data.get('branches', {}).items()},
                   str(data.get('id') or uid()))


def clone_block(block: Block) -> Block:
    """Clone a block subtree with fresh IDs so copied definitions stay independent."""
    result = deepcopy(block)
    def renew_value(value):
        if isinstance(value, dict):
            if value.get('kind')=='embedded_block' and isinstance(value.get('block'),dict):
                value['block']['id']=uid()
            for child in value.values():renew_value(child)
        elif isinstance(value,list):
            for child in value:renew_value(child)
    def renew(node: Block):
        node.id = uid()
        renew_value(node.args)
        for children in node.branches.values():
            for child in children:
                renew(child)
    renew(result)
    return result


@dataclass
class Section:
    kind: str
    name: str
    blocks: list[Block] = field(default_factory=list)
    args: dict = field(default_factory=dict)
    x: float = 40.0
    y: float = 40.0
    id: str = field(default_factory=uid)

    def to_dict(self):
        return {"id": self.id, "kind": self.kind, "name": self.name,
                "args": self.args, "x": self.x, "y": self.y,
                "blocks": [b.to_dict() for b in self.blocks]}

    @classmethod
    def from_dict(cls, data):
        return cls(str(data['kind']), str(data['name']),
                   [Block.from_dict(b) for b in data.get('blocks', [])],
                   dict(data.get('args', {})), float(data.get('x', 40)),
                   float(data.get('y', 40)), str(data.get('id') or uid()))


@dataclass
class ScriptDocument:
    name: str
    sections: list[Section] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    id: str = field(default_factory=uid)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "includes": self.includes,
                "sections": [s.to_dict() for s in self.sections]}

    @classmethod
    def from_dict(cls, data):
        return cls(str(data['name']), [Section.from_dict(s) for s in data.get('sections', [])],
                   list(data.get('includes', [])), str(data.get('id') or uid()))


@dataclass
class Project:
    name: str = 'My VScript Project'
    event_namespace: str = 'MyEvents'
    documents: list[ScriptDocument] = field(default_factory=list)
    library: dict = field(default_factory=dict)
    version: int = 1

    def to_dict(self):
        return {"version": self.version, "name": self.name,
                "event_namespace": self.event_namespace,
                "documents": [d.to_dict() for d in self.documents], "library": self.library}

    @classmethod
    def from_dict(cls, obj):
        if int(obj.get('version', -1)) != 1:
            raise ValueError('不支持的工程版本')
        return cls(str(obj.get('name', 'Untitled')),
                   str(obj.get('event_namespace', 'MyEvents')),
                   [ScriptDocument.from_dict(d) for d in obj.get('documents', [])],
                   dict(obj.get('library', {})))


def default_project():
    doc = ScriptDocument('director_base_addon.nut', [
        Section('namespace', 'MyScript', x=60, y=50),
        Section('function', 'Start', [
            Block('var', {'name': 'player', 'value': 'Entities.FindByClassname(null, "player")', 'scope': 'local'}),
            Block('if', {'condition': 'player != null'}, {'body': [
                Block('method', {'method': 'GetOrigin', 'target': 'player', 'parameters': [], 'output': 'position'}),
                Block('call', {'function': 'printl', 'parameters': ['position'], 'output': ''})
            ], 'else': []}),
            Block('return', {'value': 'true'})
        ], {'owner': 'MyScript', 'params': [], 'return_type': 'bool'}, x=470, y=50),
        Section('events', 'MyEvents', [
            Block('event', {'event': 'round_start', 'env': 'env'}, {'body': [
                Block('call', {'function': 'MyScript.Start', 'parameters': [], 'output': ''})
            ]})
        ], x=70, y=360),
        Section('init', '文件初始化', [Block('call', {'function': 'printl', 'parameters': ['"[MyScript] Loaded"'], 'output': ''})], x=500, y=360)
    ])
    return Project('示例工程', 'MyEvents', [doc])
