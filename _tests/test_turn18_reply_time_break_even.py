"""Turn 18: human-review time, real missing data, and fictional break-even parity."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import check_live

ROUTE = "/technology/ai-time-savings/"
URL = "https://nolankido.com" + ROUTE
SECTION = "reply-time-break-even"
LOG = "/downloads/review-reply-time-break-even.md"
PIN = "1c5e0487c331d5202410c9f342557d9355951c3a"


class PageLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))


def bounded_section(html):
    prefix = f'<section class="section folio-row" id="{SECTION}"'
    parts = html.split(prefix, 1)
    return parts[1].split("</section>", 1)[0] if len(parts) == 2 else ""


def evidence_errors(html):
    section = bounded_section(html)
    if not section:
        return ["missing grounded review-reply time answer"]
    errors = []
    links = PageLinks(section).hrefs
    for target in (
        LOG,
        "#time-workspace",
        "/technology/local-ai-review-replies/",
        "/technology/local-ai-review-replies/#reply-owner-gate",
        "/technology/review-reply-evidence-audit/#reply-audit-reading-checks",
        "/technology/ai-workflow-pilot/#pilot-kit",
        f"https://github.com/nolankido/reviewReplyWriter/blob/{PIN}/examples/evaluation/live-quality-smoke-2026-10-13.json",
    ):
        if links.count(target) != 1:
            errors.append("source or comparison route missing: " + target)
    for marker in (
        "Not established by a fast model response",
        "19.536 seconds",
        "18.157 seconds",
        "19.325 seconds",
        "not a current MSI laptop run",
        "no paired manual-drafting baseline",
        "cannot be called measured <em>time saved</em>",
        "Invented planning inputs, not the archived Gemma timings",
        "60 minutes",
        "75 minutes",
        "15 extra minutes",
        "Twenty-five repetitions exactly recover",
        "reply 26",
        "review instead takes 4 minutes",
        "cannot recover that overhead",
        "No new model inference",
        "Unknown review time is unknown, not zero",
    ):
        if marker not in section:
            errors.append("missing measurement or inference boundary: " + marker)
    if "\u2014" in section:
        errors.append("em dash in new section")
    return errors


class ReplyTimeBreakEvenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/technology/ai-time-savings.html").read_text()
        cls.public = (ROOT / "technology/ai-time-savings/index.html").read_text()
        cls.worksheet = (ROOT / LOG.lstrip("/")).read_text()

    def test_case_and_hub_links_are_built_without_duplicate_sections(self):
        for html in (self.source, self.public):
            with self.subTest(generated=html is self.public):
                self.assertEqual(evidence_errors(html), [])
                ids = PageLinks(html).ids
                for ident in ("time-intro", "time-workspace", "time-examples", SECTION,
                              SECTION + "-title", SECTION + "-example", "time-method", "time-worksheet"):
                    self.assertEqual(ids.count(ident), 1, ident)
                self.assertIn('href="#' + SECTION + '"', html)
                self.assertLess(html.find('id="time-examples"'), html.find('id="' + SECTION + '"'))
                self.assertLess(html.find('id="' + SECTION + '"'), html.find('id="time-method"'))
        for path in ("_source/technology/home.html", "technology/index.html", "_source/resources.html",
                     "resources/index.html", "_source/technology/local-ai-review-replies.html",
                     "technology/local-ai-review-replies/index.html"):
            hub = (ROOT / path).read_text()
            self.assertIn('href="' + ROUTE + "#" + SECTION + '"', hub, path)

    def test_worksheet_registered_and_missing_measurements_are_not_zero(self):
        self.assertEqual(check_live.targets()[LOG], (200, self.worksheet.encode("utf-8")))
        for marker in (
            "## Part 1: What an archived test actually recorded",
            "19.536 seconds | Not recorded | Not recorded | Not performed",
            "18.157 seconds | Not recorded | Not recorded | Not performed",
            "19.325 seconds | Not recorded | Not recorded | Not performed",
            "No time-saving conclusion follows from these three timings",
            "## Part 2: A deliberately fictional cafe calculation",
            "Net saved = usual - assisted = -15 minutes",
            "positive savings begin at N = 26",
            "## Part 3: Blank evidence log for an owner-controlled pilot",
            "Human assessment of each output",
            "private customer reviews",
        ):
            self.assertIn(marker, self.worksheet)
        self.assertIn(PIN, self.worksheet)
        self.assertNotIn("\u2014", self.worksheet)

    def test_calculator_core_agrees_with_new_example(self):
        # Independent arithmetic oracle; these are invented inputs, not observed times.
        manual, assisted, review, count, setup, upkeep = 6, 2, 3, 10, 20, 5
        self.assertEqual(count * manual, 60)
        self.assertEqual(setup + upkeep + count * (assisted + review), 75)
        self.assertEqual(count * (manual - assisted - review) - setup - upkeep, -15)
        self.assertEqual((setup + upkeep) // (manual - assisted - review), 25)
        self.assertEqual((setup + upkeep) // (manual - assisted - review) + 1, 26)
        self.assertEqual(manual - assisted - (review + 1), 0)
        if shutil.which("node"):
            js = ('const r=require("./assets/workflow-time.js").calculate('
                  '{manual:"6",assisted:"2",review:"3",count:"10",setup:"20",upkeep:"5"});'
                  'process.stdout.write(JSON.stringify(r));')
            result = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=False, cwd=ROOT)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual({key: data[key] for key in ("usual", "changed", "net", "breakEven", "firstSaving")},
                             {"usual": 6000, "changed": 7500, "net": -1500, "breakEven": 25, "firstSaving": 26})

    def test_existing_canonical_and_dated_search_copy(self):
        records = json.loads((ROOT / "_source/pages.json").read_text())
        case = next(p for p in records if p["path"] == ROUTE)
        self.assertEqual(case["updated"], "2026-11-18")
        self.assertIn("source-bounded review-reply example", case["description"])
        self.assertIn('<link rel="canonical" href="' + URL + '">', self.public)
        schemas = [json.loads(text) for text in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.public, re.S)]
        webpages = [s for s in schemas if s.get("@type") == "WebPage"]
        self.assertEqual(len(webpages), 1)
        self.assertEqual(webpages[0]["dateModified"], "2026-11-18")
        self.assertEqual(webpages[0]["url"], URL)
        sitemap = ET.fromstring((ROOT / "sitemap.xml").read_text())
        matching = [node for node in sitemap if node.findtext("{*}loc") == URL]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].findtext("{*}lastmod"), "2026-11-18")

    def test_source_drifts_and_inflated_outcomes_fail_closed(self):
        mutations = (
            self.source.replace("18.157 seconds", "8.157 seconds", 1),
            self.source.replace("no paired manual-drafting baseline", "a paired manual baseline", 1),
            self.source.replace("Invented planning inputs, not the archived Gemma timings", "Measured client data", 1),
            self.source.replace("cannot be called measured <em>time saved</em>", "proves time saved", 1),
            self.source.replace('href="' + LOG + '"', 'href="/downloads/missing-comparison.md"', 1),
        )
        for changed in mutations:
            with self.subTest(changed=changed != self.source):
                self.assertNotEqual(changed, self.source)
                self.assertTrue(evidence_errors(changed))


if __name__ == "__main__":
    unittest.main()
