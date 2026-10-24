"""Copy a variable and its linked Data sections without sharing symbol IDs."""
from copy import deepcopy
from .models import clone_block, uid
from .data_definitions import linked_definition


def clone_with_definitions(document, source):
    replica = clone_block(source)
    if document is None:
        return replica
    new_sections = []

    def copy_definition(original_block, copied_block, new_parent_id=''):
        definition = linked_definition(document, original_block.id)
        if definition is None:
            return
        copied = deepcopy(definition)
        copied.id = uid()
        copied.args['source_id'] = copied_block.id
        copied.args['parent_section_id'] = new_parent_id
        copied.blocks = [clone_block(member) for member in definition.blocks]
        new_sections.append(copied)
        for old_member, new_member in zip(definition.blocks, copied.blocks):
            copy_definition(old_member, new_member, copied.id)

    copy_definition(source, replica)
    document.sections.extend(new_sections)
    return replica
