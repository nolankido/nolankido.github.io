"""Weekly Reset content, exact history, schema and single-worksheet contracts."""
from copy import deepcopy
from hashlib import sha256
from html import escape
from pathlib import Path
import profile_datetime_history
from unittest.mock import patch
from xml.etree import ElementTree as ET
import html5lib
import json
import re
import shutil
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import living_well as lw
import turn09_weekly_reset_history as history

ROUTE = '/living-well/weekly-reset/'
PAGE = 'living-well/weekly-reset/index.html'
SCOPE = {'_scripts/living_well.py', '_source/living-well/launch.json', PAGE,
         'living-well/guides/index.html', 'living-well/topics/everyday-ai/index.html', 'sitemap.xml'}


class WeeklyResetTurn09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.entry = next(e for e in lw.load(ROOT) if e['slug'] == 'weekly-reset')
        cls.page = cls.outputs[Path(PAGE)]

    def test_small_start_precedes_original_article_and_has_three_steps(self):
        start = lw.weekly_reset_start(self.entry)
        self.assertEqual(start.count('<li>'), 3)
        for prefix in ('Check:', 'Choose:', 'Release:'):
            self.assertIn(prefix, start)
        self.assertLess(self.page.index('Small weekly reset'), self.page.index('id="part-1"'))
        for text in ('one manageable next action', 'uncertain as to check', 'deliberately leave unplanned'):
            self.assertIn(text, start)

    def test_example_distinguishes_verified_fact_action_and_open_space(self):
        text = self.entry['quick_start']['example']
        for part in ('Fictional', 'Confirmed:', 'checked against its confirmation',
                     'Next action:', 'Can wait:', 'Leave open:', 'not anyone’s actual schedule'):
            self.assertIn(part, text)
        self.assertIn('existing privacy notice', self.page)
        self.assertNotIn('No tracking', self.page)

    def test_seven_original_sections_and_existing_example_are_unchanged(self):
        old = history.change()['entry_pair']['old']
        self.assertEqual(old['sections'], self.entry['sections'])
        self.assertEqual(old.get('practice'), self.entry.get('practice'))
        self.assertEqual(old['question'], self.entry['question'])
        for n in range(1, 8):
            self.assertEqual(self.page.count('id="part-' + str(n) + '"'), 1)
        old_body = history.before(PAGE, self.page)
        section = re.compile(r'<h2 id="part-1".*?<h2 id="one-question"', re.S)
        self.assertEqual(section.search(old_body).group(), section.search(self.page).group())

    def test_same_original_sheet_on_guide_directory_download_and_live_target(self):
        path = Path('downloads/living-well-weekly-reset.md')
        text = lw.worksheet_exports()[path]
        self.assertEqual((ROOT / path).read_bytes(), text.encode())
        self.assertIn('<pre>' + escape(text) + '</pre>', self.page)
        self.assertIn('<pre>' + escape(text) + '</pre>', self.outputs[Path('living-well/worksheets/index.html')])
        self.assertEqual(check_live.targets()['/' + str(path)], (200, text.encode()))

    def test_preview_print_and_native_access_instructions_are_explicit(self):
        self.assertIn('id="weekly-reset-worksheet"', self.page)
        self.assertIn('Open this preview before printing or copying', self.page)
        self.assertIn('href="/living-well/worksheets/#weekly-reset"', self.page)
        self.assertIn('href="/downloads/living-well-weekly-reset.md" download', self.page)
        self.assertNotRegex(lw.weekly_reset_start(self.entry), r'<(?:form|textarea|input|script|iframe)\b')

    def test_quick_start_schema_rejects_invalid_and_wrong_scope(self):
        values = [None, [], {}, 'text', {**self.entry['quick_start'], 'extra': 'unreviewed'}]
        for key in ('label', 'intro', 'example'):
            for value in ('', '  ', 3, None):
                q = deepcopy(self.entry['quick_start']); q[key] = value; values.append(q)
        for steps in ('three', [], ['one'], ['one', 'two', None], ['one', 'two', ' '], ['x'] * 4):
            q = deepcopy(self.entry['quick_start']); q['steps'] = steps; values.append(q)
        for value in values:
            e = deepcopy(self.entry); e['quick_start'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                lw.weekly_reset_start(e)
        for key, value in [('slug', 'quiet-morning'), ('kind', 'essay')]:
            e = deepcopy(self.entry); e[key] = value
            with self.assertRaises(ValueError): lw.validate_quick_start(e)

    def test_loader_rejects_malformed_quick_start_before_rendering(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copytree(ROOT / '_source/living-well', root / '_source/living-well')
            path = root / '_source/living-well/launch.json'
            data = json.loads(path.read_text())
            e = next(e for e in data['entries'] if e['slug'] == 'weekly-reset')
            e['quick_start']['steps'] = 'not a list'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'three text steps'): lw.load(root)

    def test_missing_duplicate_and_empty_sheet_fail_closed(self):
        sheet = next(s for s in lw.SHEETS if s[0] == 'weekly-reset')
        for sheets in ([s for s in lw.SHEETS if s[0] != 'weekly-reset'], lw.SHEETS + [sheet],
                       [(*s[:4], '') if s[0] == 'weekly-reset' else s for s in lw.SHEETS]):
            with patch.object(lw, 'SHEETS', sheets), self.assertRaises(ValueError):
                lw.weekly_reset_start(self.entry)

    def test_plain_text_is_escaped_without_mutating_source(self):
        e = deepcopy(self.entry)
        e['quick_start']['label'] = '<b>Label & test</b>'
        e['quick_start']['steps'][0] = '<img src=x onerror=alert(1)>'
        untouched = deepcopy(e)
        rendered = lw.weekly_reset_start(e)
        self.assertIn('&lt;b&gt;Label &amp; test&lt;/b&gt;', rendered)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', rendered)
        self.assertNotIn('<img', rendered)
        self.assertEqual(e, untouched)

    def test_reading_estimate_includes_new_instructional_text(self):
        old = history.change()['entry_pair']['old']
        self.assertGreater(lw.minutes(self.entry), lw.minutes(old))
        self.assertIn(str(lw.minutes(self.entry)) + ' min read</p><h3><a href="' + ROUTE,
                      self.outputs[Path('living-well/guides/index.html')])

    def test_only_weekly_reset_metadata_changes_and_dates_are_consistent(self):
        restored = history.pages(self.pages)
        pairs = [(a, b) for a, b in zip(restored, self.pages) if a != b]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][1]['path'], ROUTE)
        self.assertEqual(self.entry['published'], '2026-10-08')
        self.assertEqual(self.entry['updated'], '2026-10-19')
        self.assertEqual(pairs[0][0]['updated'], '2026-10-09')
        xml = ET.fromstring(self.outputs[Path('sitemap.xml')])
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        items = [x for x in xml.findall('s:url', ns) if x.findtext('s:loc', namespaces=ns) == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].findtext('s:lastmod', namespaces=ns), self.entry['updated'])
        doc = html5lib.parse(self.page, namespaceHTMLElements=False)
        schemas = [json.loads(e.text) for e in doc.iter('script') if e.get('type') == 'application/ld+json']
        article = next(s for s in schemas if s.get('@type') == 'Article')
        self.assertEqual(article['datePublished'], self.entry['published'])
        self.assertEqual(article['dateModified'], self.entry['updated'])
        self.assertIn(self.entry['revision'], self.page)

    def test_exact_six_path_scope_and_unrelated_public_files_preserved(self):
        record = history.change()
        self.assertEqual(set(record['paths']), SCOPE)
        self.assertEqual(record['base_commit'], history.BASE)
        self.assertGreater(len(record['unchanged_files']), 700)
        for path, expected in record['unchanged_files'].items():
            with self.subTest(path=path):
                self.assertEqual(sha256(profile_datetime_history.before(path, (ROOT / path).read_bytes())).hexdigest(), expected)

    def test_exact_hash_restoration_types_and_idempotence(self):
        for path, item in history.change()['paths'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['new_sha256'])
            restored = history.before(path, raw)
            self.assertEqual(sha256(restored).hexdigest(), item['old_sha256'])
            self.assertEqual(history.before(path, restored), restored)
            self.assertEqual(history.before(path, raw.decode()).encode(), restored)
            self.assertEqual(history.before(path, raw + b'!'), raw + b'!')
        self.assertEqual(history.before('unrelated', b'content'), b'content')

    def test_complete_metadata_and_source_record_equality_required(self):
        pair = history.change()['page_pairs'][0]
        original = deepcopy(pair['new'])
        self.assertEqual(history.pages([original]), [pair['old']])
        self.assertEqual(original, pair['new'])
        for key, value in [('description', 'Unreviewed'), ('noindex', True), ('title', 'Changed')]:
            changed = deepcopy(original); changed[key] = value
            self.assertEqual(history.pages([changed]), [changed])
        changed = deepcopy(original); changed.pop('description')
        self.assertEqual(history.pages([changed]), [changed])
        e = deepcopy(self.entry)
        self.assertEqual(history.original_entry(e), history.change()['entry_pair']['old'])
        e['quick_start']['steps'][0] += ' Unreviewed advice.'
        self.assertEqual(history.original_entry(e), e)

    def test_corrupt_history_is_rejected(self):
        path = PAGE; raw = (ROOT / path).read_bytes()
        for field, value in [('old_sha256', '0' * 64), ('old_zlib_base64', 'not base64')]:
            changed = deepcopy(history.change()); changed['paths'][path][field] = value
            with patch.object(history, 'change', return_value=changed), self.assertRaises((ValueError, zlib.error)):
                history.before(path, raw)

    def test_unknown_history_versions_are_rejected(self):
        good = deepcopy(history.change())
        try:
            for field, value in [('version', 1), ('base_commit', 'unreviewed')]:
                changed = deepcopy(good); changed[field] = value
                history.change.cache_clear()
                with patch.object(Path, 'read_text', return_value=json.dumps(changed)), self.assertRaises(ValueError):
                    history.change()
        finally:
            history.change.cache_clear()


if __name__ == '__main__':
    unittest.main()
