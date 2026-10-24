"""Pure scene-boundary calculations for the expandable block workspace."""

MIN_SCENE = (-2400.0, -1800.0, 7000.0, 5500.0)


def include_rect(rect, content, margin=360):
    """Return the union of ``rect`` and content bounds with outer working room.

    Rectangles use (left, top, width, height); existing scene bounds must
    never be reduced by adding content, including in negative coordinates.
    """
    left, top, width, height = map(float, rect)
    x, y, w, h = map(float, content)
    if w < 0 or h < 0:
        raise ValueError('negative rectangle dimension')
    right = max(left + width, x + w + margin)
    bottom = max(top + height, y + h + margin)
    left = min(left, x - margin)
    top = min(top, y - margin)
    return left, top, right - left, bottom - top


def content_scene_rect(contents, margin=360, minimum=MIN_SCENE):
    """Reset to minimum size, then grow as far as actual content requires."""
    rect = minimum
    for box in contents:
        rect = include_rect(rect, box, margin)
    return rect
