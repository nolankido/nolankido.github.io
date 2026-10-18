"""Turn 11: task-first entry, file-first resources and query-first finder."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import turn11_task_navigation_history as history
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
   raw=(ROOT/path).read_bytes();self.assertEqual(sha256(raw).hexdigest(),entry['new_sha256'])
   self.assertEqual(sha256(history.before(path,raw)).hexdigest(),entry['old_sha256'])
   self.assertEqual(history.before(path,raw+b'!'),raw+b'!')
  self.assertEqual(history.before('index.html',b'unchanged'),b'unchanged')
if __name__=='__main__':unittest.main()
