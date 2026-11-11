"""Keep the two website cases connected without merging their release claims."""

import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
VISIBILITY = "/technology/ai-website-visibility/"
VERIFICATION = "/technology/checking-ai-website-changes/"


def paragraph(text: str, start: str) -> str:
    matches = re.findall(r"<p><strong>" + re.escape(start) + r"</strong>(.*?)</p>", text, re.S)
    return matches[0] if len(matches) == 1 else ""


def connection_errors(visibility: str, verification: str) -> list[str]:
    errors = []
    from_visibility = paragraph(visibility, "A separate release-checking lesson:")
    from_verification = paragraph(verification, "Release quality is not a search outcome.")
    if not from_visibility:
        errors.append("visibility case lacks its one contextual comparison")
    if not from_verification:
        errors.append("verification case lacks its one contextual comparison")

    if from_visibility.count('href="' + VERIFICATION + '"') != 1:
        errors.append("visibility case must link exactly once to the verification case")
    if from_verification.count('href="' + VISIBILITY + '"') != 1:
        errors.append("verification case must link exactly once to the visibility case")

    for detail in ("October 11", "347 tests", "HTML5 parser", "not evidence", "search rankings"):
        if detail not in from_visibility:
            errors.append("missing historical comparison boundary: " + detail)
    for detail in ("later public site changes", "Search Console", "without calling publication a ranking gain", "does not retroactively measure", "October 11"):
        if detail not in from_verification:
            errors.append("missing search measurement boundary: " + detail)

    if from_visibility.count("href=") != 1 or from_verification.count("href=") != 1:
        errors.append("the contextual comparison gained extra links")
    return errors


class WebsiteCaseLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.visibility_source = (ROOT / "_source/technology/ai-website-visibility.html").read_text()
        cls.verification_source = (ROOT / "_source/technology/checking-ai-website-changes.html").read_text()
        cls.visibility_public = (ROOT / "technology/ai-website-visibility/index.html").read_text()
        cls.verification_public = (ROOT / "technology/checking-ai-website-changes/index.html").read_text()

    def test_each_generated_case_has_a_crawlable_contextual_return_route(self):
        for left, right in ((self.visibility_source, self.verification_source),
                            (self.visibility_public, self.verification_public)):
            with self.subTest(generated=left is self.visibility_public):
                self.assertEqual(connection_errors(left, right), [])
        self.assertTrue((ROOT / VERIFICATION.lstrip("/") / "index.html").is_file())
        self.assertTrue((ROOT / VISIBILITY.lstrip("/") / "index.html").is_file())

    def test_comparison_is_a_minor_navigation_revision_not_a_new_case_date(self):
        records = json.loads((ROOT / "_source/pages.json").read_text())
        pages = {page["path"]: page for page in records}
        self.assertEqual((pages[VISIBILITY]["date"], pages[VISIBILITY]["updated"]),
                         ("2026-11-03", "2026-11-06"))
        self.assertEqual(pages[VERIFICATION]["date"], "2026-10-11")
        self.assertNotIn("updated", pages[VERIFICATION])

        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        modified = {entry.findtext("{*}loc"): entry.findtext("{*}lastmod") for entry in sitemap}
        self.assertEqual(modified["https://nolankido.com" + VISIBILITY], "2026-11-06")
        self.assertEqual(modified["https://nolankido.com" + VERIFICATION], "2026-10-11")
        for page, public in ((pages[VISIBILITY], self.visibility_public),
                             (pages[VERIFICATION], self.verification_public)):
            schema = [json.loads(t) for t in re.findall(r'<script type="application/ld\+json">(.*?)</script>', public, re.S)]
            articles = [item for item in schema if item.get("@type") == "Article"]
            self.assertEqual(len(articles), 1)
            self.assertEqual(articles[0]["datePublished"], page["date"])
            self.assertEqual(articles[0].get("dateModified"), page.get("updated"))

    def test_regressions_fail_if_the_reader_path_or_evidence_limits_break(self):
        mutations = (
            (self.visibility_source.replace('href="' + VERIFICATION + '"', 'href="/technology/"', 1), self.verification_source),
            (self.visibility_source.replace("not evidence", "proof", 1), self.verification_source),
            (self.visibility_source, self.verification_source.replace("does not retroactively measure", "measures", 1)),
            (self.visibility_source, self.verification_source.replace('href="' + VISIBILITY + '"', 'href="/about/"', 1)),
        )
        for index, (left, right) in enumerate(mutations):
            with self.subTest(which=index):
                self.assertTrue(connection_errors(left, right))


if __name__ == "__main__":
    unittest.main()
