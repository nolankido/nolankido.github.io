"""One usable workflow with exact worksheets and independent release integrity."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import shutil
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import check_live
import practical_path
import practical_path_history as history

class PracticalPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages();cls.outputs=build.build_outputs()
        cls.entries=practical_path.records(cls.pages,ROOT)
        cls.html=cls.outputs[Path('technology/index.html')]
        cls.workbook=cls.outputs[practical_path.WORKBOOK]

    def test_all_original_generated_outputs_survive_only_declared_changes(self):
        for path,digest in history.baseline()['outputs'].items():
            self.assertEqual(sha256(history.before(path,self.outputs[Path(path)]).encode()).hexdigest(),digest,path)

    def test_all_ninety_article_pages_and_five_feeds_are_directly_identical(self):
        count=0;feeds=0
        for p in self.pages:
            path=build.output_path(p['path']);raw=self.outputs[path]
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw)[1])
            if schema['@type']=='Article':
                count+=1;self.assertEqual(sha256(raw.encode()).hexdigest(),history.baseline()['outputs'][str(path)])
        for path,digest in history.baseline()['outputs'].items():
            if path.endswith('feed.xml') or path=='writing.xml':
                feeds+=1;self.assertEqual(sha256(self.outputs[Path(path)].encode()).hexdigest(),digest)
        self.assertEqual((count,feeds),(90,5))

    def test_four_original_blank_worksheets_are_present_exactly_once(self):
        self.assertEqual(len(self.entries),4)
        for entry in self.entries:
            self.assertEqual(self.workbook.count(entry['content']),1)
            self.assertIn('https://nolankido.com'+entry['path'],self.workbook)
            self.assertIn('https://nolankido.com/downloads/'+entry['sheet'],self.workbook)
        preview=re.search(r'<div class="ai-workbook".*?<pre>(.*?)</pre>',self.html,re.S)[1]
        self.assertEqual(unescape(preview),self.workbook)
        self.assertEqual((ROOT/practical_path.WORKBOOK).read_text(),self.workbook)

    def test_visible_path_and_schema_describe_the_same_four_destinations(self):
        schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',self.html)[1])
        listing=schema['mainEntity'];self.assertEqual(listing['numberOfItems'],4)
        for i,(record,item) in enumerate(zip(self.entries,listing['itemListElement']),1):
            self.assertEqual((item['position'],item['name'],item['url']),(i,record['title'],'https://nolankido.com'+record['path']))
            self.assertIn('href="'+record['path']+'">'+record['title']+'</a>',self.html)
        self.assertNotIn('technology-before-ai',self.html)
        self.assertNotIn('technology-answer-review',self.html)

    def test_search_copy_is_specific_without_changing_publication_identity(self):
        p=next(p for p in self.pages if p['id']=='technology')
        self.assertEqual(p['seo_title'],practical_path.SEO_TITLE)
        self.assertEqual(p['description'],practical_path.DESCRIPTION)
        self.assertEqual(history.pages(self.pages),history.baseline()['pages'])
        self.assertFalse(p.get('date'))

    def test_limits_and_general_answer_checks_remain_explicit(self):
        plain=unescape(self.html)
        for phrase in ['A simpler method or a decision to stop','No AI runs here','does not certify accuracy','facts, numbers, summaries, writing, code or advice','four original blank worksheets unchanged']:
            self.assertIn(phrase,plain)
        self.assertEqual(self.entries[2]['id'],'ai-answer-review')
        self.assertIn('/technology/check-ai-summary/',self.html)
        self.assertIn('Estimates are not observed results',self.workbook)

    def test_no_runtime_collection_and_exact_public_asset_inventory(self):
        original=history.before('technology/index.html',self.html)
        self.assertEqual(re.findall(r'<script[^>]*src="([^"]+)"',self.html),re.findall(r'<script[^>]*src="([^"]+)"',original))
        self.assertNotIn('<form',self.html)
        self.assertIn('href="/technology/#practical-ai-path"',self.outputs[Path('resources/index.html')])
        targets=check_live.targets()
        for path in ['/assets/practical-ai-path.css','/downloads/practical-ai-workbook.txt']:self.assertEqual(targets[path][0],200)

    def test_missing_or_private_destinations_are_rejected_without_mutation(self):
        before=deepcopy(self.pages);practical_path.records(self.pages,ROOT);self.assertEqual(before,self.pages)
        with self.assertRaises(ValueError):practical_path.records([p for p in self.pages if p['id']!='ai-answer-review'],ROOT)
        copy=deepcopy(self.pages);next(p for p in copy if p['id']=='task-brief')['noindex']=True
        with self.assertRaises(ValueError):practical_path.records(copy,ROOT)

    def test_unmarked_article_changes_remain_detectable(self):
        path='technology/check-ai-answers/index.html'
        raw=self.outputs[Path(path)].replace('<body','<!-- unreviewed --><body',1)
        self.assertNotEqual(sha256(history.before(path,raw).encode()).hexdigest(),history.baseline()['outputs'][path])

if __name__=='__main__':unittest.main()
