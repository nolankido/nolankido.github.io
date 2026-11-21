"""Turn 41: verify editorial opportunity ranking and the first-live reader path.

No network queries, simulated search-volume data, or GitHub Actions.
"""
from pathlib import Path
import csv
import json
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "_reports/visibility-sprint/seo-geo-turn41-priority-ledger-2026-11-20.csv"
SOURCE = ROOT / "_source/poker/first-live-tournament.html"
PUBLISHED = ROOT / "poker/first-live-tournament/index.html"
PATH = "/poker/first-live-tournament/"
PREREQS = ("/poker/holdem-basics/", "/poker/hand-rankings/")


def ledger():
    with LEDGER.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        columns = list(reader.fieldnames or [])
    return columns, rows


def target_html(path):
    return ROOT / path.lstrip("/") / "index.html"


class Turn41OpportunityTests(unittest.TestCase):
    def test_priority_rows_are_bounded_and_editorial_not_keyword_claims(self):
        fields, rows = ledger()
        self.assertEqual(fields, [
            "editorial_rank", "cluster", "canonical_path", "public_evidence",
            "current_gap_or_limit", "next_verified_action",
            "future_measurement_gate", "gsc_web_impressions",
            "assistant_citation_count"])
        self.assertEqual(len(rows), 12)
        self.assertEqual([int(row["editorial_rank"]) for row in rows], list(range(1, 13)))
        self.assertEqual(len({row["cluster"] for row in rows}), len(rows))
        self.assertEqual(len({row["canonical_path"] for row in rows}), len(rows))
        for row in rows:
            self.assertEqual(row["gsc_web_impressions"], "unavailable")
            self.assertEqual(row["assistant_citation_count"], "unavailable")
            self.assertTrue(all(row[key].strip() for key in fields))
            self.assertTrue(row["canonical_path"].startswith("/"))
            self.assertTrue(row["canonical_path"].endswith("/"))

    def test_all_ranked_canons_are_existing_published_html_and_sitemap_routes(self):
        _, rows = ledger()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = ElementTree.parse(ROOT / "sitemap.xml").getroot()
        found = [x.text for x in root.findall("sm:url/sm:loc", ns)]
        self.assertEqual(len(found), len(set(found)))
        for row in rows:
            url = "https://nolankido.com" + row["canonical_path"]
            with self.subTest(url=url):
                self.assertEqual(found.count(url), 1)
                page = target_html(row["canonical_path"])
                self.assertTrue(page.is_file())
                self.assertEqual(page.read_text(encoding="utf-8").count(
                    '<link rel="canonical" href="' + url + '">'), 1)

    def test_first_live_contains_exactly_two_relevant_prerequisite_links(self):
        source = SOURCE.read_text(encoding="utf-8")
        public = PUBLISHED.read_text(encoding="utf-8")
        anchor = "<p>For the whole beginner route,"
        for page in (source, public):
            self.assertEqual(page.count(anchor), 1)
            section = page.split(anchor, 1)[1].split("</p>", 1)[0]
            self.assertIn('href="/poker/getting-started/"', section)
            for route in PREREQS:
                self.assertEqual(section.count('href="' + route + '"'), 1)
                self.assertTrue(target_html(route).is_file())
            self.assertIn("before attending", section)
            self.assertIn("not aids to consult during a live hand", section)
        self.assertEqual(
            source.split(anchor, 1)[1].split("</p>", 1)[0],
            public.split(anchor, 1)[1].split("</p>", 1)[0])

    def test_prerequisite_link_edit_does_not_reset_original_article_dates(self):
        pages = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        match = [p for p in pages if p["path"] == PATH]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["date"], "2026-10-08")
        self.assertEqual(match[0]["updated"], "2026-10-27")
        public = PUBLISHED.read_text(encoding="utf-8")
        self.assertIn('"datePublished": "2026-10-08"', public)
        self.assertIn('"dateModified": "2026-10-27"', public)
        self.assertIn('href="https://nolankido.com' + PATH + '"', public)
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("https://www.pokertda.com/view-poker-tda-rules/", source)
        self.assertIn("Examples are fictional", source)

    def test_ledger_reflects_specific_executed_change_not_search_impressions(self):
        _, rows = ledger()
        self.assertEqual(rows[0]["canonical_path"], "/technology/checking-ai-website-changes/")
        event = next(r for r in rows if r["cluster"] == "first_live_poker")
        self.assertEqual(int(event["editorial_rank"]), 5)
        self.assertIn("Added one contextual primer link", event["next_verified_action"])
        self.assertTrue(all("0%" not in row["next_verified_action"] for row in rows))
        text = LEDGER.read_text(encoding="utf-8")
        self.assertNotIn("—", text)

    def test_no_paid_workflows_and_turn_41_release_coverage(self):
        workflow = ROOT / ".github/workflows"
        self.assertFalse(any(p.suffix in (".yml", ".yaml")
                             for p in workflow.glob("*") if p.is_file()))
        release = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn41_evidence_opportunities.py", release)


if __name__ == "__main__":
    unittest.main()
