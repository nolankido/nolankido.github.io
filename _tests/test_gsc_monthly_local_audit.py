"""Synthetic-only validation of the offline, private GSC CSV summarizer."""

from __future__ import annotations

import importlib.util
import calendar
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "downloads" / "gsc-monthly-local-audit.py"
SPEC = importlib.util.spec_from_file_location("gsc_monthly_local_audit", SCRIPT)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class GscLocalAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def csv(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_page_exports_are_section_bounded_without_sitewide_inference(self):
        pages = self.csv("Pages.csv", "\ufeffTop pages,Clicks,Impressions,CTR,Position\n"
                         "https://nolankido.com/technology/task-brief/,12,900,1.3%,8.2\n"
                         "https://nolankido.com/poker/,4,100,4%,2.2\n"
                         "https://nolankido.com/about/,3,40,7.5%,1.2\n"
                         "https://nolankido.com.evil.test/technology/,99,100,99%,1\n")
        result = audit.summarize("2026-10", pages)
        self.assertEqual(result["declared_window"], {"start": "2026-10-01", "end": "2026-10-31"})
        self.assertEqual(result["page_export"]["outside_site_rows"], 1)
        totals = result["page_export"]["observed_section_totals"]
        self.assertEqual(totals["technology"], {"clicks": 12, "impressions": 900, "visible_rows": 1})
        self.assertEqual(totals["poker"]["clicks"], 4)
        self.assertEqual(totals["other"]["clicks"], 3)
        self.assertIsNone(result["property_web_clicks"])
        self.assertIsNone(result["query_page_export"]["visible_nonbrand_technology_clicks"])
        self.assertFalse(result["export_date_range_verified"])

    def test_visible_brand_counts_are_distinct_and_can_overlap(self):
        pages = self.csv("Pages.csv", "Top pages,Clicks,Impressions\nhttps://nolankido.com/,1,10\n")
        queries = self.csv("Queries.csv", "Top queries,Clicks,Impressions\n"
                           "Nolan Kido AI,5,100\n"
                           '"AI Works, Human Decides Nolan Y. Kido",3,50\n'
                           "nolankido local AI,2,30\n"
                           "how to check an ai answer,7,60\n")
        result = audit.summarize("2026-10", pages, queries)
        self.assertEqual(result["query_export"]["person_brand_visible_clicks"], 10)
        self.assertEqual(result["query_export"]["tagline_visible_clicks"], 3)
        self.assertIsNone(result["query_page_export"]["visible_nonbrand_technology_clicks"])

    def test_query_page_nonbrand_never_joins_separate_aggregates(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\n"
                         "https://nolankido.com/technology/a/,7,70\n")
        pairs = self.csv("query_pages.csv", "Query,Page,Clicks,Impressions\n"
                         "check AI calculations,https://nolankido.com/technology/a/,4,40\n"
                         "Nolan Kido,https://nolankido.com/technology/a/,2,20\n"
                         "poker basics,https://nolankido.com/poker/,8,80\n"
                         "AI Works Human Decides,https://nolankido.com/technology/b/,1,10\n"
                         "free tools,https://not-nolankido.com/technology/,100,200\n")
        result = audit.summarize("2026-10", pages, query_pages=pairs)
        self.assertEqual(result["query_page_export"]["visible_nonbrand_technology_clicks"], 4)
        self.assertEqual(result["query_page_export"]["outside_site_rows"], 1)
        self.assertIsNone(result["query_export"]["person_brand_visible_clicks"])

    def test_empty_exports_are_missing_not_measured_zero(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\n")
        queries = self.csv("Queries.csv", "Query,Clicks,Impressions\n")
        pairs = self.csv("Pairs.csv", "Query,Page,Clicks,Impressions\n")
        result = audit.summarize("2026-10", pages, queries, pairs)
        self.assertIsNone(result["page_export"]["observed_section_totals"]["technology"]["clicks"])
        self.assertIsNone(result["query_export"]["person_brand_visible_clicks"])
        self.assertIsNone(result["query_page_export"]["visible_nonbrand_technology_clicks"])

    def test_invalid_and_ambiguous_exports_are_rejected(self):
        bad_columns = self.csv("Pages.csv", "Page,Clicks,Impressions,Top pages\n"
                               "https://nolankido.com/,1,5,https://nolankido.com/\n")
        with self.assertRaises(audit.ExportError):
            audit.summarize("2026-10", bad_columns)
        bad_counts = self.csv("bad.csv", "Page,Clicks,Impressions\n"
                              "https://nolankido.com/,-1,5\n")
        with self.assertRaises(audit.ExportError):
            audit.summarize("2026-10", bad_counts)
        with self.assertRaises(audit.ExportError):
            audit.summarize("2026-13", bad_counts)

    def test_cli_is_read_only_json_with_no_query_text(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\n"
                         "https://nolankido.com/technology/,1,30\n")
        queries = self.csv("Queries.csv", "Query,Clicks,Impressions\n"
                           "a private experimental keyword,1,10\n")
        before = set(self.root.iterdir())
        proc = subprocess.run([sys.executable, str(SCRIPT), "--month", "2026-10",
                               "--pages", str(pages), "--queries", str(queries)],
                              capture_output=True, text=True, check=True)
        output = json.loads(proc.stdout)
        self.assertEqual(output["declared_month"], "2026-10")
        self.assertNotIn("private experimental keyword", proc.stdout)
        self.assertNotIn(str(self.root), proc.stdout)
        self.assertEqual(set(self.root.iterdir()), before)

    def test_public_link_and_private_evidence_boundary(self):
        source = (ROOT / "_source" / "technology" / "home.html").read_text(encoding="utf-8")
        rendered = (ROOT / "technology" / "index.html").read_text(encoding="utf-8")
        for body in (source, rendered):
            self.assertEqual(body.count('href="/downloads/gsc-monthly-local-audit.py"'), 1)
            self.assertEqual(body.count('id="site-visibility-limits"'), 1)
            self.assertIn("With a complete daily chart export", body)
            self.assertIn("makes no network calls", body)
        self.assertEqual(source.count("A no-cost monthly check:"), 1)
        self.assertEqual(rendered.count("A no-cost monthly check:"), 1)
        paragraph = r'<p><strong>A no-cost monthly check:</strong>.*?</p>'
        source_match = re.search(paragraph, source)
        rendered_match = re.search(paragraph, rendered)
        self.assertIsNotNone(source_match)
        self.assertIsNotNone(rendered_match)
        self.assertEqual(source_match.group(), rendered_match.group())
        self.assertNotIn("\u2014", source_match.group())
        protocol = (ROOT / "_reports" / "visibility-sprint" / "seo-geo-measurement-v1.md").read_text(encoding="utf-8")
        self.assertIn("## Offline local CSV summary", protocol)
        self.assertIn("--month 2026-10", protocol)
        self.assertIn("never private owner results", protocol)

    def test_script_has_no_network_or_paid_client_dependencies(self):
        content = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("import requests", "import socket", "urllib.request", "http.client",
                          "googleapiclient", "subprocess.run(", "os.system("):
            self.assertNotIn(forbidden, content)

    def test_complete_chart_supplies_property_totals_not_page_row_sums(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\n"
                         "https://nolankido.com/technology/,3,90\n")
        days = [f"2026-10-{n:02d},2,100" for n in range(1, 32)]
        days[0] = '2026-10-01,"1,234","4,321"'
        chart = self.csv("Chart.csv", "\ufeffDate,Clicks,Impressions,CTR,Position\n" + "\n".join(days) + "\n")
        result = audit.summarize("2026-10", pages, chart=chart)
        self.assertEqual(result["property_web_clicks"], 1234 + 30 * 2)
        self.assertEqual(result["property_web_impressions"], 4321 + 30 * 100)
        self.assertTrue(result["chart_export"]["calendar_days_validated"])
        self.assertEqual(result["chart_export"]["days"], 31)
        self.assertFalse(result["export_date_range_verified"])
        self.assertEqual(result["page_export"]["observed_section_totals"]["technology"]["clicks"], 3)

    def test_leap_february_chart_and_separate_calendar_validation(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\nhttps://nolankido.com/,1,2\n")
        self.assertEqual(calendar.monthrange(2028, 2)[1], 29)
        chart = self.csv("Chart.csv", "Date,Clicks,Impressions\n" +
                         "\n".join(f"2028-02-{n:02d},0,0" for n in range(1, 30)) + "\n")
        result = audit.summarize("2028-02", pages, chart=chart)
        self.assertEqual(result["chart_export"]["days"], 29)
        self.assertEqual(result["property_web_clicks"], 0)

    def test_partial_duplicate_outside_and_ambiguous_dates_rejected(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\nhttps://nolankido.com/,1,2\n")
        good_rows = [f"2026-10-{n:02d},1,3" for n in range(1, 32)]
        cases = {
            "missing": good_rows[:-1],
            "duplicate": good_rows + [good_rows[-1]],
            "outside": good_rows[:-1] + ["2026-11-01,1,3"],
            "ambiguous": ["10/01/2026,1,3"] + good_rows[1:],
        }
        for label, rows in cases.items():
            with self.subTest(label=label):
                chart = self.csv("Chart.csv", "Date,Clicks,Impressions\n" + "\n".join(rows) + "\n")
                with self.assertRaises(audit.ExportError):
                    audit.summarize("2026-10", pages, chart=chart)

    def test_chart_cli_keeps_property_totals_private_and_prints_no_dates(self):
        pages = self.csv("Pages.csv", "Page,Clicks,Impressions\nhttps://nolankido.com/,2,10\n")
        chart = self.csv("Chart.csv", "Date,Clicks,Impressions\n" +
                         "\n".join(f"2026-10-{n:02d},3,40" for n in range(1, 32)) + "\n")
        before = set(self.root.iterdir())
        run = subprocess.run([sys.executable, str(SCRIPT), "--month", "2026-10", "--pages", str(pages),
                              "--chart", str(chart)], check=True, text=True, capture_output=True)
        payload = json.loads(run.stdout)
        self.assertEqual(payload["property_web_clicks"], 93)
        self.assertEqual(payload["property_web_impressions"], 1240)
        self.assertNotIn(str(self.root), run.stdout)
        self.assertEqual(before, set(self.root.iterdir()))


if __name__ == "__main__":
    unittest.main()
