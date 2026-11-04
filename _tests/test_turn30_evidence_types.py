"""Turn 30: a readable evidence-by-type index, not a new authority claim."""
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
import turn31_episode_ledger_history as turn31

SOURCE = ROOT / "_source/start-here.html"
PUBLIC = ROOT / "start-here/index.html"
ABOUT_SOURCE = ROOT / "_source/about.html"
ABOUT_PUBLIC = ROOT / "about/index.html"
SECTION = '<section class="section folio-row" id="evidence-types"'
ORIGIN = "https://nolankido.com"
CATEGORIES = (
    "Working browser tool:",
    "Public software and demonstration:",
    "Recorded AI-assisted task:",
    "Peer-reviewed scholarship:",
    "Tournament records and first-person video:",
    "Essay or viewpoint:",
    "Proposed exercise:",
)
LINKS = (
    "/technology/ai-time-savings/",
    "/technology/local-ai-review-replies/",
    "/technology/ai-book-continuity-checker/",
    "/technology/organize-public-notes/#notes-repro-audit",
    "https://doi.org/10.1111/j.1475-679X.2012.00447.x",
    "/poker/nolan-kido/",
    "/notes/keep-the-judgment/",
    "/living-well/field-notes/",
)


class Tags(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if "id" in props:
            self.ids.append(props["id"])
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unbalanced evidence index element: " + tag)


def section(body):
    if body.count(SECTION) != 1:
        raise AssertionError("Missing or duplicated evidence-by-type section")
    offset = body.index(SECTION)
    return body[offset:body.index("</section>", offset) + len("</section>")]


class EvidenceByTypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.public = PUBLIC.read_text(encoding="utf-8")
        cls.about = ABOUT_PUBLIC.read_text(encoding="utf-8")

    def test_original_and_published_index_are_identical_semantic_html(self):
        content = section(self.public)
        self.assertEqual(content, section(self.source))
        self.assertIn('aria-labelledby="evidence-types-title"', content)
        self.assertIn('<h2 class="section-title" id="evidence-types-title">What kind of evidence is this?</h2>', content)
        self.assertIn('<ul class="task-route-list evidence-type-list"', content)
        self.assertEqual(content.count("<li>"), 7)
        self.assertEqual(content.count("</li>"), 7)
        self.assertEqual(content.count("<strong>"), 7)
        self.assertNotIn("<table", content)
        self.assertNotIn("<script", content)
        self.assertNotIn("<iframe", content)
        self.assertNotIn("\u2014", content)
        parser = Tags()
        parser.feed(content)
        self.assertEqual(parser.stack, [])
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertLess(self.public.index("id=\"start-projects-title\""),
                        self.public.index("id=\"evidence-types\""))
        self.assertLess(self.public.index("id=\"evidence-types\""),
                        self.public.index("id=\"start-routes-title\""))

    def test_types_are_distinct_and_limits_not_buried(self):
        content = section(self.public)
        self.assertTrue(all(content.count(kind) == 1 for kind in CATEGORIES))
        self.assertIn("No AI model", content.replace("no model", "No AI model"))
        for phrase in ("does not establish", "does not authenticate",
                       "does not establish an AI benchmark", "not net profit",
                       "not a controlled study", "not a completed personal experiment"):
            self.assertIn(phrase.lower(), content.lower())
        for url in LINKS:
            self.assertEqual(content.count('href="' + url + '"'), 1, url)

    def test_all_local_examples_are_existing_pages_and_fragments(self):
        for href in LINKS:
            if not href.startswith("/"):
                continue
            path, sep, fragment = href.partition("#")
            relative = ROOT / path.lstrip("/") / "index.html"
            self.assertTrue(relative.is_file(), href)
            page = relative.read_text(encoding="utf-8")
            self.assertIn('<link rel="canonical" href="' + ORIGIN + path + '">', page)
            if sep:
                self.assertEqual(page.count('id="' + fragment + '"'), 1)

    def test_about_links_to_map_without_changing_primary_proof_or_schema(self):
        current = self.about
        self.assertEqual(current.count('href="/start-here/#evidence-types"'), 1)
        self.assertEqual(ABOUT_SOURCE.read_text().count('href="/start-here/#evidence-types"'), 1)
        self.assertLess(current.index('id="about-evidence-title"'),
                        current.index('href="/start-here/#evidence-types"'))
        for marker in ("about-evidence-list", "https://onlinelibrary.wiley.com/doi/",
                       "/technology/local-ai-review-replies/", "/poker/nolan-kido/"):
            self.assertIn(marker, current)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', current).group(1))
        person = schema["mainEntity"]
        self.assertEqual(person["@id"], ORIGIN + "/about/#nolan-kido")
        self.assertEqual(set(person), {"@type", "@id", "name", "url", "description", "sameAs"})

    def test_entry_choices_and_copy_are_preserved(self):
        page = self.public
        self.assertEqual(page.count('class="entry-card"'), 4)
        self.assertEqual(page.count('class="identity-reading"'), 3)
        self.assertIn('href="#evidence-types">Check the evidence</a>', page)
        previous = subprocess.check_output(
            ["git", "show", "c259d366176f3411e89777646135262178cc75b3:start-here/index.html"],
            cwd=ROOT
        ).decode("utf-8")
        for route in ("/technology/task-brief/", "/technology/check-ai-answers/",
                      "/living-well/weekly-reset/", "/poker/first-live-tournament/"):
            self.assertEqual(page.count('href="' + route + '"'),
                             previous.count('href="' + route + '"'), route)
        self.assertIn('id="study-interest"', page)
        self.assertIn("plans, not completed results", page)

    def test_modified_date_is_true_and_sitemap_scope_is_one_url(self):
        pages = build.public_pages()
        start = next(p for p in pages if p["id"] == "start-here")
        about = next(p for p in pages if p["id"] == "about")
        self.assertEqual(start["updated"], "2026-11-04")
        self.assertEqual(about["updated"], "2026-11-04")
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.public).group(1))
        self.assertEqual(schema["dateModified"], "2026-11-04")
        self.assertIn('<link rel="canonical" href="' + ORIGIN + '/start-here/">', self.public)
        old_xml = subprocess.check_output(["git", "show",
            "c259d366176f3411e89777646135262178cc75b3:sitemap.xml"], cwd=ROOT
        ).decode("utf-8")
        new_xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        def rows(xml):
            root = ET.fromstring(xml)
            return {item.findtext(ns + "loc"): item.findtext(ns + "lastmod") for item in root}
        older, newer = rows(old_xml), rows(turn31.before("sitemap.xml", new_xml))
        self.assertEqual(set(older), set(newer))
        self.assertEqual({url for url in older if older[url] != newer[url]},
                         {ORIGIN + "/start-here/"})
        self.assertEqual(newer[ORIGIN + "/start-here/"], "2026-11-04")

    def test_generated_pages_and_sitemap_match_sources(self):
        outputs = build.build_outputs()
        for path in ("start-here/index.html", "about/index.html", "sitemap.xml"):
            with self.subTest(path=path):
                self.assertEqual(outputs[Path(path)],
                                 (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
