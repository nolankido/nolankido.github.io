"""Intentional search submission, composition safety and production preservation."""
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import build
import find_submission_history as history


def digest(records):
    return sha256(json.dumps(sorted(records),separators=(',',':')).encode()).hexdigest()


class FindSubmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=history.baseline();cls.outputs=build.build_outputs();cls.pages=build.public_pages()

    def run_events(self,*args):
        result=subprocess.run(['node',str(ROOT/'_tests/find_submission_harness.js'),*args],capture_output=True,text=True,check=True)
        return json.loads(result.stdout)

    def test_explicit_search_reaches_results_while_typing_filters_and_composition_keep_focus(self):
        results=self.run_events()
        self.assertEqual(results['typing'],{'active':'find-query','pending':1})
        self.assertEqual(results['compositionStart'],{'active':'find-query','pending':0})
        for name in ['composing','boundary']:
            self.assertEqual(results[name],{'active':'find-query','prevented':False,'pending':0,'statusUnchanged':True})
        self.assertEqual(results['compositionEnd'],{'active':'find-query','pending':0,'heading':'Search results.'})
        self.assertEqual(results['enter'],{'active':'find-results','prevented':True})
        self.assertEqual(results['button'],{'active':'find-results'})
        for name in ['find-interest','find-kind']:self.assertEqual(results[name],{'active':name})
        self.assertEqual(results['live'],{'active':'find-query','pending':0})
        self.assertEqual(results['reset'],{'active':'find-query','value':'','heading':'Browse the collections.'})
        self.assertEqual(results['leave'],{'value':'','pending':0})
        old=self.run_events('baseline')
        self.assertTrue(old['composing']['prevented'])
        self.assertEqual(old['button']['active'],'find-submit')
        self.assertEqual(old['compositionStart']['pending'],1)

    def test_all_production_outputs_articles_feeds_and_metadata_remain_exact_except_cache_version(self):
        b=self.baseline
        records=[[str(p),sha256(history.before(p,text).encode()).hexdigest()] for p,text in self.outputs.items()]
        self.assertEqual((len(records),digest(records)),(198,b['outputs_digest']))
        self.assertEqual(sha256(json.dumps(self.pages,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),b['pages_digest'])
        articles=[];feeds=[]
        for page in self.pages:
            p=build.output_path(page['path']);text=self.outputs[p]
            schema=json.loads(re.search(r'<script type="application/ld[+]json">(.*?)</script>',text)[1])
            if schema['@type']=='Article':articles.append([str(p),sha256(text.encode()).hexdigest()])
        for p,text in self.outputs.items():
            if str(p).endswith('feed.xml') or str(p)=='writing.xml':feeds.append([str(p),sha256(text.encode()).hexdigest()])
        self.assertEqual((len(articles),digest(articles)),(90,b['articles_digest']))
        self.assertEqual((len(feeds),digest(feeds)),(5,b['feeds_digest']))

    def test_all_original_sources_assets_and_downloads_allow_only_the_frozen_event_change(self):
        paths=[p for directory in ['_source','assets','downloads'] for p in (ROOT/directory).rglob('*') if p.is_file()]
        records=[[p.relative_to(ROOT).as_posix(),sha256(history.before(p.relative_to(ROOT),p.read_bytes())).hexdigest()] for p in paths]
        self.assertEqual((len(records),digest(records)),(316,self.baseline['files_digest']))
        code=(ROOT/history.SCRIPT).read_bytes()
        self.assertEqual(sha256(code).hexdigest(),self.baseline['new_script_sha256'])
        self.assertEqual(sha256(history.before(history.SCRIPT,code)).hexdigest(),self.baseline['old_script_sha256'])

    def test_adapter_does_not_hide_other_code_or_page_changes(self):
        script=(ROOT/history.SCRIPT).read_text();page=self.outputs[Path(history.PAGE)]
        for changed in [script.replace('heading.focus();','query.focus();',1),script.replace('const stops =','const unexpected = 1; const stops =',1)]:
            self.assertNotEqual(sha256(history.before(history.SCRIPT,changed).encode()).hexdigest(),self.baseline['old_script_sha256'])
        modified=page.replace('<body','<!-- unexpected --> <body',1)
        self.assertNotEqual(history.before(history.PAGE,page),history.before(history.PAGE,modified))
        self.assertEqual(history.before('about/index.html',page),page)


if __name__=='__main__':unittest.main()
