"""Verify Turn 04 public-source editorial provenance and access."""
import json
from pathlib import Path
import sys
import unittest
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_scripts'))
import turn04_public_source_history as history
import turn11_task_navigation_history as task_nav_history
import build
from test_site import Page

class PublicSourceCaseTests(unittest.TestCase):
    def test_case_is_traceable_and_has_no_fabricated_personal_result(self):
        body=(ROOT/'_source/technology/ai-weekly-reset.html').read_text()
        self.assertEqual(body.count('id="notes-to-plan-case"'),1)
        for slug in ['weekly-reset','decide-what-matters','what-to-decide-yourself']:
            self.assertIn('/living-well/'+slug+'/', body)
            self.assertIn(slug, (ROOT/'_reports/website-growth/turn-04-public-source-plan.md').read_text())
        self.assertIn('not a personal weekly schedule', body)
        self.assertIn('No calendar was accessed',body)
        self.assertIn('a separate human reviewer has not signed off',body)
        self.assertIn('not a reconstructed output from a separate AI service', body)
        self.assertNotIn('<script',body)
        for anchor in ['notes-case-sources','notes-case-revisions','notes-case-result','notes-case-limits']:
            self.assertEqual(body.count('id="'+anchor+'"'),1)
        outputs=build.build_outputs()
        plan=Page(outputs[Path('technology/ai-weekly-reset/index.html')])
        self.assertIn('notes-to-plan-case', {a.get('id') for _,a in plan.elements})
        hub=Page(outputs[Path('technology/index.html')])
        self.assertIn('/technology/ai-weekly-reset/', {a.get('href') for _,a in hub.elements})
        self.assertIn('notes-to-plan-case', {a.get('id') for _,a in hub.elements})

    def test_reversal_rejects_mutation_and_reconstructs_frozen_parent(self):
        record=history.change()
        self.assertEqual(record['base_commit'],'97194dd226297901c59960313d3a78c1e251eb30')
        self.assertEqual(set(record['paths']),{'_source/technology/home.html','technology/index.html','find/index.html'})
        for path,item in record['paths'].items():
            with self.subTest(path=path):
                original=task_nav_history.before(path,(ROOT/path).read_bytes())
                self.assertEqual(sha256(original).hexdigest(),item['new_sha256'])
                previous=history.before(path,original)
                self.assertEqual(sha256(previous).hexdigest(),item['old_sha256'])
                self.assertEqual(history.before(path,previous),previous)
                self.assertEqual(history.before(path,original+b'other edit'),original+b'other edit')
                self.assertEqual(history.before(path,b'extra'+original),b'extra'+original)

if __name__=='__main__': unittest.main()
