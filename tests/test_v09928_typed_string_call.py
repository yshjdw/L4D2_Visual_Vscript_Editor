import unittest
from l4visual.models import Block
from l4visual.codegen import expression
from l4visual.expressions import as_embedded, string_argument_expression

class TypedStringCallTests(unittest.TestCase):
    def test_classname_is_quoted_and_escaped(self):
        b=Block('string_call', {'function':'give_used_pill',
            'parameters':['env.userid','pills.GetClassname()','now_used'],
            'parameter_specs':[{'name':'userid','type':'int'},{'name':'pills_classname','type':'string'},{'name':'has_used','type':'int'}]})
        result=expression(as_embedded(b))
        self.assertIn(r'\"', result)
        self.assertNotIn('(function(', result)
        self.assertIn('(pills.GetClassname())',result)
        self.assertIn('(env.userid)',result)
        self.assertIn('(now_used)',result)
        self.assertEqual(result.count('pills.GetClassname()'),1)
    def test_unknown_type_remains_legacy(self):
        self.assertEqual(string_argument_expression('env.userid','auto',expression),'(env.userid)')
    def test_non_serializable_types_rejected(self):
        with self.assertRaises(ValueError):string_argument_expression('player','handle',expression)

if __name__=='__main__':unittest.main()
