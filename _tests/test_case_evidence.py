"""Primary evidence stays usable without rewriting the recorded case or site."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build, case_evidence
import case_evidence_history as history
from test_site import Page


class CaseEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.baseline = json.loads((ROOT / '_tests/case-evidence-baseline.json').read_text())

    def test_all_original_content_metadata_assets_and_other_outputs_remain_exact(self):
        b = self.baseline
        self.assertEqual(build.public_pages(), b['pages'])
        self.assertEqual(set(map(str, self.outputs)), set(b['outputs']))
        changed = []
        for path, expected in b['outputs'].items():
            value = self.outputs[Path(path)]
            if sha256(value.encode()).hexdigest() != expected:
                changed.append(path)
            self.assertEqual(sha256(history.before(path, value).encode()).hexdigest(), expected, path)
        self.assertEqual(changed, [case_evidence.PATH])
        files = {p.relative_to(ROOT).as_posix() for d in ['_source', 'assets', 'downloads']
                 for p in (ROOT / d).rglob('*') if p.is_file()}
        self.assertEqual(files, set(b['files']))
        self.assertEqual(len(files), 343)
        for path, expected in b['files'].items():
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), expected, path)

    def test_links_point_to_the_verified_historical_source_checks_and_release(self):
        block = case_evidence.block(ROOT)
        page = Page(block)
        self.assertEqual([a['href'] for a in page.tags('a')], [
            'https://github.com/nolankido/nolankido.github.io/compare/2bf8908339e06f604cea00f0254494e17171ecf4...73782caa4697204690c679626b36427c28201234',
            'https://github.com/nolankido/nolankido.github.io/actions/runs/38196825689',
            'https://github.com/nolankido/nolankido.github.io/pull/40',
        ])
        self.assertEqual(page.tags('nav')[0]['aria-labelledby'], page.tags('h3')[0]['id'])
        self.assertFalse(page.tags('h2') or page.tags('script'))
        self.assertTrue(all('target' not in a and 'onclick' not in a for a in page.tags('a')))
        self.assertNotIn('\u2014', block)
        self.assertEqual(sha256(block.encode()).hexdigest(), history.BLOCK_SHA256)

    def test_addition_is_scoped_and_fails_on_missing_or_duplicate_original_anchor(self):
        body = (ROOT / '_source/technology/checking-ai-website-changes.html').read_text()
        page = {'id': case_evidence.PAGE_ID}
        result = case_evidence.decorate(page, body, ROOT)
        self.assertEqual(history.before(case_evidence.PATH, result), body)
        self.assertEqual(case_evidence.decorate({'id': 'about'}, body, ROOT), body)
        for invalid in [result, body.replace(case_evidence.ANCHOR, ''), body + case_evidence.ANCHOR]:
            with self.assertRaises(ValueError):
                case_evidence.decorate(page, invalid, ROOT)

    def test_historical_adapter_cannot_hide_copy_or_link_changes(self):
        path = case_evidence.PATH
        original = self.outputs[Path(path)]
        for old, new in [('Compare the actual repair', 'Changed label'), ('/pull/40', '/pull/59'),
                         ('The candidate built.', 'Unexpected claim.')]:
            modified = original.replace(old, new, 1)
            self.assertNotEqual(modified, original)
            self.assertNotEqual(history.before(path, modified), history.before(path, original))
        self.assertEqual(history.before('about/index.html', original), original)
        self.assertEqual(history.before('assets/example.woff2', b'\xff\x00'), b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
