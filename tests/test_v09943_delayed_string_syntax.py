import unittest
from l4visual.models import Block
from l4visual.codegen import expression
from l4visual.expressions import as_embedded

class DelayedStringSyntaxTests(unittest.TestCase):
    def test_typed_string_escaping_separates_control_statements(self):
        b = Block('string_call', {'function': 'give_used_pill',
            'parameters': ['env.userid', 'pills.GetClassname()', 'now_used'],
            'parameter_specs': [
                {'name': 'userid', 'type': 'int'},
                {'name': 'pills_classname', 'type': 'string'},
                {'name': 'has_used', 'type': 'int'}]})
        result = expression(as_embedded(b))
        self.assertIn('pills.GetClassname()', result)
        self.assertIn(r'\"', result)
        self.assertNotIn('(function(', result)
        self.assertNotIn('format("%c", 34)', result)
        self.assertEqual(result.count('pills.GetClassname()'), 1)


if __name__ == '__main__': unittest.main()
