"""Turn 26: Technology visitors should see proof, an actual tool, and projects first."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import poker_reading


INTRO = '<section class="section folio-row topic-introduction"'
HEADING = "AI in real life, with the evidence visible."
CHOICES = (
    ('#identity-claim-audit', '01 / Inspect a real correction'),
    ('/technology/task-brief/', '02 / Use a free tool'),
    ('#technology-projects', '03 / Explore public projects'),
)
MORE = (
    "#technology-projects",
    "#practical-ai-path",
    "#working-examples",
    "#technology-path",
    "#technology-reading",
)


def introduction(content):
    start = content.index(INTRO)
    return content[start:content.index("</section>", start) + len("</section>")]


class Tags(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Mismatched first-screen HTML tag: " + tag)


class TechnologyFirstScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/technology/home.html").read_text(encoding="utf-8")
        cls.page = (ROOT / "technology/index.html").read_text(encoding="utf-8")
        cls.intro = introduction(cls.page)

    def test_first_screen_is_identical_to_authored_source_and_valid_html(self):
        self.assertEqual(introduction(self.source), self.intro)
        self.assertEqual(self.source.count(INTRO), 1)
        self.assertEqual(self.page.count(INTRO), 1)
        self.assertIn('<h2 class="intro" id="technology-intro-title">' + HEADING + '</h2>', self.intro)
        self.assertIn("I'm Nolan Kido.", self.intro)
        self.assertIn("AI Works, Human Decides", self.intro)
        self.assertIn("poker-video production", self.intro)
        self.assertNotIn("\u2014", self.intro)
        self.assertNotIn("<script", self.intro)
        self.assertNotIn("<iframe", self.intro)
        parsed = Tags()
        parsed.feed(self.intro)
        self.assertEqual(parsed.stack, [])

    def test_three_native_starting_choices_before_deeper_navigation(self):
        self.assertEqual(self.intro.count('class="identity-reading"'), 3)
        self.assertEqual(self.intro.count("<article"), 3)
        self.assertEqual(self.intro.count("</article>"), 3)
        self.assertIn('role="group" aria-label="Choose a starting point for practical AI"', self.intro)
        order = []
        for href, label in CHOICES:
            self.assertIn('href="' + href + '"', self.intro)
            self.assertIn(label, self.intro)
            order.append(self.intro.index('href="' + href + '"'))
        self.assertEqual(order, sorted(order))
        self.assertLess(self.intro.index('identity-readings technology-first-routes'),
                        self.intro.index('<details class="technology-more">'))
        self.assertIn("No search-ranking improvement is claimed.", self.intro)
        self.assertIn("makes no AI call", self.intro)
        self.assertIn("different evidence and limits", self.intro)

    def test_preserved_secondary_navigation_is_native_and_optional(self):
        details = re.search(r'<details class="technology-more"><summary>(.*?)</summary>(.*?)</details>', self.intro, re.S)
        self.assertIsNotNone(details)
        self.assertEqual(details.group(1), "More ways to explore this page")
        nav = re.search(r'<nav class="link-row technology-jumps".*?</nav>', details.group(2), re.S)
        self.assertIsNotNone(nav)
        self.assertIn('aria-label="On this Technology page"', nav.group(0))
        self.assertEqual(re.findall(r'href="(#[^"]+)"', nav.group(0)), list(MORE))
        self.assertNotIn("<button", nav.group(0))
        self.assertNotIn("open=", details.group(0))
        self.assertIn('href="/contact/">Talk technology</a>', self.intro)
        self.assertIn('href="#small-business-ai-pilot"', self.intro)

    def test_every_choice_targets_a_real_published_page_or_fragment(self):
        page_routes = {p["path"] for p in build.public_pages()}
        for href, _ in CHOICES:
            if href.startswith("#"):
                self.assertEqual(self.page.count('id="' + href[1:] + '"'), 1)
            else:
                self.assertIn(href, page_routes)
                page_path = ROOT / build.output_path(href)
                self.assertTrue(page_path.is_file())
        for href in MORE:
            self.assertEqual(self.page.count('id="' + href[1:] + '"'), 1)

    def test_generated_find_heading_tracks_visible_h2(self):
        html = (ROOT / "find/index.html").read_text(encoding="utf-8")
        match = re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>', html)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        rows = data["pages"]["technology"][""]
        offset = rows.index("technology-intro-title")
        self.assertEqual(rows[offset + 1], HEADING)
        self.assertEqual(rows.count("technology-intro-title"), 1)
        self.assertEqual(rows.count("identity-claim-audit-title"), 1)
        source_headings = poker_reading.VisibleHeadings(
            self.page.split("<main", 1)[1].split("</main>", 1)[0]
        ).headings
        self.assertIn(("technology-intro-title", HEADING), source_headings)

    def test_unchanged_canonical_projects_and_publication_metadata(self):
        page = self.page
        manifest = next(p for p in build.public_pages() if p["id"] == "technology")
        self.assertEqual(manifest["updated"], "2026-11-04")
        self.assertEqual(manifest["path"], "/technology/")
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/">', page)
        self.assertIn('"dateModified": "2026-11-04"', page)
        self.assertEqual(page.count('class="project-card"'), 3)
        self.assertIn('id="identity-claim-audit-title"', page)
        for route in ("/technology/local-ai-review-replies/", "/technology/ai-book-continuity-checker/",
                      "/technology/dinner-on-time/"):
            self.assertIn('href="' + route + '"', page)

    def test_all_changed_generator_owned_outputs_are_current(self):
        generated = build.build_outputs()
        for path in ("technology/index.html", "find/index.html"):
            self.assertEqual(generated[Path(path)], (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
