"""Positive and negative controls for important search discovery paths."""
import shutil
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import check_discovery


class DiscoveryGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        paths = ["robots.txt", "sitemap.xml", "poker/index.html"]
        paths += [route.lstrip("/") + "index.html" for route in check_discovery.PRIORITIES]
        for path in paths:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def tearDown(self):
        self.temp.cleanup()

    def edit(self, path, old, new):
        target = self.root / path
        content = target.read_text(encoding="utf-8")
        self.assertIn(old, content)
        target.write_text(content.replace(old, new, 1), encoding="utf-8")

    def test_current_site(self):
        self.assertEqual(check_discovery.check(self.root)["priority_pages"], 7)

    def test_canonical_mutation(self):
        self.edit("technology/task-brief/index.html", 'rel="canonical" href="https://nolankido.com/technology/task-brief/"', 'rel="canonical" href="https://example.invalid/"')
        with self.assertRaisesRegex(ValueError, "canonical mismatch"):
            check_discovery.check(self.root)

    def test_noindex_mutation(self):
        self.edit("poker/hand-rankings/index.html", "<head>", '<head><meta name="robots" content="noindex">')
        with self.assertRaisesRegex(ValueError, "noindex"):
            check_discovery.check(self.root)

    def test_robots_block(self):
        with (self.root / "robots.txt").open("a") as out:
            out.write("\nDisallow: /\n")
        with self.assertRaisesRegex(ValueError, "blanket Disallow"):
            check_discovery.check(self.root)

    def test_sitemap_missing_entry(self):
        import re
        content = (self.root / "sitemap.xml").read_text(encoding="utf-8")
        entry = re.search(r"<url>\s*<loc>https://nolankido.com/poker/hand-rankings/</loc>.*?</url>", content, re.S)
        self.assertIsNotNone(entry)
        self.edit("sitemap.xml", entry.group(), "")
        with self.assertRaisesRegex(ValueError, "sitemap URL count"):
            check_discovery.check(self.root)

    def test_internal_link_removed(self):
        self.edit("poker/index.html", 'href="/poker/hand-rankings/"', 'href="/poker/removed/"')
        with self.assertRaisesRegex(ValueError, "missing native link"):
            check_discovery.check(self.root)

    def test_schema_url_changed(self):
        self.edit("technology/task-brief/index.html", '"url": "https://nolankido.com/technology/task-brief/"', '"url": "https://nolankido.com/old/"')
        with self.assertRaisesRegex(ValueError, "structured-data URL mismatch"):
            check_discovery.check(self.root)
