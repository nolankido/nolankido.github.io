"""Bounded public-page handoff, not evidence of human task completion."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import feedback_context_history as history
import later_release_history as later_history
import study_inquiry_history as inquiry_history
import task_brief_error_history

EXPECTED = {
    'task-brief': '/technology/task-brief/',
    'ai-answer-review': '/technology/check-ai-answers/',
    'ai-time-savings': '/technology/ai-time-savings/',
    'living-well-weekly-reset': '/living-well/weekly-reset/',
    'poker-first-live-tournament': '/poker/first-live-tournament/',
    'poker-hand-rankings': '/poker/hand-rankings/',
}


class Elements(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


def digest(value):
    return sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


class FeedbackContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.contact = cls.outputs[Path('contact/index.html')]
        cls.js = (ROOT / 'assets/contact.js').read_text()

    def test_exactly_six_named_correction_links_keep_all_other_page_bytes(self):
        self.assertEqual(set(build.FEEDBACK_PAGES), set(EXPECTED))
        for page_id, route in EXPECTED.items():
            path = build.output_path(route)
            new = task_brief_error_history.before(path, self.outputs[path])
            old = history.before(path, new)
            label = build.FEEDBACK_PAGES[page_id]
            start = '<a href="/contact/">' + label + '</a>'
            finish = '<a href="/contact/#report-' + page_id + '">' + label + '</a>'
            with self.subTest(page=page_id):
                self.assertEqual(old.count(start), 1)
                self.assertEqual(new.count(finish), 1)
                self.assertEqual(new.replace(finish, start), old)
                self.assertIn('href="/contact/"', new)

    def test_contact_markers_match_actual_manifest_and_limit_input(self):
        nodes = [(tag, attrs) for tag, attrs in Elements(self.contact).items
                 if attrs.get('id', '').startswith('report-')]
        self.assertEqual(len(nodes), 6)
        by_id = {p['id']: p for p in self.pages}
        for tag, attrs in nodes:
            key = attrs['id'].removeprefix('report-')
            self.assertEqual(tag, 'span')
            self.assertIn('hidden', attrs)
            self.assertEqual(attrs['data-feedback-path'], EXPECTED[key])
            self.assertEqual(attrs['data-feedback-title'], by_id[key]['title'])
            self.assertLessEqual(len('https://nolankido.com' + EXPECTED[key]), 180)

    def test_markers_escape_authored_text_without_mutating_catalog(self):
        pages = deepcopy(self.pages)
        next(p for p in pages if p['id'] == 'task-brief')['title'] = '"><script>bad</script>&'
        before = deepcopy(pages)
        html = build.feedback_markers(pages)
        self.assertNotIn('<script>', html)
        node = next(a for _, a in Elements(html).items if a.get('id') == 'report-task-brief')
        self.assertEqual(node['data-feedback-title'], '"><script>bad</script>&')
        self.assertEqual(pages, before)

    def test_missing_duplicate_private_and_external_marker_destinations_fail(self):
        wanted = next(p for p in self.pages if p['id'] == 'task-brief')
        variants = [[p for p in self.pages if p['id'] != 'task-brief'],
                    self.pages + [wanted]]
        for key, value in [('noindex', True), ('path', 'https://example.invalid/')]:
            records = deepcopy(self.pages)
            next(p for p in records if p['id'] == 'task-brief')[key] = value
            variants.append(records)
        for records in variants:
            with self.assertRaises(ValueError):
                build.feedback_markers(records)

    def test_missing_or_ambiguous_correction_anchor_refuses_rewrite(self):
        page = {'id': 'task-brief'}
        anchor = '<a href="/contact/">Report a problem or correction</a>'
        for body in ['none', anchor + anchor]:
            with self.assertRaises(ValueError):
                build.feedback_link(page, body)
        self.assertEqual(build.feedback_link({'id': 'other'}, anchor), anchor)

    def test_normal_contact_controls_and_submission_destination_are_unchanged(self):
        old = history.before('contact/index.html', self.contact)
        def controls(html):
            return [(t, a) for t, a in Elements(html).items
                    if t in ('form', 'input', 'select', 'textarea', 'button', 'option')]
        self.assertEqual(controls(old), controls(self.contact))
        for term in ['Your tool entries were not carried over.', 'You can edit or remove it.',
                     'Do not include private worksheet entries or confidential information.']:
            self.assertIn(term, self.contact)

    def test_hidden_help_has_no_misleading_description_on_ordinary_contact(self):
        nodes = dict((a.get('id'), a) for _, a in Elements(self.contact).items if a.get('id'))
        self.assertNotIn('aria-describedby', nodes['contact-context'])
        self.assertNotIn('aria-describedby', nodes['contact-message'])
        for key in ['contact-source-notice', 'contact-feedback-help']:
            self.assertIn('hidden', nodes[key])
        self.assertIn("context.setAttribute('aria-describedby', 'contact-source-notice')", self.js)

    def test_script_adds_no_referrer_queries_storage_or_extra_transport(self):
        old = history.before('assets/contact.js', self.js)
        begin = self.js.index('  // The hash selects an authored public-page marker')
        end = self.js.index('  form.noValidate = true;', begin)
        self.assertEqual(self.js[:begin] + self.js[end:], old)
        section = self.js[begin:end]
        for term in ['document.referrer', 'location.search', 'fetch(', 'XMLHttpRequest',
                     'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML',
                     'FormData', '.submit(', 'requestSubmit', 'dispatchEvent']:
            self.assertNotIn(term, section)
        self.assertIn('!context.value', section)
        self.assertIn('title.textContent = label', section)
        self.assertNotIn('hashchange', section)

    def test_output_inventory_is_unchanged_and_exactly_seven_pages_change(self):
        outputs = later_history.outputs(self.outputs)
        prior = {p: task_brief_error_history.before(p, inquiry_history.before(p, value)) for p, value in outputs.items()}
        changed = [str(p) for p, value in prior.items() if history.before(p, value) != value]
        expected = {'contact/index.html'} | {str(build.output_path(r)) for r in EXPECTED.values()}
        self.assertEqual(set(changed), expected)
        self.assertEqual(len(prior), 222)

    def test_all_714_production_paths_restore_the_verified_parent(self):
        record = history.change()
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        files = later_history.files([p for p in tracked if p and not p.startswith(('_tests/', '_reports/'))])
        actual = [(p, digest(history.before(p, later_history.before(p, (ROOT / p).read_bytes())))) for p in files]
        self.assertEqual(len(actual), 714)
        self.assertEqual(record['production_count'], 714)
        self.assertEqual(digest(json.dumps(sorted(actual), separators=(',', ':'))),
                         record['production_fingerprint'])
        self.assertEqual(set(record['paths']),
                         {'_scripts/build.py', '_source/contact.html', 'assets/contact.js', 'contact/index.html'} |
                         {str(build.output_path(r)) for r in EXPECTED.values()})

    def test_exact_reversal_preserves_type_and_unknown_changes_stay_visible(self):
        for path, item in history.change()['paths'].items():
            raw = task_brief_error_history.before(path, (ROOT / path).read_bytes())
            self.assertEqual(digest(raw), item['new_sha256'])
            before = history.before(path, raw)
            self.assertEqual(digest(before), item['old_sha256'])
            self.assertEqual(history.before(Path(path), raw.decode()).encode(), before)
            self.assertEqual(history.before(path, before), before)
            for mutation in [raw + b'!', b'!' + raw, raw[1:]]:
                self.assertEqual(history.before(path, mutation), mutation)
        self.assertEqual(history.before('unrelated', b'unchanged'), b'unchanged')

    def test_invalid_and_overlapping_offsets_cannot_reconstruct_history(self):
        for edits in [[[True, 0, '']], [[-1, 0, '']], [[2, 1, '']],
                      [[0, 3, ''], [2, 4, '']], [[0, 999999999, '']]]:
            record = deepcopy(history.change())
            record['paths']['contact/index.html']['edits'] = edits
            with self.subTest(edits=edits), patch.object(history, 'change', return_value=record):
                with self.assertRaises(ValueError):
                    history.before('contact/index.html', self.contact)

    def test_corrupt_snapshot_cannot_hide_a_change(self):
        record = deepcopy(history.change())
        record['paths']['contact/index.html']['old_sha256'] = '0' * 64
        with patch.object(history, 'change', return_value=record):
            with self.assertRaises(ValueError):
                history.before('contact/index.html', self.contact)


if __name__ == '__main__':
    unittest.main()
