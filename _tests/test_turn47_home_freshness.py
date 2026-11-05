"""Keep the homepage's significant content date consistent across public outputs."""

from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
HOME_URL = "https://nolankido.com/"
PERSON_ID = HOME_URL + "about/#nolan-kido"
FIRST_EVIDENCE_REVISION = date(2026, 11, 5)
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.jsonld = []
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_jsonld = True

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld.append(json.loads(data))

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False


def check_home(manifest_text: str, html_text: str, sitemap_text: str):
    manifest = json.loads(manifest_text)
    home = [page for page in manifest if page.get("id") == "home"]
    if len(home) != 1 or home[0].get("path") != HOME_URL.replace("https://nolankido.com", ""):
        raise ValueError("one canonical homepage manifest entry required")
    source_date = date.fromisoformat(home[0]["updated"])
    if source_date < FIRST_EVIDENCE_REVISION:
        raise ValueError("homepage date predates substantive evidence release")

    header = HeadParser()
    header.feed(html_text)
    if header.canonicals != [HOME_URL] or len(header.jsonld) != 1:
        raise ValueError("homepage canonical or structured data changed")
    page = header.jsonld[0]
    if page.get("@type") != "WebPage" or page.get("@id") != HOME_URL + "#webpage":
        raise ValueError("homepage structured identity changed")
    if (page.get("about", {}).get("@id") != PERSON_ID
            or page.get("mainEntity", {}).get("@id") != PERSON_ID
            or page.get("isPartOf", {}).get("publisher", {}).get("@id") != PERSON_ID):
        raise ValueError("Person identity changed")
    try:
        rendered_date = date.fromisoformat(page["dateModified"])
    except (KeyError, ValueError) as exc:
        raise ValueError("homepage dateModified missing or invalid") from exc
    if rendered_date != source_date:
        raise ValueError("home manifest and rendered dateModified disagree")

    tree = ET.fromstring(sitemap_text)
    home_nodes = [entry for entry in tree.findall("s:url", SITEMAP_NS)
                  if entry.findtext("s:loc", namespaces=SITEMAP_NS) == HOME_URL]
    if len(home_nodes) != 1:
        raise ValueError("sitemap must list the homepage exactly once")
    lastmod = home_nodes[0].findtext("s:lastmod", namespaces=SITEMAP_NS)
    if lastmod != source_date.isoformat():
        raise ValueError("home sitemap lastmod and manifest disagree")

    required = [
        'id="home-proof-title"',
        'href="#home-proof-title"',
        "https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x",
        'href="/technology/review-reply-evidence-audit/"',
        'href="/poker/nolan-kido/"',
    ]
    if not all(marker in html_text for marker in required):
        raise ValueError("the November 5 evidence revision is missing")
    return source_date


class HomeFreshnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = (ROOT / "_source/pages.json").read_text(encoding="utf-8")
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        cls.release_date = check_home(cls.manifest, cls.html, cls.sitemap).isoformat()

    def test_three_public_date_signals_agree(self):
        self.assertGreaterEqual(check_home(self.manifest, self.html, self.sitemap),
                                FIRST_EVIDENCE_REVISION)

    def test_stale_manifest_is_rejected(self):
        stale = self.manifest.replace('"updated": "' + self.release_date + '"',
                                      '"updated": "2026-11-03"', 1)
        with self.assertRaisesRegex(ValueError, "predates substantive"):
            check_home(stale, self.html, self.sitemap)

    def test_stale_structured_data_is_rejected(self):
        stale = self.html.replace('"dateModified": "' + self.release_date + '"',
                                  '"dateModified": "2026-11-03"', 1)
        with self.assertRaisesRegex(ValueError, "dateModified disagree"):
            check_home(self.manifest, stale, self.sitemap)

    def test_stale_sitemap_is_rejected(self):
        stale = self.sitemap.replace("<lastmod>" + self.release_date + "</lastmod>",
                                     "<lastmod>2026-11-03</lastmod>", 1)
        with self.assertRaisesRegex(ValueError, "lastmod and manifest disagree"):
            check_home(self.manifest, self.html, stale)

    def test_missing_evidence_or_changed_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "evidence revision is missing"):
            check_home(self.manifest, self.html.replace('id="home-proof-title"',
                                                       'id="outdated-proof-title"', 1),
                       self.sitemap)
        with self.assertRaisesRegex(ValueError, "Person identity changed"):
            check_home(self.manifest, self.html.replace(
                '"@id": "https://nolankido.com/about/#nolan-kido"',
                '"@id": "https://nolankido.com/about/#wrong-person"', 1), self.sitemap)


if __name__ == "__main__":
    unittest.main()
