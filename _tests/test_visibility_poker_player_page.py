"""Locally run publication checks for the separate, source-compiled poker profile."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest

from test_site import ROOT, build

sys.path.insert(0, str(ROOT / "_scripts"))
import build_player_profile as profile


class Doc(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags_seen = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags_seen.append((tag, dict(attrs)))

    def tags(self, name):
        return [a for n, a in self.tags_seen if n == name]


class PlayerProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "poker/nolan-kido/index.html").read_text(encoding="utf-8")
        cls.doc = Doc(cls.html)
        cls.body_source = (ROOT / "_source/poker/nolan-kido-profile.html").read_text(encoding="utf-8")

    def test_compiled_page_is_exactly_reproducible_without_an_action(self):
        self.assertEqual(self.html, profile.render())
        self.assertIn(self.body_source, self.html)
        self.assertNotIn(build.MARKER, self.html)
        self.assertNotIn("\u2014", self.html)
        self.assertNotIn('<form', self.html)

    def test_one_canonical_identity_and_consistent_social_metadata(self):
        canonical = profile.URL
        self.assertEqual([a.get("href") for a in self.doc.tags("link")
                          if a.get("rel") == "canonical"], [canonical])
        self.assertEqual(len(self.doc.tags("h1")), 1)
        self.assertEqual(len(self.doc.tags("main")), 1)
        self.assertEqual(len(self.doc.tags("title")), 1)
        self.assertEqual([a.get("aria-label") for a in self.doc.tags("nav")].count("Breadcrumb"), 1)
        meta = {a.get("name", a.get("property")): a.get("content") for a in self.doc.tags("meta")}
        self.assertEqual(meta["description"], profile.DESCRIPTION)
        self.assertEqual(meta["og:url"], canonical)
        self.assertEqual(meta["og:title"], profile.TITLE)
        self.assertEqual(meta["twitter:title"], profile.TITLE)
        self.assertNotIn("noindex", meta.get("robots", ""))
        records = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        self.assertEqual(len(records), 1)
        data = json.loads(records[0])
        self.assertEqual(data["url"], canonical)
        self.assertEqual(data["@id"], canonical + "#webpage")
        self.assertEqual(data["about"]["@id"], "https://nolankido.com/about/#nolan-kido")
        self.assertEqual([e["position"] for e in data["breadcrumb"]["itemListElement"]], [1, 2, 3])
        self.assertEqual(data["breadcrumb"]["itemListElement"][-1]["item"], canonical)

    def test_four_public_result_links_and_financial_limits(self):
        urls = (
            "https://pokerdb.thehendonmob.com/event.php?a=r&n=1399113",
            "https://www.wsop.com/tournaments/result/17989/",
            "https://www.wsop.com/tournaments/result/18650/",
            "https://www.wsop.com/tournaments/result/14147/",
        )
        links = {a.get("href") for a in self.doc.tags("a")}
        self.assertTrue(set(urls) <= links)
        for required in (
            "1,652 entries", "341 entries", "638 entries", "101 entries",
            "gross payout, not net profit", "No bracelet, Circuit ring",
            "The videos are edited first-person accounts",
            "Neither written account asserts verified current-cut chapter timestamps.",
        ):
            self.assertIn(required, self.html)
        for video_id in ("qABaiIcvvpU", "I75GOBVXij4", "edNSD5BjIV8"):
            self.assertIn("watch?v=" + video_id, self.html)
        self.assertIn("public videos", self.html)
        self.assertNotIn("homeLocation", self.html)
        scripts = [a.get("src") for a in self.doc.tags("script") if a.get("src")]
        self.assertEqual(scripts, ["https://cloud.umami.is/script.js"])

    def test_native_discovery_links_and_existing_generator_boundary(self):
        self.assertNotIn("/poker/nolan-kido/", {p["path"] for p in build.public_pages()})
        outputs = build.build_outputs()
        for source, generated in (
            ("_source/poker/home.html", Path("poker/index.html")),
            ("_source/about.html", Path("about/index.html")),
        ):
            authored = (ROOT / source).read_text(encoding="utf-8")
            committed = (ROOT / generated).read_text(encoding="utf-8")
            self.assertIn('href="/poker/nolan-kido/"', authored)
            self.assertIn('href="/poker/nolan-kido/"', committed)
            self.assertEqual(outputs[generated], committed)
        self.assertTrue((ROOT / "poker/nolan-kido/index.html").is_file())


if __name__ == "__main__":
    unittest.main()
