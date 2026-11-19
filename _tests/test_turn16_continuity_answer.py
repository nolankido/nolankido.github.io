"""Turn 16: answer-first continuity evidence, reusable log and native routes."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import check_live
ROUTE = "/technology/ai-book-continuity-checker/"
URL = "https://nolankido.com" + ROUTE
LOG = "/downloads/book-continuity-editorial-review-log.md"
CHECK = "continuity-decision"
REFERENCE = "947e9c3d7dbc9bfa719579ca1e697d4479567684"


class PageLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))


def decision_section(html):
    match = html.split('<section class="section folio-row" aria-labelledby="continuity-decision">', 1)
    return match[1].split("</section>", 1)[0] if len(match) == 2 else ""


def claim_errors(html):
    section = decision_section(html)
    if not section:
        return ["missing author answer and review section"]
    errors = []
    links = PageLinks(section).hrefs
    for path in (
        LOG,
        "#continuity-results",
        f"https://github.com/nolankido/canonKeeper/blob/{REFERENCE}/README.md#what-it-found-in-sherlock-holmes",
        f"https://github.com/nolankido/canonKeeper/blob/{REFERENCE}/evals/results/holmes-seed0-2026-10-27/result.md",
    ):
        if links.count(path) != 1:
            errors.append("source or practical route missing: " + path)
    for marker in (
        "<strong>Short answer:</strong>",
        "not an automatic instruction",
        "keep both exact passages",
        "disguised eye description",
        "maiden-name example",
        "8 of 12 missed plants",
        "4 during judgment",
        "20 deliberately planted changes",
        "8 found, 12 missed, 2 false positives",
        "no new model run took place",
        "Some planted changes were themselves ambiguous",
        "not a manuscript uploader or a model evaluation",
    ):
        if marker not in section:
            errors.append("scope or answer condition missing: " + marker)
    if "\u2014" in section:
        errors.append("em dash in new section")
    return errors


class ContinuityAnswerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/technology/ai-book-continuity-checker.html").read_text()
        cls.public = (ROOT / "technology/ai-book-continuity-checker/index.html").read_text()
        cls.technology = (ROOT / "_source/technology/home.html").read_text()
        cls.creative = (ROOT / "_source/creative/home.html").read_text()
        cls.worksheet = (ROOT / LOG.lstrip("/")).read_text()

    def test_direct_question_first_and_human_decision_log(self):
        for html in (self.source, self.public):
            with self.subTest(public=html is self.public):
                self.assertEqual(claim_errors(html), [])
                self.assertIn('id="continuity-task">Can AI find continuity errors in a book series?', html)
                self.assertIn("<strong>Yes, but not reliably enough to skip an editor.</strong>", html)
                self.assertIn('href="#continuity-decision"', html)
                self.assertLess(html.find('id="continuity-example"'), html.find('id="continuity-decision"'))
                self.assertLess(html.find('id="continuity-decision"'), html.find('id="continuity-method"'))
                ids = PageLinks(html).ids
                for stable in ("continuity-example", "continuity-method", "continuity-results", "continuity-try", CHECK):
                    self.assertEqual(ids.count(stable), 1, stable)
        for hub in (self.technology, (ROOT / "technology/index.html").read_text(),
                    self.creative, (ROOT / "creative/index.html").read_text()):
            self.assertIn('href="' + ROUTE + "#" + CHECK + '"', hub)

    def test_download_is_grounded_private_and_reusable(self):
        self.assertIn("## Blank editorial decision record", self.worksheet)
        self.assertIn("Exact first quote, book, chapter, edition", self.worksheet)
        self.assertIn("Supported error / Explained change / Unresolved / Unsupported flag", self.worksheet)
        self.assertIn("## Worked example A", self.worksheet)
        self.assertIn("## Worked example B", self.worksheet)
        self.assertIn("8 were counted as found and 12 as missed", self.worksheet)
        self.assertIn("Some planted cases were ambiguous", self.worksheet)
        self.assertIn(REFERENCE, self.worksheet)
        self.assertIn("Keep your completed copy on a system you control", self.worksheet)
        self.assertNotIn("\u2014", self.worksheet)
        self.assertEqual(check_live.targets()[LOG], (200, self.worksheet.encode("utf-8")))

    def test_original_canonical_and_publication_date_remain_stable(self):
        manifest = json.loads((ROOT / "_source/pages.json").read_text())
        case = next(page for page in manifest if page["path"] == ROUTE)
        self.assertEqual((case["date"], case["updated"]), ("2026-10-27", "2026-11-18"))
        self.assertTrue(case["evidence_article"])
        self.assertIn("8 of 20", case["description"])
        creative = next(page for page in manifest if page["path"] == "/creative/")
        self.assertEqual(creative["updated"], "2026-11-18")
        self.assertIn('<link rel="canonical" href="' + URL + '">', self.public)
        schemas = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        articles = [s for s in schemas if s.get("@type") == "Article"]
        self.assertEqual(len(articles), 1)
        self.assertEqual((articles[0]["datePublished"], articles[0]["dateModified"]), ("2026-10-27", "2026-11-18"))
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        entries = [node for node in sitemap if node.findtext("{*}loc") == URL]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].findtext("{*}lastmod"), "2026-11-18")

    def test_negative_controls_reject_overclaim_and_link_drift(self):
        broken = (
            self.source.replace("8 found, 12 missed, 2 false positives", "20 found, 0 missed, 0 false positives"),
            self.source.replace("8 of 12 missed plants", "0 of 12 missed plants"),
            self.source.replace("no new model run took place", "a new benchmark passed"),
            self.source.replace('href="' + LOG + '"', 'href="/downloads/missing-log.md"'),
            self.source.replace("not an automatic instruction", "an automatic instruction"),
        )
        for altered in broken:
            with self.subTest(changed=altered != self.source):
                self.assertNotEqual(altered, self.source)
                self.assertTrue(claim_errors(altered))


if __name__ == "__main__":
    unittest.main()
