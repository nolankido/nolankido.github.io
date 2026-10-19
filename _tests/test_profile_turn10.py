"""Turn 10 public identity provenance, no invented claims, preservation."""
from pathlib import Path
from hashlib import sha256
import sys,unittest,json,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
sys.path.insert(0,str(ROOT/'_tests'))
import build,turn10_profile_history as history
class TestTurn10(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.outputs=build.build_outputs()
 def test_exact_history_only_for_six_approved_files(self):
  for path, rec in history.records().items():
   data=(ROOT/path).read_bytes()
   self.assertEqual(sha256(data).hexdigest(),rec['new_sha256'],path)
   self.assertEqual(sha256(history.before(path,data)).hexdigest(),rec['old_sha256'],path)
   self.assertEqual(history.before(path,data+b'changed'),data+b'changed',path)
  self.assertEqual(history.before('index.html',b'unchanged'),b'unchanged')
 def test_manifest_only_dates_change(self):
  current=json.loads((ROOT/'_source/pages.json').read_text())
  old=json.loads(history.before('_source/pages.json',(ROOT/'_source/pages.json').read_text()))
  changes=[]
  for old_p,new_p in zip(old,current):
   if old_p!=new_p:
    changes.append(old_p['id'])
    self.assertEqual(set(old_p)|set(new_p),set(old_p))
    self.assertEqual({k:v for k,v in old_p.items() if k!='updated'},{k:v for k,v in new_p.items() if k!='updated'})
    self.assertEqual(new_p['updated'],'2026-10-17')
  self.assertEqual(changes,['about','bio'])
 def test_public_bios_identical_to_one_original_source(self):
  site=json.loads((ROOT/'_source/site.json').read_text())
  html=self.outputs[Path('bio/index.html')]
  for size in ['short','long']:
   text=site['bio_'+size]
   self.assertIn(text,html)
   self.assertEqual((ROOT/('downloads/nolan-kido-'+size+'-bio.txt')).read_text(),text+'\n')
  for key in ['jobTitle','sameAs','award','affiliation','aggregateRating']:
   self.assertNotIn('"'+key+'"',html)
 def test_three_distinct_evidence_paths_and_preserved_bookmarks(self):
  about=self.outputs[Path('about/index.html')]
  bio=self.outputs[Path('bio/index.html')]
  for link in ['/technology/task-brief/','/technology/checking-ai-website-changes/','/notes/keep-the-judgment/']:
   self.assertIn('href="'+link+'"',about)
   self.assertIn('href="'+link+'"',bio)
  for anchor in ['what-matters-in-the-work','try-the-work']:
   self.assertEqual(about.count('id="'+anchor+'"'),1)
  for anchor in ['profile-short-text','profile-long-text','profile-site-url','profile-selected-work']:
   self.assertEqual(bio.count('id="'+anchor+'"'),1)
  self.assertIn('not a measured productivity result',about)
  self.assertIn('not a general performance claim',bio)
 def test_no_new_tracking_or_input_collection(self):
  for page in ['about/index.html','bio/index.html']:
   new=self.outputs[Path(page)]
   old=history.before(page,new)
   self.assertEqual(new.count('cloud.umami.is/script.js'),old.count('cloud.umami.is/script.js'))
   self.assertEqual(new.count('<script '),old.count('<script '))
   self.assertNotIn('<form',new)
if __name__=='__main__':unittest.main()
