"""Size the multiline raw-Squirrel editor from its visible (wrapped) lines.

Pure geometry calculations are separated from Qt's event loop so growing *and*
shrinking, including trailing newlines and soft wrapping, can be regression tested.
"""
from __future__ import annotations


def count_visual_lines(text: str, widths: list[int], available_width: int) -> int:
    """Return a conservative height budget for every explicit or soft-wrapped line.

    widths must contain the QFontMetrics.horizontalAdvance of each logical line.
    In particular, a trailing newline creates a visible empty line.
    """
    lines = text.split('\n')
    if len(widths) != len(lines):
        raise ValueError('one measured width is required for each logical line')
    available_width = max(1, int(available_width))
    return sum(max(1, (max(0, int(width)) + available_width - 1) // available_width)
               for width in widths)


def raw_editor_height(text: str, widths: list[int], viewport_width: int,
                      line_spacing: int, padding: int = 24, minimum: int = 72) -> int:
    """No arbitrary height cap: the canvas/scene provide scrolling for long code."""
    return max(minimum, count_visual_lines(text, widths, viewport_width)
               * max(1, int(line_spacing)) + max(0, padding))
