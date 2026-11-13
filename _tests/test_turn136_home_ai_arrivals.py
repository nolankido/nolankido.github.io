"""Turn 136: make homepage evidence, free-tool, and AI-method arrivals visible."""

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


HOME_SELECTOR = ".page-home :is(#home-proof-title, #selected-reading-title):target"
METHOD_SELECTOR = (
    ".page-technology #ai-works-human-decides:target #ai-works-human-decides-title"
)


def target_errors(home_css: str, method_css: str) -> list[str]:
    errors = []
    for selector, css in ((HOME_SELECTOR, home_css), (METHOD_SELECTOR, method_css)):
        rules = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", css, re.S)
        if len(rules) != 1:
            errors.append("missing or repeated native arrival style: " + selector)
        elif ("outline: 2px solid var(--red);" not in rules[0]
              or "outline-offset: 4px;" not in rules[0]):
            errors.append("arrival heading lacks a visible red outline: " + selector)
    if ":root { scroll-behavior: auto; }" not in home_css:
        errors.append("homepage native jumps lost reduced-motion-safe behavior")
    return errors


class HomeAiArrivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home_source = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        cls.tech_source = (ROOT / "_source/technology/home.html").read_text(encoding="utf-8")
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.tech = (ROOT / "technology/index.html").read_text(encoding="utf-8")
        cls.home_css = (ROOT / "assets/first-steps.css").read_text(encoding="utf-8")
        cls.tech_css = (ROOT / "assets/practical-ai-path.css").read_text(encoding="utf-8")

    def test_hero_and_mobile_shortcuts_have_unique_native_destinations(self):
        for home in (self.home_source, self.home):
            self.assertEqual(home.count('href="#home-proof-title"'), 1)
            self.assertEqual(home.count('id="home-proof-title"'), 1)
            self.assertEqual(home.count('href="#selected-reading-title"'), 1)
            self.assertEqual(home.count('id="selected-reading-title"'), 1)
            self.assertIn('<h2 class="section-title" id="selected-reading-title">', home)
            self.assertIn('<h2 class="section-title" id="home-proof-title">', home)
            self.assertEqual(home.count('href="/technology/#ai-works-human-decides"'), 1)
        for tech in (self.tech_source, self.tech):
            self.assertEqual(tech.count('id="ai-works-human-decides"'), 1)
            self.assertEqual(tech.count('id="ai-works-human-decides-title"'), 1)
            self.assertRegex(
                tech,
                r'<section[^>]*id="ai-works-human-decides"[^>]*aria-labelledby="ai-works-human-decides-title"',
            )

    def test_only_linked_arrival_headings_receive_scoped_target_styles(self):
        self.assertEqual(target_errors(self.home_css, self.tech_css), [])
        self.assertIn(".page-home", HOME_SELECTOR)
        self.assertIn(".page-technology", METHOD_SELECTOR)
        self.assertNotIn("scroll-margin", self.home_css.split(HOME_SELECTOR, 1)[1].split("}", 1)[0])
        self.assertNotIn("scroll-margin", self.tech_css.split(METHOD_SELECTOR, 1)[1].split("}", 1)[0])

    def test_exact_content_versioned_stylesheets_are_loaded_only_where_needed(self):
        home_version = sha256(self.home_css.encode()).hexdigest()[:12]
        tech_version = sha256(self.tech_css.encode()).hexdigest()[:12]
        self.assertIn(f'/assets/first-steps.css?v={home_version}', self.home)
        self.assertIn(f'/assets/practical-ai-path.css?v={tech_version}', self.tech)
        self.assertNotIn("/assets/practical-ai-path.css", self.home)
        self.assertNotIn("/assets/first-steps.css", self.tech)
        self.assertNotIn("/assets/practical-ai-path.css", (ROOT / "about/index.html").read_text())

    def test_source_build_dates_and_public_identity_remain_unchanged(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path("index.html")], self.home)
        self.assertEqual(outputs[Path("technology/index.html")], self.tech)
        pages = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text())}
        self.assertEqual(pages["/"]["updated"], "2026-11-13")
        self.assertEqual(pages["/technology/"]["updated"], "2026-11-13")
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        dates = {node.findtext("{*}loc"): node.findtext("{*}lastmod") for node in sitemap}
        self.assertEqual(dates["https://nolankido.com/"], "2026-11-13")
        self.assertEqual(dates["https://nolankido.com/technology/"], "2026-11-13")
        for page in (self.home, self.tech):
            self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', page)

    def test_damage_to_target_selectors_or_outlines_is_detected(self):
        variants = (
            (self.home_css.replace(HOME_SELECTOR, HOME_SELECTOR.replace(":target", ":hover")), self.tech_css),
            (self.home_css.replace("outline: 2px solid var(--red);", "outline: none;", 1), self.tech_css),
            (self.home_css, self.tech_css.replace(METHOD_SELECTOR, METHOD_SELECTOR.replace(":target", ":hover"))),
            (self.home_css, self.tech_css.replace("outline-offset: 4px;", "outline-offset: 0;", 1)),
        )
        for home_css, method_css in variants:
            with self.subTest(home_changed=home_css != self.home_css):
                self.assertTrue(target_errors(home_css, method_css))


if __name__ == "__main__":
    unittest.main()
