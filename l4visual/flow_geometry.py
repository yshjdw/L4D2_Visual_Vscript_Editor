"""Pure line-wrapping geometry shared by layout measurement and placement.

Always measure and lay out with the same algorithm so visual rows cannot spill
below the containing QWidget's allocated height.
"""
from __future__ import annotations

def plan_flow(sizes, width, spacing=5):
    """Return (total_height, rectangles) for (width, height) child sizes.

    The rectangles use (x,y,width,height), preserve a child as an indivisible
    unit, and may exceed available width for a single long expression.
    """
    width=max(1,int(width))
    spacing=max(0,int(spacing))
    x=y=line_height=0
    rectangles=[]
    for item_width,item_height in sizes:
        w=max(0,int(item_width));h=max(0,int(item_height))
        if x and x+w>width:
            x=0
            y+=line_height+spacing
            line_height=0
        rectangles.append((x,y,w,h))
        x+=w+spacing
        line_height=max(line_height,h)
    return y+line_height,rectangles
