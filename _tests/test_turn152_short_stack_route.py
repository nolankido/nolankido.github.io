"""Turn 152: discover each published short-stack guide from the Poker reader path.

The links form a task-based route. A countable stack is not a strategy grade,
and this check does not claim to evaluate opponent ranges or ICM solutions.
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

SOURCE = ROOT / "_source/poker/home.html"
PUBLIC = ROOT / "poker/index.html"
MARKER = '<p class="poker-entry-note poker-stack-route">'
ROUTES = (
    ("/poker/three-to-five-bb-tournament-decisions/", "3–5 BB: shoves and calls"),
    ("/poker/six-to-ten-bb-tournament-decisions/", "6–10 BB: opens and rejams"),
    ("/poker/short-stack-decisions/", "10–20 BB: context and ICM"),
)

SUPPORTING = (
    ("/poker/six-to-ten-bb-tournament-decisions/#bridge-bubble",
     "Compare chip value and payout value in a worked bubble call"),
    ("/poker/10bb/#practice-title",
     "try the 10 BB Playbook's answered exercises"),
    ("/poker/evaluating-poker-advice/#solver-fit-test",
     "check whether a ten-blind solver recommendation actually fits the hand"),
)


def route_errors(content):
    errors = []
    if content.count(MARKER) != 1:
        return ["missing or repeated stack-depth navigation"]
    match = re.search(re.escape(MARKER) + r"(.*?)</p>", content, re.S)
    if not match:
        return ["unclosed navigation paragraph"]
    fragment = match.group(1)
    links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', fragment)
    if links != [*ROUTES, *SUPPORTING]:
        errors.append("stack ranges, contextual destinations or order differ from source guides")
    if "Short-stacked in a tournament?" not in fragment:
        errors.append("the intended reader context is missing")
    if "None is a universal shove chart." not in fragment:
        errors.append("a strategy limitation is missing")
    if any(token in fragment for token in ("—", "<script", "onclick=", "utm_", "youtube.com")):
        errors.append("unexpected punctuation, scripting or tracking")
    section_start = content.find('id="reading-routes"')
    section_end = content.find('id="in-depth"', section_start)
    if section_start < 0 or section_end < 0:
        errors.append("the intended Poker learning section is missing")
    else:
        paragraph = content.find(MARKER, section_start)
        if not section_start < paragraph < section_end:
            errors.append("stack guidance is not with the reader choices")
    return errors


class ShortStackNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")

    def test_sources_and_generated_page_have_one_clear_ordered_route(self):
        for html in (self.source, self.public):
            with self.subTest(rendered=html is self.public):
                self.assertEqual(route_errors(html), [])
        self.assertIn("${poker_goal_routes}", self.source)
        self.assertEqual(self.public.count('id="goal-decisions"'), 1)
        self.assertEqual(self.public.count('id="nolanpoker-deepstack"'), 1)

    def test_all_three_destinations_are_real_published_local_guides(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        routes = {p["path"] for p in pages}
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        sitemap_urls = {node.text for node in sitemap.iter() if node.tag.endswith("}loc")}
        for url, label in ROUTES:
            with self.subTest(url=url):
                self.assertIn(url, routes)
                self.assertIn("https://nolankido.com" + url, sitemap_urls)
                self.assertTrue((ROOT / url.lstrip("/") / "index.html").is_file())
                self.assertIn(label, self.public)
        poker = next(p for p in pages if p["path"] == "/poker/")
        self.assertEqual(poker["updated"], "2026-11-20")
        self.assertIn('"dateModified": "2026-11-20"', self.public)

    def test_current_poker_source_rebuilds_to_exact_committed_html(self):
        self.assertEqual(build.build_outputs()[Path("poker/index.html")], self.public)

    def test_broken_range_destination_or_claim_is_detected(self):
        mutations = (
            self.source.replace("/poker/three-to-five-bb-tournament-decisions/", "/poker/missing-guide/", 1),
            self.source.replace("6–10 BB: opens and rejams", "8–20 BB: shoves", 1),
            self.source.replace("None is a universal shove chart.", "These are guaranteed shoves.", 1),
            self.source.replace('/poker/10bb/#practice-title', '/poker/10bb/#missing-anchor', 1),
            self.source.replace(MARKER, MARKER + MARKER, 1),
        )
        for index, altered in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertTrue(route_errors(altered))


if __name__ == "__main__":
    unittest.main()
