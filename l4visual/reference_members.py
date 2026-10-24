"""Resolve saved variable references back to their original declaration.

The reference may be nested in a function call, but its symbol id belongs to
an event parameter or variable declaration in the document.
"""
from .variable_paths import reference_for_symbol


def find_reference_source(document, symbol_id):
    if document is None or not symbol_id:
        return None
    def walk(blocks):
        for block in blocks:
            if block.id == symbol_id and block.kind in ('var', 'event'):
                return block
            for children in block.branches.values():
                found = walk(children)
                if found is not None:
                    return found
        return None
    for section in document.sections:
        found = walk(section.blocks)
        if found is not None:
            return found
    return None


def reference_root(document, reference):
    source = find_reference_source(document, reference.get('symbol_id'))
    if source is None:
        return None, None
    if source.kind == 'event':
        return source, str(source.args.get('env', 'env'))
    return source, reference_for_symbol(document, source.id) or str(source.args.get('name', ''))
