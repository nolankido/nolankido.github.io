"""Public synthetic CSVs demonstrate the private Search Console checker honestly."""

import csv
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "downloads/gsc-monthly-local-audit.py"
PAGES = ROOT / "downloads/gsc-synthetic-pages.csv"
DATES = ROOT / "downloads/gsc-synthetic-dates.csv"
SOURCE = ROOT / "_source/technology/ai-website-visibility.html"
PUBLIC = ROOT / "technology/ai-website-visibility/index.html"
PROTOCOL = ROOT / "_reports/visibility-sprint/seo-geo-measurement-v1.md"

INTRO = "<p><strong>Try it before exporting private data.</strong>"
END = "<p class=\"small-copy\">Google explains the"


def sample_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def ensure_synthetic(rows):
    if not rows or any(row.get("Synthetic") != "YES" for row in rows):
        raise ValueError("A public demonstration must be conspicuously synthetic")


def run_demo(chart=DATES, date_format="mdy"):
    return subprocess.run(
        [sys.executable, str(TOOL), "--month", "2026-10",
         "--pages", str(PAGES), "--chart", str(chart),
         "--chart-date-format", date_format],
        text=True, capture_output=True, check=False, cwd=ROOT,
    )


def demo_section(html):
    if html.count(INTRO) != 1 or html.count(END) != 1:
        raise ValueError("One public demo followed by original source notes required")
    return html[html.index(INTRO):html.index(END)]


class SyntheticVisibilityDemoTests(unittest.TestCase):
    def test_fixtures_have_explicit_synthetic_provenance(self):
        page_rows = sample_rows(PAGES)
        date_rows = sample_rows(DATES)
        ensure_synthetic(page_rows)
        ensure_synthetic(date_rows)
        self.assertEqual(len(page_rows), 3)
        self.assertEqual(len(date_rows), 31)
        self.assertEqual([row["Date"] for row in date_rows],
                         [f"10/{day}/2026" for day in range(1, 32)])
        self.assertTrue(all(row["Top pages"].startswith("https://nolankido.com/")
                            for row in page_rows))
        self.assertEqual(sum(int(row["Clicks"]) for row in page_rows), 22)
        self.assertEqual(sum(int(row["Clicks"]) for row in date_rows), 62)
        self.assertEqual(sum(int(row["Impressions"]) for row in date_rows), 3100)

    def test_actual_public_checker_prints_expected_aggregates_and_no_urls(self):
        result = run_demo()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual((data["chart_export"]["days"], data["property_web_clicks"],
                          data["property_web_impressions"]), (31, 62, 3100))
        totals = data["page_export"]["observed_section_totals"]
        self.assertEqual([totals[part]["clicks"] for part in ("technology", "poker", "other")],
                         [12, 7, 3])
        self.assertEqual(data["page_export"]["rows"], 3)
        self.assertEqual(data["page_export"]["outside_site_rows"], 0)
        self.assertFalse(data["query_export"]["provided"])
        self.assertIsNone(data["query_page_export"]["visible_nonbrand_technology_clicks"])
        self.assertNotIn("https://nolankido.com/technology/", result.stdout)
        self.assertNotIn("https://nolankido.com/poker/", result.stdout)

    def test_missing_day_is_rejected_instead_of_claiming_property_totals(self):
        rows = DATES.read_text(encoding="utf-8").splitlines()
        with TemporaryDirectory() as folder:
            incomplete = Path(folder) / "incomplete.csv"
            incomplete.write_text("\n".join(rows[:-1]) + "\n", encoding="utf-8")
            result = run_demo(chart=incomplete)
        self.assertEqual(result.returncode, 2)
        self.assertIn("incomplete daily chart (30 of 31 distinct dates)", result.stderr)

    def test_wrong_locale_is_rejected_instead_of_guessed(self):
        result = run_demo(date_format="iso")
        self.assertEqual(result.returncode, 2)
        self.assertIn("expected YYYY-MM-DD", result.stderr)
        self.assertNotIn("https://nolankido.com/", result.stderr)

    def test_page_instructions_match_source_and_do_not_claim_real_growth(self):
        source = SOURCE.read_text(encoding="utf-8")
        public = PUBLIC.read_text(encoding="utf-8")
        self.assertEqual(demo_section(source), demo_section(public))
        for filename in ("gsc-synthetic-pages.csv", "gsc-synthetic-dates.csv"):
            self.assertIn('href="/downloads/' + filename + '" download', public)
        self.assertIn(r"py -3 .\gsc-monthly-local-audit.py --month 2026-10 --pages .\gsc-synthetic-pages.csv --chart .\gsc-synthetic-dates.csv --chart-date-format mdy", public)
        self.assertIn("not</strong> genuine Google exports", public)
        self.assertIn("using it for another website requires adapting those rules", public)
        self.assertIn('"datePublished": "2026-11-03"', public)
        self.assertIn('"dateModified": "2026-11-06"', public)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/ai-website-visibility/">', public)
        self.assertNotIn(chr(0x2014), demo_section(public))
        protocol = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("### Practice with deliberately synthetic data", protocol)
        self.assertIn("property_web_clicks=62", protocol)
        for filename in ("gsc-synthetic-pages.csv", "gsc-synthetic-dates.csv"):
            self.assertIn("../../downloads/" + filename, protocol)

    def test_removed_synthetic_marker_is_rejected_by_fixture_guard(self):
        rows = sample_rows(PAGES)
        rows[0]["Synthetic"] = ""
        with self.assertRaisesRegex(ValueError, "conspicuously synthetic"):
            ensure_synthetic(rows)


if __name__ == "__main__":
    unittest.main()
