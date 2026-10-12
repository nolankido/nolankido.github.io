"""Summary review content, truthful publication type, and independent preservation."""
from pathlib import Path
from html import unescape
from copy import deepcopy
from hashlib import sha256
from xml.etree import ElementTree as ET
import json, re, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build,check_live,site_find,practical_discovery
ROUTE='/technology/check-ai-summary/'
EXCLUDE_SOURCES={'_source/pages.json','_source/technology/home.html','_source/resources.html','_source/technology/check-ai-summary.html'}
EXCLUDE_BODIES={'find/index.html','notes/index.html','resources/index.html','technology/index.html','technology/check-ai-summary/index.html'}
def digest(v):return sha256(v).hexdigest()
def signature(v):return digest(json.dumps(v,separators=(',',':')).encode())
def feed_records(raw):
 return {i.findtext('link'):[(c.tag,sorted(c.attrib.items()),c.text) for c in i] for i in ET.fromstring(raw).findall('./channel/item')}
class SummaryReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pages=build.public_pages();cls.outputs=build.build_outputs();cls.html=cls.outputs[build.output_path(ROUTE)]
  cls.baseline=json.loads((ROOT/'_tests/summary-review-baseline.json').read_text())
 def test_every_original_article_identity_and_private_boundary_stay_intact(self):
  records=[(p.relative_to(ROOT).as_posix(),digest(p.read_bytes())) for p in sorted((ROOT/'_source').rglob('*')) if p.is_file() and p.relative_to(ROOT).as_posix() not in EXCLUDE_SOURCES]
  records.sort(key=lambda x:x[0]);self.assertEqual(len(records),self.baseline['source_count']);self.assertEqual(signature(records),self.baseline['source_digest'])
  pages=json.loads((ROOT/'_source/pages.json').read_text());pages=[p for p in pages if p['id']!='ai-summary-review']
  self.assertEqual(digest(json.dumps(pages,sort_keys=True).encode()),self.baseline['manifest_digest'])
 def test_164_original_page_bodies_are_identical(self):
  records=[]
  for p,raw in sorted(self.outputs.items()):
   if p.suffix=='.html' and p.as_posix() not in EXCLUDE_BODIES:
    records.append((p.as_posix(),digest(re.search(rb'<body\b[^>]*>(.*?)</body>',raw.encode(),re.S)[1])))
  records.sort(key=lambda x:x[0]);self.assertEqual(len(records),self.baseline['body_count']);self.assertEqual(signature(records),self.baseline['body_digest'])
 def test_every_historical_feed_item_is_preserved_exactly(self):
  for path,expected in self.baseline['feeds'].items():
   now=feed_records(self.outputs[Path(path)]);now.pop('https://nolankido.com'+ROUTE,None)
   self.assertEqual(len(now),expected['count'],path)
   self.assertEqual(digest(json.dumps(now,sort_keys=True).encode()),expected['digest'],path)
 def test_new_publication_is_once_in_each_relevant_feed(self):
  for path in ['technology/feed.xml','writing.xml']:
   items=ET.fromstring(self.outputs[Path(path)]).findall('./channel/item')
   new=[i for i in items if i.findtext('link')=='https://nolankido.com'+ROUTE]
   self.assertEqual(len(new),1);self.assertIn('12 Oct 2026',new[0].findtext('pubDate'))
  for path in ['feed.xml','poker/feed.xml','living-well/feed.xml']:
   self.assertNotIn('https://nolankido.com'+ROUTE,feed_records(self.outputs[Path(path)]))
 def test_worked_guide_is_not_misrepresented_as_a_real_case(self):
  self.assertIn('Worked guide',self.html);self.assertNotIn('Recorded case study',self.html)
  schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',self.html)[1])
  self.assertEqual(schema['@type'],'Article');self.assertEqual(schema['datePublished'],'2026-10-12')
  self.assertEqual(schema['author']['@id'],'https://nolankido.com/about/#nolan-kido')
  self.assertNotIn('aggregateRating',schema);self.assertNotIn('reviewRating',schema)
  page=next(p for p in self.pages if p['path']==ROUTE)
  bad=deepcopy(page);bad['evidence_article']=True
  with self.assertRaises(ValueError):practical_discovery.articles([bad])
 def test_source_links_cover_all_seven_passages_and_six_distinct_problems(self):
  for n in range(1,8):
   self.assertEqual(self.html.count('id="source-'+str(n)+'"'),1);self.assertIn('href="#source-'+str(n)+'"',self.html)
  self.assertEqual(len(re.findall(r'class="summary-finding" id="finding-',self.html)),6)
  for text in ['booking confirmation is still pending','if transport is arranged','attendance will not depend on payment','They have not agreed to send it','No sign-up deadline has been decided','do not add them to the public invitation']:
   self.assertIn(text,unescape(self.html))
 def test_repaired_example_preserves_dependencies_and_has_no_invented_deadline(self):
  repair=unescape(re.search(r'<blockquote class="summary-repair">(.*?)</blockquote>',self.html,re.S)[1])
  for text in ['subject to room confirmation','transport is unassigned','not agreed','not conditional on payment','not to send it','No sign-up deadline is set','out of the public invitation']:
   self.assertIn(text,repair)
  self.assertNotIn('10 November',repair)
  for text in ['not a captured response','Fictional teaching example','Source fidelity, external truth, and permission']:
   self.assertIn(text,self.html)
 def test_exact_download_preview_and_live_coverage(self):
  sheet=(ROOT/'downloads/ai-summary-review.txt').read_text()
  self.assertIn('<pre>'+sheet+'</pre>',unescape(self.html))
  targets=check_live.targets()
  for path in ['assets/summary-review.css','downloads/ai-summary-review.txt']:
   self.assertEqual(targets['/'+path],(200,(ROOT/path).read_bytes()))
  self.assertEqual(targets[ROUTE],(200,self.html.encode()))
 def test_native_discovery_and_no_new_runtime_collection(self):
  for p in ['technology/index.html','resources/index.html','notes/index.html']:
   self.assertIn('href="'+ROUTE+'"',self.outputs[Path(p)])
  entry=next(e for e in site_find.entries(ROOT,self.pages) if e['path']==ROUTE)
  self.assertEqual(entry['kind'],'guide');self.assertEqual(entry['date'],'2026-10-12')
  self.assertIn('https://nolankido.com'+ROUTE,self.outputs[Path('sitemap.xml')])
  self.assertNotIn('<form',self.html);self.assertNotIn('<textarea',self.html)
  self.assertEqual(re.findall(r'<script[^>]+src="([^"]+)"',self.html),['https://cloud.umami.is/script.js'])
  for p in self.pages:
   self.assertEqual('/assets/summary-review.css?' in self.outputs[build.output_path(p['path'])],p['path']==ROUTE)
if __name__=='__main__':unittest.main(verbosity=2)
