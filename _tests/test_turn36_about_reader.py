"""The About evidence page remains accessible, scannable and source-faithful."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import check_live
from reviewed_release import read as reviewed_bytes
import turn36_about_reader_history as history

RELEASE = "8171c33bdaf354654bd1c1e0920e14d44b38974c"

NAV_PATTERN = re.compile(r'<nav class="about-jump-nav" aria-label="([^"]+)">(.*?)</nav>', re.S)
SCHEMA_PATTERN = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
LINKS = [
    ("about-evidence-title", "Evidence"),
    ("what-matters-in-the-work", "My approach"),
    ("about-interests", "Other interests"),
    ("wine-games-and-life", "Wine and games"),
    ("try-the-work", "Try the work"),
    ("public-work-elsewhere", "Public profiles"),
]


class AboutReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        cls.html = (ROOT / "about/index.html").read_text(encoding="utf-8")

    def test_native_section_navigation_is_named_and_complete(self):
        for value in (self.source, self.html):
            with self.subTest(file="source" if value == self.source else "output"):
                match = NAV_PATTERN.search(value)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), "Sections of Nolan Kido's profile")
                self.assertIn("Explore this profile", match.group(2))
                self.assertEqual(re.findall(r'<a href="#([^"]+)">([^<]+)</a>', match.group(2)), LINKS)
                for target, _ in LINKS:
                    self.assertEqual(value.count('id="' + target + '"'), 1)
                    self.assertRegex(value, r'<h2 id="' + target + r'">')

    def test_credible_first_screen_remains_ahead_of_navigation(self):
        self.assertLess(self.source.index('id="about-evidence-title"'),
                        self.source.index('class="about-jump-nav"'))
        self.assertLess(self.source.index('class="about-jump-nav"'),
                        self.source.index('id="what-matters-in-the-work"'))
        self.assertIn("I coauthored", self.source)
        self.assertIn("not audited business outcomes", self.source)
        self.assertIn("Tournament cashes are gross results, not profit.", self.source)
        self.assertNotIn("\u2014", self.source)

    def test_about_only_gets_small_scoped_responsive_stylesheet(self):
        css = (ROOT / "assets/about-reader.css").read_text(encoding="utf-8")
        version = sha256(css.encode("utf-8")).hexdigest()[:12]
        self.assertIn(f'href="/assets/about-reader.css?v={version}"', self.html)
        self.assertNotIn("/assets/about-reader.css", (ROOT / "technology/index.html").read_text())
        for token in (".page-about", "min-height: 44px", "max-width: 480px",
                      "overflow-wrap: anywhere", "@media print"):
            self.assertIn(token, css)
        self.assertNotIn("<script", self.source)

    def test_profile_metadata_and_public_identity_are_not_changed(self):
        old = subprocess.check_output([
            "git", "show", history.PARENT + ":about/index.html"
        ], cwd=ROOT).decode("utf-8")
        original_schema = json.loads(SCHEMA_PATTERN.search(old).group(1))
        current_schema = json.loads(SCHEMA_PATTERN.search(self.html).group(1))
        # Turn 125 restores punctuation in the canonical brand line only.
        # Compare all remaining metadata, including the stable public Person ID.
        self.assertEqual(original_schema, json.loads(
            json.dumps(current_schema).replace(
                "AI Works, Human Decides", "AI Works Human Decides"
            )
        ))
        self.assertIn('<h1 class="page-title">About Nolan Kido</h1>', self.html)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/about/">', self.html)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.html)

    def test_generator_and_public_get_inventory_are_deterministic(self):
        self.assertEqual(build.build_outputs()[Path("about/index.html")], self.html)
        self.assertEqual(check_live.targets()["/assets/about-reader.css"],
                         (200, (ROOT / "assets/about-reader.css").read_bytes()))
        self.assertEqual(check_live.targets()["/about/"], (200, self.html.encode("utf-8")))


class AboutReaderHistoryTests(unittest.TestCase):
    def test_exact_predecessors_for_each_rewound_file(self):
        for name, (old, new) in history.records()["files"].items():
            with self.subTest(path=name):
                release = reviewed_bytes(RELEASE, name, new)
                predecessor = reviewed_bytes(history.PARENT, name, old)
                self.assertEqual(history.before(name, release), predecessor)

    def test_unknown_edits_cannot_be_hidden_from_history(self):
        for name in history.records()["files"]:
            value = (ROOT / name).read_bytes()
            self.assertEqual(history.before(name, value + b"OTHER"), value + b"OTHER")
            self.assertEqual(history.before("other/" + name, value), value)

    def test_added_css_is_exactly_accounted_for(self):
        for name, value in history.records()["added"].items():
            body = reviewed_bytes(RELEASE, name, value)
            self.assertTrue(history.is_added_file(name, body))
            self.assertFalse(history.is_added_file(name, body + b"OTHER"))
        css = reviewed_bytes(RELEASE, "assets/about-reader.css",
                             history.records()["added"]["assets/about-reader.css"])
        self.assertEqual(history.live_targets({"/assets/about-reader.css": (200, css)}), {})
        altered = {"/assets/about-reader.css": (200, css + b"OTHER")}
        self.assertEqual(history.live_targets(altered), altered)


if __name__ == "__main__":
    unittest.main()
