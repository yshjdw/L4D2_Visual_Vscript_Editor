import unittest
from l4visual.models import Block, Section, ScriptDocument, Project
from l4visual.data_definitions import create_definition
from l4visual.codegen import SquirrelGenerator

class ScopeInitTests(unittest.TestCase):
    def make(self, mode=None):
        owner=Block('var',{'name':'scope','container_type':'ScriptScope','value':'player','scope':'local'})
        fn=Section('function','Update',[owner],{'params':[]})
        doc=ScriptDocument('director_base_addon.nut',[fn]); project=Project(documents=[doc]); data=create_definition(doc,fn,owner)
        args={'name':'ammo_keep','value':'20','container_type':'普通'}
        if mode:args['init_mode']=mode
        data.blocks.append(Block('var',args))
        return project,doc

    def test_first_only_is_default(self):
        project,doc=self.make(); g=SquirrelGenerator(); script=g.compile(project,doc)
        self.assertFalse(g.errors,g.errors)
        self.assertIn('if (!scope.rawin("ammo_keep")) scope.ammo_keep <- 20;',script)

    def test_every_time_overwrites(self):
        project,doc=self.make('overwrite');g=SquirrelGenerator();script=g.compile(project,doc)
        self.assertFalse(g.errors,g.errors)
        self.assertIn('scope.ammo_keep <- 20;',script)
        self.assertNotIn('rawin("ammo_keep")',script)

    def test_only_existing(self):
        project,doc=self.make('existing');g=SquirrelGenerator();script=g.compile(project,doc)
        self.assertFalse(g.errors,g.errors)
        self.assertIn('if (scope.rawin("ammo_keep")) scope.ammo_keep = 20;',script)

    def test_nested_container_first_only(self):
        project,doc=self.make(); data=[s for s in doc.sections if s.kind=='data'][0]
        nested=Block('var',{'name':'inventory','value':'{}','container_type':'Table'})
        data.blocks.append(nested)
        sub=create_definition(doc,data,nested)
        sub.blocks.append(Block('var',{'name':'ammo','value':'8','container_type':'普通'}))
        g=SquirrelGenerator();script=g.compile(project,doc)
        self.assertFalse(g.errors,g.errors)
        self.assertIn('if (!scope.rawin("inventory")) scope.inventory <- {ammo = 8};',script)

    def test_save_roundtrip_preserves_mode(self):
        project,doc=self.make('existing')
        saved=Project.from_dict(project.to_dict())
        restored=[s for s in saved.documents[0].sections if s.kind=='data'][0]
        self.assertEqual(restored.blocks[0].args['init_mode'],'existing')

if __name__=='__main__':unittest.main()
