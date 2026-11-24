"""Turn 84: the published 10 BB Playbook is discoverable without fake catalog counts.

All checks are local and source-owned. This does not query search traffic,
interpret tournament results, or certify a production deployment.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
GUIDE = '/poker/10bb/#six-checks'
WORKSHEET = '/downloads/ten-bb-tournament-checklist.md'
LIB_RE = re.compile(r'<p class="reader-help poker-standalone-playbook">.*?</p>', re.S)
STUDY_RE = re.compile(r'<p class="small-copy poker-study-tenbb">.*?</p>', re.S)


def paragraph(html, pattern):
    matches = pattern.findall(html)
    if len(matches) != 1:
        raise ValueError('Exactly one source-owned educational handoff required')
    return matches[0]


def problems(html, pattern, kind):
    try:
        part = paragraph(html, pattern)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for value in (f'href="{GUIDE}"', f'href="{WORKSHEET}" download'):
        if part.count(value) != 1:
            errors.append('Missing or repeated route: ' + value)
    if kind == 'library':
        for phrase in ('Separate written tournament companion:',
                       'six decision checks',
                       'six answered practice questions',
                       'reproducible fictional ICM example',
                       'not part of the filtered library cards below',
                       'not a real-hand solver verdict'):
            if part.count(phrase) != 1:
                errors.append('Missing source-backed label or limit: ' + phrase)
        if not (html.index('id="in-depth"') < html.index(part)
                < html.index('id="all-guides"')):
            errors.append('The separate companion must sit before the filtered catalog')
    else:
        for phrase in ('Ten-blind tournament decisions:',
                       'Review the Playbook', 'for after-play practice',
                       'fictional, not an opponent range for an actual hand'):
            if part.count(phrase) != 1:
                errors.append('Missing study context or limit: ' + phrase)
        a = html.index('<article><h3>I am studying tournaments.</h3>')
        b = html.index('<article><h3>I am making an episode.</h3>', a)
        if not a < html.index(part) < b:
            errors.append('The guide belongs to the tournament study route')
    if any(x in part for x in ('utm_', 'onclick=', '<script', 'guaranteed winnings',
                               'official creator', chr(0x2014))):
        errors.append('Unreviewed tracking, executable markup or success claim')
    return errors


class Turn84PokerDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library_source = (ROOT / '_source/poker/library.html').read_text(
            encoding='utf-8')
        cls.library_public = (ROOT / 'poker/library/index.html').read_text(
            encoding='utf-8')
        cls.study_source = (ROOT / '_source/poker/study.html').read_text(
            encoding='utf-8')
        cls.study_public = (ROOT / 'poker/study/index.html').read_text(
            encoding='utf-8')
        cls.playbook = (ROOT / 'poker/10bb/index.html').read_text(encoding='utf-8')

    def test_library_source_and_public_handoff_are_identical_and_single(self):
        for html in (self.library_source, self.library_public):
            self.assertEqual(problems(html, LIB_RE, 'library'), [])
            self.assertEqual(html.count(f'href="{GUIDE}"'), 1)
            self.assertEqual(html.count(f'href="{WORKSHEET}"'), 1)
        self.assertEqual(paragraph(self.library_source, LIB_RE),
                         paragraph(self.library_public, LIB_RE))

    def test_study_source_and_public_handoff_are_identical_and_single(self):
        for html in (self.study_source, self.study_public):
            self.assertEqual(problems(html, STUDY_RE, 'study'), [])
            self.assertEqual(html.count(f'href="{GUIDE}"'), 1)
            self.assertEqual(html.count(f'href="{WORKSHEET}"'), 1)
        self.assertEqual(paragraph(self.study_source, STUDY_RE),
                         paragraph(self.study_public, STUDY_RE))

    def test_existing_filtered_75_guide_catalog_is_not_falsely_expanded(self):
        library = self.library_public
        self.assertIn('All 75 free guides.', library)
        self.assertEqual(len(re.findall(r'\bdata-library-card\b', library)), 75)
        self.assertEqual(library.count('id="poker-library"'), 1)
        in_depth = library[library.index('id="in-depth"'):library.index('id="all-guides"')]
        self.assertEqual(in_depth.count('class="poker-long-read"'), 4)
        self.assertEqual(in_depth.count('class="reader-help poker-standalone-playbook"'), 1)
        cards = library[library.index('id="poker-library"'):]
        self.assertNotIn('data-library-card data-topic="tournaments" data-search="10 Big Blind Tournament Playbook', cards)

    def test_original_study_route_keeps_four_ordered_decisions(self):
        for html in (self.study_source, self.study_public):
            start = html.index('<article><h3>I am studying tournaments.</h3>')
            section = html[start:html.index('</article>', start)]
            choices = re.search(r'<ol>(.*?)</ol>', section, re.S)
            self.assertIsNotNone(choices)
            self.assertEqual(choices.group(1).count('<li>'), 4)
            for route in ('/poker/short-stack-decisions/',
                          '/poker/tournament-equity/',
                          '/poker/tournament-entry-prize-pool-ledger/#ledger-guarantee',
                          '/poker/practice-room/#spot-check'):
                self.assertIn(f'href="{route}"', choices.group(1))

    def test_published_guide_and_download_are_real_not_future_resources(self):
        self.assertEqual(self.playbook.count('id="six-checks"'), 1)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/10bb/">',
                      self.playbook)
        self.assertIn('No video is required.', self.playbook)
        self.assertIn('six answered questions', self.playbook.lower())
        self.assertTrue((ROOT / WORKSHEET.lstrip('/')).is_file())
        self.assertIn('## Three calculations',
                      (ROOT / WORKSHEET.lstrip('/')).read_text(encoding='utf-8'))
        self.assertIn('href="' + WORKSHEET + '"', self.playbook)

    def test_pages_keep_canonical_and_original_editorial_dates(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        by_path = {p['path']: p for p in pages}
        self.assertEqual(by_path['/poker/library/']['updated'], '2026-10-08')
        self.assertEqual(by_path['/poker/study/']['updated'], '2026-10-16')
        for html, route in ((self.library_public, '/poker/library/'),
                            (self.study_public, '/poker/study/')):
            self.assertEqual(
                html.count(f'<link rel="canonical" href="https://nolankido.com{route}">'),
                1)
            self.assertEqual(len(re.findall(r'<h1\b', html)), 1)

    def test_current_deterministic_builder_reproduces_both_public_pages(self):
        import build
        generated = build.build_outputs()
        for path, html in (
            ('poker/library/index.html', self.library_public),
            ('poker/study/index.html', self.study_public),
        ):
            self.assertEqual(generated[Path(path)], html)

    def test_negative_controls_reject_missing_route_and_false_model_claim(self):
        cases = [
            (self.library_source, LIB_RE, 'library',
             lambda s: s.replace(GUIDE, '/poker/unpublished/', 1)),
            (self.library_source, LIB_RE, 'library',
             lambda s: s.replace('not a real-hand solver verdict',
                                 'guaranteed winnings', 1)),
            (self.library_source, LIB_RE, 'library',
             lambda s: s + s),
            (self.study_source, STUDY_RE, 'study',
             lambda s: s.replace(WORKSHEET, '/downloads/missing-worksheet.md', 1)),
            (self.study_source, STUDY_RE, 'study',
             lambda s: s.replace('fictional, not an opponent range for an actual hand',
                                 'approved against every opponent', 1)),
            (self.study_source, STUDY_RE, 'study',
             lambda s: s + s),
        ]
        for source, regex, kind, change in cases:
            original = paragraph(source, regex)
            modified = source.replace(original, change(original), 1)
            with self.subTest(kind=kind, change=change(original)[:60]):
                self.assertNotEqual(problems(modified, regex, kind), [])

    def test_registered_manual_release_no_new_actions_or_canonicals(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8')
        self.assertIn('test_turn84_standalone_poker_discovery.py', runner)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertEqual(sitemap.count('<loc>'), 231)
        self.assertEqual(sitemap.count('https://nolankido.com/poker/10bb/'), 1)
        workflow = ROOT / '.github/workflows'
        self.assertFalse(workflow.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yaml', '.yml')
            for p in workflow.iterdir()
        ))


if __name__ == '__main__':
    unittest.main()
