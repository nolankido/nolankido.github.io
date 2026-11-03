"""Cross-platform public profiles stay verified, visible and source aligned."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import public_identity

EXPECTED = [
    "https://github.com/nolankido",
    "https://dev.to/kidon",
    "https://nolankido.substack.com/",
    "https://www.youtube.com/@NolanPoker",
]


class CrossPlatformIdentityTests(unittest.TestCase):
    def test_verified_profiles_keep_stable_order_and_unique_urls(self):
        self.assertEqual(public_identity.same_as(), EXPECTED)
        self.assertEqual(len(EXPECTED), len(set(EXPECTED)))
        self.assertTrue(all(url.startswith("https://") for url in EXPECTED))
        copy = public_identity.same_as()
        copy.pop()
        self.assertEqual(public_identity.same_as(), EXPECTED)

    def test_home_and_about_person_nodes_match_visible_profiles(self):
        about = (ROOT / "about/index.html").read_text(encoding="utf-8")
        source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        for path in ("index.html", "about/index.html"):
            html = (ROOT / path).read_text(encoding="utf-8")
            match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
            self.assertIsNotNone(match)
            schema = json.loads(match.group(1))
            self.assertEqual(schema["about"]["sameAs"], EXPECTED)
            self.assertEqual(schema["mainEntity"]["sameAs"], EXPECTED)
            self.assertEqual(schema["about"]["@id"],
                             "https://nolankido.com/about/#nolan-kido")
            self.assertNotIn("jobTitle", schema["mainEntity"])
            self.assertNotIn("homeLocation", schema["mainEntity"])
        for url in EXPECTED:
            self.assertEqual(about.count('href="' + url + '" rel="me"'), 1)
        self.assertEqual(about.count('id="public-work-profiles"'), 1)
        self.assertIn('<h2 id="public-work-elsewhere">Public work across platforms</h2>', about)
        self.assertIn("Publishing a story or conclusion does not make its claims independently verified.", about)
        self.assertIn("AI Works, Human Decides essay on Substack", about)
        self.assertIn("NolanPoker YouTube channel", about)
        self.assertNotIn("\u2014", source)

    def test_rich_identity_stays_separate_and_generated_from_source(self):
        authored = json.loads((ROOT / "_source/person-schema.jsonld").read_text())
        published = json.loads((ROOT / "assets/nolan-kido-identity.jsonld").read_text())
        self.assertEqual(published, authored)
        person = next(item for item in published["@graph"] if item["@type"] == "Person")
        for url in EXPECTED:
            self.assertIn(url, person["sameAs"])
        self.assertEqual(len(person["sameAs"]), len(set(person["sameAs"])))
        self.assertNotIn("homeLocation", person)
        self.assertNotIn("address", person)
        self.assertIn("Former Chief Operating Officer", person["description"])
        for path in ("index.html", "about/index.html"):
            self.assertNotIn("/assets/nolan-kido-identity.jsonld",
                             (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
