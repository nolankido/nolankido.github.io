"""Independent positive and negative tests for the seven-page discovery guard."""
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_tests"))
import check_discovery as guard


class DiscoveryGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        paths = ["robots.txt", "sitemap.xml", "poker/index.html"]
        paths.extend(route.lstrip("/") + "index.html" for route in guard.ROUTES)
        for name in paths:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    def tearDown(self):
        self.temp.cleanup()

    def replace(self, name, old, new):
        path = self.root / name
        content = path.read_text(encoding="utf-8")
        self.assertIn(old, content)
        path.write_text(content.replace(old, new, 1), encoding="utf-8")

    def rejects(self, message):
        with self.assertRaisesRegex(ValueError, message):
            guard.check(self.root)

    def test_unmodified_site_passes(self):
        self.assertEqual(guard.check(self.root)["priority_pages"], 7)

    def test_missing_generated_page(self):
        (self.root / "poker/school/index.html").unlink()
        self.rejects("missing generated page")

    def test_canonical_changed(self):
        self.replace(
            "technology/task-brief/index.html",
            'rel="canonical" href="https://nolankido.com/technology/task-brief/"',
            'rel="canonical" href="https://example.invalid/"',
        )
        self.rejects("canonical mismatch")

    def test_noindex_directive(self):
        self.replace(
            "poker/hand-rankings/index.html",
            "<head>", '<head><meta name="robots" content="noindex">',
        )
        self.rejects("noindex")

    def test_uppercase_none_directive(self):
        self.replace(
            "poker/hand-rankings/index.html",
            "<head>", '<head><meta name="ROBOTS" content="NONE">',
        )
        self.rejects("noindex")

    def test_blanket_root_disallow(self):
        path = self.root / "robots.txt"
        path.write_text(path.read_text() + "\nDisallow: / # temporary\n")
        self.rejects("blanket root Disallow")

    def test_wildcard_root_disallow_is_a_blanket_block(self):
        path = self.root / "robots.txt"
        path.write_text(path.read_text() + "\nDisallow: /* # blocks all URLs\n")
        self.rejects("blanket root Disallow")

    def test_image_preview_none_does_not_deindex_page(self):
        self.replace(
            "poker/hand-rankings/index.html",
            "<head>", '<head><meta name="ROBOTS" content="max-image-preview:none">',
        )
        self.assertEqual(guard.check(self.root)["status"], "pass")

    def test_multiple_robots_directives_detect_noindex(self):
        self.replace(
            "poker/hand-rankings/index.html", "<head>",
            '<head><meta name="robots" content="max-image-preview:none, NOINDEX">',
        )
        self.rejects("noindex")

    def test_commented_disallow_is_not_active(self):
        path = self.root / "robots.txt"
        path.write_text(path.read_text() + "\n# Disallow: /\n")
        self.assertEqual(guard.check(self.root)["status"], "pass")

    def test_commented_sitemap_is_not_active(self):
        self.replace(
            "robots.txt", "Sitemap: https://nolankido.com/sitemap.xml",
            "# Sitemap: https://nolankido.com/sitemap.xml",
        )
        self.rejects("missing active canonical sitemap")

    def test_duplicate_sitemap_entry(self):
        path = self.root / "sitemap.xml"
        xml = path.read_text()
        match = re.search(
            r"<url>\s*<loc>https://nolankido.com/poker/hand-rankings/</loc>.*?</url>",
            xml, re.S,
        )
        self.assertIsNotNone(match)
        path.write_text(xml.replace(match.group(), match.group() * 2, 1))
        self.rejects("sitemap entry count")

    def test_invalid_sitemap_revision(self):
        path = self.root / "sitemap.xml"
        xml = path.read_text()
        match = re.search(
            r"(<loc>https://nolankido.com/poker/hand-rankings/</loc>\s*"
            r"<lastmod>)[^<]+(</lastmod>)", xml,
        )
        self.assertIsNotNone(match)
        path.write_text(
            xml[:match.start()] + match.group(1) + "not-a-date"
            + match.group(2) + xml[match.end():]
        )
        self.rejects("invalid sitemap lastmod")

    def test_metadata_description_removed(self):
        path = self.root / "technology/task-brief/index.html"
        html = path.read_text()
        html = re.sub(
            r'<meta name="description" content="[^"]+">\n', "",
            html, count=1,
        )
        self.assertNotEqual(html, path.read_text())
        path.write_text(html)
        self.rejects("description")

    def test_jsonld_url_changed(self):
        self.replace(
            "technology/task-brief/index.html",
            '"url": "https://nolankido.com/technology/task-brief/"',
            '"url": "https://example.invalid/old/"',
        )
        self.rejects("structured-data URL mismatch")

    def test_native_link_removed_even_when_prefetch_exists(self):
        self.replace(
            "poker/index.html", 'href="/poker/hand-rankings/"',
            'href="/poker/removed/"',
        )
        self.replace(
            "poker/index.html", "<head>",
            '<head><link rel="prefetch" href="/poker/hand-rankings/">',
        )
        self.rejects("missing native link")

    def test_og_url_changed(self):
        self.replace(
            "technology/task-brief/index.html",
            '<meta property="og:url" content="https://nolankido.com/technology/task-brief/">',
            '<meta property="og:url" content="https://example.invalid/">',
        )
        self.rejects("Open Graph URL mismatch")


if __name__ == "__main__":
    unittest.main()
