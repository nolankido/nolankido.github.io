"""Turn 68: help practical-AI readers find the existing no-cost workflow pilot.

This is a source-backed user journey, not a new landing page, measured
productivity gain, SEO ranking assertion, or external data transfer.
"""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

PILOT = "/technology/ai-workflow-pilot/#pilot-protocol"
HOME_SOURCE = Path("_source/home.html")
HOME_PUBLIC = Path("index.html")
START_SOURCE = Path("_source/start-here.html")
START_PUBLIC = Path("start-here/index.html")
HOME_CLASS = "practical-home-pilot"
START_CLASS = "start-pilot-route"


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.ids = [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if data.get("id"):
            self.ids.append(data["id"])


def contextual_block(source, label):
    matches = re.findall(r'<p class="small-copy ' + label + r'">.*?</p>', source, re.S)
    if len(matches) != 1:
        raise ValueError("Missing or duplicated reader pilot route")
    return matches[0]


def pilot_route_issues(source, label):
    try:
        block = contextual_block(source, label)
    except ValueError:
        return ["missing or duplicated pilot block"]
    issues = []
    if block.count('href="' + PILOT + '"') != 1:
        issues.append("missing or incorrect full pilot destination")
    if label == HOME_CLASS and "Will AI save your business time?" not in block:
        issues.append("missing concrete business question")
    if label == START_CLASS and "Running a small business?" not in block:
        issues.append("missing business reader intent")
    if "fictional" not in block or "not measured" not in block:
        issues.append("unproven example presented without limitation")
    if any(token in block for token in ("onclick=", "<script", "guaranteed ROI", "measured client savings", chr(0x2014))):
        issues.append("unsafe claim or non-native interaction")
    return issues


class Turn68WorkflowPilotDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home_source = (ROOT / HOME_SOURCE).read_text(encoding="utf-8")
        cls.home_public = (ROOT / HOME_PUBLIC).read_text(encoding="utf-8")
        cls.start_source = (ROOT / START_SOURCE).read_text(encoding="utf-8")
        cls.start_public = (ROOT / START_PUBLIC).read_text(encoding="utf-8")
        cls.pilot = (ROOT / "technology/ai-workflow-pilot/index.html").read_text(encoding="utf-8")

    def test_one_explanatory_route_on_home_and_start_with_source_parity(self):
        for source, public, label in (
            (self.home_source, self.home_public, HOME_CLASS),
            (self.start_source, self.start_public, START_CLASS),
        ):
            with self.subTest(label=label):
                self.assertEqual(pilot_route_issues(source, label), [])
                self.assertEqual(pilot_route_issues(public, label), [])
                self.assertEqual(contextual_block(source, label), contextual_block(public, label))
                self.assertEqual(Elements(source).links.count(PILOT), 1)
                self.assertEqual(Elements(public).links.count(PILOT), 1)

    def test_real_worksheet_and_quality_protocol_without_client_claims(self):
        self.assertEqual(Elements(self.pilot).ids.count("pilot-protocol"), 1)
        for expected in (
            "a completely fictional six-case demonstration",
            "/downloads/ai-workflow-pilot-blank.csv",
            "not a report that my clients adopted AI",
        ):
            self.assertIn(expected, self.pilot)
        for source in (self.home_source, self.start_source):
            self.assertNotIn("clients saved", contextual_block(
                source, HOME_CLASS if source == self.home_source else START_CLASS))

    def test_first_screen_and_existing_task_choices_remain_intact(self):
        home = self.home_public
        self.assertLess(home.index('data-home-choice="understand"'), home.index('class="small-copy practical-home-pilot"'))
        self.assertLess(home.index('class="small-copy practical-home-pilot"'), home.index('<details class="practical-home">'))
        self.assertEqual(len(re.findall(r'data-home-choice="(use|inspect|understand)"', home)), 3)
        self.assertEqual(len(re.findall(r'<nav class="link-row identity-actions".*?</nav>', home, re.S)), 1)
        details = re.search(r'<details class="practical-home">.*?</details>', home, re.S)
        self.assertIsNotNone(details)
        self.assertEqual(len(re.findall(r'<a\b', details.group())), 6)
        task = re.search(r'<ul class="task-route-list">.*?</ul>', self.start_public, re.S)
        self.assertIsNotNone(task)
        self.assertEqual(task.group().count('<li>'), 4)
        self.assertLess(self.start_public.index(task.group()), self.start_public.index('class="small-copy start-pilot-route"'))
        self.assertLess(self.start_public.index('class="small-copy start-pilot-route"'),
                        self.start_public.index('Looking for a blank worksheet or calculator?'))

    def test_dates_canonicals_and_sitemap_match_substantive_linking_change(self):
        manifest = json.loads((ROOT / "_source/pages.json").read_text(encoding="utf-8"))
        by_path = {page["path"]: page for page in manifest}
        for route, public in (("/", self.home_public), ("/start-here/", self.start_public)):
            with self.subTest(route=route):
                self.assertEqual(by_path[route]["updated"], "2026-11-21")
                self.assertIn('"dateModified": "2026-11-21"', public)
                self.assertEqual(public.count('rel="canonical" href="https://nolankido.com' + route + '"'), 1)
        xml = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual(len(list(xml)), 230)
        for route in ("/", "/start-here/"):
            rows = [node for node in xml if node.findtext("{*}loc") == "https://nolankido.com" + route]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].findtext("{*}lastmod"), "2026-11-21")
        self.assertEqual(by_path["/technology/ai-workflow-pilot/"]["updated"], "2026-11-20")

    def test_current_generator_produces_both_unchanged_public_shapes(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[HOME_PUBLIC], self.home_public)
        self.assertEqual(outputs[START_PUBLIC], self.start_public)
        self.assertEqual(outputs[Path("sitemap.xml")],
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

    def test_broken_destination_or_unsupported_roi_claim_is_detected(self):
        for source, label in ((self.home_source, HOME_CLASS), (self.start_source, START_CLASS)):
            for bad in (
                source.replace(PILOT, "/technology/unknown-pilot/#missing", 1),
                source.replace(contextual_block(source, label),
                               contextual_block(source, label).replace(
                                   "fictional", "independently measured", 1), 1),
                source.replace('class="small-copy ' + label + '"',
                               'class="small-copy deleted-pilot"', 1),
                source + contextual_block(source, label),
            ):
                with self.subTest(label=label):
                    self.assertTrue(pilot_route_issues(bad, label))

    def test_no_extra_automation_or_tracking_added(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn68_workflow_pilot_discovery.py", runner)
        for source in (self.home_source, self.start_source):
            block = contextual_block(source, HOME_CLASS if source == self.home_source else START_CLASS)
            self.assertNotIn("<script", block)
            self.assertNotIn("utm_", block)
        workflows = ROOT / ".github/workflows"
        self.assertFalse(workflows.exists() and any(
            p.is_file() and p.suffix.lower() in {".yml", ".yaml"} for p in workflows.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
