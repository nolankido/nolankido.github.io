"""Specific study-tool search labels preserve every existing page body."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import beginner_history
import build
import study_titles_history as history
import search_public_titles_history
from test_site import Page


class StudyTitlesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = {p: search_public_titles_history.before(p, value) for p, value in build.build_outputs().items()}
        cls.baseline = json.loads((ROOT / '_tests/study-titles-baseline.json').read_text())

    def test_only_five_head_labels_change_against_production(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        b = self.baseline
        self.assertEqual(history.pages(beginner_history.pages(self.pages)), b['pages'])
        self.assertEqual((len(b['outputs']), len(b['files']), len(b['bodies'])), (198, 343, 171))
        self.assertEqual(set(map(str, historical_outputs)), set(b['outputs']))
        changed = []
        for path, expected in b['outputs'].items():
            raw = historical_outputs[Path(path)]
            if sha256(raw.encode()).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw).encode()).hexdigest(), expected, path)
        self.assertCountEqual(changed, [e['path'].lstrip('/') + 'index.html' for e in history.change()['entries']])
        # Later search-only metadata is independently proved by its own baseline.
        # These title changes still preserve every page body at this release.
        for path, expected in b['bodies'].items():
            body = re.search(r'<body\b[^>]*>.*?</body>', historical_outputs[Path(path)], re.S)[0]
            self.assertEqual(sha256(body.encode()).hexdigest(), expected, path)
        files = beginner_history.files({p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file()})
        self.assertEqual(files, set(b['files']))
        changed = []
        for path, expected in b['files'].items():
            raw = search_public_titles_history.before(path, (ROOT / path).read_bytes())
            if sha256(raw).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), expected, path)
        self.assertEqual(changed, ['_source/pages.json'])

    def test_search_and_sharing_names_identify_the_real_study_subject(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        old = {p['id']: p for p in self.baseline['pages']}
        entries = {e['id']: e for e in history.change()['entries']}
        self.assertEqual(len(entries), 5)
        for p in beginner_history.pages(self.pages):
            if p['id'] not in entries:
                self.assertEqual(p, old[p['id']])
                continue
            e = entries[p['id']]
            self.assertEqual({**p, 'seo_title': old[p['id']]['seo_title']}, old[p['id']])
            self.assertEqual(p['seo_title'], e['new'])
            self.assertTrue(e['new'].startswith('Poker '))
            self.assertTrue(e['new'].endswith(' | Nolan Kido'))
            self.assertNotIn('\u2014', e['new'])
            raw = historical_outputs[build.output_path(p['path'])]
            self.assertEqual(unescape(re.search(r'<title>(.*?)</title>', raw)[1]), e['new'])
            doc = Page(raw)
            meta = {a.get('name', a.get('property')): a.get('content') for a in doc.tags('meta')}
            self.assertEqual([meta['og:title'], meta['twitter:title']], [e['new'], e['new']])
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', raw)[1])
            self.assertEqual(schema['name'], e['new'])
            self.assertEqual(schema['url'], 'https://nolankido.com' + p['path'])
            self.assertEqual(schema['dateModified'], old[p['id']]['updated'])
            if p.get('poker_guide'):
                self.assertEqual(schema['headline'], old[p['id']]['title'])
                self.assertEqual(schema['datePublished'], old[p['id']]['date'])
                self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
            self.assertFalse(p.get('noindex'))

    def test_adapter_does_not_hide_unreviewed_titles_copy_or_identity(self):
        historical_outputs = beginner_history.outputs(self.outputs)
        e = next(e for e in history.change()['entries'] if e['id'] == 'poker-side-pot-lab')
        path = e['path'].lstrip('/') + 'index.html'
        raw = historical_outputs[Path(path)]
        for old, new in [('Poker Side-Pot Exercise', 'Guaranteed Poker Wins'),
                         ('Three all-ins. Two pots.', 'An invented personal result'),
                         ('2026-10-06', '2026-10-14'),
                         ('https://nolankido.com/poker/side-pot-lab/', 'https://other.example/'),
                         ('The best hand does not win every chip.', 'The best hand wins everything.')]:
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertNotEqual(history.before(path, changed), history.before(path, raw))
        changed = raw.replace('</main>', '<p>' + e['new'] + '</p></main>', 1)
        self.assertNotEqual(history.before(path, changed), history.before(path, raw))
        for key, value in [('seo_title', 'Unreviewed'), ('date', '2026-10-14'), ('title', 'Invented result'), ('path', '/poker/moved/')]:
            changed = deepcopy(beginner_history.pages(self.pages))
            next(p for p in changed if p['id'] == e['id'])[key] = value
            self.assertNotEqual(history.pages(changed), self.baseline['pages'])
        self.assertEqual(history.before('about/index.html', raw), raw)
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')
        self.assertEqual(history.before(path, history.before(path, raw)), history.before(path, raw))


if __name__ == '__main__':
    unittest.main()
