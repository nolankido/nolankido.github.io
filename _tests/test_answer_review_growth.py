"""Reader guidance and exact, integrated predecessor controls for PR117."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import answer_review_growth_history as history
import turn11_task_navigation_history as task_nav_history
import profile_datetime_history
import later_release_history as later_history


class GuideGrowth(unittest.TestCase):
    def test_previous_bytes_and_idempotence(self):
        self.assertEqual(set(history.record()), {
            '_source/pages.json', '_source/technology/check-ai-answers.html',
            'technology/check-ai-answers/index.html', 'sitemap.xml', '_scripts/build.py'})
        for path, item in history.record().items():
            with self.subTest(path=path):
                raw = task_nav_history.before(path, (ROOT / path).read_bytes())
                self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
                old = history.before(path, raw)
                self.assertEqual(sha256(old).hexdigest(), item['old_sha256'])
                self.assertEqual(history.before(path, old), old)
                self.assertEqual(history.before(path, raw.decode()), old.decode())

    def test_unknown_changes_are_not_erased(self):
        for path in history.record():
            raw = (ROOT / path).read_bytes()
            for altered in (raw + b'UNREVIEWED', b'UNREVIEWED' + raw, raw[1:]):
                with self.subTest(path=path, altered_digest=sha256(altered).hexdigest()):
                    self.assertEqual(history.before(path, altered), altered)
        self.assertEqual(history.before('unrelated.bin', b'\xff\x00'), b'\xff\x00')

    def test_corrupt_edit_and_digest_fail_closed(self):
        path = '_source/technology/check-ai-answers.html'
        raw = (ROOT / path).read_bytes()
        for kind in ('offset', 'content', 'digest'):
            record = deepcopy(history.change())
            item = record['paths'][path]
            if kind == 'offset':
                item['edits'][0]['start'] = -1
            elif kind == 'content':
                item['edits'][0]['new'] += 'unreviewed'
            else:
                item['old_sha256'] = '0' * 64
            with self.subTest(kind=kind), patch.object(history, 'change', return_value=record):
                with self.assertRaises(ValueError):
                    history.before(path, raw)

    def test_metadata_adapter_requires_the_complete_approved_record(self):
        for pair in history.change()['page_pairs']:
            new = deepcopy(pair['new'])
            self.assertEqual(history.pages([new]), [pair['old']])
            self.assertEqual(new, pair['new'])
            for field, value in [('description', 'Unreviewed claim'), ('noindex', True), ('path', '/wrong/')]:
                changed = deepcopy(new)
                changed[field] = value
                self.assertEqual(history.pages([changed]), [changed])
            missing = deepcopy(new)
            missing.pop('description')
            self.assertEqual(history.pages([missing]), [missing])

    def test_only_guide_revision_changes_and_profile_dates_survive(self):
        raw = task_nav_history.before('_source/pages.json', (ROOT / '_source/pages.json').read_text())
        current = json.loads(raw)
        previous = json.loads(history.before('_source/pages.json', raw))
        self.assertEqual([p['id'] for p in previous], [p['id'] for p in current])
        changed = [(a, b) for a, b in zip(previous, current) if a != b]
        self.assertEqual(len(changed), 1)
        old, new = changed[0]
        self.assertEqual(new['id'], 'ai-answer-review')
        self.assertEqual({**old, 'updated': '2026-10-19', 'revision': new['revision']}, new)
        self.assertIn('unfaithful summary', new['revision'])
        self.assertEqual(new['date'], '2026-10-12')
        for name in ('about', 'bio'):
            self.assertEqual(next(p for p in current if p['id'] == name),
                             next(p for p in previous if p['id'] == name))
        # Read real XML rather than asserting indentation or escaped newlines.
        namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        tree = ET.fromstring(later_history.before('sitemap.xml', (ROOT / 'sitemap.xml').read_text()))
        revisions = {u.findtext('s:loc', namespaces=namespace):
                     u.findtext('s:lastmod', namespaces=namespace)
                     for u in tree.findall('s:url', namespace)}
        self.assertEqual(revisions['https://nolankido.com/technology/check-ai-answers/'], '2026-10-19')
        self.assertEqual(revisions['https://nolankido.com/about/'], '2026-10-17')
        self.assertEqual(revisions['https://nolankido.com/bio/'], '2026-10-17')

    def test_existing_six_exercises_remain_byte_identical(self):
        path = '_source/technology/check-ai-answers.html'
        current = (ROOT / path).read_text()
        previous = history.before(path, current)
        pattern = r'<details class="review-example" id="[^"]+">.*?</details>'
        old = re.findall(pattern, previous, re.S)
        new = re.findall(pattern, current, re.S)
        self.assertEqual(len(old), 6)
        self.assertEqual(new, old)

    def test_first_pass_and_status_distinction_are_explicit(self):
        raw = (ROOT / 'technology/check-ai-answers/index.html').read_text()
        for term in ('A quick first pass: claim, evidence, decision',
                     'What the three evidence statuses mean', 'Supported for a stated purpose',
                     'Worked mini-check, fictional', 'unresolved, not contradicted',
                     'Missing support is not itself a contradiction.',
                     'October 19, 2026</time>:', 'Do not turn missing evidence into a negative fact.',
                     'Send meetup questions to the organizer.',
                     'A different question: is a summary faithful?',
                     'That summary is not faithful to its supplied source'):
            self.assertIn(term, raw)
        steps = re.search(r'<ol class="review-steps review-fast-list">(.*?)</ol>', raw, re.S)
        self.assertIsNotNone(steps)
        self.assertEqual(steps[1].count('<li>'), 4)
        self.assertIn('"datePublished": "2026-10-12"', raw)
        self.assertIn('"dateModified": "2026-10-19"', raw)
        self.assertNotIn('contradicted by the source wording', raw)
        self.assertNotIn('<form', raw)

    def test_revision_note_uses_canonical_metadata_and_escapes_text(self):
        sys.path.insert(0, str(ROOT / '_scripts'))
        import build
        original_pages = build.public_pages()
        page = next(p for p in original_pages if p['id'] == 'ai-answer-review')
        current = build.build_outputs()[Path('technology/check-ai-answers/index.html')]
        self.assertIn(build.text(page['revision']), current)
        self.assertEqual(current.count(build.text(page['revision'])), 1)
        self.assertIn('<time datetime="2026-10-19">October 19, 2026</time>', current)
        changed = deepcopy(original_pages)
        guide = next(p for p in changed if p['id'] == 'ai-answer-review')
        guide['revision'] = 'Independent review marker <script>not executable</script> & context'
        guide['updated'] = '2026-10-20'
        with patch.object(build, 'public_pages', return_value=changed):
            rendered = build.build_outputs()[Path('technology/check-ai-answers/index.html')]
        self.assertIn(build.text(guide['revision']), rendered)
        self.assertNotIn(guide['revision'], rendered)
        self.assertIn('<time datetime="2026-10-20">October 20, 2026</time>', rendered)
        self.assertNotIn('October 19, 2026</time>', rendered)
        self.assertEqual(page['updated'], '2026-10-19')

    def test_bios_calculator_download_and_release_workflow_are_unchanged(self):
        for path, expected in history.change()['protected_hashes'].items():
            self.assertEqual(sha256(profile_datetime_history.before(path, (ROOT / path).read_bytes())).hexdigest(), expected, path)

    def test_all_old_links_and_ids_survive_without_new_runtime(self):
        path = 'technology/check-ai-answers/index.html'
        current = (ROOT / path).read_text()
        previous = history.before(path, current)

        # The page-scoped stylesheet uses a content-addressed cache token. This
        # release changes that stylesheet, so compare the stable asset identity
        # while the exact print-history contract checks both approved versions.
        normalize = lambda s: re.sub(
            r'(/assets/answer-review\.css)\?v=[0-9a-f]{12}', r'\1?v=<content>', s)
        normalized_current = normalize(current)
        normalized_previous = normalize(previous)

        for pattern in (r'\bid="([^"]+)"', r'\bhref="([^"]+)"'):
            self.assertLessEqual(set(re.findall(pattern, normalized_previous)),
                                 set(re.findall(pattern, normalized_current)))
        for pattern in (r'<script\b[^>]*>.*?</script>', r'<link\b[^>]*rel="stylesheet"[^>]*>'):
            # JSON-LD is metadata, not executable runtime.
            strip = lambda s: re.sub(r'<script type="application/ld\+json">.*?</script>', '', s)
            self.assertEqual(re.findall(pattern, strip(normalized_current), re.S),
                             re.findall(pattern, strip(normalized_previous), re.S))


if __name__ == '__main__':
    unittest.main()
