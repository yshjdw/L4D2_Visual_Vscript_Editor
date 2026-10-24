import unittest
from l4visual.codegen import expression
from l4visual.expressions import block_from_method, as_embedded
from l4visual.models import Block
from l4visual.official_docs import official_functions

class StringCallTests(unittest.TestCase):
    def test_string_call_with_dynamic_id(self):
        block=Block('string_call', {'function':'::datas.RestorePills','parameters':['env.userid']})
        self.assertEqual(expression(as_embedded(block)), '("::datas.RestorePills(" + (env.userid) + ")")')

    def test_string_call_zero_args(self):
        block=Block('string_call', {'function':'MyFunction','parameters':[]})
        self.assertEqual(expression(as_embedded(block)), '"MyFunction()"')

    def test_entfire_defaults(self):
        block=block_from_method(official_functions()['Globals.EntFire'])
        self.assertEqual(block.args['parameters'],['"worldspawn"','"RunScriptCode"','""','0.1','null'])
        self.assertEqual([s['name'] for s in block.args['parameter_specs']],['target','action','value','delay','activator'])

    def test_doentfire_defaults(self):
        block=block_from_method(official_functions()['Globals.DoEntFire'])
        self.assertEqual(block.args['parameters'][:2],['"worldspawn"','"RunScriptCode"'])

if __name__=='__main__':unittest.main()
