"""Turn 15: one answer-first AI website case with inspectable release evidence."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = "/technology/ai-website-visibility/"
URL = "https://nolankido.com" + ROUTE
SECTION_ID = "site-visibility-recent-release"


class Markup(HTMLParser):
    def __init__(self, html: str):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))


def release_section(html: str) -> str:
    sections = html.split(f'<section class="section folio-row" id="{SECTION_ID}"', 1)
    if len(sections) < 2:
        return ""
    return sections[1].split("</section>", 1)[0]


def release_errors(html: str) -> list[str]:
    section = release_section(html)
    if not section:
        return ["missing direct-answer release section"]
    errors = []
    anchors = Markup(section).links
    required_links = (
        "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=edNSD5BjIV8&format=json",
        "/downloads/reserve-day1-public-source-ledger.json",
        "/poker/#watch",
        "/poker/nolan-kido/#player-vlog-title",
        "/poker/episodes/reserve-day-1/",
        "/poker/episodes/reserve-day-1/#reserve-pots",
        "https://github.com/nolankido/nolankido.github.io/pull/386/files",
        "https://github.com/nolankido/nolankido.github.io/blob/main/_scripts/check_reserve_video_listing.py",
        "https://github.com/nolankido/nolankido.github.io/blob/main/_reports/visibility-sprint/seo-geo-turn14-reserve-video-listing-2026-11-18.md",
        "#free-visibility-check",
        "#ai-answer-visibility-check",
    )
    for link in required_links:
        if anchors.count(link) != 1:
            errors.append("missing or repeated public evidence link: " + link)
    for boundary in (
        "<strong>Short answer:</strong>",
        "four separate steps",
        "not a claimed SEO win",
        "Neither metadata nor an illustration verifies",
        "Synthetic negative controls reject",
        "253 files without drift",
        "225 sitemap URLs",
        "230 HTML pages",
        "16,240 internal links",
        "five destinations",
        "not permanent uptime",
        "not an arbitrary older checkout",
        "<strong>No.</strong>",
        "unavailable</strong>, not zero",
        "was not independently reviewed from a complete transcript",
    ):
        if boundary not in section:
            errors.append("missing verification boundary: " + boundary)
    if "\u2014" in section:
        errors.append("em dash in published case")
    return errors


class AIAssistedWebsiteReleaseAnswerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article_source = (ROOT / "_source/technology/ai-website-visibility.html").read_text()
        cls.article_public = (ROOT / "technology/ai-website-visibility/index.html").read_text()
        cls.hub_source = (ROOT / "_source/technology/home.html").read_text()
        cls.hub_public = (ROOT / "technology/index.html").read_text()

    def test_direct_answer_and_sources_survive_generation(self):
        for html in (self.article_source, self.article_public):
            with self.subTest(generated=html is self.article_public):
                self.assertEqual(release_errors(html), [])
                ids = Markup(html).ids
                self.assertEqual(ids.count(SECTION_ID), 1)
                self.assertEqual(ids.count(SECTION_ID + "-title"), 1)
                self.assertEqual(ids.count(SECTION_ID + "-example"), 1)
                self.assertEqual(ids.count(SECTION_ID + "-outcomes"), 1)
                self.assertLess(html.find(f'id="{SECTION_ID}"'), html.find('id="site-visibility-evidence"'))
                self.assertIn('href="#' + SECTION_ID + '"', html)
        for hub in (self.hub_source, self.hub_public):
            self.assertIn('href="' + ROUTE + "#" + SECTION_ID + '"', hub)
            self.assertIn("Search growth and AI citations remain unmeasured", hub)

    def test_release_claims_match_public_ledger_and_keep_old_publication(self):
        ledger = json.loads((ROOT / "downloads/reserve-day1-public-source-ledger.json").read_text())
        video = ledger["video"]
        self.assertEqual(video["public_title_checked_on"], "2026-11-18")
        self.assertIn(video["public_title"], self.article_source)
        self.assertFalse(video["current_youtube_cut_compared_with_archive"])

        manifest = json.loads((ROOT / "_source/pages.json").read_text())
        pages = [page for page in manifest if page["path"] == ROUTE]
        self.assertEqual(len(pages), 1)
        self.assertEqual((pages[0]["date"], pages[0]["updated"]), ("2026-11-03", "2026-11-18"))
        self.assertTrue(pages[0]["evidence_article"])
        self.assertIn("live files", pages[0]["description"])

        public = self.article_public
        self.assertIn('rel="canonical" href="' + URL + '"', public)
        schemas = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', public, re.S)]
        articles = [schema for schema in schemas if schema.get("@type") == "Article"]
        self.assertEqual(len(articles), 1)
        self.assertEqual((articles[0]["datePublished"], articles[0]["dateModified"]), ("2026-11-03", "2026-11-18"))

        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        entries = [node for node in sitemap if node.findtext("{*}loc") == URL]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].findtext("{*}lastmod"), "2026-11-18")

    def test_missing_evidence_and_inflated_claims_fail_closed(self):
        source = self.article_source
        examples = (
            source.replace("/pull/386/files", "/pull/999/files", 1),
            source.replace("253 files without drift", "500 files without drift", 1),
            source.replace("not a claimed SEO win", "a measured SEO win", 1),
            source.replace("<strong>No.</strong>", "<strong>Yes.</strong>", 1),
            source.replace("unavailable</strong>, not zero", "zero</strong>, not unavailable", 1),
            source.replace('href="#ai-answer-visibility-check">separate AI-answer citation sample', 'href="#unsupported-citations">separate AI-answer citation sample', 1),
        )
        for changed in examples:
            with self.subTest(change=changed != source):
                self.assertNotEqual(changed, source)
                self.assertTrue(release_errors(changed))


if __name__ == "__main__":
    unittest.main()
