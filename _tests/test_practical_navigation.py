"""Native checkpoints with an independently verified prior production tree."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import build
import local_fonts_history
import check_live
import practical_navigation
import practical_navigation_history as history
import time_export_history
import find_submission_history

STAGES = (
    ('ai-task-choice', '/technology/should-i-use-ai/', 'Decide'),
    ('task-brief', '/technology/task-brief/', 'Brief'),
    ('ai-answer-review', '/technology/check-ai-answers/', 'Check'),
    ('ai-time-savings', '/technology/ai-time-savings/', 'Measure'),
)


class NavigationParser(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.current=[]; self.links=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if attrs.get('aria-current') == 'page': self.current.append((tag,attrs))
        if tag == 'a': self.links.append(attrs.get('href'))


class PracticalNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages(); cls.outputs=build.build_outputs()
        cls.baseline=history.baseline()

    def test_every_prior_output_survives_only_the_exact_reviewed_additions(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        self.assertEqual(len(self.baseline['outputs']),198)
        self.assertEqual(set(self.baseline['additions']),history.PATHS)
        self.assertEqual(local_fonts_history.pages(beginner_history.pages(self.pages)),self.baseline['pages'])
        self.assertEqual(set(map(str,historical_outputs)),set(self.baseline['outputs']))
        changed=[]
        for path,digest in self.baseline['outputs'].items():
            raw=find_submission_history.before(path,historical_outputs[Path(path)])
            if sha256(raw.encode()).hexdigest()!=digest: changed.append(path)
            self.assertEqual(sha256(history.before(path,raw).encode()).hexdigest(),digest,path)
        self.assertCountEqual(changed,history.PATHS)

    def test_original_sources_assets_and_downloads_survive_only_reviewed_export_recovery(self):
        self.assertEqual(len(self.baseline['files']),315)
        for path,digest in self.baseline['files'].items():
            original=time_export_history.before(path,(ROOT/path).read_bytes())
            self.assertEqual(sha256(original).hexdigest(),digest,path)
        self.assertEqual(sha256((ROOT/practical_navigation.CSS).read_bytes()).hexdigest(),self.baseline['navigation_css_sha256'])

    def test_original_article_metadata_content_and_five_feeds_survive(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        articles=[]; identical=[]; feeds=[]
        for page in beginner_history.pages(self.pages):
            path=build.output_path(page['path']); raw=local_fonts_history.before(path,historical_outputs[path])
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw)[1])
            if schema['@type']!='Article': continue
            articles.append(str(path))
            if sha256(raw.encode()).hexdigest()==self.baseline['outputs'][str(path)]: identical.append(str(path))
            restored=history.before(path,raw)
            self.assertEqual(sha256(restored.encode()).hexdigest(),self.baseline['outputs'][str(path)])
            self.assertEqual(schema,json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',restored)[1]))
        for path,digest in self.baseline['outputs'].items():
            if path.endswith('feed.xml') or path=='writing.xml':
                feeds.append(path);self.assertEqual(sha256(historical_outputs[Path(path)].encode()).hexdigest(),digest)
        self.assertEqual((len(articles),len(identical),len(feeds)),(90,88,5))

    def test_exact_stage_order_and_current_page_are_native_without_a_self_link(self):
        for key,path,label in STAGES:
            page=next(p for p in self.pages if p['id']==key)
            top,after=practical_navigation.blocks(page,self.pages,ROOT)
            listing=re.search(r'<ol>(.*?)</ol>',top,re.S)[1]
            parser=NavigationParser(listing)
            self.assertEqual(len(parser.current),1)
            self.assertEqual(parser.current[0][0],'span')
            self.assertNotIn(path,parser.links)
            self.assertEqual(parser.links,[route for _,route,_ in STAGES if route!=path])
            self.assertEqual(re.findall(r'</span> (Decide|Brief|Check|Measure)',listing),[name for _,_,name in STAGES])
            self.assertIn('This page',top)
            self.assertIn('Save results in your own notes before moving between pages.',top)
            self.assertIn('A simpler method or a decision to stop is a valid end.',after)

    def test_onward_choices_match_the_existing_guides_and_allow_stopping(self):
        destinations=['/technology/task-brief/','/technology/check-ai-answers/','/technology/ai-time-savings/','/technology/#practical-ai-path']
        for (key,_,_),destination in zip(STAGES,destinations):
            page=next(p for p in self.pages if p['id']==key)
            top,after=practical_navigation.blocks(page,self.pages,ROOT)
            self.assertEqual(NavigationParser(after).links,[destination])
            self.assertIn('href="/downloads/practical-ai-workbook.txt" download',top)
        self.assertIn('Keep, adjust, stop or gather more observations.',after)

    def test_page_scope_and_runtime_inventory_are_unchanged(self):
        ids={key for key,_,_ in STAGES}
        for page in self.pages:
            path=build.output_path(page['path']);raw=local_fonts_history.before(path,self.outputs[path])
            self.assertEqual('id="ai-workflow-navigation"' in raw,page['id'] in ids)
            self.assertEqual('/assets/practical-ai-navigation.css?' in raw,page['id'] in ids)
            restored=history.before(path,raw)
            versioned=time_export_history.before(path,raw)
            self.assertEqual(re.findall(r'<script[^>]*src="([^"]+)"',versioned),re.findall(r'<script[^>]*src="([^"]+)"',restored))
        self.assertEqual(len(check_live.targets()),460)
        self.assertEqual(check_live.targets()['/assets/practical-ai-navigation.css'],(200,(ROOT/practical_navigation.CSS).read_bytes()))
        css=(ROOT/practical_navigation.CSS).read_text()
        self.assertIn('@media print',css)

    def test_tampered_article_and_tampered_marked_navigation_remain_detectable(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        path='technology/check-ai-answers/index.html';raw=historical_outputs[Path(path)]
        mutations=[raw.replace('Use the stages you need.','An unreviewed claim.',1),
                   raw.replace('<body','<!-- unreviewed article change --><body',1),
                   raw.replace('See the whole path','An unreviewed destination label',1),
                   raw.replace('practical-ai-navigation.css?v=','practical-ai-navigation.css?v=0',1)]
        for changed in mutations:
            self.assertNotEqual(raw,changed)
            self.assertNotEqual(sha256(history.before(path,changed).encode()).hexdigest(),self.baseline['outputs'][path])
        unrelated='about/index.html'
        changed=historical_outputs[Path(unrelated)]+self.baseline['additions'][path]['blocks'][0]
        self.assertEqual(history.before(unrelated,changed),local_fonts_history.before(unrelated,changed))

    def test_repeated_navigation_and_missing_destinations_fail_without_mutation(self):
        page=next(p for p in self.pages if p['id']=='task-brief')
        original=deepcopy(self.pages)
        once=practical_navigation.decorate(page,'<p>Original content.</p>',self.pages,ROOT)
        self.assertEqual(self.pages,original)
        with self.assertRaises(ValueError): practical_navigation.decorate(page,once,self.pages,ROOT)
        with self.assertRaises(ValueError): practical_navigation.blocks(page,[p for p in self.pages if p['id']!='ai-answer-review'],ROOT)
        private=deepcopy(self.pages);next(p for p in private if p['id']=='ai-answer-review')['noindex']=True
        with self.assertRaises(ValueError): practical_navigation.blocks(page,private,ROOT)


if __name__=='__main__': unittest.main(verbosity=2)
