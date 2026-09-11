import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
import skills_portable as p

class PortableTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='portable-test-')
        self.root=Path(self.temp.name);self.repo=self.root/'repo';self.repo.mkdir()
        self.override=patch.object(p,'REPO',self.repo);self.override.start();p.public_reviews.cache_clear()
        lib=self.root/'source';codex=self.root/'codex';cursor=self.root/'cursor'
        for folder in [lib/'skills/demo',lib/'scripts',lib/'tests',lib/'web',lib/'registry',codex/'demo',cursor/'demo']:
            folder.mkdir(parents=True)
        (lib/'skills/demo/SKILL.md').write_text('shared')
        (codex/'demo/SKILL.md').write_text('codex-custom')
        (cursor/'demo/SKILL.md').write_text('cursor-custom')
        (lib/'registry/overrides.json').write_text('{}')
        self.config=self.root/'config.json'
        p.dump(self.config,{'library':str(lib),'codex':str(codex),'cursor':str(cursor)})
    def tearDown(self):
        self.override.stop();p.public_reviews.cache_clear();self.temp.cleanup()
    def test_roundtrip_preserves_variants_and_installs_idempotently(self):
        p.export(self.config);target=self.root/'restored';p.restore(target,False)
        self.assertEqual((target/'user/.codex/skills/demo/SKILL.md').read_text(),'codex-custom')
        self.assertEqual((target/'user/.agents/skills/demo/SKILL.md').read_text(),'shared')
        user=self.root/'new-user';p.install(target,user);p.install(target,user)
        self.assertEqual((user/'.cursor/skills/demo/SKILL.md').read_text(),'cursor-custom')
    def test_conflict_causes_no_partial_install(self):
        p.export(self.config);target=self.root/'restored';p.restore(target,False)
        user=self.root/'new-user';(user/'.cursor/skills/demo').mkdir(parents=True)
        (user/'.cursor/skills/demo/SKILL.md').write_text('my-edit')
        with self.assertRaisesRegex(ValueError,'Local conflict'):p.install(target,user)
        self.assertFalse((user/'.agents').exists())
    def test_restore_refuses_existing_target(self):
        p.export(self.config)
        with self.assertRaisesRegex(ValueError,'must not exist'):p.restore(self.root,False)
    def test_tamper_fails_before_restore(self):
        p.export(self.config);(self.repo/'skills/demo/SKILL.md').write_text('changed')
        target=self.root/'restored'
        with self.assertRaises(ValueError):p.restore(target,False)
        self.assertFalse(target.exists())
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):p.checked_path(self.root,'../escape')
    def test_secret_blocks_export_without_replacing_snapshot(self):
        p.export(self.config)
        (self.root/'source/skills/demo/SKILL.md').write_text('sk-'+('AbC123xYz9'*4))
        with self.assertRaisesRegex(ValueError,'secret review'):p.export(self.config)
        self.assertEqual((self.repo/'skills/demo/SKILL.md').read_text(),'shared')
    def test_missing_source_blocks_export(self):
        config=p.read(self.config);config['codex']=str(self.root/'missing');p.dump(self.config,config)
        with self.assertRaisesRegex(ValueError,'Missing source'):p.export(self.config)
        self.assertFalse((self.repo/'skills').exists())
    def test_vendor_gitignore_cannot_drop_manifest_assets(self):
        p.export(self.config)
        p.git('init')
        (self.repo/'.gitignore').write_text('skills/\nprofiles/\n')
        p.stage_manifest()
        tracked=set(p.git('ls-files','-z').split('\0'))
        self.assertTrue(set(p.read(self.repo/'portable/manifest.json')['files']).issubset(tracked))

if __name__=='__main__':unittest.main()
