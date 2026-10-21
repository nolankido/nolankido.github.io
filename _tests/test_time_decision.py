"""Turn 08: decision interpretation and exact historical preservation."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import unittest,sys,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tests'))
import time_decision_history
import feedback_context_history
class TimeDecisionTests(unittest.TestCase):
 def test_real_release_only_restores_whole_sha_approved_files(self):
  for path,rec in time_decision_history.change().items():
   raw=feedback_context_history.before(path,(ROOT/path).read_bytes())
   self.assertEqual(sha256(raw).hexdigest(),rec['new_sha256'])
   self.assertEqual(sha256(time_decision_history.before(path,raw)).hexdigest(),rec['old_sha256'])
   self.assertEqual(sha256(time_decision_history.before(path,raw+b" ")).hexdigest(),sha256(raw+b" ").hexdigest())
  self.assertEqual(time_decision_history.before('about/index.html',b'unchanged'),b'unchanged')
 def test_review_time_sensitivity_can_reverse_fictional_saving(self):
  manual,assisted,review,count,setup,upkeep=map(Fraction,['30','8','7','6','60','15'])
  def net(review_minutes):return count*(manual-assisted-review_minutes)-setup-upkeep
  self.assertEqual(net(review),15)
  self.assertEqual(net(review+2),3)
  self.assertEqual(net(review+3),-3)
  self.assertEqual(manual-assisted-(setup+upkeep)/count,Fraction(19,2))
 def test_new_result_exposes_decision_and_not_fake_measurement(self):
  s=(ROOT/'assets/workflow-time.js').read_text()
  h=(ROOT/'_source/technology/ai-time-savings.html').read_text()
  for term in ['time-decision','time-review-budget','time-sensitivity']:
   self.assertIn(term,s);self.assertIn(term,h)
  for term in ['Quality check not met','MEASURE MORE','TRIAL AND MEASURE','CONSIDER KEEPING','STOP OR REDESIGN']:
   self.assertIn(term,s)
  self.assertIn('This is an illustration, not observed variation.',s)
  self.assertIn('fictional',h.lower())
 def test_original_arithmetic_and_no_collection(self):
  s=(ROOT/'assets/workflow-time.js').read_text()
  for phrase in ['fetch(','XMLHttpRequest','sendBeacon','localStorage','sessionStorage','innerHTML','eval(']:
   self.assertNotIn(phrase,s)
  code="const c=require('./assets/workflow-time.js').calculate;const x={manual:'30',assisted:'8',review:'7',count:'6',setup:'60',upkeep:'15'};console.log(c(x).net,c({...x,review:'10'}).net)"
  result=subprocess.run(['node','-e',code],cwd=ROOT,capture_output=True,text=True,check=True)
  self.assertEqual(result.stdout.strip(),'1500 -300')
if __name__=='__main__':unittest.main()
