"""Structural block drag/drop operations, independent of Qt.

Statement blocks are moveable; expression slots can own nested expressions.
"""
from .data_definitions import DATA_BLOCKS


def locate_block(document, block_id):
    for section in document.sections:
        def walk(items):
            for block in items:
                if block.id == block_id:
                    return section, items, block
                for nested in block.branches.values():
                    found = walk(nested)
                    if found is not None:
                        return found
            return None
        found = walk(section.blocks)
        if found is not None:
            return found
    return None


def contains_block(block, target_id):
    if block.id == target_id:
        return True
    return any(contains_block(child, target_id)
               for branch in block.branches.values() for child in branch)


def accepts_block(section, target, kind):
    """Apply destination region restrictions for both new and moved blocks."""
    if section.kind == 'events' and target is section.blocks:
        return kind == 'event'
    if section.kind == 'data' and kind not in DATA_BLOCKS:
        return False
    if section.kind == 'data' and kind == 'array_op' and section.args.get('container') != 'Set':
        return False
    if kind == 'event':
        return section.kind == 'events' and target is section.blocks
    if section.kind == 'namespace' and target is section.blocks:
        return kind not in ('break', 'continue', 'return', 'event')
    return True


def move_block(document, block_id, destination_section, destination_list, index):
    """Move a statement node (not a clone). Return True if accepted and changed."""
    found = locate_block(document, block_id)
    if found is None:
        return False
    _, source, block = found
    if not accepts_block(destination_section, destination_list, block.kind):
        return False
    # Moving a C-shaped block into one of its own branches would form a cycle.
    for branch in block.branches.values():
        if destination_list is branch or _contains_collection(branch, destination_list):
            return False
    old = source.index(block)
    if source is destination_list and index > old:
        index -= 1
    index = max(0, min(index, len(destination_list) - (1 if source is destination_list else 0)))
    if source is destination_list and index == old:
        return False
    source.pop(old)
    destination_list.insert(index, block)
    return True


def _contains_collection(branch, sought):
    if branch is sought:
        return True
    for child in branch:
        for nested in child.branches.values():
            if _contains_collection(nested, sought):
                return True
    return False


def remove_block(document, block_id):
    """Remove a statement from any nested C-slot; safe for trash drops."""
    found = locate_block(document, block_id)
    if not found:
        return False
    _section, collection, block = found
    collection.remove(block)
    return True


def remove_wrapper_preserve_children(document, block_id):
    """Remove only one statement wrapper, promoting its immediate branch contents.

    Refuse when promotion would violate top-level section constraints.
    """
    found = locate_block(document, block_id)
    if found is None:
        return False
    section, collection, block = found
    children = [child for branch in block.branches.values() for child in branch]
    if any(not accepts_block(section, collection, child.kind) for child in children):
        return False
    index = collection.index(block)
    collection[index:index + 1] = children
    return True
