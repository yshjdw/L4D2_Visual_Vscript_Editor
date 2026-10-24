import unittest
from l4visual.models import ScriptDocument, Section, Block
from l4visual.complex_copy import clone_with_definitions
from l4visual.data_definitions import linked_definition, render_definition

class TestComplexCopy(unittest.TestCase):
    def test_copy_table_and_nested_array(self):
        first=Block('var',{'name':'cfg','container_type':'Table','value':'{}'})
        child=Block('var',{'name':'numbers','container_type':'Set','value':'[1,2]'})
        root=Section('namespace','Game',[first])
        table=Section('data','cfg',[child],{'source_id':first.id,'parent_section_id':'','container':'Table'})
        array=Section('data','numbers',[Block('var',{'name':'0','value':'1'}),Block('var',{'name':'1','value':'2'})],{'source_id':child.id,'parent_section_id':table.id,'container':'Set'})
        doc=ScriptDocument('main.nut',[root,table,array])
        copied=clone_with_definitions(doc,first)
        root.blocks.append(copied)
        duplicate_table=linked_definition(doc,copied.id)
        self.assertIsNotNone(duplicate_table)
        self.assertNotEqual(duplicate_table.id,table.id)
        nested=duplicate_table.blocks[0]
        self.assertIsNotNone(linked_definition(doc,nested.id,duplicate_table.id))
        self.assertEqual(render_definition(doc,duplicate_table)['items']['numbers']['items'],['1','2'])
        duplicate_table.blocks[0].args['name']='different'
        self.assertEqual(table.blocks[0].args['name'],'numbers')

    def test_copy_without_definition_falls_back_to_literal(self):
        source=Block('var',{'name':'items','container_type':'Set','value':'[4,5]'})
        doc=ScriptDocument('main.nut',[Section('namespace','Game',[source])])
        duplicate=clone_with_definitions(doc,source)
        self.assertNotEqual(duplicate.id,source.id)
        self.assertIsNone(linked_definition(doc,duplicate.id))

if __name__=='__main__':unittest.main()
