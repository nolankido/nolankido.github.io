"""Turn 132: case readers can inspect the author without inflating case evidence."""

import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


AUTHOR_ROUTE = "/about/#about-evidence-title"
CASES = {
    "local-ai-review-replies": (
        "reply-sources", "saved time or helped real customers", "2026-10-27"
    ),
    "ai-book-continuity-checker": (
        "continuity-sources", "Preflight's accuracy, author time savings, or paying customers", "2026-10-27"
    ),
    "ai-poker-video-evidence": (
        "poker-ai-reuse", "does not certify a current video cut", "2026-11-04"
    ),
}


def author_context(html: str) -> str:
    matches = re.findall(
        r'<p class="small-copy"><strong>About the author:</strong>(.*?)</p>', html, re.S
    )
    return matches[0] if len(matches) == 1 else ""


def context_errors(html: str, section: str, limit: str) -> list[str]:
    errors = []
    block_marker = '<p class="small-copy"><strong>About the author:</strong>'
    if html.count(block_marker) != 1:
        errors.append("duplicated or missing author context paragraph")
    block = author_context(html)
    if not block:
        return ["one visible author context paragraph required"]
    if block.count('href="' + AUTHOR_ROUTE + '"') != 1 or block.count("<a ") != 1:
        errors.append("missing, misdirected or duplicated author evidence link")
    if "Nolan Kido" not in block or limit not in block:
        errors.append("author identity or case-specific evidence limit missing")
    if 'target="_blank"' in block or "\u2014" in block:
        errors.append("unexpected new tab or prohibited dash")
    section_start = html.find('aria-labelledby="' + section + '"')
    start = html.find(block_marker)
    section_end = html.find("</section>", section_start) if section_start >= 0 else -1
    if not (0 <= section_start < start < section_end):
        errors.append("author context does not belong to its case conclusion")
    if html.find('class="editorial-note"', section_start, start) < 0:
        errors.append("author context no longer follows source limitations")
    return errors


class CaseAuthorContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.about_source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        cls.about_public = (ROOT / "about/index.html").read_text(encoding="utf-8")

    def test_three_source_and_published_cases_offer_a_bounded_author_route(self):
        for slug, (section, limit, _) in CASES.items():
            source = (ROOT / "_source/technology" / (slug + ".html")).read_text(encoding="utf-8")
            public = (ROOT / "technology" / slug / "index.html").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                self.assertEqual(context_errors(source, section, limit), [])
                self.assertEqual(context_errors(public, section, limit), [])
                self.assertIn(source, public)

    def test_about_evidence_anchor_exists_and_already_links_to_all_cases(self):
        for about in (self.about_source, self.about_public):
            self.assertEqual(about.count('id="about-evidence-title"'), 1)
            for slug in CASES:
                with self.subTest(slug=slug):
                    self.assertIn('href="/technology/' + slug + '/"', about)

    def test_only_navigation_changes_and_freshness_dates_stay_put(self):
        expected = build.build_outputs()
        manifest = {row["path"]: row for row in json.loads((ROOT / "_source/pages.json").read_text())}
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        dates = {row.findtext("{*}loc"): row.findtext("{*}lastmod") for row in sitemap}
        for slug, (_, _, lastmod) in CASES.items():
            relative = Path("technology") / slug / "index.html"
            url = "https://nolankido.com/technology/" + slug + "/"
            page = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                self.assertEqual(expected[relative], page)
                self.assertEqual(manifest["/technology/" + slug + "/"].get("updated", manifest["/technology/" + slug + "/"]["date"]), lastmod)
                self.assertEqual(dates[url], lastmod)
                self.assertIn('rel="canonical" href="' + url + '"', page)

    def test_broken_destinations_duplicates_and_inflated_claims_fail(self):
        for slug, (section, limit, _) in CASES.items():
            source = (ROOT / "_source/technology" / (slug + ".html")).read_text(encoding="utf-8")
            marker = '<p class="small-copy"><strong>About the author:</strong>'
            variants = (
                source.replace(AUTHOR_ROUTE, "/about/#not-a-real-heading", 1),
                source.replace(marker, marker + marker, 1),
                source.replace(limit, "independently proven business impact", 1),
                source.replace('class="editorial-note"', 'class="unlabeled-note"', 1),
            )
            for n, bad in enumerate(variants):
                with self.subTest(slug=slug, variant=n):
                    self.assertTrue(context_errors(bad, section, limit))


if __name__ == "__main__":
    unittest.main()
