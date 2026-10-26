"""Bounded followup for two previously inconclusive public sources."""
from datetime import date
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,poker_resources,resource_followup_history as history
import regional_link_history
class FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/'_source/poker/resources.json').read_text()
        cls.current=json.loads(cls.raw)['entries']
        cls.prior=json.loads(history.before('_source/poker/resources.json',cls.raw))['entries']
        cls.entries=poker_resources.load(ROOT)
    def test_exactly_two_changes_and_all_links_preserved(self):
        self.assertEqual(len(self.current),146)
        self.assertEqual([e['id'] for e in self.current],[e['id'] for e in self.prior])
        diffs=[(a,b) for a,b in zip(self.prior,self.current) if a!=b]
        self.assertEqual({b['id'] for a,b in diffs},history.IDS)
        for a,b in diffs:
            self.assertEqual(a['url'],b['url'])
            self.assertEqual(a['description'],b['description'])
            self.assertEqual(b['reviewed_on'],'2026-10-24')
            self.assertEqual({k for k in b if a[k]!=b[k]},
             {'notes','review_method','reviewed_on'} if b['id']=='nj-dge-information' else {'notes','reviewed_on'})
    def test_limits_and_review_queue(self):
        e={r['id']:r for r in self.entries}
        self.assertEqual(e['nj-dge-information']['review_method'],'page')
        self.assertIn('eligibility were not checked',e['nj-dge-information']['notes'])
        self.assertIn('real-time',e['wynn-poker']['notes'].replace('live game','real-time'))
        self.assertEqual({r['id'] for r in poker_resources.review_queue(history.resources(self.entries),date(2026,10,24))},history.IDS)
        self.assertEqual(poker_resources.review_queue(self.entries,date(2026,10,24)),[])
    def test_export_exact_and_predecessor_bytes(self):
        out=build.build_outputs()
        r=json.loads(out[Path('downloads/poker-resource-directory.json')])['entries']
        self.assertEqual({e['id']:e for e in r},{e['id']:e for e in self.entries})
        for f,v in history.change()['paths'].items():
            raw=(ROOT/f).read_bytes();parent=regional_link_history.before(f,raw)
            old=history.before(f,raw)
            self.assertEqual(sha256(parent).hexdigest(),v['new_sha256'])
            self.assertEqual(sha256(old).hexdigest(),v['old_sha256'])
            self.assertEqual(history.before(f,raw+b'x'),raw+b'x')
    def test_corrupt_history_rejected(self):
        x=deepcopy(history.change());x['paths']['_source/poker/resources.json']['old_sha256']='0'*64
        with patch.object(history,'change',return_value=x),self.assertRaises(ValueError):
            history.before('_source/poker/resources.json',(ROOT/'_source/poker/resources.json').read_bytes())
    def test_scope(self):
        self.assertEqual(set(history.change()['paths']),{
          '_source/poker/resources.json','downloads/poker-resource-directory.json',
          'downloads/poker-resource-directory.md','poker/find/index.html',
          'poker/poker-access-and-protection/index.html',
          'poker/resource-quality/index.html','poker/resources/index.html'})
if __name__=='__main__':unittest.main()
