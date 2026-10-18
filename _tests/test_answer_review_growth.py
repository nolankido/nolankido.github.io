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
   self.assertEqual(sha256(raw).hexdigest(),item['new_sha256'])
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
if __name__=='__main__':unittest.main()
