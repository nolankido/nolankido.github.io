"""Export failure injection and independently captured production integrity."""
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import beginner_history
import build
import local_fonts_history
import time_export_history as history
import find_submission_history
import time_examples_history


class TimeExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=build.public_pages();cls.outputs=build.build_outputs();cls.baseline=history.baseline()
        run=subprocess.run(['node',str(ROOT/'_tests/time_export_harness.js')],capture_output=True,text=True,check=True)
        cls.cases={v['phase']:v for v in json.loads(run.stdout)}

    def test_failed_exports_preserve_and_select_the_complete_record(self):
        for phase in ['blob','create','element','append','click']:
            case=self.cases[phase]
            self.assertIsNone(case['uncaught'],phase)
            self.assertEqual(case['value'],case['original'])
            self.assertFalse(case['hidden'])
            self.assertTrue(case['focused'])
            self.assertEqual((case['selectionStart'],case['selectionEnd']),(0,len(case['original'])))
            self.assertEqual(case['feedback'],'Download unavailable. Copy the selected comparison into your own notes.')
            self.assertEqual(case['inputs'],dict(manual='30',assisted='8',review='7',count='6',setup='60',upkeep='15'))
            self.assertEqual(case['attached'],0)
            self.assertEqual(case['revoked'],[entry['url'] for entry in case['created']])

    def test_success_exports_exact_text_without_claiming_a_file_was_saved(self):
        case=self.cases['ok']
        self.assertIsNone(case['uncaught'])
        self.assertEqual(case['created'][0]['text'],case['original'])
        self.assertEqual(case['downloads'],[{'filename':'workflow-time-comparison.txt','href':'blob:synthetic-0','hidden':True}])
        self.assertEqual(case['feedback'],'Text download requested. Keep the comparison in your own notes.')
        self.assertEqual(case['value'],case['original'])
        self.assertEqual(case['timerDelays'],[1000])
        self.assertEqual(case['revoked'],['blob:synthetic-0'])
        self.assertEqual(case['attached'],0)

    def test_cleared_or_hidden_results_do_not_receive_stale_feedback(self):
        stale=self.cases['stale']
        self.assertEqual(stale['value'],'');self.assertTrue(stale['hidden'])
        self.assertEqual(stale['feedback'],'');self.assertFalse(stale['focused'])
        self.assertEqual(stale['attached'],0);self.assertEqual(stale['revoked'],['blob:synthetic-0'])
        for phase in ['hidden','empty']:
            case=self.cases[phase]
            self.assertIsNone(case['uncaught']);self.assertEqual(case['created'],[])
            self.assertEqual(case['downloads'],[]);self.assertEqual(case['feedback'],'')

    def test_all_original_outputs_survive_only_the_calculator_cache_version(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        self.assertEqual(len(self.baseline['outputs']),198)
        changed=[]
        for path,digest in self.baseline['outputs'].items():
            raw=find_submission_history.before(path,historical_outputs[Path(path)])
            if sha256(raw.encode()).hexdigest()!=digest:changed.append(path)
            self.assertEqual(sha256(history.before(path,raw).encode()).hexdigest(),digest,path)
        self.assertEqual(changed,[history.PAGE])
        self.assertEqual(sha256(json.dumps(local_fonts_history.pages(beginner_history.pages(self.pages)),sort_keys=True,ensure_ascii=False).encode()).hexdigest(),self.baseline['pages_sha256'])
        article_count=0
        for page in beginner_history.pages(self.pages):
            path=build.output_path(page['path']);raw=local_fonts_history.before(path,historical_outputs[path])
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw)[1])
            if schema['@type']=='Article':
                article_count+=1;self.assertEqual(sha256(raw.encode()).hexdigest(),self.baseline['outputs'][str(path)])
        self.assertEqual(article_count,90)

    def test_all_original_source_assets_and_downloads_survive_only_the_reviewed_handler(self):
        self.assertEqual(len(self.baseline['files']),316)
        changed=[]
        for path,digest in self.baseline['files'].items():
            raw=find_submission_history.before(path,(ROOT/path).read_bytes())
            if sha256(raw).hexdigest()!=digest:changed.append(path)
            self.assertEqual(sha256(history.before(path,raw)).hexdigest(),digest,path)
        self.assertEqual(changed,[history.SCRIPT])
        self.assertEqual(sha256(time_examples_history.before(history.SCRIPT,(ROOT/history.SCRIPT).read_bytes())).hexdigest(),self.baseline['new_script_sha256'])

    def test_history_does_not_hide_unmarked_script_or_html_changes(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        script=(ROOT/history.SCRIPT).read_text();page=historical_outputs[Path(history.PAGE)]
        for raw in [script.replace('const keys =','const unexpected = []; const keys =',1),
                    script.replace('Download unavailable.','An unsupported claim.',1)]:
            self.assertNotEqual(sha256(history.before(history.SCRIPT,raw).encode()).hexdigest(),self.baseline['files'][history.SCRIPT])
        changed=page.replace('<body','<!-- unreviewed --><body',1)
        self.assertNotEqual(sha256(history.before(history.PAGE,changed).encode()).hexdigest(),self.baseline['outputs'][history.PAGE])
        untouched='technology/check-ai-answers/index.html'
        self.assertEqual(history.before(untouched,page),local_fonts_history.before(untouched,page))


if __name__=='__main__':unittest.main(verbosity=2)
