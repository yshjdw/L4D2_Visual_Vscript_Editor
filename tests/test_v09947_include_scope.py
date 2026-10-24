"""IncludeScript defaults are editor choices, not changes to Valve's signature."""
import unittest
from l4visual.catalog import Catalog
from l4visual.expressions import block_from_method, method_call_expression
from l4visual.codegen import SquirrelGenerator, expression
from l4visual.models import Block, ScriptDocument, Project, Section
from l4visual.api_docs import method_tooltip
from l4visual.display_profile import current_profile, use_profile
from l4visual.official_docs import official_functions

class IncludeScopeTests(unittest.TestCase):
    def setUp(self):
        self.cat = Catalog()
    def tearDown(self):
        self.cat.close()

    def test_default_call_from_official_method(self):
        b=block_from_method(self.cat.method('Globals','IncludeScript'))
        self.assertEqual(b.args['parameters'], ['""','getroottable()'])
        self.assertEqual(b.args['parameter_specs'], [
            {'name':'file','type':'string'}, {'name':'scope','type':'handle/table'}])
        self.assertEqual(method_call_expression(b,expression), 'IncludeScript("", getroottable())')
        self.assertEqual(b.kind,'call')

    def test_scope_can_be_customized(self):
        b=block_from_method(self.cat.method('Globals','IncludeScript'))
        b.args['parameters']=['"other_script"','entity.GetScriptScope()']
        self.assertEqual(method_call_expression(b,expression),
                         'IncludeScript("other_script", entity.GetScriptScope())')

    def test_native_documentation_still_says_null(self):
        self.assertIn('scope = null', official_functions()['Globals.IncludeScript']['signature'])

    def test_saved_calls_not_replaced(self):
        original=Block('call',{'function':'IncludeScript','parameters':['"old"','null'],
                               'parameter_specs':[{'name':'file','type':'string'},{'name':'scope','type':'handle'}],
                               'return_type':'bool','output':''})
        doc=ScriptDocument('director_base_addon.nut',[Section('init','init',[original])])
        restored=Project.from_dict(Project('p',documents=[doc]).to_dict())
        b=restored.documents[0].sections[0].blocks[0]
        self.assertEqual(b.args['parameters'][1],'null')
        code=SquirrelGenerator().compile(restored,restored.documents[0])
        self.assertIn('IncludeScript("old", null);',code)

    def test_editor_default_compiles_as_explicit_root(self):
        b=block_from_method(self.cat.method('Globals','IncludeScript'))
        b.args['parameters'][0]='"sample"'
        b.args['output']=''
        doc=ScriptDocument('director_base_addon.nut',[Section('init','init',[b])])
        code=SquirrelGenerator().compile(Project('p',documents=[doc]),doc)
        self.assertIn('IncludeScript("sample", getroottable());',code)

    def test_editor_default_note_is_bilingual(self):
        origin=current_profile()
        try:
            row=self.cat.method('Globals','IncludeScript')
            for style in ('general','professional'):
                use_profile('en',style)
                en=method_tooltip(row)
                self.assertIn('Editor default: scope = getroottable()',en)
                use_profile('zh',style)
                zh=method_tooltip(row)
                self.assertIn('编辑器默认：scope = getroottable()',zh)
        finally:
            use_profile(origin.language,origin.style)

if __name__=='__main__': unittest.main()
