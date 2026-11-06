"""A moved case remains reachable from old fragments and publishes only once."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = Path(__file__).resolve().parents[1]
ROUTE = "/technology/ai-website-visibility/"
URL = "https://nolankido.com" + ROUTE
ALIASES = ("site-visibility-checks", "site-visibility-choices",
           "site-visibility-limits", "free-visibility-check")
CASE_IDS = ("site-visibility-evidence", "site-visibility-evidence-title", *ALIASES)


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.anchors = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "id" in attrs:
            self.anchors[attrs["id"]] = attrs.get("href")


def migration_errors(hub, article):
    errors = []
    h, a = Tags(hub), Tags(article)
    for target in CASE_IDS:
        if h.ids.count(target) != 1 or a.ids.count(target) != 1:
            errors.append("missing or repeated destination: " + target)
    for target in ALIASES:
        if h.anchors.get(target) != ROUTE + "#" + target:
            errors.append("old fragment does not lead to the matching article section: " + target)
    for target in ("small-business-ai-pilot", "identity-claim-audit"):
        if 'href="/technology/#' + target + '"' not in article:
            errors.append("hub cross-reference lost: " + target)
        if 'href="#' + target + '"' in article:
            errors.append("article contains a stranded local fragment: " + target)
    if '<h3 id="free-visibility-check">' in hub:
        errors.append("the full guide is duplicated on the hub")
    return errors


class WebsiteVisibilityArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = (ROOT / "_source/technology/home.html").read_text()
        cls.article = (ROOT / "_source/technology/ai-website-visibility.html").read_text()
        cls.public = (ROOT / "technology/ai-website-visibility/index.html").read_text()

    def test_old_fragment_routes_reach_the_same_article_sections(self):
        self.assertEqual(migration_errors(self.hub, self.article), [])
        self.assertEqual(migration_errors((ROOT / "technology/index.html").read_text(), self.public), [])
        for source in ("about.html", "bio.html"):
            self.assertEqual((ROOT / "_source" / source).read_text().count('href="' + ROUTE + '"'), 1)

    def test_broken_aliases_and_stranded_cross_references_are_detected(self):
        cases = [
            (self.hub.replace('id="site-visibility-checks"', 'id="lost-checks"'), self.article),
            (self.hub.replace(ROUTE + '#free-visibility-check', ROUTE + '#missing-guide'), self.article),
            (self.hub, self.article.replace('id="site-visibility-limits"', 'id="lost-limits"')),
            (self.hub, self.article.replace('/technology/#small-business-ai-pilot', '#small-business-ai-pilot')),
        ]
        for hub, article in cases:
            with self.subTest(hub_changed=hub != self.hub):
                self.assertTrue(migration_errors(hub, article))

    def test_article_identity_and_dates_preserve_the_original_case(self):
        manifest = json.loads((ROOT / "_source/pages.json").read_text())
        records = [p for p in manifest if p["path"] == ROUTE]
        self.assertEqual(len(records), 1)
        page = records[0]
        self.assertEqual((page["date"], page["updated"]), ("2026-11-03", "2026-11-06"))
        self.assertTrue(page["evidence_article"])
        schemas = [json.loads(t) for t in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        articles = [s for s in schemas if s.get("@type") == "Article"]
        self.assertEqual(len(articles), 1)
        article = articles[0]
        self.assertEqual((article["datePublished"], article["dateModified"]), ("2026-11-03", "2026-11-06"))
        self.assertEqual(article["author"]["@id"], "https://nolankido.com/about/#nolan-kido")
        self.assertIn('rel="canonical" href="' + URL + '"', self.public)
        self.assertIn('datetime="2026-11-03"', self.article)
        self.assertIn('/pull/173', self.article)

    def test_sitemap_and_feeds_have_one_canonical_case(self):
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        entries = [node for node in sitemap if node.findtext("{*}loc") == URL]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].findtext("{*}lastmod"), "2026-11-06")
        for feed in ("technology/feed.xml", "writing.xml"):
            items = ET.fromstring((ROOT / feed).read_text()).findall("./channel/item")
            cases = [item for item in items if item.findtext("link") == URL]
            self.assertEqual(len(cases), 1, feed)
            self.assertEqual(cases[0].findtext("guid"), URL)
            self.assertEqual(str(parsedate_to_datetime(cases[0].findtext("pubDate")).date()), "2026-11-03")
        for output in ("find/index.html", "notes/index.html"):
            self.assertIn('href="' + ROUTE + '"', (ROOT / output).read_text())


if __name__ == "__main__":
    unittest.main()
