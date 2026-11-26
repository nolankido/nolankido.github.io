"""Turn 80: About distinguishes source-backed poker teaching from playing results.

Local source/output, genuine destination, builder and negative controls.
Does not make public HTTP requests or infer ranks, clients or winnings.
"""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
START = ROOT / '_source/about.html'
PUBLIC = ROOT / 'about/index.html'
BEGINNER = '/poker/free-poker-learning-path/'
ADVANCED = '/poker/10bb/#six-checks'
PARA = re.compile(r'<p class="small-copy about-poker-study-proof">.*?</p>', re.S)


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.routes = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.routes.append(dict(attrs).get('href'))


def teaching_paragraph(document):
    matches = PARA.findall(document)
    if len(matches) != 1:
        raise ValueError('About requires one and only one source-backed poker study proof')
    return matches[0]


def contract_errors(document):
    try:
        paragraph = teaching_paragraph(document)
    except ValueError as exc:
        return [str(exc)]
    links = Anchors()
    links.feed(paragraph)
    errors = []
    if links.routes != [BEGINNER, ADVANCED]:
        errors.append('Study routes missing, reordered or broadened')
    for claim in ('Original poker instruction, separate from tournament results:',
                  'six connected beginner lessons and practice',
                  'six short-stack decision checks',
                  'answered questions',
                  'reproducible fictional ICM example',
                  'do not establish live-hand solver accuracy',
                  'tournament profit or official professional credentials'):
        if paragraph.count(claim) != 1:
            errors.append('Claim or limit missing: ' + claim)
    for disallowed in ('utm_', '<script', 'onclick=', 'guaranteed winnings',
                       'proven profit', 'official creator status', chr(0x2014)):
        if disallowed in paragraph:
            errors.append('Unreviewed claim or behavior: ' + disallowed)
    if not document.index('</div>\n' + paragraph) < document.index(
        '<p>There are different kinds of evidence behind my work.'):
        errors.append('Teaching route should follow the identity evidence cards')
    return errors


class Turn80AboutTeaching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = START.read_text(encoding='utf-8')
        cls.public = PUBLIC.read_text(encoding='utf-8')
        cls.course = (ROOT / 'poker/free-poker-learning-path/index.html').read_text(
            encoding='utf-8')
        cls.playbook = (ROOT / 'poker/10bb/index.html').read_text(encoding='utf-8')

    def test_one_identical_early_teaching_route_in_source_and_published_about(self):
        self.assertEqual(contract_errors(self.source), [])
        self.assertEqual(contract_errors(self.public), [])
        self.assertEqual(teaching_paragraph(self.source), teaching_paragraph(self.public))
        self.assertEqual(self.public.count('href="' + BEGINNER + '"'), 1)
        self.assertEqual(self.public.count('href="' + ADVANCED + '"'), 1)

    def test_real_beginner_course_and_standalone_written_playbook(self):
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com' + BEGINNER + '">',
            self.course)
        self.assertIn('six connected lessons', self.course)
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com/poker/10bb/">',
            self.playbook)
        self.assertEqual(self.playbook.count('id="six-checks"'), 1)
        self.assertIn('No video is required.', self.playbook)
        self.assertIn('href="/downloads/ten-bb-tournament-checklist.md"', self.playbook)
        self.assertIn('href="/downloads/ten-bb-playbook-icm-verify.py"', self.playbook)
        self.assertTrue((ROOT / 'downloads/ten-bb-tournament-checklist.md').is_file())
        self.assertTrue((ROOT / 'downloads/ten-bb-playbook-icm-verify.py').is_file())

    def test_independent_personal_records_stay_distinct_from_teaching(self):
        for page in (self.source, self.public):
            self.assertIn('id="who-is-nolan-kido"', page)
            self.assertIn('id="nolanpoker-ai-link"', page)
            self.assertIn('href="/poker/nolan-kido/#player-record-title"', page)
            self.assertIn('https://www.youtube.com/@NolanPoker', page)
            self.assertIn('Tournament cashes are gross results, not profit.', page)
            self.assertIn('https://doi.org/10.1111/j.1475-679X.2012.00447.x', page)

    def test_existing_canonical_and_revision_provenance_unchanged(self):
        record = next(p for p in json.loads(
            (ROOT / '_source/pages.json').read_text(encoding='utf-8'))
            if p['id'] == 'about')
        self.assertGreaterEqual(record['updated'], '2026-11-20')
        self.assertIn(
            '<link rel="canonical" href="https://nolankido.com/about/">',
            self.public)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S).group(1))
        self.assertNotIn('dateModified', schema)
        self.assertIn('<loc>https://nolankido.com/about/</loc>\n    <lastmod>' + record['updated'] + '</lastmod>',
                      (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        self.assertEqual(len(re.findall(r'<h1\b', self.public)), 1)

    def test_deterministic_generator_reproduces_committed_about(self):
        import build
        self.assertEqual(build.build_outputs()[Path('about/index.html')],
                         self.public)

    def test_negative_controls_reject_false_or_unpublished_claims(self):
        paragraph = teaching_paragraph(self.source)
        for altered in (
            paragraph.replace(BEGINNER, '/poker/unknown-course/', 1),
            paragraph.replace(ADVANCED, '/poker/10bb/#not-a-section', 1),
            paragraph.replace('reproducible fictional ICM example',
                              'guaranteed winnings', 1),
            paragraph.replace('do not establish live-hand solver accuracy',
                              'prove live-hand solver accuracy', 1),
            paragraph + paragraph,
        ):
            with self.subTest(altered=altered[:80]):
                self.assertNotEqual(
                    contract_errors(self.source.replace(paragraph, altered, 1)), [])

    def test_existing_local_runner_includes_new_contract_and_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn80_about_poker_teaching.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in ('.yaml', '.yml')
            for p in actions.iterdir()
        ))


if __name__ == '__main__':
    unittest.main()
