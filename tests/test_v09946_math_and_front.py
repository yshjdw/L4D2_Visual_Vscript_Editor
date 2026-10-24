"""Regression coverage for custom max/min and new-section stacking."""
from pathlib import Path
import unittest
from l4visual.math_blocks import MATH_FUNCTIONS, emit_math
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.models import Block, Project, ScriptDocument, Section
from l4visual.expressions import as_embedded
from l4visual.utility_helpers import insert_named_helpers

ROOT=Path(__file__).resolve().parents[1]


class Math46Tests(unittest.TestCase):
    def test_arity_and_emission(self):
        for name, func in [('max','Max'), ('min','Min')]:
            with self.subTest(name=name):
                self.assertEqual(MATH_FUNCTIONS[name], 2)
                self.assertEqual(emit_math({'function':name,'parameters':['7','3']},expression),
                                 f'::L4VP_Utils.{func}(7, 3)')
                with self.assertRaises(ValueError):
                    emit_math({'function':name,'parameters':['7']},expression)

    def test_nested_math_expression_helpers_once(self):
        larger=Block('math_call',{'function':'max','parameters':['a','b']})
        smaller=Block('math_call',{'function':'min','parameters':[as_embedded(larger),'limit']})
        document=ScriptDocument('test.nut',[Section('function','Choose',[
            Block('return',{'value':as_embedded(smaller)}),
        ],{'params':['a','b','limit']})])
        code=SquirrelGenerator().compile(Project('test',documents=[document]),document)
        self.assertIn('::L4VP_Utils.Max(a, b)',code)
        self.assertIn('::L4VP_Utils.Min(::L4VP_Utils.Max(a, b), limit)',code)
        self.assertEqual(code.count('::L4VP_Utils.Max <- function('),1)
        self.assertEqual(code.count('::L4VP_Utils.Min <- function('),1)
        self.assertIn('return a >= b ? a : b;',code)
        self.assertIn('return a <= b ? a : b;',code)
        self.assertNotIn('(function(',code)
        self.assertLess(code.index('::L4VP_Utils.Min <- function('), code.index('::Choose <- function('))

    def test_only_used_math_helper_is_injected(self):
        doc=ScriptDocument('test.nut',[Section('function','OnlyMax',[
            Block('return',{'value':as_embedded(Block('math_call',{'function':'max','parameters':['4','9']}))})
        ])])
        output=SquirrelGenerator().compile(Project('p',documents=[doc]),doc)
        self.assertIn('::L4VP_Utils.Max <- function(',output)
        self.assertNotIn('::L4VP_Utils.Min <- function(',output)
        self.assertEqual(insert_named_helpers('local x = pow(2,3);'), 'local x = pow(2,3);')

    def test_drag_payload_and_localized_palette_exist(self):
        dialogs=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf-8')
        palette=(ROOT/'l4visual/ui/palette.py').read_text(encoding='utf-8')
        self.assertIn("payload.startswith('math:')",dialogs)
        self.assertIn("block.args.update(function=name, parameters=['0','0']",dialogs)
        self.assertIn("class CustomMathPaletteBlock",palette)
        self.assertIn("('math:'+self.function)",palette)
        for snippet in ('Maximum','Minimum','较大值','较小值','professional','description'):
            if snippet=='description':continue
            self.assertIn(snippet,palette)

    def test_new_sections_are_raised_without_reordering_models(self):
        canvas=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        region=canvas[canvas.index('    def add_section_item('):canvas.index('    def load(',canvas.index('    def add_section_item('))]
        self.assertIn('self.raise_item(item)',region)
        window=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        sec=window[window.index('    def add_section('):window.index('    def show_entity_help(',window.index('    def add_section('))]
        self.assertIn('self.current_doc.sections.append(section)',sec)
        self.assertIn('self.canvas.board.add_section_item(section)',sec)


if __name__=='__main__':unittest.main()
