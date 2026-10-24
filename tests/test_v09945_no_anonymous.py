import json
import re
import unittest
from pathlib import Path

from l4visual.models import Project, ScriptDocument, Section, Block
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.expressions import as_embedded, string_argument_expression
from l4visual.utility_blocks import UTILITY_BLOCKS, create_utility_args


class NoAnonymousWrapperTests(unittest.TestCase):
    def test_classname_string_call_is_simple_and_single_evaluation(self):
        block = Block('string_call', {
            'function': 'give_used_pill',
            'parameters': ['env.userid', 'pills.GetClassname()', 'now_used'],
            'parameter_specs': [{'type':'int'}, {'type':'string'}, {'type':'int'}],
        })
        code = expression(as_embedded(block))
        self.assertEqual(code.count('pills.GetClassname()'), 1)
        self.assertIn(r'\"', code)
        self.assertNotIn('(function(', code)
        self.assertNotIn('format(', code)

    def test_static_string_quotation_is_escaped_at_generation_time(self):
        code = string_argument_expression('"hello\\\"world"', 'string', expression)
        self.assertNotIn('(function(', code)
        self.assertEqual(json.loads(code), json.dumps(json.loads('"hello\\\"world"'), ensure_ascii=False))

    def test_all_utility_operations_no_immediately_invoked_functions(self):
        for op in UTILITY_BLOCKS:
            with self.subTest(op=op):
                code = expression(as_embedded(Block('utility', create_utility_args(op))))
                self.assertNotIn('(function(', code)
                self.assertFalse(re.search(r'\}\)\s*\(',code))

    def test_named_helpers_are_injected_once_with_dependencies(self):
        b = Block('utility', create_utility_args('inventory_slot_classname'))
        doc = ScriptDocument('test.nut', [Section('function','GetPills', [
            Block('return', {'value': as_embedded(b)}),
            Block('return', {'value': as_embedded(b)}),
        ])])
        code = SquirrelGenerator().compile(Project('p', documents=[doc]), doc)
        self.assertEqual(code.count('::L4VP_Utils <- {};'), 1)
        self.assertEqual(code.count('::L4VP_Utils.InventorySlot <- function('), 1)
        self.assertEqual(code.count('::L4VP_Utils.InventorySlotClassname <- function('), 1)
        self.assertEqual(code.count('::L4VP_Utils.Valid <- function('), 1)
        self.assertIn('GetInvTable(p, inv);', code)
        self.assertNotIn('(function(', code)
        self.assertLess(code.index('::L4VP_Utils.Valid <-'),code.index('::GetPills <-'))

    def test_plain_document_has_no_unused_helpers(self):
        doc = ScriptDocument('test.nut', [Section('function','Hello',[
            Block('return',{'value':'42'})])])
        out=SquirrelGenerator().compile(Project('p',documents=[doc]),doc)
        self.assertNotIn('L4VP_Utils',out)


if __name__=='__main__': unittest.main()
