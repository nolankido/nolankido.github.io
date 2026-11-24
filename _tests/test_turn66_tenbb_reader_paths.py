"""Turn 66: source-backed reader routes into the published 10 BB Playbook.

These tests keep navigation useful without presenting different fictional
bubble/ICM models as one solver recommendation. No network or account data.
"""
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import poker_library
import tenbb_companion

HOME_SOURCE = Path("_source/poker/home.html")
HOME_PUBLIC = Path("poker/index.html")
GUIDE_SOURCE = Path("_source/poker/six-to-ten-bb-tournament-decisions.html")
GUIDE_PUBLIC = Path("poker/six-to-ten-bb-tournament-decisions/index.html")
PRACTICE_LINK = '/poker/10bb/#practice-title'
ICM_LINK = '/poker/10bb/#icm-title'


def paragraph(html: str, kind: str) -> str:
    if kind == "home":
        pattern = r'<p class="poker-entry-note poker-stack-route">.*?</p>'
    else:
        pattern = r'<p class="poker-entry-note"><strong>About 10 BB near the money\?</strong>.*?</p>'
    items = re.findall(pattern, html, re.S)
    if len(items) != 1:
        raise ValueError("Expected exactly one existing short-stack route paragraph")
    return items[0]


class Turn66TenBBReaderPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home_source = (ROOT / HOME_SOURCE).read_text(encoding="utf-8")
        cls.home_public = (ROOT / HOME_PUBLIC).read_text(encoding="utf-8")
        cls.guide_source = (ROOT / GUIDE_SOURCE).read_text(encoding="utf-8")
        cls.guide_public = (ROOT / GUIDE_PUBLIC).read_text(encoding="utf-8")
        cls.playbook = (ROOT / tenbb_companion.OUTPUT).read_text(encoding="utf-8")
        cls.pages = build.public_pages()

    def test_one_practice_route_from_poker_home_with_exact_source_parity(self):
        start = paragraph(self.home_source, "home")
        released = paragraph(self.home_public, "home")
        self.assertEqual(start, released)
        self.assertEqual(start.count('href="' + PRACTICE_LINK + '"'), 1)
        self.assertIn('10 BB Playbook', start)
        self.assertIn('six more after-play questions', start)
        self.assertEqual(self.home_source.count('href="' + PRACTICE_LINK + '"'), 1)
        self.assertEqual(self.home_public.count('href="' + PRACTICE_LINK + '"'), 1)
        self.assertIn('href="/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble"', start)
        self.assertNotIn('href="' + ICM_LINK + '"', start)

    def test_one_model_distinction_route_from_six_to_ten_guide(self):
        start = paragraph(self.guide_source, "guide")
        released = paragraph(self.guide_public, "guide")
        self.assertEqual(start, released)
        self.assertEqual(start.count('href="' + ICM_LINK + '"'), 1)
        self.assertEqual(self.guide_source.count('href="' + ICM_LINK + '"'), 1)
        self.assertEqual(self.guide_public.count('href="' + ICM_LINK + '"'), 1)
        self.assertIn('three-player ICM example', start)
        self.assertIn('different payouts and assumptions from this four-player bubble case', start)
        self.assertIn('href="#bridge-bubble"', start)
        self.assertNotIn('href="' + PRACTICE_LINK + '"', start)

    def test_both_deep_links_resolve_only_to_real_visible_playbook_sections(self):
        self.assertEqual(tenbb_companion.record(ROOT)["route"], "/poker/10bb/")
        for link in (PRACTICE_LINK, ICM_LINK):
            anchor = link.split("#", 1)[1]
            with self.subTest(anchor=anchor):
                self.assertEqual(self.playbook.count('id="' + anchor + '"'), 1)
                self.assertRegex(self.playbook, r'<h2\s+id="' + re.escape(anchor) + r'"')
        # The answer and prize-equity sections are different, not copied advice.
        self.assertIn('three-player', self.playbook)
        self.assertIn('58.88%', self.playbook)
        self.assertIn('four-player', self.guide_source)

    def test_generated_outputs_remain_deterministic_and_reading_time_stable(self):
        generated = build.build_outputs()
        self.assertEqual(generated[HOME_PUBLIC], self.home_public)
        self.assertEqual(generated[GUIDE_PUBLIC], self.guide_public)
        self.assertEqual(poker_library.minutes(self.guide_source), 24)

    def test_no_sitemap_or_publication_date_manipulation(self):
        pages = {p["path"]: p for p in self.pages}
        for route in ('/poker/', '/poker/six-to-ten-bb-tournament-decisions/'):
            self.assertEqual(pages[route]["updated"], "2026-11-20")
        self.assertEqual(tenbb_companion.record(ROOT)["lastmod"], "2026-11-21")
        root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        locs = [e.findtext("{*}loc") for e in root]
        self.assertEqual((len(locs), len(set(locs))), (231, 231))
        self.assertEqual(locs.count("https://nolankido.com/poker/10bb/"), 1)
        for changed in (self.home_source, self.guide_source):
            self.assertNotIn(chr(0x2014), changed)

    def test_bad_or_repeated_routes_fail_static_invariant(self):
        for snippet, link in ((paragraph(self.home_source, "home"), PRACTICE_LINK),
                              (paragraph(self.guide_source, "guide"), ICM_LINK)):
            marker = 'href="' + link + '"'
            self.assertEqual(snippet.count(marker), 1)
            for edited in (snippet.replace(marker, 'href="/poker/10bb/#invented-anchor"', 1),
                           snippet.replace(marker, '', 1),
                           snippet + snippet):
                with self.subTest(link=link, modification=edited[:45]):
                    self.assertNotEqual(edited.count(marker), 1)

    def test_manual_release_runner_checks_both_routes(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn66_tenbb_reader_paths.py", runner)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in {".yaml", ".yml"} for p in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
