"""Turn 79: course completion leads to the actual written short-stack study guide.

The original beginner course remains complete without advanced study. The
additional route is optional, fictional and source checked. All tests local.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
sys.path.insert(0, str(ROOT / '_tests'))
SOURCE = ROOT / '_source/poker/beginner-learning-path.html'
PUBLIC = ROOT / 'poker/free-poker-learning-path/index.html'
SHORT = ROOT / 'poker/10bb/index.html'
ROUTE = '/poker/10bb/#six-checks'
SECTION = re.compile(r'<section class="viewer-example" aria-labelledby="course-finish">.*?</section>', re.S)


def course_finish(document: str) -> str:
    matches = SECTION.findall(document)
    if len(matches) != 1:
        raise ValueError('The six-lesson course must have exactly one completion menu')
    return matches[0]


def defects(document: str) -> list[str]:
    try:
        section = course_finish(document)
    except ValueError as error:
        return [str(error)]
    issues = []
    for marker in ('href="' + ROUTE + '"', 'written 10 BB Playbook',
                   'fictional stacks and payouts',
                   'not a solver recommendation for a real hand',
                   'after you can explain the cards, action and call price'):
        if section.count(marker) != 1:
            issues.append('Missing or duplicated safe optional next step: ' + marker)
    if section.count('<li>') != 5:
        issues.append('Completion menu must retain four old options plus one advanced option')
    for href in ('/poker/beginner-practice/', '/poker/getting-started/',
                 '/poker/start-here/', '/poker/cash-game-study-path/',
                 '/poker/first-live-tournament/'):
        if section.count('href="' + href + '"') != 1:
            issues.append('Removed original completion choice: ' + href)
    if any(mark in section for mark in ('guaranteed', 'solver-approved',
                                       'YouTube video is published', chr(0x2014))):
        issues.append('Unsupported solver, video or success assertion')
    return issues


class Turn79CompletionToTenBB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.public = PUBLIC.read_text(encoding='utf-8')
        cls.tenbb = SHORT.read_text(encoding='utf-8')

    def test_source_public_completion_menu_same_single_version(self):
        self.assertEqual(defects(self.source), [])
        self.assertEqual(defects(self.public), [])
        self.assertEqual(course_finish(self.source), course_finish(self.public))
        self.assertEqual(self.public.count('href="' + ROUTE + '"'), 1)

    def test_next_step_is_optional_after_completed_six_stages(self):
        for html in (self.source, self.public):
            self.assertLess(html.index('id="beginner-practice"') if 'id="beginner-practice"' in html
                            else html.index('id="course-finish"'),
                            html.index('href="' + ROUTE + '"'))
            self.assertIn('There is no certificate or required purchase.', html)
            self.assertIn('explain one complete hand at the beginner checkpoint', html)
            self.assertNotIn('Get a guaranteed return', course_finish(html))

    def test_real_destination_is_a_standalone_educational_guide(self):
        self.assertIn('id="six-checks"', self.tenbb)
        self.assertEqual(self.tenbb.count('id="six-checks"'), 1)
        self.assertIn('No video is required.', self.tenbb)
        self.assertIn('href="/downloads/ten-bb-tournament-checklist.md"', self.tenbb)
        self.assertTrue((ROOT / 'downloads/ten-bb-tournament-checklist.md').is_file())
        self.assertTrue((ROOT / 'downloads/ten-bb-playbook-icm-verify.py').is_file())

    def test_publication_meta_dates_and_canonicals_remain_original(self):
        pages = json.loads((ROOT / '_source/pages.json').read_text(encoding='utf-8'))
        course = next(p for p in pages if p['path'] == '/poker/free-poker-learning-path/')
        self.assertEqual((course['date'], course['updated']), ('2026-10-08', '2026-10-16'))
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/free-poker-learning-path/">',
                      self.public)
        self.assertIn('"datePublished": "2026-10-08"', self.public)
        self.assertIn('"dateModified": "2026-10-16"', self.public)
        self.assertIn('About 50 min read', self.public)

    def test_builder_still_owns_generated_output(self):
        import build
        self.assertEqual(
            build.build_outputs()[Path('poker/free-poker-learning-path/index.html')],
            self.public)

    def test_course_is_required_by_the_priority_live_byte_audit(self):
        import diagnose_live_crawl
        self.assertIn('/poker/free-poker-learning-path/', diagnose_live_crawl.PRIORITY)
        self.assertIn('/poker/10bb/', diagnose_live_crawl.PRIORITY)

    def test_mobile_offline_contract_now_includes_free_course(self):
        browser = (ROOT / '_tests/visibility_core_journeys_browser.py').read_text(
            encoding='utf-8')
        self.assertIn("ROUTES = ('/', '/start-here/', '/technology/', '/books/', '/poker/free-poker-learning-path/', '/poker/10bb/')",
                      browser)
        self.assertIn('WIDTHS = (320, 390, 768, 1440)', browser)
        self.assertIn("assert 'href=\"/poker/10bb/#six-checks\"' in beginner", browser)
        self.assertIn("assert 'id=\"six-checks\"' in playbook", browser)
        self.assertIn("java_script_enabled=False", browser)

    def test_adversarial_missing_or_false_link_is_caught(self):
        original = course_finish(self.source)
        altered = (
            original.replace(ROUTE, '/poker/10bb/#unpublished-lesson', 1),
            original.replace('not a solver recommendation for a real hand',
                             'a solver-approved real-money play', 1),
            original.replace('fictional stacks and payouts', 'verified tournament winnings', 1),
            original.replace('</li></ul>', '</li><li>Duplicate.</li></ul>', 1),
            original + original,
        )
        for case in altered:
            with self.subTest(probe=case[:68]):
                self.assertTrue(defects(self.source.replace(original, case, 1)))

    def test_manual_release_registration_no_actions(self):
        runner = (ROOT / '_scripts/local_release_checks.py').read_text(
            encoding='utf-8')
        self.assertIn('test_turn79_course_to_tenbb.py', runner)
        actions = ROOT / '.github/workflows'
        self.assertFalse(actions.exists() and any(
            x.is_file() and x.suffix.lower() in ('.yaml', '.yml')
            for x in actions.iterdir()
        ))


if __name__ == '__main__':
    unittest.main()
