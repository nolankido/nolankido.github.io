"""Turn 50: first-screen practical AI emphasis and inspectable work routes.

Offline source and generated HTML checks do not certify mobile rendering,
search ranking, visitor behavior, or current deployment.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPAIR = "/technology/checking-ai-website-changes/"
TOOL = "/technology/task-brief/"
PROJECT_EVIDENCE = "/projects/#projects-checks"
HOME_NAV = re.compile(r'<nav class="link-row identity-actions"[^>]*>.*?</nav>', re.S)
ABOUT_NAV = re.compile(r'<nav class="link-row about-first-proof"[^>]*>.*?</nav>', re.S)


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class Anchors(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
        self.ids = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "a" and attr.get("href"):
            self.hrefs.append(attr["href"])
        if attr.get("id"):
            self.ids.append(attr["id"])


def home_errors(html: str) -> list[str]:
    match = HOME_NAV.findall(html)
    if len(match) != 1:
        return ["Need exactly one homepage hero action row"]
    nav = match[0]
    routes = re.findall(r'<a\\b[^>]*href="([^"]+)"', nav)
    errors = []
    if routes != [REPAIR, TOOL, "#home-proof-title"]:
        errors.append("First-screen tasks do not prefer documented AI repair, free tool, and evidence")
    if nav.count('class="button"') != 1 or nav.count('class="text-link"') != 2:
        errors.append("Need one primary action and two secondary actions")
    if "Inspect a documented AI repair" not in nav or "Try a free AI tool" not in nav:
        errors.append("No clear task-based link labels")
    if len(re.findall(r'<a\\b', nav)) != 3:
        errors.append("Too many hero choices")
    if "<script" in nav or "onclick=" in nav:
        errors.append("Hero actions must be native links")
    for target in ("home-proof-title", "selected-reading-title"):
        if Anchors(html).ids.count(target) != 1:
            errors.append("Missing unique target: " + target)
    return errors


def about_errors(html: str) -> list[str]:
    match = ABOUT_NAV.findall(html)
    if len(match) != 1:
        return ["Need exactly one early About proof route"]
    nav = match[0]
    links = re.findall(r'<a\\b[^>]*href="([^"]+)"', nav)
    errors = []
    if links != [REPAIR, PROJECT_EVIDENCE]:
        errors.append("About routes must target recorded AI repair and project evidence")
    if nav.count('class="button"') != 1 or nav.count('class="text-link"') != 1:
        errors.append("About must have one primary proof action")
    if not (html.index('class="intro"') < html.index(nav) < html.index('id="who-is-nolan-kido"')):
        errors.append("About proof links must follow the lead and precede the long identity section")
    if "Inspect a documented AI repair" not in nav:
        errors.append("Primary about evidence action mislabeled")
    if "<script" in nav or "onclick=" in nav:
        errors.append("About proof actions must be native links")
    return errors


class FirstScreenIdentityTests(unittest.TestCase):
    def test_home_hero_promotes_three_distinct_useful_actions(self):
        src, generated = text("_source/home.html"), text("index.html")
        for html in (src, generated):
            self.assertEqual(home_errors(html), [])
        self.assertEqual(HOME_NAV.search(src).group(), HOME_NAV.search(generated).group())
        self.assertIn('href="/poker/"', generated, "Poker remains in primary site navigation")
        self.assertIn('href="/about/"', generated, "About remains in primary site navigation")

    def test_about_early_proof_is_direct_and_preserves_source(self):
        src, generated = text("_source/about.html"), text("about/index.html")
        for html in (src, generated):
            self.assertEqual(about_errors(html), [])
        self.assertEqual(ABOUT_NAV.search(src).group(), ABOUT_NAV.search(generated).group())
        self.assertEqual(Anchors(text("projects/index.html")).ids.count("projects-checks"), 1)
        self.assertIn("Checking an AI-assisted website change", text("technology/checking-ai-website-changes/index.html"))

    def test_canonicals_author_identity_and_evidence_types_remain(self):
        home, about = text("index.html"), text("about/index.html")
        for html, route in ((home, "/"), (about, "/about/")):
            self.assertEqual(html.count('rel="canonical" href="https://nolankido.com' + route + '"'), 1)
            self.assertEqual(len(re.findall(r'<h1\\b', html)), 1)
        record = re.search(r'<script type="application/ld\\+json">(.*?)</script>', about, re.S)
        self.assertIsNotNone(record)
        schema = json.loads(record.group(1))
        self.assertEqual(schema["mainEntity"]["@id"], "https://nolankido.com/about/#nolan-kido")
        for boundary in ("2012", "not independently measured client results",
                         "Tournament cashes are gross results, not profit"):
            self.assertIn(boundary, about)
        self.assertIn("AI Works, Human Decides", home)
        self.assertIn("AI Works, Human Decides", about)

    def test_manifest_dates_not_changed_for_same_day_navigation(self):
        pages = {p["path"]: p for p in json.loads(text("_source/pages.json"))}
        self.assertEqual(pages["/"]["updated"], "2026-11-20")
        self.assertEqual(pages["/about/"]["updated"], "2026-11-20")

    def test_existing_shared_accessible_link_style_without_custom_js(self):
        css = text("assets/site-core.css")
        self.assertIn(".link-row { display: flex; flex-wrap: wrap;", css)
        self.assertIn(".text-link, .button { display: inline-flex;", css)
        self.assertIn("min-height: 44px", css)
        for html in (text("_source/home.html"), text("_source/about.html")):
            self.assertNotIn(chr(0x2014), html)

    def test_removed_main_action_or_wrong_target_fails(self):
        home, about = text("index.html"), text("about/index.html")
        self.assertTrue(home_errors(home.replace(REPAIR, "/missing-repair/", 1)))
        self.assertTrue(home_errors(home.replace('href="#home-proof-title"', 'href="#missing-proof"', 1)))
        self.assertTrue(about_errors(about.replace(PROJECT_EVIDENCE, "/missing-project/", 1)))
        self.assertTrue(about_errors(about.replace('class="button"', 'class="text-link"', 1)))

    def test_local_release_registers_regression_without_actions(self):
        runner = text("_scripts/local_release_checks.py")
        self.assertIn("test_turn50_first_screen_identity.py", runner)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml") for p in workflows.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
