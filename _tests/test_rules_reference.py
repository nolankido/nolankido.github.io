"""One current rules record, coherent publication, and independent preservation."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from test_site import ROOT, build
import poker_resources
import poker_finder
import poker_library
import rules_reference_history as history

GUIDES = ('follow-along', 'table-etiquette', 'position-and-stacks',
          'poker-rules-and-fair-play', 'first-decisions', 'getting-started')


class RulesReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = build.public_pages()
        cls.resources = poker_resources.load(ROOT)
        cls.raw = json.loads((ROOT / '_source/poker/resources.json').read_text())
        cls.version = poker_resources.rules_values(ROOT)
        cls.baseline = json.loads((ROOT / '_tests/rules-reference-baseline.json').read_text())

    def test_current_citations_and_exports_use_the_same_reviewed_record(self):
        v = self.version
        for slug in GUIDES:
            with self.subTest(slug=slug):
                text = self.outputs[Path('poker') / slug / 'index.html']
                self.assertIn(v['poker_tda_version'], text)
                self.assertIn(v['poker_tda_reviewed_label'], text)
                self.assertIn(v['poker_tda_long_label'], text)
                self.assertNotIn('version 1.0', text.lower())
                self.assertNotIn('${poker_tda_', text)
        entry = next(r for r in self.resources if r['id'] == 'tda-rules')
        self.assertIn('version ' + v['poker_tda_version'], entry['notes'])
        self.assertIn(v['poker_tda_published_label'], entry['notes'])
        self.assertEqual(entry['reviewed_on'], v['poker_tda_reviewed_on'])
        self.assertNotIn('source_version', entry)
        for path in ['poker/resources/index.html', 'poker/find/index.html',
                     'downloads/poker-resource-directory.md', 'downloads/poker-resource-directory.json']:
            self.assertIn(entry['notes'], self.outputs[Path(path)])
            self.assertIn(entry['reviewed_on'], self.outputs[Path(path)])
        for file in (ROOT / '_source/poker').rglob('*.html'):
            self.assertNotIn('version 1.0', file.read_text().lower(), str(file))
        self.assertIn('version 1.0', (ROOT / '_source/poker/RESOURCE_BATCH_002.md').read_text())

    def test_next_version_propagates_from_one_in_memory_edit(self):
        data = deepcopy(self.raw)
        entry = next(e for e in data['entries'] if e['id'] == 'tda-rules')
        entry['source_version'] = {'edition': 2026, 'version': '1.2', 'published_on': '2026-10-15'}
        target = ROOT / '_source/poker/resources.json'
        read = Path.read_text
        def synthetic(path, *args, **kwargs):
            return json.dumps(data) if path == target else read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', synthetic):
            outputs = build.build_outputs()
            entries = poker_resources.load(ROOT)
            for slug in GUIDES:
                text = outputs[Path('poker') / slug / 'index.html']
                self.assertIn('2026 Rules, Version 1.2, October 15, 2026', text)
                self.assertNotIn('version 1.1', text.lower())
            tda = next(e for e in entries if e['id'] == 'tda-rules')
            for path in ['poker/resources/index.html', 'poker/find/index.html',
                         'downloads/poker-resource-directory.md', 'downloads/poker-resource-directory.json']:
                self.assertIn(tda['notes'], outputs[Path(path)])
            library = poker_library.load(ROOT, build.public_pages())
            page = next(p for p in self.pages if p['path'] == '/poker/poker-rules-and-fair-play/')
            sections = poker_finder.guide_sections(ROOT, page, build.poker_content.load(ROOT))
            self.assertTrue(any('Version 1.2' in s['text'] for s in sections))
            self.assertFalse(any('${poker_tda_' in s['text'] for s in sections))
            self.assertEqual(len(library), 60)

    def test_invalid_versions_dates_and_unreviewed_sources_fail_closed(self):
        original = next(e for e in self.raw['entries'] if e['id'] == 'tda-rules')
        variants = []
        for field in [{'edition': True}, {'edition': 2025}, {'version': 'unknown'},
                      {'version': '<script>'}, {'published_on': '2026-02-30'},
                      {'published_on': '2026-10-17'}, {'extra': 'unsupported'}]:
            bad = deepcopy(original); bad['source_version'].update(field); variants.append(bad)
        for update in [{'reviewed_on': '2026-09-20'}, {'reviewed_on': '2026-10-17'},
                       {'review_method': 'index'}, {'url': 'https://example.org/rules/'},
                       {'notes': '${poker_tda_typo}'}]:
            bad = deepcopy(original); bad.update(update); variants.append(bad)
        bad = deepcopy(original); del bad['source_version']; variants.append(bad)
        bad = deepcopy(original); bad['id'] = 'different-source'; variants.append(bad)
        with TemporaryDirectory() as folder:
            root = Path(folder); path = root / '_source/poker/resources.json'; path.parent.mkdir(parents=True)
            for bad in variants:
                with self.subTest(bad=bad):
                    path.write_text(json.dumps({'version': 1, 'entries': [bad]}))
                    with self.assertRaises(ValueError):
                        poker_resources.load(root, as_of=date(2026, 10, 16))
        with self.assertRaises(ValueError):
            poker_resources.resolve_rules('${poker_tda_typo}', ROOT)
        self.assertEqual(poker_resources.resolve_rules('${unrelated}', ROOT), '${unrelated}')

    def test_only_tda_review_changes_and_older_evidence_stays_exact(self):
        self.assertEqual((self.baseline['commit'], len(self.baseline['pages']),
                          len(self.baseline['outputs']), len(self.baseline['files'])),
                         ('bc0d6ae893e59b89aaa63fd7c6aa58be78045fae', 193, 221, 481))
        prior = {e['id']: e for e in self.baseline['resources']}
        self.assertEqual(len(prior), 146)
        changed = [e['id'] for e in self.resources if e != prior[e['id']]]
        self.assertEqual(changed, ['tda-rules'])
        self.assertEqual(history.resources(self.resources), self.baseline['resources'])
        mutated = deepcopy(self.resources); mutated[1]['notes'] += 'Unreviewed edit'
        self.assertNotEqual(history.resources(mutated), self.baseline['resources'])
        self.assertEqual(history.pages(self.pages), self.baseline['pages'])
        for path, digest in self.baseline['outputs'].items():
            self.assertEqual(sha256(history.before(path, self.outputs[Path(path)]).encode()).hexdigest(), digest, path)
        for path, digest in self.baseline['files'].items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(sha256(history.before(path, raw)).hexdigest(), digest, path)
        for path in history.change()['paths']:
            raw = (ROOT / path).read_bytes() + b'Unreviewed edit'
            self.assertEqual(history.before(path, raw), raw, path)


if __name__ == '__main__':
    unittest.main()
