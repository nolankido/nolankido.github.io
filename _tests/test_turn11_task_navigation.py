"""Turn 11: task-first entry, file-first resources and query-first finder."""
from pathlib import Path
import profile_datetime_history
from hashlib import sha256
from html.parser import HTMLParser
import sys,unittest,json,zlib
from copy import deepcopy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import turn11_task_navigation_history as history
import turn09_weekly_reset_history as weekly_history
TASKS={'/technology/task-brief/','/technology/check-ai-answers/','/living-well/weekly-reset/','/poker/first-live-tournament/'}
OTHER={'/technology/ai-time-savings/','/poker/hand-rankings/'}
class Reader(HTMLParser):
 def __init__(self,s):
  super().__init__();self.links=[];self.ids=[];self.scripts=[];self.forms=[];self.feed(s)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a':self.links.append(a.get('href'))
  if tag=='script' and a.get('src'):self.scripts.append(a['src'])
  if tag in ('form','textarea'):self.forms.append(tag)
class TaskRouteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.outputs=build.build_outputs()
 def page(self,path):return self.outputs[build.output_path(path)]
 def test_task_first_and_original_destinations_remain(self):
  s=self.page('/start-here/');page=Reader(s)
  self.assertLess(s.index('id="start-tasks-title"'),s.index('id="start-routes-title"'))
  self.assertLess(s.index('id="start-routes-title"'),s.index('id="start-reading-title"'))
  for t in TASKS:self.assertIn(t,page.links)
  self.assertEqual(s.count('class="entry-card"'),4)
  self.assertEqual(s.count('class="identity-reading"'),3)
  self.assertIn('Stopping after one useful result is enough.',s)
  self.assertIn('/resources/',page.links);self.assertIn('/find/',page.links)
 def test_all_six_priorities_findable_without_duplicate_site_menu(self):
  start=Reader(self.page('/start-here/'));resources=Reader(self.page('/resources/'))
  self.assertTrue(TASKS <= set(start.links));self.assertTrue(OTHER <= set(resources.links))
  for href in ['/downloads/ai-task-brief.txt','/downloads/ai-answer-review.txt','/downloads/living-well-weekly-reset.md']:
   self.assertIn(href,resources.links)
   self.assertTrue((ROOT/href.lstrip('/')).is_file())
  self.assertIn('/creative/#creative-brief',resources.links)
  self.assertEqual(len(set(start.ids)),len(start.ids));self.assertEqual(len(set(resources.ids)),len(resources.ids))
  self.assertNotIn('form',start.forms);self.assertNotIn('form',resources.forms)
 def test_search_is_local_and_existing_nojs_browse_survives(self):
  s=self.page('/find/');read=Reader(s)
  self.assertIn('It does not search your own files',s)
  self.assertIn('Filtering happens on this page.',s)
  self.assertIn('works without JavaScript',s)
  self.assertIn('id="find-results"',s)
  self.assertIn('id="find-query"',s)
  self.assertFalse(read.forms)
  self.assertEqual(len(set(read.ids)),len(read.ids))
 def test_bounded_history_refuses_unapproved_edits(self):
  for path,entry in history.change()['paths'].items():
   raw=weekly_history.before(path,(ROOT/path).read_bytes());self.assertEqual(sha256(raw).hexdigest(),entry['new_sha256'])
   self.assertEqual(sha256(history.before(path,raw)).hexdigest(),entry['old_sha256'])
   self.assertEqual(history.before(path,raw+b'!'),raw+b'!')
  self.assertEqual(history.before('index.html',b'unchanged'),b'unchanged')
 def test_published_guide_profile_calculator_and_baselines_are_unchanged(self):
  protected=history.change()['protected_hashes']
  self.assertEqual(len(protected),22)
  for path,digest in protected.items():
   with self.subTest(path=path):
    self.assertEqual(sha256(profile_datetime_history.before(path, (ROOT/path).read_bytes())).hexdigest(),digest)
 def test_exact_nine_path_scope_and_three_metadata_records(self):
  self.assertEqual(history.change()['base_commit'],'caa8916ad5738ad53fc39c7df4329a33ed435efa')
  self.assertEqual(set(history.change()['paths']),{
   '_source/start-here.html','_source/resources.html','_source/find.html',
   '_source/pages.json','_source/search-entrypoints.json','start-here/index.html',
   'resources/index.html','find/index.html','sitemap.xml'})
  self.assertEqual(set(history.change()['pages']),{'start-here','resources','find'})
  for key,pair in history.change()['pages'].items():
   self.assertEqual(pair['new']['updated'],'2026-10-19')
  finder=next(p for p in build.public_pages() if p['id']=='find')
  self.assertTrue(finder['noindex'])
  self.assertIn('<meta name="robots" content="noindex',self.page('/find/'))
 def test_latest_dates_do_not_republish_articles(self):
  current=json.loads((ROOT/'_source/pages.json').read_text())
  previous=json.loads(history.before('_source/pages.json',(ROOT/'_source/pages.json').read_text()))
  changes=[a['id'] for a,b in zip(current,previous) if a!=b]
  self.assertEqual(changes,['find'])
  for key in ['about','bio','ai-answer-review']:
   self.assertEqual(next(p for p in current if p['id']==key),next(p for p in previous if p['id']==key))
 def test_page_history_requires_exact_record_and_does_not_mutate(self):
  for pair in history.change()['pages'].values():
   original=deepcopy(pair['new'])
   self.assertEqual(history.pages([original]),[pair['old']])
   self.assertEqual(original,pair['new'])
   for key,value in [('noindex',not original.get('noindex',False)),('description','Unreviewed change'),('path','/unreviewed/')]:
    changed=deepcopy(original);changed[key]=value
    self.assertEqual(history.pages([changed]),[changed])
   changed=deepcopy(original);changed.pop('description')
   self.assertEqual(history.pages([changed]),[changed])
 def test_corrupt_snapshot_is_not_accepted_as_a_predecessor(self):
  path='_source/start-here.html';raw=(ROOT/path).read_bytes()
  for field,value in [('old_sha256','0'*64),('old_zlib_base64','not-valid-base64')]:
   corrupt=deepcopy(history.change());corrupt['paths'][path][field]=value
   with patch.object(history,'change',return_value=corrupt):
    with self.assertRaises((ValueError,zlib.error)):history.before(path,raw)
 def test_three_roles_have_direct_native_cross_links(self):
  finder=Reader(self.page('/find/'))
  self.assertIn('/start-here/#start-tasks-title',finder.links)
  self.assertIn('/resources/',finder.links)
  for route in ['/start-here/','/resources/','/find/']:
   new=self.page(route);path=str(build.output_path(route));old=history.before(path,new)
   self.assertEqual(Reader(new).scripts,Reader(old).scripts)
   self.assertLessEqual(set(Reader(old).ids),set(Reader(new).ids))
   self.assertLessEqual(set(Reader(old).links),set(Reader(new).links))
if __name__=='__main__':unittest.main()
