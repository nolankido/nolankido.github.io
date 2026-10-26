"""Independent examples, source boundaries, publication, and old-content integrity."""
from fractions import Fraction
from hashlib import sha256
from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import build
import check_live
import site_find
import answer_review_history as history


class AnswerReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.html = cls.outputs[build.output_path(history.ROUTE)]
        cls.baseline = json.loads((ROOT / '_tests/answer-review-baseline.json').read_text())

    def test_original_files_and_identity_are_preserved_after_declared_insertions(self):
        for path, expected in self.baseline['files'].items():
            actual = history.before(path, (ROOT / path).read_bytes())
            self.assertEqual(sha256(actual).hexdigest(), expected, path)
        self.assertEqual(json.loads(history.before('_source/pages.json', (ROOT / '_source/pages.json').read_text())), self.baseline['manifest'])

    def test_all_original_page_bodies_are_preserved(self):
        for path, expected in self.baseline['bodies'].items():
            restored = history.before(path, self.outputs[Path(path)])
            body = re.search(r'<body\b[^>]*>(.*?)</body>', restored, re.S)[1]
            self.assertEqual(sha256(body.encode()).hexdigest(), expected, path)

    def test_predecessor_view_does_not_hide_an_unmarked_article_change(self):
        path = 'notes/trustworthy-tools/index.html'
        changed = self.outputs[Path(path)].replace('A claim small enough to check', 'An unreviewed new claim', 1)
        restored = history.before(path, changed)
        body = re.search(r'<body\b[^>]*>(.*?)</body>', restored, re.S)[1]
        self.assertNotEqual(sha256(body.encode()).hexdigest(), self.baseline['bodies'][path])

    def test_historical_feed_entries_keep_every_field_and_each_feed_scope(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        url = 'https://nolankido.com' + history.ROUTE
        for path, original in self.baseline['feeds'].items():
            items = ET.fromstring(historical_outputs[Path(path)]).findall('./channel/item')
            now = {i.findtext('guid'): ET.tostring(i, encoding='unicode') for i in items}
            self.assertEqual({k: v for k, v in now.items() if k != url}, original, path)
            self.assertEqual(sum(i.findtext('guid') == url for i in items), int(path in {'technology/feed.xml', 'writing.xml'}))

    def test_numbers_example_counts_every_cost_using_independent_exact_arithmetic(self):
        usual = Fraction(20) * 12
        costs = [Fraction(30), Fraction(6) * 12, Fraction(7) * 12, Fraction(18)]
        ai = sum(costs)
        self.assertEqual((usual, ai, usual - ai), (240, 204, 36))
        self.assertEqual(12 * (20 - 6), 168)
        for number in ['240', '204', '36']:
            self.assertIn('<strong>' + number + ' minutes</strong>', self.html)
        self.assertIn('these fictional inputs do not establish actual savings', self.html)

    def test_code_example_has_a_real_discriminating_counterexample(self):
        code = unescape(re.search(r'<pre><code>(function discountedPrice.*?)</code></pre>', self.html, re.S)[1])
        result = subprocess.run(['node', '-e', code + ';console.log(JSON.stringify([discountedPrice(100,20),discountedPrice(50,20)]))'], capture_output=True, text=True, check=True)
        observed = json.loads(result.stdout)
        expected = [Fraction(price) * (1 - Fraction(20, 100)) for price in [100, 50]]
        self.assertEqual(observed[0], expected[0])
        self.assertNotEqual(observed[1], expected[1])
        self.assertEqual((observed[1], expected[1]), (30, 40))
        self.assertIn('deliberately wrong JavaScript', self.html)
        self.assertIn('not production pricing code', self.html)

    def test_source_and_example_limits_are_explicit(self):
        for phrase in ['not captured model output', 'unsupported number', 'does not provide the claimed percentage or agreement rule',
                       'section 2.2', 'printed page 6; PDF page 9', 'does not validate this site', 'AI assistance',
                       'A faithful summary', 'permission to act']:
            self.assertIn(phrase, unescape(self.html) + (ROOT / 'downloads/ai-answer-review.txt').read_text())
        self.assertIn('https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf#page=9', self.html)
        self.assertEqual(len(re.findall(r'class="review-example" id="', self.html)), 6)

    def test_native_discovery_metadata_and_sharing_match_the_published_guide(self):
        for path in ['index.html', 'technology/index.html', 'resources/index.html', 'notes/index.html', 'find/index.html']:
            self.assertIn('href="' + history.ROUTE + '"', self.outputs[Path(path)], path)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.html)[1])
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['datePublished'], '2026-10-12')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertNotIn('image', schema)
        self.assertNotIn('aggregateRating', schema)
        self.assertIn('https://nolankido.com' + history.ROUTE, self.outputs[Path('sitemap.xml')])
        self.assertEqual(next(e for e in site_find.entries(ROOT, self.pages) if e['path'] == history.ROUTE)['kind'], 'guide')
        self.assertIn('/assets/social/check-ai-answers.png', self.html)

    def test_complete_print_copy_needs_no_disclosure_state_or_runtime(self):
        css = (ROOT / 'assets/answer-review.css').read_text()
        visible = unescape(self.html)
        self.assertIn('The print version includes all six worked examples and the complete blank record', visible)
        self.assertIn('class="review-download-action"', self.html)
        self.assertIn('.review-example::details-content', css)
        self.assertIn('.review-sheet::details-content', css)
        self.assertIn('.review-download-action { display: none !important; }', css)
        self.assertIn('.review-sheet pre { break-inside: auto; overflow: visible;', css)
        self.assertEqual(len(re.findall(r'<details class="review-example" id="', self.html)), 6)
        self.assertEqual(len(re.findall(r'<details class="review-example"[^>]*\sopen(?:\s|=|>)', self.html)), 0)
        self.assertNotRegex(self.html, r'<details class="review-sheet"[^>]*\sopen(?:\s|=|>)')

    def test_exact_portable_record_and_no_new_runtime_collection(self):
        sheet = (ROOT / 'downloads/ai-answer-review.txt').read_text()
        self.assertIn('<pre>' + sheet + '</pre>', unescape(self.html))
        self.assertNotIn('<form', self.html)
        self.assertNotIn('<textarea', self.html)
        scripts = re.findall(r'<script[^>]+src="([^"]+)"', self.html)
        self.assertEqual(scripts, ['/assets/page-sharing.js?v=' + sha256((ROOT / 'assets/page-sharing.js').read_bytes()).hexdigest()[:12], 'https://cloud.umami.is/script.js'])
        for p in self.pages:
            self.assertEqual('/assets/answer-review.css?' in self.outputs[build.output_path(p['path'])], p['path'] == history.ROUTE)
        for path in [history.ROUTE, '/assets/answer-review.css', '/downloads/ai-answer-review.txt', '/assets/social/check-ai-answers.png']:
            self.assertEqual(check_live.targets()[path][0], 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
