"""Source-supported entry, offline worksheet, and reciprocal case links for Turn 07."""

from hashlib import sha256
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live


class Turn07AnswerEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.html = cls.outputs[Path('technology/check-ai-answers/index.html')]
        cls.manifest = next(p for p in build.public_pages() if p['id'] == 'ai-answer-review')
        cls.checklist = (ROOT / 'downloads/ai-answer-quick-check.txt').read_text(encoding='utf-8')

    def test_direct_answer_and_offline_checklist_before_long_examples(self):
        html = self.html
        self.assertIn('How do you check an AI-generated answer before using it?', html)
        self.assertIn('supported</strong>', html)
        self.assertIn('contradicted</strong>', html)
        self.assertIn('unresolved</strong>', html)
        self.assertIn('href="/downloads/ai-answer-quick-check.txt" download', html)
        self.assertLess(html.index('id="review-start"'), html.index('id="review-fast-method"'))
        self.assertLess(html.index('id="review-fast-method"'), html.index('id="review-claim-map"'))
        self.assertLess(html.index('id="review-claim-map"'), html.index('class="review-picker"'))
        self.assertLess(html.index('class="review-picker"'), html.index('id="review-recorded-examples"'))

    def test_map_has_six_distinct_independently_checkable_claim_types(self):
        section = self.html.split('<table class="review-evidence-map">', 1)[1].split('</table>', 1)[0]
        self.assertEqual(len(re.findall(r'<th scope="row">', section)), 6)
        for anchor in ('review-research', 'review-numbers', 'review-summary',
                       'review-writing', 'review-code', 'review-advice'):
            self.assertIn('href="#' + anchor + '"', section)
            self.assertIn('id="' + anchor + '"', self.html)
        for result in ('99% reliable', '36 minutes', 'weather permitting',
                       'Ask for two times', 'correct output 40, wrong output 30',
                       'verify offer terms'):
            self.assertIn(result.lower(), section.lower())
        self.assertIn('fictional teaching material', self.html)
        self.assertIn('Still unknown', section)
        self.assertEqual(self.html.count('class="review-picker"'), 1)

    def test_one_page_worksheet_is_private_reusable_and_served(self):
        self.assertLessEqual(len(self.checklist.splitlines()), 52)
        self.assertLessEqual(max(map(len, self.checklist.splitlines())), 74)
        for phrase in ('NAME THE ACTION', 'CHOOSE INDEPENDENT EVIDENCE',
                       'SUPPORTED:', 'CONTRADICTED:', 'UNRESOLVED:',
                       'Exact claim:', 'Remaining unknown:', 'responsible person:',
                       'This file collects or sends nothing'):
            self.assertIn(phrase, self.checklist)
        self.assertEqual(check_live.targets()['/downloads/ai-answer-quick-check.txt'],
                         (200, self.checklist.encode('utf-8')))
        self.assertNotIn('<form', self.html)
        self.assertNotIn('<textarea', self.html)
        css = (ROOT / 'assets/answer-review.css').read_text(encoding='utf-8')
        self.assertIn('.review-evidence-map { min-width: 49rem; }', css)
        self.assertIn('.review-evidence-map { min-width: 0; }', css)
        self.assertIn('.review-quick-action { display: none !important; }', css)
        self.assertIn('aria-describedby="answer-check-map-table-hint" tabindex="0"', self.html)

    def test_archived_example_is_sourced_and_not_presented_as_an_live_run(self):
        html = self.html
        self.assertIn('25 minute wait', html)
        self.assertIn('extended wait you experienced', html)
        self.assertIn('Proposed human edit, not a new model output', html)
        self.assertIn('does not establish that a person approved it', html)
        self.assertIn('1c5e0487c331d5202410c9f342557d9355951c3a/examples/evaluation/live-smoke-2026-10-13.json', html)
        self.assertIn('not a customer conversation or a new evaluation', html)

    def test_case_backlinks_and_metadata_dates_are_consistent(self):
        for path in ('technology/ai-book-continuity-checker/index.html',
                     'technology/checking-ai-website-changes/index.html'):
            self.assertIn('href="/technology/check-ai-answers/#review-claim-map"',
                          self.outputs[Path(path)], path)
        self.assertEqual(self.manifest['date'], '2026-10-12')
        self.assertGreaterEqual(self.manifest['updated'], '2026-11-18')
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                      self.html)[1])
        self.assertEqual(schema['datePublished'], '2026-10-12')
        self.assertEqual(schema['dateModified'], self.manifest['updated'])
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        scripts = re.findall(r'<script[^>]+src="([^"]+)"', self.html)
        self.assertEqual(scripts, ['/assets/page-sharing.js?v=' + sha256((ROOT / 'assets/page-sharing.js').read_bytes()).hexdigest()[:12],
                                   'https://cloud.umami.is/script.js'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
