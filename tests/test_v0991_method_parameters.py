import unittest
from l4visual.catalog import Catalog
from l4visual.expressions import block_from_method
from l4visual.official_docs import official_functions


class MethodParameterAuditTests(unittest.TestCase):
    def test_weapon_clip_setters_have_amount_socket(self):
        c=Catalog()
        try:
            for name in ('SetClip1','SetClip2'):
                row=c.method('CTerrorWeapon',name)
                block=block_from_method(row)
                self.assertEqual(len(block.args['parameters']),1)
                self.assertEqual(block.args['parameter_specs'][0],{'name':'amount','type':'int'})
                self.assertEqual(block.args['parameters'][0],'0')
        finally:c.close()

    def test_catalog_is_consistent_with_documented_method_parameters(self):
        c=Catalog()
        try:
            for doc in official_functions().values():
                row=c.method(doc['owner'],doc['name'])
                if row and doc.get('parameters'):
                    block=block_from_method(row)
                    self.assertEqual(len(block.args['parameters']),len(doc['parameters']),
                                     doc['owner']+'.'+doc['name'])
        finally:c.close()

    def test_other_methods(self):
        c=Catalog()
        try:
            examples=[('CBaseEntity','SetHealth',1),('CTerrorWeapon','Reload',0),('CBaseEntity','TakeDamage',3)]
            for owner,name,count in examples:
                row=c.method(owner,name)
                self.assertIsNotNone(row)
                self.assertEqual(len(block_from_method(row).args['parameters']),count)
        finally:c.close()

if __name__=='__main__':unittest.main()

class ExistingProjectRepairTests(unittest.TestCase):
    def test_repair_old_set_clip_without_arguments(self):
        from l4visual.models import Block
        from l4visual.expressions import repair_documented_method_parameters
        b=Block('method',{'owner':'CTerrorWeapon','target':'weapon','method':'SetClip1','parameters':[]})
        self.assertTrue(repair_documented_method_parameters(b))
        self.assertEqual(b.args['parameters'],['0'])
        self.assertFalse(repair_documented_method_parameters(b))

    def test_preserve_arguments(self):
        from l4visual.models import Block
        from l4visual.expressions import repair_documented_method_parameters
        b=Block('method',{'owner':'CTerrorWeapon','method':'SetClip2','parameters':['ammo']})
        self.assertFalse(repair_documented_method_parameters(b))
        self.assertEqual(b.args['parameters'],['ammo'])
