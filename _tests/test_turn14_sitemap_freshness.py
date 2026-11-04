"""Turn 14: sitemap dates reflect observed substantial edits, not build time."""
import json
import subprocess
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

import turn14_freshness_history as history
import turn15_evidence_links_history
import turn16_small_business_pilot_history
import turn23_technology_metadata_history as turn23_history


ROOT = Path(__file__).resolve().parents[1]
CHANGED = {
    "/": "2026-10-28",
    "/about/": "2026-10-28",
    "/technology/": "2026-10-28",
    "/poker/": "2026-10-15",
}
REVIEWED_DATE = "2026-11-03"
ORIGIN = "https://nolankido.com"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def sitemap_rows(text):
    root = ET.fromstring(text)
    rows = {}
    for item in root.findall("sm:url", NS):
        url = item.findtext("sm:loc", namespaces=NS)
        modified = item.findtext("sm:lastmod", namespaces=NS)
        if not url or url in rows:
            raise AssertionError("Missing or repeated sitemap canonical URL")
        rows[url] = modified
    return rows


class Turn14SitemapFreshnessTests(unittest.TestCase):
    def test_only_four_reviewed_source_dates_changed(self):
        previous_text = subprocess.check_output(
            ["git", "show", history.PARENT + ":_source/pages.json"], cwd=ROOT
        ).decode("utf-8")
        previous = {p["path"]: p for p in json.loads(previous_text)}
        source = turn23_history.before(
            "_source/pages.json", (ROOT / "_source/pages.json").read_text(encoding="utf-8")
        )
        current = {p["path"]: p for p in json.loads(source)}
        self.assertEqual(set(previous), set(current))
        for route, page in current.items():
            before = previous[route]
            if route in CHANGED:
                self.assertEqual(before["updated"], CHANGED[route])
                self.assertEqual(page, {**before, "updated": REVIEWED_DATE})
            else:
                self.assertEqual(page, before)

    def test_sitemap_preserves_all_urls_and_other_dates(self):
        previous_text = subprocess.check_output(
            ["git", "show", history.PARENT + ":sitemap.xml"], cwd=ROOT
        ).decode("utf-8")
        previous = sitemap_rows(previous_text)
        current = sitemap_rows(turn23_history.before(
            "sitemap.xml", (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        ))
        self.assertEqual(set(previous), set(current))
        for url, old_date in previous.items():
            route = url.removeprefix(ORIGIN)
            if route in CHANGED:
                self.assertEqual(old_date, CHANGED[route])
                self.assertEqual(current[url], REVIEWED_DATE)
            else:
                self.assertEqual(current[url], old_date)

    def test_schema_freshness_matches_sitemap(self):
        for path in ("index.html", "technology/index.html", "poker/index.html"):
            with self.subTest(path=path):
                html = turn23_history.before(path, (ROOT / path).read_text(encoding="utf-8"))
                self.assertEqual(html.count('"dateModified": "' + REVIEWED_DATE + '"'), 1)
        # ProfilePage deliberately omits a day-only DateTime. Do not invent one.
        about = (ROOT / "about/index.html").read_text(encoding="utf-8")
        self.assertNotIn('"dateModified": "' + REVIEWED_DATE + '"', about)

    def test_exact_predecessor_rewinds_only_reviewed_blobs(self):
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                content = turn16_small_business_pilot_history.before(path, (ROOT / path).read_bytes())
                content = turn15_evidence_links_history.before(path, content)
                self.assertEqual(history.blob(content), current_sha)
                older = history.before(path, content)
                self.assertEqual(history.blob(older), old_sha)
                self.assertEqual(older, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=ROOT
                ))
                self.assertEqual(
                    history.before(Path(path), content.decode("utf-8")),
                    older.decode("utf-8")
                )

    def test_unknown_mutations_survive(self):
        for path in history.BLOBS:
            current = (ROOT / path).read_bytes()
            for changed in (current + b"UNKNOWN", b"UNKNOWN" + current, current[1:]):
                self.assertEqual(history.before(path, changed), changed)
            self.assertEqual(history.before("other/" + path, current), current)
        self.assertEqual(history.before("other.bin", bytes([0, 255])),
                         bytes([0, 255]))


if __name__ == "__main__":
    unittest.main()
