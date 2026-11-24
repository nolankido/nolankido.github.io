"""Turn 110: staged third author page and its current public evidence handoff."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "_reports/book-discovery/ai-works-human-decides-author-page-candidate.html"
URL = "https://nolankido.com/books/ai-works-human-decides/"

class Tags(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])

class StagedAuthorPageTests(unittest.TestCase):
    def test_candidate_identity_and_no_false_edition_data(self):
        html = CANDIDATE.read_text(encoding="utf-8")
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(schema["url"], URL)
        self.assertEqual(schema["mainEntity"]["@id"], URL + "#book")
        self.assertEqual(schema["mainEntity"]["author"]["@id"], "https://nolankido.com/about/#nolan-kido")
        for field in ("isbn", "offers", "datePublished", "bookFormat", "aggregateRating"):
            self.assertNotIn(field, schema["mainEntity"])
        self.assertEqual(html.count('<link rel="canonical" href="' + URL + '">'), 1)
        self.assertEqual(html.count("<h1"), 1)
        self.assertEqual(html.count("<main "), 1)
        self.assertNotIn("cloud.umami.is", html)
        self.assertIn("not independently verified", html)

    def test_candidate_fragments_and_source_links(self):
        html = CANDIDATE.read_text(encoding="utf-8")
        tags = Tags(html)
        self.assertEqual(len(tags.ids), len(set(tags.ids)))
        for link in tags.links:
            if link.startswith("#"):
                self.assertIn(link[1:], tags.ids)
            elif link.startswith("/") and "#" in link:
                route, fragment = link.split("#", 1)
                target = ROOT / route.strip("/") / "index.html"
                self.assertTrue(target.is_file(), route)
                self.assertIn(fragment, Tags(target.read_text(encoding="utf-8")).ids)
        self.assertIn("not a real transaction or a verified chapter excerpt", html)
        self.assertIn("$480 + $36", html)
        self.assertEqual(480 + 36 - 500, 16)

    def test_catalog_evidence_handoff_and_integrated_route(self):
        source = (ROOT / "_source/books/index.html").read_text(encoding="utf-8")
        public = (ROOT / "books/index.html").read_text(encoding="utf-8")
        self.assertEqual(source, public)
        self.assertIn('href="/technology/local-ai-review-replies/#reply-failure"', public)
        self.assertIn('href="/technology/checking-ai-website-changes/#case-evidence"', public)
        self.assertIn('href="/books/ai-works-human-decides/"', public)
        self.assertIn(URL, (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / "books/ai-works-human-decides/index.html").read_text(encoding="utf-8"),
                         (ROOT / "_source/books/ai-works-human-decides.html").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
