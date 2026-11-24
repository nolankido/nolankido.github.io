"""Turn 67: the 10 BB Playbook must work as a standalone written guide.

The page cannot claim a verified public video, exact synchronized chapter
times or a playable upload when no such specific URL is confirmed in source.
This is a local, read-only regression for source and published HTML.
"""
from html import escape
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import player_find
import search_sections
import tenbb_companion


def lesson_issues(page):
    """Return observable defects; use the same checks on deliberate bad copies."""
    issues = []
    if page.count('href="https://www.youtube.com/@NolanPoker"') < 1:
        issues.append("missing honest channel path")
    if "matching public NolanPoker course-video URL and synchronized chapter times have not been verified" not in page:
        issues.append("missing video availability boundary")
    if "No video is required." not in page:
        issues.append("missing standalone reading promise")
    if re.search(r"\bVideo [0-9]{2}:[0-9]{2}\b", page) or "Select the matching point in the YouTube player" in page:
        issues.append("unverified video timecodes")
    chapter = re.search(r'<section id="chapter-map"\b.*?</section>', page, re.S)
    if not chapter:
        issues.append("missing lesson map")
        return issues
    links = re.findall(r'<li><a href="#([a-z0-9-]+)">[^<]+</a></li>', chapter.group())
    expected = ["six-checks", "first-in", "facing-action", "postflop",
                "icm", "icm-reproduce", "practice", "sources"]
    if links != expected:
        issues.append("wrong lesson links")
    for anchor in expected:
        if page.count('id="' + anchor + '"') != 1:
            issues.append("missing or duplicate section " + anchor)
    for key in ("q1", "q2", "q3", "q4", "q5", "q6"):
        if page.count('id="' + key + '"') != 1:
            issues.append("question missing or duplicated " + key)
    return issues


class Turn67WrittenPlaybook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / tenbb_companion.OUTPUT).read_text(encoding="utf-8")
        cls.find = (ROOT / "find/index.html").read_text(encoding="utf-8")
        cls.entry = player_find.tenbb_entry(ROOT)

    def test_standalone_lesson_links_and_six_answered_questions(self):
        self.assertEqual(lesson_issues(self.page), [])
        self.assertEqual(self.page.count('<section class="tenbb-question" id="q'), 6)
        for number in range(1, 7):
            match = re.search(r'<section class="tenbb-question" id="q' + str(number) +
                              r'"[^>]*>.*?</section>', self.page, re.S)
            self.assertIsNotNone(match)
            self.assertIn("<details>", match.group())
            self.assertIn("<summary>Show answer and reasoning</summary>", match.group())
        self.assertNotIn("one-hour tournament course", self.page)
        self.assertNotIn("Find the lesson in the video", self.page)
        self.assertIn("same three-player ICM fixture with different assumed win chances", self.page)
        self.assertNotRegex(self.page, r'\b[0-9]:[0-9]{2}:[0-9]{2}\b')
        self.assertNotIn(chr(0x2014), self.page)

    def test_real_article_identity_and_accurate_revision_provenance(self):
        self.assertEqual(self.page.count('<link rel="canonical" href="https://nolankido.com/poker/10bb/">'), 1)
        self.assertEqual(self.page.count('<h1 class="page-title">The 10 Big Blind Tournament Playbook</h1>'), 1)
        self.assertIn('<meta property="article:published_time" content="2026-11-19">', self.page)
        self.assertIn('<meta property="article:modified_time" content="2026-11-21">', self.page)
        self.assertIn('Updated <time datetime="2026-11-21">November 21, 2026</time>', self.page)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.page, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema["datePublished"], "2026-11-19")
        self.assertEqual(schema["dateModified"], "2026-11-21")
        self.assertEqual(schema["url"], "https://nolankido.com/poker/10bb/")
        self.assertEqual(schema["author"]["@id"], "https://nolankido.com/about/#nolan-kido")
        self.assertEqual(schema["description"], self.entry["description"])
        self.assertIn("Written Poker Study Guide", self.entry["search_title"])

    def test_local_find_result_and_section_index_are_consistent(self):
        self.assertEqual(self.entry["kind"], "guide")
        self.assertEqual(self.entry["path"], "/poker/10bb/")
        self.assertEqual(self.entry["home"], "poker")
        self.assertEqual(self.find.count('href="/poker/10bb/"'), 1)
        cards = [match.group() for match in re.finditer(
            r'<li class="find-item"[^>]*>.*?</li>', self.find, re.S)
            if 'href="/poker/10bb/"' in match.group()]
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertIn('data-kind="guide"', card)
        self.assertIn(escape(self.entry["description"], quote=True), card)
        self.assertNotIn("Video companion", card)
        headings = search_sections.headings(self.page)
        self.assertEqual(len(headings), 8)
        self.assertIn(["chapter-map-title", "Choose a written lesson"], headings)
        data = json.loads(re.search(
            r'<script type="application/json" id="find-section-data">(.*?)</script>',
            self.find, re.S).group(1))
        flat = data["pages"]["poker"]["10bb/"]
        decoded = [[flat[i], data["labels"][flat[i + 1]] if type(flat[i + 1]) is int
                    else flat[i + 1]] for i in range(0, len(flat), 2)]
        self.assertEqual(decoded, headings)

    def test_sitemap_still_registers_single_published_page_and_verifier(self):
        approval = tenbb_companion.record(ROOT)
        self.assertEqual(approval["lastmod"], "2026-11-21")
        locs = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        matches = [node for node in locs if node.findtext("{*}loc") == approval["url"]]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext("{*}lastmod"), "2026-11-21")
        self.assertEqual(len(list(locs)), 231)
        self.assertIn('href="/' + tenbb_companion.CODE + '"', self.page)

    def test_missing_disclaimer_false_video_claim_and_broken_anchor_fail(self):
        bad_versions = [
            self.page.replace("No video is required.", "Watch the complete course now.", 1),
            self.page.replace('<li><a href="#practice">Six answered questions</a></li>',
                              '<li><a href="#missing-lesson">Six answered questions</a></li>', 1),
            self.page.replace('id="icm-reproduce"', 'id="unknown"', 1),
            self.page.replace("matching public NolanPoker course-video URL and synchronized chapter times have not been verified", "The complete video is published", 1),
            self.page.replace('id="practice"', 'id="icm"', 1),
        ]
        for index, tampered in enumerate(bad_versions):
            with self.subTest(mutation=index):
                self.assertNotEqual(tampered, self.page)
                self.assertTrue(lesson_issues(tampered))

    def test_local_runner_does_not_add_ci_or_paid_checking(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn67_playbook_standalone.py", runner)
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(
            x.is_file() and x.suffix.lower() in (".yaml", ".yml") for x in folder.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
