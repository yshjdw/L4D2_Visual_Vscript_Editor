"""Pure geometry and locator helpers used by validation jump-to-block."""

def find_block(blocks, block_id):
    for block in blocks:
        if block.id==block_id:
            return block
        for children in block.branches.values():
            found=find_block(children,block_id)
            if found is not None:
                return found
    return None


def issue_target(document, section_id='', block_id='', section_name=''):
    if document is None:
        return None,None
    section=next((s for s in document.sections if section_id and s.id==section_id),None)
    if section is None and section_name:
        section=next((s for s in document.sections if s.name==section_name),None)
    if section is None:
        return None,None
    return section,find_block(section.blocks,block_id) if block_id else None


def viewport_focus_center(target_center_x, target_top_y, viewport_height, scale, top_padding=40):
    """A block's midpoint is horizontally centered and its top sits near the viewport top."""
    if scale<=0:
        raise ValueError('scale must be positive')
    return (target_center_x, target_top_y+(viewport_height/2-top_padding)/scale)
