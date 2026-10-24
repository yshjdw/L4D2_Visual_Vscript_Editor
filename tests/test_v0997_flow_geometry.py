import unittest
from l4visual.flow_geometry import plan_flow

class FlowGeometryTests(unittest.TestCase):
    def test_single_line_no_extra_height(self):
        h,placements=plan_flow([(80,28),(95,37)],200,5)
        self.assertEqual(h,37)
        self.assertEqual(placements[1][:2],(85,0))

    def test_wrap_increases_height(self):
        h,placements=plan_flow([(110,35),(140,42),(130,28)],250,5)
        self.assertEqual(h,35+5+42+5+28)
        self.assertEqual([p[1] for p in placements],[0,40,87])

    def test_resize_changes_height_not_hidden(self):
        children=[(105,32),(95,41),(150,29),(110,35),(145,34)]
        narrow,placements=plan_flow(children,300,4)
        wide,_=plan_flow(children,650,4)
        self.assertGreater(narrow,wide)
        self.assertEqual(max(y+h for _,y,_,h in placements),narrow)

    def test_single_large_nested_expression_kept_intact(self):
        h,rectangles=plan_flow([(720,52),(120,24)],420,4)
        self.assertEqual(rectangles[0][2],720)
        self.assertEqual(rectangles[1][1],56)
        self.assertEqual(h,80)

if __name__=='__main__':unittest.main()
