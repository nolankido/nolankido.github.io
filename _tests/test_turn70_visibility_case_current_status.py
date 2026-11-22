"""Turn 70: date the website visibility case without rewriting its 25-turn history.

No connected Search Console, private analytics, live API or remote test runner.
Checks source-backed reader status, available public paths and preserved caveats.
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

ROUTE = "/technology/ai-website-visibility/"
ORIGIN = "https://nolankido.com"
DATE = "2026-11-21"
FOLLOWUP = "site-visibility-followup"
TARGETS = (
    ("/sitemap.xml", None),
    ("/poker/10bb/", None),
    ("/technology/ai-workflow-pilot/", None),
    ("/technology/ai-weekly-reset/", "notes-case-sources"),
)
LEDGER = ("https://github.com/nolankido/nolankido.github.io/"
          "pull/443")


def dated_followup(html: str) -> str:
    matches = re.findall(
        r'<p class="small-copy ' + FOLLOWUP + r'">.*?</p>', html, re.S
    )
    if len(matches) != 1:
        raise ValueError("exactly one dated status paragraph is required")
    return matches[0]


def status_errors(html: str) -> list[str]:
    try:
        part = dated_followup(html)
    except ValueError:
        return ["missing or duplicated dated status"]
    errors = []
    for href, _ in TARGETS:
        if part.count('href="' + href + '"') != 1:
            errors.append("missing or duplicate original public route: " + href)
    if part.count('href="' + LEDGER + '"') != 1:
        errors.append("missing pinned publication record")
    if "November 21 follow-up:" not in part:
        errors.append("no date that qualifies the older historical count")
    if "224-to-225 URL table" not in part or "November 19" not in part:
        errors.append("historical closeout not distinguished from current site")
    if "now lists <strong>230 URLs</strong>" not in part:
        errors.append("updated technical inventory is missing")
    if "None measures indexing, Google impressions, visits, or AI citations." not in part:
        errors.append("search outcome evidence boundary has been removed")
    if any(x in part for x in ("<script", "onclick=", "utm_", chr(0x2014))):
        errors.append("unreviewed behavior or punctuation")
    return errors


class Turn70VisibilityStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/technology/ai-website-visibility.html").read_text(
            encoding="utf-8")
        cls.page = (ROOT / "technology/ai-website-visibility/index.html").read_text(
            encoding="utf-8")
        cls.manifest = json.loads((ROOT / "_source/pages.json").read_text(
            encoding="utf-8"))
        cls.sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text(
            encoding="utf-8"))

    def test_one_dated_followup_with_exact_source_public_copy(self):
        self.assertEqual(status_errors(self.source), [])
        self.assertEqual(status_errors(self.page), [])
        self.assertEqual(dated_followup(self.source), dated_followup(self.page))
        self.assertLess(
            self.page.index('class="small-copy ' + FOLLOWUP + '"'),
            self.page.index("224 listed URLs in the"),
        )

    def test_historical_closeout_remains_truthful_and_separate(self):
        for html in (self.source, self.page):
            self.assertIn("Did 25 SEO, GEO and AEO improvement turns make this site more visible?", html)
            self.assertIn("224 listed URLs in the", html)
            self.assertIn("225 after Turn 24 on November 19", html)
            self.assertIn("It did <strong>not</strong> establish higher search rankings", html)
            self.assertEqual(html.count("Not measured in this sprint."), 2)
            self.assertIn("December is the first full month afterward", html)
            self.assertEqual(html.count('id="site-visibility-sprint-outcome"'), 1)
        self.assertIn("The 25-turn evidence ledger", self.source) if "The 25-turn evidence ledger" in self.source else self.assertIn("25-turn evidence ledger", self.source)

    def test_target_routes_have_representative_published_sources(self):
        for route, anchor in TARGETS:
            path = ROOT / route.lstrip("/")
            if route.endswith("/"):
                path = path / "index.html"
            with self.subTest(route=route):
                self.assertTrue(path.is_file())
                if anchor:
                    self.assertEqual(
                        path.read_text(encoding="utf-8").count('id="' + anchor + '"'), 1
                    )
        locs = [node.findtext("{*}loc") for node in self.sitemap]
        self.assertEqual(len(locs), 230)
        self.assertEqual(len(set(locs)), 230)
        for route in ("/poker/10bb/", "/technology/ai-workflow-pilot/",
                      "/technology/ai-weekly-reset/"):
            self.assertEqual(locs.count(ORIGIN + route), 1)

    def test_public_modification_is_not_an_invented_original_publication(self):
        page = next(p for p in self.manifest if p["path"] == ROUTE)
        self.assertEqual(page["date"], "2026-11-03")
        self.assertEqual(page["updated"], DATE)
        self.assertIn("original November 19", page["revision"])
        self.assertIn('property="article:published_time" content="2026-11-03"', self.page)
        self.assertIn('property="article:modified_time" content="' + DATE + '"', self.page)
        records = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                             self.page, re.S)
        self.assertEqual(len(records), 1)
        article = json.loads(records[0])
        self.assertEqual(article["@type"], "Article")
        self.assertEqual(article["datePublished"], "2026-11-03")
        self.assertEqual(article["dateModified"], DATE)
        self.assertEqual(article["url"], ORIGIN + ROUTE)
        self.assertEqual(article["author"]["@id"], ORIGIN + "/about/#nolan-kido")
        rows = [node for node in self.sitemap
                if node.findtext("{*}loc") == ORIGIN + ROUTE]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].findtext("{*}lastmod"), DATE)

    def test_existing_reading_estimate_and_metadata_stay_in_scope(self):
        self.assertEqual(self.page.count("About 17 min read"), 1)
        self.assertEqual(self.source.count('class="small-copy ' + FOLLOWUP + '"'), 1)
        self.assertEqual(self.page.count('class="small-copy ' + FOLLOWUP + '"'), 1)
        self.assertEqual(self.page.count('<link rel="canonical" href="' +
                                         ORIGIN + ROUTE + '">'), 1)
        self.assertEqual(self.page.count('<h1 class="page-title">What AI helped change on my website.</h1>'), 1)
        self.assertNotIn("AI citation growth was measured", self.source)

    def test_builder_matches_committed_case_and_sitemap(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("technology/ai-website-visibility/index.html")],
                         self.page)
        self.assertEqual(outputs[Path("sitemap.xml")],
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

    def test_negative_mutations_fail_for_unearned_outcome_or_stale_count(self):
        original = dated_followup(self.source)
        cases = (
            original.replace("230 URLs", "225 URLs", 1),
            original.replace("November 21 follow-up:", "Latest improvement:", 1),
            original.replace(LEDGER, "https://example.invalid/", 1),
            original.replace("None measures indexing, Google impressions, visits, or AI citations.",
                             "Rankings improved thanks to these edits.", 1),
            original.replace('/poker/10bb/', '/poker/nonexistent/', 1),
            original + original,
        )
        for value in cases:
            with self.subTest(change=value[:100]):
                content = self.source.replace(original, value, 1)
                self.assertNotEqual(status_errors(content), [])

    def test_existing_manual_runner_and_no_user_authored_ci(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(
            encoding="utf-8")
        self.assertIn("test_turn70_visibility_case_current_status.py", runner)
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(
            f.is_file() and f.suffix.lower() in (".yml", ".yaml")
            for f in folder.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
