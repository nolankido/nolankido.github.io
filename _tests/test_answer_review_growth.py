"""Turn 07 reading and exact predecessor checks."""
import sys,unittest
from hashlib import sha1,sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tests'))
import answer_review_growth_history as history
class GuideGrowth(unittest.TestCase):
 def test_previous_bytes(self):
  for path,item in history.record().items():
   raw=(ROOT/path).read_bytes()
   actual=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() if 'new_git_sha' in item else sha256(raw).hexdigest()
   self.assertEqual(actual,item.get('new_git_sha',item.get('new_sha256')))
   old=history.before(path,raw)
   self.assertEqual(sha1(b'blob '+str(len(old)).encode()+b'\0'+old).hexdigest(),item['old_git_sha'])
 def test_unknown_changes(self):
  for path in history.record():
   raw=(ROOT/path).read_bytes()
   for altered in (raw+b'UNREVIEWED',b'UNREVIEWED'+raw,raw[1:]):
    self.assertEqual(history.before(path,altered),altered)
 def test_reader_guidance(self):
  raw=(ROOT/'technology/check-ai-answers/index.html').read_text()
  for term in ('A quick first pass: claim, evidence, decision','What the three evidence statuses mean','Supported for a stated purpose','Worked mini-check, fictional','Revision, October 17, 2026'):
   self.assertIn(term,raw)
  self.assertEqual(raw.count('class="review-example" id="'),6)
  self.assertNotIn('<form',raw)
  import json,re
  manifest=json.loads((ROOT/'_source/pages.json').read_text())
  page=next(x for x in manifest if x['id']=='ai-answer-review')
  self.assertEqual(page['date'],'2026-10-12')
  self.assertEqual(page['updated'],'2026-10-17')
  self.assertIn('"dateModified": "2026-10-17"',raw)
  xml=(ROOT/'sitemap.xml').read_text()
  self.assertIn('<loc>https://nolankido.com/technology/check-ai-answers/</loc>\n    <lastmod>2026-10-17</lastmod>',xml)
if __name__=='__main__':unittest.main()
