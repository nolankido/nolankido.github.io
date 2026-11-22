"""Turn 75: bring the already-published release runbook into the early case proof path.

Checks local static source/public parity and existing documented boundaries.
No new search claims, remote requests, tracking or GitHub Actions.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))

SOURCE = ROOT / '_source/technology/checking-ai-website-changes.html'
OUTPUT = ROOT / 'technology/checking-ai-website-changes/index.html'
RUNBOOK = '/downloads/website-check-offline-runbook.md'
PROOF = re.compile(r'<p class="evidence-note"><strong>Follow the original repair:</strong>.*?</p>', re.S)
EARLY = re.compile(r'<p class="small-copy case-checklist-early">.*?</p>', re.S)


def check_early(html: str) -> list[str]:
    errors = []
    proof = PROOF.findall(html)
    early = EARLY.findall(html)
    if len(proof) != 1 or len(early) != 1:
        return ['one source proof and one early runbook introduction required']
    paragraph = early[0]
    if html.count('href="' + RUNBOOK + '"') != 1:
        errors.append('runbook missing or linked more than once')
    if 'href="' + RUNBOOK + '" download' not in paragraph:
        errors.append('early link is not the real downloadable worksheet')
    if 'without relying on GitHub Actions or a hosted testing service' not in paragraph:
        errors.append('release checklist limits altered')
    if not html.index(proof[0]) < html.index(paragraph) < html.index('<div class="entry-jumps">'):
        errors.append('runbook must be found immediately after the proof and before jumps')
    if html.index(paragraph) > html.index('id="case-evidence"'):
        errors.append('runbook appears after the first case section')
    if 'case-checklist-early' in html[html.index('id="case-source-diff"'):]:
        errors.append('runbook repeated at the end instead of moving it')
    if chr(0x2014) in paragraph or 'utm_' in paragraph or '<script' in paragraph:
        errors.append('unapproved content, punctuation or behavior')
    return errors


class Turn75EarlyReleaseRunbook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.page = OUTPUT.read_text(encoding='utf-8')

    def test_source_public_copy_and_early_position(self):
        self.assertEqual(check_early(self.source), [])
        self.assertEqual(check_early(self.page), [])
        self.assertEqual(EARLY.findall(self.source), EARLY.findall(self.page))
        self.assertEqual(PROOF.findall(self.source), PROOF.findall(self.page))

    def test_pinned_repair_paths_remain_unchanged(self):
        for html in (self.source, self.page):
            self.assertIn(
                'https://github.com/nolankido/nolankido.github.io/blob/'
                '2bf8908339e06f604cea00f0254494e17171ecf4/_source/technology/task-brief.html',
                html)
            self.assertIn(
                'https://github.com/nolankido/nolankido.github.io/blob/'
                '73782caa4697204690c679626b36427c28201234/_source/technology/task-brief.html',
                html)
            self.assertIn('347 passing tests', html)
            self.assertIn('not a measured productivity study', html)
            self.assertEqual(html.count('id="case-source-diff"'), 1)

    def test_download_exists_and_is_registered_for_live_byte_check(self):
        import check_live
        expected = (ROOT / RUNBOOK.lstrip('/')).read_bytes()
        self.assertTrue(expected.startswith(b'#'))
        self.assertEqual(check_live.targets(ROOT)[RUNBOOK], (200, expected))

    def test_reader_route_source_provenance_preserved(self):
        manifest = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        record = next(p for p in manifest if p['path'] ==
                      '/technology/checking-ai-website-changes/')
        self.assertEqual(record['date'], '2026-10-11')
        self.assertEqual(record['updated'], '2026-11-18')
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/checking-ai-website-changes/">',
                      self.page)
        self.assertIn('"datePublished": "2026-10-11"', self.page)
        self.assertIn('"dateModified": "2026-11-18"', self.page)
        self.assertIn('About 6 min read', self.page)

    def test_deterministic_public_builder_remains_in_sync(self):
        import build
        self.assertEqual(
            build.build_outputs()[Path('technology/checking-ai-website-changes/index.html')],
            self.page)

    def test_negative_controls_reject_missing_or_late_duplicate_link(self):
        original = EARLY.search(self.source).group()
        for replacement in (
            original.replace(RUNBOOK, '/downloads/unknown.md'),
            original.replace(' download', ''),
            original + original,
            '',
        ):
            with self.subTest(replacement=replacement[:90]):
                altered = self.source.replace(original, replacement, 1)
                self.assertNotEqual(check_early(altered), [])

    def test_registered_manual_release_without_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn75_early_case_checklist.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            file.is_file() and file.suffix.lower() in ('.yml', '.yaml')
            for file in actions.iterdir()
        ))


if __name__ == '__main__':
    unittest.main()
