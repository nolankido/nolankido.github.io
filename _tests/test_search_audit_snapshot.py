#!/usr/bin/env python3
"""Negative controls for the committed SEO audit release gate."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))

import build
import check_search


class SearchAuditSnapshotTests(unittest.TestCase):
    def compare(self, recorded, current):
        with TemporaryDirectory() as work:
            target = Path(work) / "search-audit.json"
            target.write_text(json.dumps(recorded), encoding="utf-8")
            return check_search.snapshot_differences(current, target)

    def test_identical_report_is_accepted(self):
        report = {"status": "pass", "sitemap_urls": 229, "errors": []}
        self.assertEqual(self.compare(report, report.copy()), [])

    def test_stale_sitemap_count_is_rejected(self):
        actual = {"status": "pass", "sitemap_urls": 229, "errors": []}
        prior = {"status": "pass", "sitemap_urls": 228, "errors": []}
        self.assertTrue(any("sitemap_urls" in item for item in self.compare(prior, actual)))

    def test_missing_field_is_rejected(self):
        actual = {"status": "pass", "manual_book_hubs": 1, "errors": []}
        self.assertTrue(any("manual_book_hubs" in item for item in
                            self.compare({"status": "pass", "errors": []}, actual)))

    def test_obsolete_field_is_rejected(self):
        actual = {"status": "pass", "errors": []}
        self.assertTrue(any("obsolete" in item for item in
                            self.compare({"status": "pass", "errors": [], "obsolete": 1}, actual)))

    def test_missing_file_is_rejected(self):
        with TemporaryDirectory() as work:
            missing = Path(work) / "missing.json"
            self.assertTrue(check_search.snapshot_differences({}, missing))

    def test_invalid_json_is_rejected(self):
        with TemporaryDirectory() as work:
            target = Path(work) / "broken.json"
            target.write_text("{broken", encoding="utf-8")
            self.assertTrue(check_search.snapshot_differences({}, target))

    def test_non_object_json_is_rejected(self):
        self.assertTrue(self.compare([], {"status": "pass"}))

    def test_current_site_agrees_with_committed_snapshot(self):
        # Expensive by design: the release gate must compare generated truth
        # against the committed snapshot, not simply compare two fixtures.
        current = check_search.audit(ROOT, build.public_pages(), "https://nolankido.com")
        self.assertEqual(current["errors"], [])
        differences = check_search.snapshot_differences(
            current, ROOT / "_reports/search-audit.json")
        self.assertEqual(differences, [])


if __name__ == "__main__":
    unittest.main()
