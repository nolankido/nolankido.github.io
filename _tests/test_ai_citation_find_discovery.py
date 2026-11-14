"""Make the public citation-audit article findable without inventing search results.

Uses the published Find card and the actual offline search matcher.
No network, paid services, visitor data or private analytics.
"""
from __future__ import annotations

from html import escape, unescape
import json
from pathlib import Path
import re
import subprocess
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ROUTE = "/technology/ai-website-visibility/"
OLD = ("Follow Nolan Kido's AI-assisted website changes, public release checks "
       "and a free Search Console method, with search outcomes kept separate from publication.")
QUERIES = ["citation audit", "ChatGPT citation", "AI answer links",
           "Search Console", "SEO", "website improvements"]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def page_record() -> dict:
    return next(p for p in json.loads(read("_source/pages.json"))
                if p["id"] == "ai-website-visibility")


def find_item() -> tuple[str, str, str]:
    document = read("find/index.html")
    pattern = (r'<li class="find-item"(?P<attrs>[^>]*)>'
               r'(?P<body>(?:(?!</li>).)*?<h3><a href="' + re.escape(ROUTE) +
               r'">.*?</a></h3>(?:(?!</li>).)*?)</li>')
    matches = list(re.finditer(pattern, document, flags=re.S))
    if len(matches) != 1:
        raise AssertionError("Expected exactly one public Find result for the citation article.")
    item = matches[0]
    description = re.search(r'<p class="find-description">(.*?)</p>',
                            item["body"], re.S)
    if description is None:
        raise AssertionError("Missing index description")
    return item["attrs"], item["body"], unescape(description.group(1))


class AICitationDiscoveryTests(unittest.TestCase):
    def test_manifest_description_is_specific_without_claiming_performance(self):
        page = page_record()
        self.assertEqual(page["path"], ROUTE)
        self.assertEqual(page["date"], "2026-11-03")
        self.assertEqual(page["updated"], "2026-11-14")
        self.assertEqual(page["find_aliases"], ["SEO", "GEO"])
        desc = page["description"]
        self.assertNotIn(OLD, desc)
        for term in ("Search Console", "ChatGPT citations", "AI-answer links",
                     "offline checker", "website changes"):
            with self.subTest(term=term):
                self.assertIn(term, desc)
        self.assertNotIn("\u2014", desc)
        for invented in ("now ranks", "increased traffic", "verified ChatGPT links",
                         "client results", "published citations achieved"):
            self.assertNotIn(invented, desc.lower())

    def test_generated_page_shares_descriptions_in_metadata(self):
        page = page_record()
        html = read("technology/ai-website-visibility/index.html")
        desc = page["description"]
        escaped = escape(desc, quote=True)
        self.assertIn('<meta name="description" content="' + escaped + '">', html)
        self.assertIn('<meta property="og:description" content="' + escaped + '">', html)
        self.assertIn('<meta name="twitter:description" content="' + escaped + '">', html)
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                             html, flags=re.S)
        self.assertEqual(len(scripts), 1)
        schema = json.loads(scripts[0])
        self.assertEqual(schema["description"], desc)
        self.assertEqual(schema["datePublished"], "2026-11-03")
        self.assertEqual(schema["dateModified"], "2026-11-14")
        self.assertIn('href="#ai-answer-visibility-check"', html)
        self.assertIn('href="/downloads/ai-citation-panel-audit.py"', html)
        self.assertIn('<link rel="canonical" href="https://nolankido.com' + ROUTE + '">', html)

    def test_find_index_card_uses_revised_public_description(self):
        page = page_record()
        attrs, body, description = find_item()
        self.assertEqual(description, page["description"])
        self.assertIn('data-find-aliases="SEO GEO"', attrs)
        self.assertIn('data-search-title="' + escape(page["seo_title"], quote=True) + '"', attrs)
        self.assertIn('>What AI helped change on my website.</a>', body)

    def test_real_find_matcher_returns_citation_guide_for_new_queries(self):
        page = page_record()
        attrs, _, description = find_item()
        record = {
            "path": ROUTE, "title": page["title"],
            "searchTitle": unescape(re.search(r'data-search-title="([^"]+)"', attrs).group(1)),
            "description": description,
            "subjects": "Technology",
            "aliases": unescape(re.search(r'data-find-aliases="([^"]+)"', attrs).group(1)),
            "sections": [],
        }
        script = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {score} = require('./assets/site-find.js');
const record = JSON.parse(fs.readFileSync(0, 'utf8'));
for (const query of ['citation audit', 'ChatGPT citation', 'AI answer links',
                      'Search Console', 'SEO', 'website improvements']) {
  assert(score(record, query) >= 0, 'Missing visible result for ' + query);
}
for (const query of ['private client revenue', 'unrelated nonsense']) {
  assert.equal(score(record, query), -1);
}
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT, input=json.dumps(record),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_feeds_preserve_original_publication_and_new_summary(self):
        expected = page_record()["description"]
        for relative in ("technology/feed.xml", "writing.xml"):
            with self.subTest(file=relative):
                channel = ET.fromstring(read(relative)).find("channel")
                self.assertIsNotNone(channel)
                items = [item for item in channel.findall("item")
                         if item.findtext("link") == "https://nolankido.com" + ROUTE]
                self.assertEqual(len(items), 1)
                item = items[0]
                self.assertEqual(item.findtext("description"), expected)
                self.assertEqual(item.findtext("guid"), "https://nolankido.com" + ROUTE)
                self.assertIn("03 Nov 2026", item.findtext("pubDate"))
        sitemap = ET.fromstring(read("sitemap.xml"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        matches = [row for row in sitemap.findall(ns + "url")
                   if row.findtext(ns + "loc") == "https://nolankido.com" + ROUTE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext(ns + "lastmod"), "2026-11-14")


if __name__ == "__main__":
    unittest.main()
