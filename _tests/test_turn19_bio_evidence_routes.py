"""Turn 19: the public biography routes readers to source-backed AI and poker work."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest

from test_site import ROOT, build
import turn19_bio_evidence_routes_history as history

SOURCE = ROOT / "_source/bio.html"
PUBLIC = ROOT / "bio/index.html"


class Links(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
        self.ids = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        item = dict(attrs)
        if tag == "a":
            self.hrefs.append(item.get("href"))
        if "id" in item:
            self.ids.append(item["id"])


class Turn19EvidenceRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.html = PUBLIC.read_text(encoding="utf-8")

    def test_generated_biography_remains_exactly_buildable(self):
        self.assertEqual(build.build_outputs()[Path("bio/index.html")], self.html)
        self.assertEqual(self.source.count(history.INSERTION), 1)
        self.assertEqual(self.html.count(history.INSERTION), 1)
        self.assertEqual(self.source.count('id="profile-evidence-routes"'), 1)
        self.assertNotIn("\u2014", self.source)
        self.assertNotIn("<form", self.source.lower())

    def test_paths_are_unique_and_public_targets_exist(self):
        routes = {
            "/technology/#site-visibility-evidence": ROOT / "technology/index.html",
            "/technology/#small-business-ai-pilot": ROOT / "technology/index.html",
            "/poker/nolan-kido/#creator-introduction": ROOT / "poker/nolan-kido/index.html",
        }
        for document in (self.source, self.html):
            for route in routes:
                self.assertEqual(document.count('href="' + route + '"'), 1)
        parsed = Links(self.html)
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        for route, target in routes.items():
            self.assertTrue(target.is_file(), route)
            self.assertIn('id="' + route.split("#", 1)[1] + '"',
                          target.read_text(encoding="utf-8"), route)
            self.assertIn(route, parsed.hrefs)

    def test_no_biography_copy_metadata_or_tracking_regression(self):
        site = json.loads((ROOT / "_source/site.json").read_text(encoding="utf-8"))
        for kind in ("short", "long"):
            self.assertIn(site["bio_" + kind], self.html)
            self.assertEqual((ROOT / ("downloads/nolan-kido-" + kind + "-bio.txt")).read_text(encoding="utf-8"),
                             site["bio_" + kind] + "\n")
        self.assertEqual(len(re.findall(r'data-profile-copy="[^"]+"', self.html)), 3)
        self.assertEqual(self.html.count("cloud.umami.is/script.js"), 1)
        self.assertIn('"dateModified": "2026-10-28"', self.html)
        manifest = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        self.assertEqual(next(p["updated"] for p in manifest if p["id"] == "bio"), "2026-10-28")
        self.assertIn('id="profile-short-text"', self.html)
        self.assertIn('id="profile-long-text"', self.html)
        self.assertIn("not endorsements, official creator credentials", history.INSERTION)
        self.assertIn("not a general performance claim", self.html)

    def test_exact_prior_versions_and_fail_open_mutations(self):
        for path, (old_sha, new_sha) in history.BLOBS.items():
            current = (ROOT / path).read_bytes()
            self.assertEqual(history.blob(current), new_sha)
            previous = history.before(path, current)
            self.assertEqual(history.blob(previous), old_sha)
            self.assertEqual(history.before(path, previous), previous)
            self.assertEqual(history.before(Path(path), current.decode("utf-8")),
                             previous.decode("utf-8"))
            for modified in (current + b"UNKNOWN", b"UNKNOWN" + current, current[1:]):
                self.assertEqual(history.before(path, modified), modified)
            self.assertEqual(history.before("other/" + path, current), current)


if __name__ == "__main__":
    unittest.main()
