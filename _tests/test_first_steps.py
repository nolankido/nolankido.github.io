"""Useful first actions without invented credentials or a new application surface."""
from html import unescape
from pathlib import Path
import hashlib
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import check_live
STARTS={
 'technology':'/technology/task-brief/',
 'living-well':'/living-well/worksheets/#weekly-reset',
 'poker':'/poker/study-calculators/',
 'creative':'/creative/#creative-brief',
}
class FirstStepTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.outputs=build.build_outputs()
  cls.home=cls.outputs[Path('index.html')]
  cls.creative=cls.outputs[Path('creative/index.html')]

 def test_four_ordered_cards_have_separate_native_links(self):
  cards=re.findall(r'<article class="destination destination-([a-z-]+)"[^>]*>(.*?)</article>',self.home,re.S)
  self.assertEqual([k for k,_ in cards],list(STARTS))
  for key,body in cards:
   links=re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',body,re.S)
   self.assertEqual([url for url,_ in links],['/'+key+'/',STARTS[key]])
   self.assertTrue(all('<a ' not in text for _,text in links))
   self.assertIn('id="'+key+'-destination-title"',body)
   self.assertIn('A useful first step',body)
   self.assertNotIn('onclick',body)

 def test_person_and_selected_writing_still_come_first(self):
  self.assertLess(self.home.index('id="home-title"'),self.home.index('id="selected-reading-title"'))
  self.assertLess(self.home.index('id="selected-reading-title"'),self.home.index('id="destinations-title"'))
  self.assertEqual(self.home.count('class="identity-reading"'),3)
  self.assertIn('No AI runs here.',self.home)
  self.assertIn('For review away from play',self.home)

 def test_creative_preview_is_exactly_the_download(self):
  match=re.search(r'<details class="creative-template">.*?<pre>(.*?)</pre>',self.creative,re.S)
  self.assertIsNotNone(match)
  self.assertEqual(unescape(match.group(1)),(ROOT/'downloads/creative-brief.txt').read_text())
  self.assertIn('href="/downloads/creative-brief.txt" download',self.creative)
  self.assertNotIn('<form',self.creative)
  self.assertNotIn('<textarea',self.creative)
  for phrase in ['Complete your copy privately','MATERIAL AND PERMISSION','OPTIONAL AI ASSISTANCE','READY ENOUGH TO SHARE']:
   self.assertIn(phrase,unescape(match.group(1)))

 def test_existing_creative_reading_and_anchors_remain(self):
  for anchor in ['creative-intro-title','creative-reading','creative-practice','creative-brief']:
   self.assertEqual(self.creative.count('id="'+anchor+'"'),1)
  for path in ['/notes/generous-explanations/','/notes/finishing-is-a-decision/',
               '/living-well/rough-idea-to-small-creation/','/living-well/preserve-family-story/',
               '/poker/hand-to-vlog/','/resources/#resources-creative']:
   self.assertIn('href="'+path+'"',self.creative)
  self.assertIn('a guide, not a published vlog episode',self.creative)

 def test_discovery_does_not_republish_articles(self):
  self.assertIn('href="/creative/#creative-brief"',self.outputs[Path('resources/index.html')])
  self.assertIn('with a free creative brief',self.outputs[Path('find/index.html')])
  for path in ['feed.xml','writing.xml','living-well/feed.xml','poker/feed.xml']:
   self.assertNotIn('creative-brief',self.outputs[Path(path)])

 def test_css_is_scoped_cached_and_checked_live(self):
  sha=hashlib.sha256((ROOT/'assets/first-steps.css').read_bytes()).hexdigest()[:12]
  for page in build.public_pages():
   html=self.outputs[build.output_path(page['path'])]
   self.assertEqual('/assets/first-steps.css?v='+sha in html,page['id'] in {'home','creative'})
  targets=check_live.targets()
  for path in ['assets/first-steps.css','downloads/creative-brief.txt']:
   self.assertEqual(targets['/'+path],(200,(ROOT/path).read_bytes()))

 def test_no_new_scripts_and_existing_design_tokens(self):
  for html in [self.home,self.creative]:
   scripts=re.findall(r'<script[^>]*src="([^"]+)"',html)
   self.assertEqual(scripts,['https://cloud.umami.is/script.js'])
  css=(ROOT/'assets/first-steps.css').read_text()
  self.assertIn(':root { scroll-behavior: auto; }',css)
  declared=set(re.findall(r'(--[a-z-]+)\s*:',(ROOT/'styles.css').read_text()))
  self.assertLessEqual(set(re.findall(r'var\((--[a-z-]+)\)',css)),declared)

if __name__=='__main__':unittest.main()
