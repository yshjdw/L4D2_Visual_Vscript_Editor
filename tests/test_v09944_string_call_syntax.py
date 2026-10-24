import unittest
from l4visual.models import Block
from l4visual.codegen import expression
from l4visual.expressions import as_embedded

class StringCallSyntaxTests(unittest.TestCase):
    def test_all_block_boundaries_separated(self):
        b=Block('string_call',{'function':'give_used_pill','parameters':['env.userid', 'pills.GetClassname()', 'now_used'], 'parameter_specs':[{'type':'int'}, {'type':'string'}, {'type':'int'}]})
        output=expression(as_embedded(b))
        self.assertNotIn('(function(', output)
        self.assertNotIn('for (local ', output)
        self.assertIn('pills.GetClassname()', output)
        self.assertIn(r'\"', output)
        self.assertEqual(output.count('pills.GetClassname()'), 1)


if __name__=='__main__': unittest.main()
