"""Turn 27: one verifiable public identity with audience-specific profile links.

Local-only checks. Does not authenticate or edit third-party accounts.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import turn29_source_notes_history as turn29

SOURCE = ROOT / "_source/bio.html"
PUBLIC = ROOT / "bio/index.html"
KIT = ROOT / "downloads/nolan-kido-public-profile-kit.md"
PROFILE = {
    "GitHub": "https://github.com/nolankido",
    "DEV": "https://dev.to/kidon",
    "Substack": "https://nolankido.substack.com/",
    "NolanPoker": "https://www.youtube.com/@NolanPoker",
}
SECTION = '<section class="section" aria-labelledby="profile-link-guide">'


class Tags(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unbalanced profile section at " + tag)


def section(document):
    if document.count(SECTION) != 1:
        raise AssertionError("Missing or repeated profile section")
    start = document.index(SECTION)
    return document[start:document.index("</section>", start) + len("</section>")]


class ProfileLinkKitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.html = PUBLIC.read_text(encoding="utf-8")
        cls.kit = KIT.read_text(encoding="utf-8")

    def test_visible_section_is_identical_and_in_main(self):
        self.assertEqual(section(self.source), section(self.html))
        self.assertLess(self.html.index(SECTION), self.html.index("</main>"))
        self.assertEqual(self.source.count('id="profile-link-guide"'), 1)
        self.assertEqual(self.html.count('id="profile-link-guide"'), 1)
        self.assertIn('href="#profile-link-guide">Public profile links</a>', self.html)
        self.assertIn('id="profile-claims-evidence"', self.html)
        tags = Tags()
        tags.feed(section(self.html))
        self.assertEqual(tags.stack, [])
        self.assertNotIn("\u2014", section(self.html))
        self.assertNotIn("<script", section(self.html))
        self.assertNotIn("<form", section(self.html))

    def test_four_existing_public_work_profiles_have_relevant_evidence_routes(self):
        for name, url in PROFILE.items():
            with self.subTest(name=name):
                self.assertEqual(section(self.html).count('href="' + url + '"'), 1)
                self.assertIn(url, self.kit)
        for route in (
            "/technology/",
            "/technology/local-ai-review-replies/",
            "/poker/nolan-kido/",
        ):
            self.assertIn('href="' + route + '"', section(self.html))
        self.assertIn("https://doi.org/10.1111/j.1475-679X.2012.00447.x", self.html)
        self.assertNotIn("sameAs", self.html)
        self.assertNotIn("jobTitle", self.html)
        self.assertNotIn("aggregateRating", self.html)

    def test_copy_ready_file_is_accessible_without_js_or_external_publishing(self):
        self.assertIn('href="/downloads/nolan-kido-public-profile-kit.md" download', self.html)
        for heading in (
            "## GitHub", "## DEV Community", "## Substack",
            "## NolanPoker on YouTube", "## LinkedIn, pending ownership",
        ):
            self.assertIn(heading, self.kit)
        self.assertIn("404 bio not found", self.kit)
        self.assertIn("not been posted", self.kit)
        self.assertIn("do not", self.kit.lower())
        self.assertNotIn("\u2014", self.kit)
        self.assertNotIn("password", self.kit.lower())
        self.assertNotIn("api_key", self.kit.lower())

    def test_existing_bios_copy_buttons_and_person_id_remain_stable(self):
        site = json.loads((ROOT / "_source/site.json").read_text(encoding="utf-8"))
        for key in ("bio_short", "bio_long"):
            self.assertIn(site[key], self.html)
            expected = site[key] + "\n"
            path = ROOT / "downloads" / ("nolan-kido-" + key.split("_")[1] + "-bio.txt")
            self.assertEqual(path.read_text(encoding="utf-8"), expected)
        self.assertEqual(len(re.findall(r'data-profile-copy="[^"]+"', self.html)), 3)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.html)

    def test_bio_revision_has_matching_manifest_schema_and_sitemap(self):
        page = next(p for p in build.public_pages() if p["id"] == "bio")
        self.assertEqual(page["updated"], "2026-11-04")
        self.assertIn('"dateModified": "2026-11-04"', self.html)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/bio/">', self.html)
        old_sitemap = subprocess.check_output(
            ["git", "show", "f2ce3bd71474bc0cec1ad39cf6feb7feb357ce43:sitemap.xml"],
            cwd=ROOT
        ).decode("utf-8")
        def rows(text):
            root = ET.fromstring(text)
            return {item.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                    item.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
                    for item in root}
        before = rows(old_sitemap)
        after = rows(turn29.before("sitemap.xml", (ROOT / "sitemap.xml").read_text(encoding="utf-8")))
        self.assertEqual(set(before), set(after))
        changed = {url for url in before if before[url] != after[url]}
        self.assertEqual(changed, {"https://nolankido.com/bio/"})
        self.assertEqual(before["https://nolankido.com/bio/"], "2026-10-28")
        self.assertEqual(after["https://nolankido.com/bio/"], "2026-11-04")

    def test_full_generator_preserves_committed_public_page(self):
        generated = build.build_outputs()[Path("bio/index.html")]
        self.assertEqual(generated, self.html)


if __name__ == "__main__":
    unittest.main()
