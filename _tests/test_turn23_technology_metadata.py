"""Turn 23: Technology metadata reflects the current, public evidence.

Tests are offline and deterministic. Earlier release assertions continue to
use SHA-gated historical snapshots, never rewritten production content.
"""
import json
import subprocess
import sys
import unittest
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

import turn23_technology_metadata_history as history
import turn26_technology_entry_history as turn26_history


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/pages.json"
PAGE = "technology/index.html"
FIND = "find/index.html"
SITEMAP = "sitemap.xml"
DATE = "2026-11-04"
DESCRIPTION = (
    "Explore Nolan Kido's practical AI work: small-business review checks, "
    "poker-vlog evidence QA, book continuity, and repeatable tools. "
    "AI Works Human Decides."
)
CANONICAL = "https://nolankido.com/technology/"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def sitemap_rows(text):
    rows = {}
    root = ET.fromstring(text)
    for element in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = element.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        date = element.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        if loc in rows or loc is None or date is None:
            raise AssertionError("Invalid sitemap URL/date pairing")
        rows[loc] = date
    return rows


class Turn23TechnologyMetadataTests(unittest.TestCase):
    def test_source_and_generator_metadata_match(self):
        manifest = json.loads(read(SOURCE))
        technology = [page for page in manifest if page["id"] == "technology"]
        self.assertEqual(len(technology), 1)
        self.assertEqual(technology[0]["path"], "/technology/")
        self.assertEqual(technology[0]["updated"], DATE)
        self.assertEqual(technology[0]["description"], DESCRIPTION)
        self.assertGreaterEqual(len(DESCRIPTION), 130)
        self.assertLessEqual(len(DESCRIPTION), 160)
        for phrase in ("Nolan Kido", "AI", "poker-vlog", "book", "small-business"):
            self.assertIn(phrase, DESCRIPTION)
        sys.path.insert(0, str(ROOT / "_scripts"))
        import practical_path
        import build
        self.assertEqual(practical_path.DESCRIPTION, DESCRIPTION)
        self.assertEqual(
            next(page["description"] for page in build.public_pages()
                 if page["id"] == "technology"), DESCRIPTION
        )

    def test_metadata_all_surfaces_and_content_are_aligned(self):
        page = read(PAGE)
        find = read(FIND)
        escaped = escape(DESCRIPTION, quote=True)
        self.assertEqual(page.count(escaped), 3)
        self.assertEqual(page.count('"description": "' + DESCRIPTION + '"'), 1)
        self.assertIn('<meta name="description" content="' + escaped + '">', page)
        self.assertIn('<meta property="og:description" content="' + escaped + '">', page)
        self.assertIn('<meta name="twitter:description" content="' + escaped + '">', page)
        self.assertIn('<link rel="canonical" href="' + CANONICAL + '">', page)
        self.assertEqual(page.count('"dateModified": "' + DATE + '"'), 1)
        self.assertEqual(page.count('class="project-card"'), 3)
        for anchor in ("small-business-ai-pilot", "poker-vlog-qa",
                       "poker-vlog-qa-demo", "practical-ai-path"):
            self.assertEqual(page.count('id="' + anchor + '"'), 1)
        self.assertEqual(find.count(escaped), 1)
        self.assertNotIn("local review replies, book continuity checks", find)
        self.assertNotIn("local review replies, book continuity checks", page)
        self.assertNotIn("\u2014", DESCRIPTION)

    def test_only_technology_sitemap_date_changes(self):
        old = subprocess.check_output(
            ["git", "show", history.PARENT + ":" + SITEMAP], cwd=ROOT
        ).decode("utf-8")
        old_rows = sitemap_rows(old)
        new_rows = sitemap_rows(read(SITEMAP))
        self.assertEqual(set(new_rows), set(old_rows))
        self.assertEqual(new_rows[CANONICAL], DATE)
        self.assertEqual(old_rows[CANONICAL], "2026-11-03")
        for url in old_rows:
            if url != CANONICAL:
                self.assertEqual(new_rows[url], old_rows[url])

    def test_committed_files_are_generated_outputs(self):
        sys.path.insert(0, str(ROOT / "_scripts"))
        import build
        outputs = build.build_outputs()
        for path in (PAGE, FIND, SITEMAP):
            with self.subTest(path=path):
                self.assertEqual(outputs[Path(path)], read(path))

    def test_only_exact_approved_blobs_rewind(self):
        self.assertEqual(len(history.BLOBS), 5)
        for path, (old_sha, new_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                current = (ROOT / path).read_bytes()
                self.assertEqual(history.blob(turn26_history.before(path, current)), new_sha)
                restored = history.before(path, current)
                self.assertEqual(history.blob(restored), old_sha)
                self.assertEqual(restored, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=ROOT
                ))
                self.assertEqual(history.before(path, restored), restored)
                self.assertEqual(
                    history.before(Path(path), current.decode("utf-8")),
                    restored.decode("utf-8")
                )
                for mutation in (current + b"X", b"X" + current, current[1:]):
                    self.assertEqual(history.before(path, mutation), mutation)
                self.assertEqual(history.before("other/" + path, current), current)
        self.assertEqual(history.before("unrelated.bin", bytes([255, 0])),
                         bytes([255, 0]))


if __name__ == "__main__":
    unittest.main()
