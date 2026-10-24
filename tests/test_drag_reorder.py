import unittest
from l4visual.models import Block, Section, ScriptDocument
from l4visual.block_reorder import move_block, locate_block

class DragReorderTests(unittest.TestCase):
    def setUp(self):
        self.inner=Block('assign',{'target':'value','value':'4'})
        self.cond=Block('if',{'condition':'true'},{'body':[self.inner],'else':[]})
        self.tail=Block('return',{'value':'false'})
        self.origin=Section('function','Main',[self.cond,self.tail])
        self.other=Section('function','Other',[])
        self.events=Section('events','Events',[])
        self.data=Section('data','State',[])
        self.doc=ScriptDocument('main.nut',[self.origin,self.other,self.events,self.data])

    def test_reorder_top_level(self):
        self.assertTrue(move_block(self.doc,self.tail.id,self.origin,self.origin.blocks,0))
        self.assertEqual([x.id for x in self.origin.blocks],[self.tail.id,self.cond.id])

    def test_nested_to_other_section(self):
        self.assertTrue(move_block(self.doc,self.inner.id,self.other,self.other.blocks,0))
        self.assertEqual(self.cond.branches['body'],[])
        self.assertIs(self.other.blocks[0],self.inner)
        self.assertIs(locate_block(self.doc,self.inner.id)[0],self.other)

    def test_move_into_own_branch_denied(self):
        self.assertFalse(move_block(self.doc,self.cond.id,self.origin,self.cond.branches['body'],0))
        self.assertIs(self.origin.blocks[0],self.cond)

    def test_events_restriction(self):
        self.assertFalse(move_block(self.doc,self.tail.id,self.events,self.events.blocks,0))
        ev=Block('event',{'event':'round_start'},{'body':[]})
        self.origin.blocks.append(ev)
        self.assertTrue(move_block(self.doc,ev.id,self.events,self.events.blocks,0))

    def test_data_restriction(self):
        self.assertFalse(move_block(self.doc,self.cond.id,self.data,self.data.blocks,0))
        value=Block('var',{'name':'x','value':'1'})
        self.origin.blocks.append(value)
        self.assertTrue(move_block(self.doc,value.id,self.data,self.data.blocks,0))

    def test_nested_to_top(self):
        self.assertTrue(move_block(self.doc,self.inner.id,self.origin,self.origin.blocks,1))
        self.assertEqual([b.kind for b in self.origin.blocks],['if','assign','return'])

if __name__=='__main__': unittest.main()
