"""Turn 65: the published 10 BB companion belongs in local Find and section search.

Run locally after complete checkout. Uses only repository-owned public data and
does not submit a search, change the sitemap, or access external services.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import player_find
import search_sections
import site_find
import tenbb_companion


class Turn65TenBBFind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = site_find.entries(ROOT, build.public_pages())
        cls.extras = player_find.add(ROOT, cls.manifest)
        cls.entry = player_find.tenbb_entry(ROOT)
        cls.html = (ROOT / "find/index.html").read_text(encoding="utf-8")
        cls.course = (ROOT / tenbb_companion.OUTPUT).read_text(encoding="utf-8")

    def test_existing_canonical_appears_once_as_written_study_guide(self):
        self.assertIsNotNone(self.entry)
        self.assertEqual(self.entry["path"], tenbb_companion.ROUTE)
        self.assertEqual(self.entry["kind"], "guide")
        self.assertEqual(self.entry["home"], "poker")
        self.assertEqual(self.entry["interests"], ["poker"])
        self.assertEqual(self.entry["title"], "The 10 Big Blind Tournament Playbook")
        self.assertEqual(self.entry["date"], "2026-11-19")
        self.assertIn("ICM", self.entry["description"])
        self.assertNotIn(tenbb_companion.ROUTE, {p["path"] for p in build.public_pages()})
        self.assertEqual([x["path"] for x in self.extras].count(tenbb_companion.ROUTE), 1)
        self.assertEqual(self.html.count('href="/poker/10bb/"'), 1)
        self.assertIn('data-kind="guide" data-interests="poker"', self.html)

    def test_published_index_matches_deterministic_generator(self):
        self.assertEqual(build.build_outputs()[Path("find/index.html")], self.html)
        # A generated card must use the same title, summary and publication
        # information that the fail-closed release registry validates.
        self.assertIn('data-search-title="' + self.entry["search_title"] + '"', self.html)
        self.assertIn('Published <time datetime="2026-11-19">November 19, 2026</time>', self.html)
        self.assertIn('id="browse-poker"><summary>Poker <span class="find-group-count" hidden>(113)</span>',
                      self.html)

    def test_search_sections_use_eight_visible_h2_only(self):
        visible = search_sections.headings(self.course)
        self.assertEqual(len(visible), 8)
        self.assertEqual(visible[0][0], "six-checks-title")
        self.assertEqual(visible[-1][0], "sources-title")
        self.assertNotIn("q1-title", [row[0] for row in visible])
        match = re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>',
                          self.html, re.S)
        self.assertIsNotNone(match)
        payload = json.loads(match.group(1))
        self.assertEqual(payload["version"], 4)
        flat = payload["pages"]["poker"]["10bb/"]
        labels = payload["labels"]
        decoded = [[flat[i], labels[flat[i + 1]] if type(flat[i + 1]) is int else flat[i + 1]]
                   for i in range(0, len(flat), 2)]
        self.assertEqual(decoded, visible)

    def test_local_browser_search_can_find_the_published_companion(self):
        js = """
const assert = require('node:assert/strict');
const { score } = require('./assets/site-find.js');
const record = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
record.subjects = 'Poker';
for (const query of ['10 BB', 'tournament playbook', 'NolanPoker', 'ICM']) {
  assert(score(record, query) >= 0, query);
}
assert.equal(score(record, 'unrelatedinventedstring'), -1);
"""
        done = subprocess.run(["node", "-e", js], cwd=ROOT, input=json.dumps(self.entry),
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_partial_publication_or_tampered_metadata_fail_closed(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertIsNone(player_find.tenbb_entry(root))
            course = root / tenbb_companion.OUTPUT
            course.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / tenbb_companion.OUTPUT, course)
            with self.assertRaises(ValueError):
                player_find.tenbb_entry(root)
            checker = root / tenbb_companion.CODE
            checker.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / tenbb_companion.CODE, checker)
            # Turn 72 requires the free worksheet as well as the Python checker.
            # Copying only the two original files is intentionally incomplete.
            with self.assertRaisesRegex(ValueError, 'written worksheet is missing'):
                player_find.tenbb_entry(root)
            worksheet = root / tenbb_companion.WORKSHEET
            worksheet.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / tenbb_companion.WORKSHEET, worksheet)
            self.assertEqual(player_find.tenbb_entry(root)["path"], tenbb_companion.ROUTE)
            worksheet.unlink()
            with self.assertRaisesRegex(ValueError, 'written worksheet is missing'):
                player_find.tenbb_entry(root)
            shutil.copyfile(ROOT / tenbb_companion.WORKSHEET, worksheet)
            corrupted = self.course.replace(
                '<meta name="description" content="',
                '<meta name="description" content="Unsupported marketing claim. ', 1)
            course.write_text(corrupted, encoding="utf-8")
            with self.assertRaises(ValueError):
                player_find.tenbb_entry(root)

    def test_duplicates_and_site_publishing_boundaries(self):
        with self.assertRaises(ValueError):
            player_find.add(ROOT, [*self.manifest, self.entry])
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(sitemap.count("https://nolankido.com/poker/10bb/"), 1)
        # The Find page remains a noindex utility rather than a new SEO URL.
        self.assertIn('<meta name="robots" content="noindex, follow">', self.html)
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            f.is_file() and f.suffix.lower() in {".yml", ".yaml"}
            for f in actions.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
