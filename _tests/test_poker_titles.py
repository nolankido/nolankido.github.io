"""Clear search labels preserve the independently captured production content."""
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
import build
import poker_titles_history as history
from test_site import Page


class PokerTitlesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/poker-titles-baseline.json').read_text())

    def test_seven_search_titles_are_the_only_changes_to_production_content(self):
        b = self.baseline
        self.assertEqual(history.pages(self.pages), b['pages'])
        self.assertEqual((len(b['outputs']), len(b['files']), len(b['bodies'])), (198, 343, 171))
        self.assertEqual(set(map(str, self.outputs)), set(b['outputs']))
        changed = []
        for path, expected in b['outputs'].items():
            raw = self.outputs[Path(path)]
            if sha256(raw.encode()).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw).encode()).hexdigest(), expected, path)
        self.assertCountEqual(changed, [e['path'].lstrip('/') + 'index.html' for e in history.change()['entries']])
        # Compare every body directly. This proof does not use any adapter.
        for path, expected in b['bodies'].items():
            body = re.search(r'<body\b[^>]*>.*?</body>', self.outputs[Path(path)], re.S)[0]
            self.assertEqual(sha256(body.encode()).hexdigest(), expected, path)
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads'] for p in (ROOT / d).rglob('*') if p.is_file()}
        self.assertEqual(files, set(b['files']))
        changed = []
        for path, expected in b['files'].items():
            raw = (ROOT / path).read_bytes()
            if sha256(raw).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), expected, path)
        self.assertEqual(changed, ['_source/pages.json'])

    def test_search_and_sharing_labels_agree_without_renaming_or_redating_articles(self):
        old = {p['id']: p for p in self.baseline['pages']}
        expected = {e['id']: e for e in history.change()['entries']}
        self.assertEqual(len(expected), 7)
        for p in self.pages:
            if p['id'] not in expected:
                self.assertEqual(p, old[p['id']])
                continue
            e = expected[p['id']]
            self.assertEqual({**p, 'seo_title': old[p['id']]['seo_title']}, old[p['id']])
            self.assertTrue(p['poker_guide'])
            self.assertEqual(p['seo_title'], e['new'])
            self.assertTrue(e['new'].endswith(' | Nolan Kido'))
            self.assertLessEqual(len(e['new']), 65)
            self.assertNotIn('\u2014', e['new'])
            raw = self.outputs[build.output_path(p['path'])]
            doc = Page(raw)
            self.assertEqual(unescape(re.search(r'<title>(.*?)</title>', raw)[1]), e['new'])
            meta = {a.get('name', a.get('property')): a.get('content') for a in doc.tags('meta')}
            self.assertEqual([meta['og:title'], meta['twitter:title']], [e['new'], e['new']])
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', raw)[1])
            self.assertEqual(schema['name'], e['new'])
            self.assertEqual(schema['headline'], old[p['id']]['title'])
            self.assertEqual(schema['datePublished'], old[p['id']]['date'])
            self.assertEqual(schema['dateModified'], old[p['id']]['updated'])
            self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')

    def test_frozen_adapter_exposes_changed_copy_dates_urls_and_unapproved_titles(self):
        e = history.change()['entries'][1]
        path = e['path'].lstrip('/') + 'index.html'
        raw = self.outputs[Path(path)]
        for old, new in [(e['new'], 'Guaranteed winning poker strategy | Nolan Kido'),
                         ('Which hand wins?', 'A fabricated personal result'),
                         ('2026-10-05', '2026-10-14'),
                         ('https://nolankido.com/poker/hand-rankings/', 'https://other.example/'),
                         ('Compare only the best five cards', 'Compare seven cards')]:
            changed = raw.replace(old, new, 1)
            self.assertNotEqual(changed, raw)
            self.assertNotEqual(history.before(path, changed), history.before(path, raw))
        # A title phrase added to body prose must survive normalization too.
        changed = raw.replace('</main>', '<p>' + e['new'] + '</p></main>', 1)
        self.assertNotEqual(history.before(path, changed), history.before(path, raw))
        for key, value in [('seo_title', 'An unreviewed label'), ('date', '2026-10-14'), ('title', 'An invented result'), ('path', '/poker/changed/')]:
            changed = deepcopy(self.pages)
            next(p for p in changed if p['id'] == e['id'])[key] = value
            self.assertNotEqual(history.pages(changed), self.baseline['pages'])
        source = (ROOT / '_source/pages.json').read_text()
        modified = source.replace('Which hand wins?', 'A fabricated result', 1)
        self.assertNotEqual(history.before('_source/pages.json', source), history.before('_source/pages.json', modified))
        self.assertEqual(history.before('about/index.html', raw), raw)
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')
        self.assertEqual(history.before(path, history.before(path, raw)), history.before(path, raw))


if __name__ == '__main__':
    unittest.main()
