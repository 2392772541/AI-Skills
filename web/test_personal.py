import json
from pathlib import Path
import tempfile
import unittest
from personal import Catalog

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'skills'
        self.root.mkdir()
        self.store = Path(self.tmp.name) / 'state'
        self.catalog = Catalog([self.root], self.store, interval=.05)

    def skill(self, relative, text='---\nname: example\ndescription: Test skill\n---\nBody'):
        p = self.root / relative / 'SKILL.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def test_exclusions_and_independent_copies(self):
        self.skill('one'); self.skill('two')
        for p in ['.system/builtin','plugins/cache/builtin','one.backup-123','archived/old','node_modules/embedded']:
            self.skill(p)
        self.assertTrue(self.catalog.scan())
        rows = self.catalog.snapshot()['items']
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(x['copies'] == 2 for x in rows))
        self.assertEqual(self.catalog.snapshot()['events'], [])

    def test_changes_labels_and_restart(self):
        self.catalog.scan()
        p=self.skill('new')
        self.catalog.scan()
        row=self.catalog.snapshot()['items'][0]
        sid=row['id']
        self.catalog.annotate(sid, {'source':'self','note':'test','favorite':True})
        p.parent.joinpath('helper.py').write_text('x=1')
        self.catalog.scan()
        p.unlink()
        self.catalog.scan()
        restored=Catalog([self.root], self.store)
        self.assertEqual(restored.snapshot()['items'][0]['source'],'self')
        self.skill('new')
        restored.scan()
        self.assertEqual([e['kind'] for e in restored.snapshot()['events']], ['restored','removed','modified','added'])
        self.assertTrue(restored.snapshot()['items'][0]['favorite'])

    def test_root_failure_does_not_remove(self):
        self.skill('one'); self.catalog.scan()
        self.catalog.roots.append(self.root/'unavailable')
        self.assertFalse(self.catalog.scan())
        self.assertEqual(self.catalog.snapshot()['items'][0]['status'],'active')
        self.assertEqual(self.catalog.snapshot()['events'],[])

    def test_aliases_are_deduplicated(self):
        self.skill('one')
        self.catalog.roots=[self.root,self.root]
        self.catalog.scan()
        self.assertEqual(len(self.catalog.snapshot()['items']),1)

    def test_epoch_timestamp_on_windows(self):
        import os
        p=self.skill('old-archive')
        os.utime(p, (0, 0))
        self.assertTrue(self.catalog.scan())
        self.assertEqual(len(self.catalog.snapshot()['items']), 1)

    @unittest.skipUnless(__import__('os').name == 'nt', 'Windows junction test')
    def test_windows_junction_alias(self):
        import subprocess
        import os
        self.skill('original')
        alias=self.root/'linked'
        subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(alias),str(self.root/'original')],check=True,capture_output=True)
        try:
            self.catalog.scan()
            rows=self.catalog.snapshot()['items']
            self.assertEqual(len(rows),1)
            self.assertEqual(len(rows[0]['aliases']),2)
        finally:
            os.rmdir(alias)

    def test_manual_source_overrides_receipt(self):
        self.skill('one'); self.catalog.scan()
        sid=self.catalog.snapshot()['items'][0]['id']
        self.catalog.state['items'][sid]['source_hint']='external'
        self.assertEqual(self.catalog.snapshot()['items'][0]['source'],'external')
        self.catalog.annotate(sid,{'source':'self'})
        self.assertEqual(self.catalog.snapshot()['items'][0]['source'],'self')

    def test_validation_and_safe_detail(self):
        self.skill('one'); self.catalog.scan()
        sid=self.catalog.snapshot()['items'][0]['id']
        with self.assertRaises(KeyError): self.catalog.detail('../../secret')
        with self.assertRaises(ValueError): self.catalog.annotate(sid, {'source':'invented'})
        with self.assertRaises(ValueError): self.catalog.annotate(sid, {'note':'x'*2001})

    def test_background_watcher(self):
        import time
        self.catalog.start()
        self.addCleanup(self.catalog.stop.set)
        self.skill('background')
        deadline=time.monotonic()+3
        while time.monotonic()<deadline and not self.catalog.snapshot()['events']:
            time.sleep(.03)
        self.catalog.stop.set()
        self.catalog.thread.join(timeout=2)
        self.assertEqual(self.catalog.snapshot()['events'][0]['kind'],'added')

    def test_categories_and_description_survive_scan_and_partial_update(self):
        self.skill('one');self.catalog.scan()
        sid=self.catalog.snapshot()['items'][0]['id']
        self.catalog.annotate(sid, {'categories':['writing','我的常用'], 'guide_override':{'summary':'帮我把文章写顺。'}, 'source':'self'})
        self.catalog.annotate(sid, {'favorite':True})
        self.catalog.scan()
        resumed=Catalog([self.root],self.store)
        row=resumed.snapshot()['items'][0]
        self.assertEqual(row['categories'],['writing','我的常用'])
        self.assertEqual(row['guide']['summary'],'帮我把文章写顺。')
        self.assertEqual(row['guide_status'],'manual')
        self.assertEqual(row['source'],'self')
        self.assertTrue(row['favorite'])

    def test_new_skill_pending_and_changed_guide_stale(self):
        p=self.skill('one','---\nname: shuorenhua\ndescription: Rewrite text\n---\nBody')
        self.catalog.scan()
        row=self.catalog.snapshot()['items'][0]
        self.assertEqual(row['guide_status'],'stale')
        self.catalog.guide_revisions={'shuorenhua':[row['md_hash']]}
        self.assertEqual(self.catalog.snapshot()['items'][0]['guide_status'],'reviewed')
        p.write_text(p.read_text()+'\nChanged')
        self.catalog.scan()
        self.assertEqual(self.catalog.snapshot()['items'][0]['guide_status'],'stale')
        self.skill('new');self.catalog.scan()
        row=next(x for x in self.catalog.snapshot()['items'] if x['name']=='example')
        self.assertEqual(row['guide_status'],'pending')
        self.assertEqual(row['categories'],['other'])

    def test_reject_invalid_categories_and_guide(self):
        self.skill('one');self.catalog.scan();sid=self.catalog.snapshot()['items'][0]['id']
        for cats in [[], ['x']*9, [''], ['a'*41], 'video']:
            with self.assertRaises(ValueError):self.catalog.annotate(sid,{'categories':cats})
        with self.assertRaises(ValueError):self.catalog.annotate(sid,{'guide_override':{'run':'anything'}})

    def test_publication_is_separate_from_video_production(self):
        from guidebook import GUIDES
        for name in ['bilibili-upload','douyin-upload','kuaishou-upload','xiaohongshu-upload']:
            self.assertEqual(GUIDES[name]['categories'],['publish'])
        self.assertEqual(GUIDES['douyin-favorite-links']['categories'],['bookmarks'])
        self.assertEqual(GUIDES['remotion-video']['categories'],['video'])
        self.assertEqual(GUIDES['hyperframes-animation']['categories'],['video-motion'])

if __name__=='__main__': unittest.main()
