"""Resolve draggable variable tokens to Squirrel member/index access paths."""
from .codegen import require_name
from .data_definitions import find_source


def reference_for_symbol(document, symbol_id):
    """Use source declaration identity instead of the display label.

    Namespace members are root-qualified. A nested data section inherits its
    owning declaration path, with array entries using numeric indices.
    """
    if document is None:
        return None
    def walk(blocks):
        for block in blocks:
            if block.id == symbol_id and block.kind == 'var':
                return block
            for children in block.branches.values():
                found = walk(children)
                if found is not None:
                    return found
        return None
    for section in document.sections:
        block = walk(section.blocks)
        if block is not None:
            name = str(block.args.get('name', ''))
            if section.kind == 'namespace':
                return '::' + require_name(section.name) + '.' + require_name(name)
            if section.kind == 'data':
                base = reference_for_symbol(document, section.args.get('source_id')) if section.args.get('source_id') else (
                    ('::' + require_name(section.args['owner']) + '.') if section.args.get('owner') else '::') + require_name(section.name)
                if not base:
                    return None
                if section.args.get('container') == 'Set':
                    if not name.isdecimal():
                        return None
                    return base + '[' + str(int(name)) + ']'
                return base + '.' + require_name(name)
            return require_name(name)
    return None
