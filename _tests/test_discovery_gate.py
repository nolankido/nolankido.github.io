"""Regression checks for priority-page crawling metadata."""
import sys,unittest,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_tests'))
import check_discovery as guard
class TestDiscovery(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for p in ['robots.txt','sitemap.xml','poker/index.html']+[r.lstrip('/')+'index.html' for r in guard.ROUTES]:
   target=self.root/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
 def tearDown(self):self.tmp.cleanup()
 def change(self,path,old,new):
  p=self.root/path;v=p.read_text();self.assertIn(old,v);p.write_text(v.replace(old,new,1))
 def test_original(self):self.assertEqual(guard.check(self.root)['priority_pages'],7)
 def test_canonical(self):
  self.change('technology/task-brief/index.html','rel="canonical" href="https://nolankido.com/technology/task-brief/"','rel="canonical" href="https://example.org/"')
  with self.assertRaisesRegex(ValueError,'canonical'):guard.check(self.root)
 def test_noindex(self):
  self.change('poker/hand-rankings/index.html','<head>','<head><meta name="robots" content="noindex">')
  with self.assertRaisesRegex(ValueError,'noindex'):guard.check(self.root)
 def test_robots(self):
  p=self.root/'robots.txt';p.write_text(p.read_text()+'\nDisallow: /\n')
  with self.assertRaisesRegex(ValueError,'robots'):guard.check(self.root)
 def test_none_disallows_indexing(self):
  self.change('poker/hand-rankings/index.html','<head>','<head><meta name="robots" content="none">')
  with self.assertRaisesRegex(ValueError,'noindex'):guard.check(self.root)
 def test_commented_sitemap_is_not_active(self):
  self.change('robots.txt','Sitemap: https://nolankido.com/sitemap.xml','# Sitemap: https://nolankido.com/sitemap.xml')
  with self.assertRaisesRegex(ValueError,'Missing sitemap'):guard.check(self.root)
 def test_prefetch_is_not_a_navigation_link(self):
  self.change('poker/index.html','href="/poker/hand-rankings/"','href="/poker/removed/"')
  p=self.root/'poker/index.html';p.write_text(p.read_text().replace('<head>','<head><link rel="prefetch" href="/poker/hand-rankings/">',1))
  with self.assertRaisesRegex(ValueError,'missing link'):guard.check(self.root)
 def test_internal_link(self):
  self.change('poker/index.html','href="/poker/hand-rankings/"','href="/poker/removed/"')
  with self.assertRaisesRegex(ValueError,'missing link'):guard.check(self.root)
if __name__=='__main__':unittest.main()
