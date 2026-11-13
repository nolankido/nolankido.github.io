"""Turn 134: wine and games are public interests, not invented proof of expertise."""

from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


HOBBY_ID = "wine-games-and-life"
HOBBY_HEADING = f'<h2 id="{HOBBY_ID}">Wine, games, and the rest of life</h2>'
HOBBY_LINK = f'href="/about/#{HOBBY_ID}"'
HOBBY_GUARDS = (
    "A wine note starts with what I actually taste; a game needs playtesting.",
    "AI might help organize observations or suggest questions",
    "it cannot supply the experience or make the judgment for me.",
    "not claims to wine credentials, public game releases, or verified AI outcomes.",
    "Some work and much of ordinary life belong outside a public website.",
)
PRIVATE_PROJECT_NAMES = ("federation", "idlecolor", "bitegrove", "byte garden")


def about_hobby(html: str) -> str:
    match = re.search(
        re.escape(HOBBY_HEADING) + r"(.*?)<h2 id=\"public-ai-projects\">",
        html, re.S,
    )
    return match.group(1) if match else ""


def home_connection(html: str) -> str:
    match = re.search(
        r'<section class="section folio-row home-connection"[^>]*>(.*?)</section>',
        html, re.S,
    )
    return match.group(1) if match else ""


def bridge_errors(about: str, home: str) -> list[str]:
    errors = []
    hobby = about_hobby(about)
    connection = home_connection(home)
    if about.count(HOBBY_HEADING) != 1 or not hobby:
        errors.append("missing unique native About destination")
    if not connection or home.count(HOBBY_LINK) != 1:
        errors.append("homepage lacks the unique native interest route")
    if hobby.count("<p>") != 2:
        errors.append("About interest section lost its readable scope and limits")
    if not all(phrase in hobby for phrase in HOBBY_GUARDS):
        errors.append("experience, human judgment or honest limits missing")
    for phrase in ("Wine tasting, making games", "asking whether a tool helped"):
        if phrase not in connection:
            errors.append("homepage interest statement missing: " + phrase)
    for topic in ("wine", "game", "AI", "playtesting"):
        if topic.casefold() not in hobby.casefold():
            errors.append("missing hobby topic: " + topic)
    for private_name in PRIVATE_PROJECT_NAMES:
        if private_name in (hobby + connection).casefold():
            errors.append("private prototype name exposed: " + private_name)
    if "github.com/nolankido/" in hobby + connection:
        errors.append("a private game repository has been linked")
    if "\u2014" in hobby + connection:
        errors.append("prohibited em dash in new public copy")
    return errors


class HobbyIdentityBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.about_source = (ROOT / "_source/about.html").read_text(encoding="utf-8")
        cls.about_public = (ROOT / "about/index.html").read_text(encoding="utf-8")
        cls.home_source = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        cls.home_public = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/about-reader.css").read_text(encoding="utf-8")

    def test_home_route_lands_on_bounded_about_interest_description(self):
        for about, home in (
            (self.about_source, self.home_source),
            (self.about_public, self.home_public),
        ):
            self.assertEqual(bridge_errors(about, home), [])
            self.assertEqual(about.count('id="' + HOBBY_ID + '"'), 1)

    def test_native_target_is_visible_without_scripts_or_animation(self):
        selector = ".page-about #wine-games-and-life:target"
        rules = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", self.css)
        self.assertEqual(len(rules), 1)
        self.assertIn("outline: 2px solid var(--red);", rules[0])
        self.assertIn("outline-offset: 4px;", rules[0])
        self.assertIn(".page-about h2[id] { scroll-margin-top: 2rem; }", self.css)
        self.assertIn(".page-about h2[id] { scroll-margin-top: 7rem; }", self.css)
        version = sha256((ROOT / "assets/about-reader.css").read_bytes()).hexdigest()[:12]
        self.assertIn(f'href="/assets/about-reader.css?v={version}"', self.about_public)
        self.assertNotIn("/assets/about-reader.css", self.home_public)

    def test_find_directory_exposes_native_wine_and_games_section(self):
        find_page = (ROOT / "find/index.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script type="application/json" id="find-section-data">(.*?)</script>',
            find_page, re.S,
        )
        self.assertIsNotNone(match)
        records = json.loads(match.group(1))["pages"]["about"][""]
        self.assertEqual(records.count(HOBBY_ID), 1)
        self.assertEqual(records[records.index(HOBBY_ID) + 1], "Wine, games, and the rest of life")

    def test_home_and_about_rebuild_without_metadata_or_date_freshness_claims(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("about/index.html")], self.about_public)
        self.assertEqual(outputs[Path("index.html")], self.home_public)
        pages = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text())}
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        dates = {n.findtext("{*}loc"): n.findtext("{*}lastmod") for n in sitemap}
        for route, previous in (("/", "2026-11-13"), ("/about/", "2026-11-13")):
            self.assertEqual(pages[route]["updated"], previous)
            self.assertEqual(dates["https://nolankido.com" + route], previous)
            self.assertIn('rel="canonical" href="https://nolankido.com' + route + '"',
                          self.home_public if route == "/" else self.about_public)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.about_public)
        self.assertIn("AI Works, Human Decides", self.home_public)

    def test_rejects_broken_links_unsupported_claims_and_private_project_names(self):
        self.assertTrue(bridge_errors(self.about_source.replace(HOBBY_HEADING, "", 1), self.home_source))
        self.assertTrue(bridge_errors(self.about_source, self.home_source.replace(HOBBY_LINK, 'href="/about/"', 1)))
        self.assertTrue(bridge_errors(self.about_source.replace(HOBBY_GUARDS[3], "Certified sommelier and successful game publisher.", 1), self.home_source))
        self.assertTrue(bridge_errors(self.about_source.replace("building games", "building Federation", 1), self.home_source))
        self.assertNotIn(":target", self.css.replace("#wine-games-and-life:target", "#wine-games-and-life:hover", 1).split("#wine-games-and-life:hover", 1)[1].split("}", 1)[0])


if __name__ == "__main__":
    unittest.main()
