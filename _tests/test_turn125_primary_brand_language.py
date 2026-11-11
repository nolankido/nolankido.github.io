"""Keep the preferred tagline coherent on identity, search and sharing surfaces."""

import html
import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TAGLINE = "AI Works, Human Decides"
ROUTES = {
    "/": ("index.html", "2026-11-10"),
    "/about/": ("about/index.html", "2026-11-06"),
    "/technology/": ("technology/index.html", "2026-11-06"),
    "/notes/keep-the-judgment/": ("notes/keep-the-judgment/index.html", "2026-11-06"),
}


def current_metadata_errors(page: dict, public: str) -> list[str]:
    errors = []
    for field in ("seo_title", "description"):
        if TAGLINE not in page[field] or "AI Works Human Decides" in page[field]:
            errors.append(field + " does not use the agreed brand phrase")
    if "<title>" + html.escape(page["seo_title"]) + "</title>" not in public:
        errors.append("browser title drifted from the manifest")
    for name in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        if f'<meta {name} content="{html.escape(page["description"], quote=True)}">' not in public:
            errors.append("description metadata drifted: " + name)
    schema = [json.loads(value) for value in re.findall(r'<script type="application/ld\+json">(.*?)</script>', public, re.S)]
    if not schema or not any(item.get("name") == page["seo_title"] and item.get("description") == page["description"] for item in schema):
        errors.append("structured page name or description drifted")
    if 'rel="canonical" href="https://nolankido.com' + page['path'] + '"' not in public:
        errors.append("canonical URL changed")
    return errors


class PrimaryBrandLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = json.loads((ROOT / "_source/site.json").read_text())
        cls.pages = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text())}
        cls.public = {route: (ROOT / path).read_text() for route, (path, _) in ROUTES.items()}

    def test_primary_pages_have_matching_visible_search_and_structured_language(self):
        self.assertEqual(self.site["tagline"], TAGLINE)
        for route in ROUTES:
            with self.subTest(route=route):
                page = self.pages[route]
                self.assertEqual(current_metadata_errors(page, self.public[route]), [])
                self.assertIn(TAGLINE, self.public[route])
        self.assertIn('<p class="hero-copy brand-statement">' + TAGLINE + '</p>', self.public['/'])
        self.assertIn('<h2 class="section-title" id="ai-works-human-decides-title">' + TAGLINE + '</h2>', self.public['/technology/'])
        self.assertIn('<strong>' + TAGLINE + '</strong>', self.public['/about/'])
        self.assertIn('<strong>' + TAGLINE + '</strong>', self.public['/notes/keep-the-judgment/'])
        self.assertIn('id="ai-works-human-decides"', self.public['/technology/'])

    def test_biographies_machine_identity_and_share_descriptions_agree(self):
        self.assertTrue((ROOT / "README.md").read_text().startswith("# Nolan Kido | " + TAGLINE + "\n"))
        for key, file in (("bio_short", "nolan-kido-short-bio.txt"), ("bio_long", "nolan-kido-long-bio.txt")):
            self.assertIn(TAGLINE, self.site[key])
            self.assertEqual((ROOT / "downloads" / file).read_text(), self.site[key] + "\n")
            self.assertIn(html.escape(self.site[key]), (ROOT / "bio/index.html").read_text())
        identity = json.loads((ROOT / "assets/nolan-kido-identity.jsonld").read_text())
        self.assertIn(TAGLINE, json.dumps(identity))
        self.assertIn("Former Chief Operating Officer of Hawaii Dental Clinic and Affiliates", json.dumps(identity))
        self.assertIn("https://nolankido.com/about/#nolan-kido", json.dumps(identity))
        for route in ("/", "/about/"):
            self.assertIn('content="Nolan Kido. ' + TAGLINE + '. Practical AI for real life. nolankido.com."', self.public[route])
            self.assertIn('content="https://nolankido.com/assets/social/nolan-kido-ai.png"', self.public[route])

    def test_copyedit_does_not_republish_existing_pages(self):
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        modified = {entry.findtext("{*}loc"): entry.findtext("{*}lastmod") for entry in sitemap}
        for route, (_, prior_date) in ROUTES.items():
            with self.subTest(route=route):
                self.assertEqual(self.pages[route]["updated"], prior_date)
                self.assertEqual(modified["https://nolankido.com" + route], prior_date)
        self.assertEqual(self.pages["/notes/keep-the-judgment/"]["date"], "2026-10-11")

    def test_old_brand_variant_and_metadata_drift_are_rejected(self):
        page = self.pages["/"]
        public = self.public["/"]
        self.assertTrue(current_metadata_errors({**page, "seo_title": page["seo_title"].replace(TAGLINE, "AI Works Human Decides")}, public))
        self.assertTrue(current_metadata_errors({**page, "description": page["description"].replace(TAGLINE, "AI Works Human Decides")}, public))
        self.assertTrue(current_metadata_errors(page, public.replace('name="description"', 'name="broken-description"', 1)))
        self.assertTrue(current_metadata_errors(page, public.replace('rel="canonical"', 'rel="alternate"', 1)))


if __name__ == "__main__":
    unittest.main()
