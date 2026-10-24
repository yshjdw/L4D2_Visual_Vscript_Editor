import unittest
from pathlib import Path
from l4visual.math_blocks import OPERATORS, MATH_FUNCTIONS, CUSTOM_MATH_HELPERS, emit_math
from l4visual.codegen import expression
ROOT=Path(__file__).resolve().parents[1]

class UpgradeTests(unittest.TestCase):
    def test_switch_groups_are_disjoint(self):
        groups=[set(v) for v in OPERATORS.values()]
        for i,one in enumerate(groups):
            for two in groups[i+1:]:self.assertFalse(one & two)
        self.assertIn('!=',OPERATORS['比较'])
        self.assertIn('*',OPERATORS['算术'])

    def test_math_parameter_arities(self):
        for name,arity in MATH_FUNCTIONS.items():
            self.assertIn(arity,(1,2))
            expr=emit_math({'function':name,'parameters':['4']*arity},expression)
            expected=('::L4VP_Utils.'+CUSTOM_MATH_HELPERS[name]) if name in CUSTOM_MATH_HELPERS else name
            self.assertTrue(expr.startswith(expected+'('))

    def test_nested_and_statement_controls_exist(self):
        text=(ROOT/'l4visual/ui/canvas.py').read_text(encoding='utf-8')
        self.assertIn('切换运算符 / Switch operator',text)
        self.assertIn('切换 Math 函数 / Switch Math',text)
        self.assertIn('编辑参数槽 / Edit arguments…',text)
        self.assertIn("picker.currentTextChanged.connect(select_math)",text)

    def test_section_dialog_does_not_clear_inactive_fields(self):
        text=(ROOT/'l4visual/ui/dialogs.py').read_text(encoding='utf-8')
        sec=text[text.index('    def update_fields(self):'):text.index('    def accept(self):',text.index('    def update_fields(self):'))]
        self.assertIn('setVisible(enabled)',sec)
        self.assertNotIn('.clear()',sec)

    def test_shortcuts(self):
        text=(ROOT/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        for item in ('＋函数','＋Namespace','＋复杂变量'):
            self.assertIn(item,text)
        self.assertIn('create_definition(self.current_doc,section,block)',text)

if __name__=='__main__':unittest.main()
