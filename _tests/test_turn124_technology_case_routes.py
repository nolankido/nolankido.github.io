"""The Technology method sends readers directly to two distinct release cases."""

import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
VISIBILITY = "/technology/ai-website-visibility/"
VERIFICATION = "/technology/checking-ai-website-changes/"
METHOD = 'id="ai-works-human-decides"'


def method_section(page: str) -> str:
    sections = page.split('<section class="section folio-row" ' + METHOD, 1)
    return sections[1].split("</section>", 1)[0] if len(sections) == 2 else ""


def route_errors(page: str) -> list[str]:
    section = method_section(page)
    if not section:
        return ["method section missing"]
    errors = []
    for route in (VISIBILITY, VERIFICATION):
        if section.count('href="' + route + '"') != 1:
            errors.append("missing or duplicated direct case route: " + route)
    if 'href="#site-visibility-evidence"' in section:
        errors.append("method still sends readers to the intermediate hub teaser")
    comparison = re.findall(r"<p><strong>Verification and impact require different evidence\.</strong>(.*?)</p>", section, re.S)
    if len(comparison) != 1:
        errors.append("one contextual comparison paragraph required")
        return errors
    for detail in ("October 11", "347 passing tests", "HTML5 parser", "separate",
                   "free Search Console method", "search outcomes unmeasured", "Neither establishes higher rankings"):
        if detail not in comparison[0]:
            errors.append("release identity or impact boundary lost: " + detail)
    if comparison[0].count("href=") != 2:
        errors.append("comparison must expose exactly the two article destinations")
    return errors


class TechnologyCaseRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/technology/home.html").read_text()
        cls.public = (ROOT / "technology/index.html").read_text()

    def test_method_links_the_two_real_cases_directly(self):
        for page in (self.source, self.public):
            with self.subTest(generated=page is self.public):
                self.assertEqual(route_errors(page), [])
        for route in (VISIBILITY, VERIFICATION):
            self.assertTrue((ROOT / route.lstrip("/") / "index.html").exists())
        # Retain the old Technology bookmark for existing incoming links.
        self.assertIn('id="site-visibility-evidence"', self.source)
        self.assertIn('href="' + VISIBILITY + '"', self.source)

    def test_minor_reader_path_edit_keeps_existing_freshness_dates(self):
        manifest = json.loads((ROOT / "_source/pages.json").read_text())
        dates = {page["path"]: page.get("updated", page.get("date")) for page in manifest}
        self.assertEqual(dates["/technology/"], "2026-11-06")
        self.assertEqual(dates[VISIBILITY], "2026-11-06")
        self.assertEqual(dates[VERIFICATION], "2026-10-11")
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        modified = {item.findtext("{*}loc"): item.findtext("{*}lastmod") for item in sitemap}
        for route in ("/technology/", VISIBILITY, VERIFICATION):
            self.assertEqual(modified["https://nolankido.com" + route], dates[route])

    def test_misdirected_links_and_inflated_conclusions_are_detected(self):
        variants = (
            self.source.replace('href="' + VISIBILITY + '"', 'href="#site-visibility-evidence"', 1),
            self.source.replace('href="' + VERIFICATION + '"', 'href="#site-visibility-evidence"', 1),
            self.source.replace("search outcomes unmeasured", "search outcomes improved", 1),
            self.source.replace("October 11", "November 11", 1),
            self.source.replace("Neither establishes higher rankings", "Both establish higher rankings", 1),
        )
        for index, variant in enumerate(variants):
            with self.subTest(variant=index):
                self.assertTrue(route_errors(variant))


if __name__ == "__main__":
    unittest.main()
