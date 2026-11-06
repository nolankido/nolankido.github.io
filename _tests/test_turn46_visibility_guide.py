"""The public, free Search Console how-to stays navigable and evidence-bounded."""

from pathlib import Path
import re
import unittest
import html5lib


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source" / "technology" / "ai-website-visibility.html"
OUTPUT = ROOT / "technology" / "ai-website-visibility" / "index.html"
TOOL = ROOT / "downloads" / "gsc-monthly-local-audit.py"
START = '<h3 id="free-visibility-check">'
END = '<p><strong>A method you can reuse:</strong>'
PR_URLS = tuple(f'https://github.com/nolankido/nolankido.github.io/pull/{number}'
                for number in (199, 200, 201))


def section(page: str) -> str:
    if page.count(START) != 1 or page.count(END) != 1:
        return ""
    return page.split(START, 1)[1].split(END, 1)[0]


def guide_errors(page: str) -> list[str]:
    errors: list[str] = []
    content = section(page)
    if not content:
        return ["missing or duplicated how-to guide"]
    if page.count('href="#free-visibility-check"') != 1:
        errors.append("missing or duplicate introduction route")
    if page.find('href="#free-visibility-check"') > page.find(START):
        errors.append("how-to shortcut is not in the introductory section")
    if content.count("<li>") != 4 or content.count("</li>") != 4:
        errors.append("not exactly four ordered steps")
    if content.count('<ol>') != 1 or content.count('<div class="worksheet"><pre>') != 2:
        errors.append("continuous numbered steps or either wrapped PowerShell example missing")
    for text in ("--chart-date-format mdy", "<code>dmy</code>",
                 "every date in the selected month", "visible nonbrand Technology click lower bound",
                 "a combined Query + Page export", "no measured search improvement",
                 "A month-over-month difference does not establish causation",
                 "writes no file on its own", "never sends your CSV data away"):
        if text not in content:
            errors.append("missing check or caveat: " + text)
    for url in PR_URLS:
        if content.count('href="' + url + '"') != 1:
            errors.append("release source missing or duplicated: " + url)
    for url in ("https://support.google.com/webmasters/answer/17011364",
                "https://support.google.com/webmasters/answer/12919797"):
        if content.count('href="' + url + '"') != 1:
            errors.append("official reference missing or duplicated: " + url)
    for unwanted in ("rankings increased", "improved our traffic", "AI citations grew", "<script", "\u2014"):
        if unwanted in content:
            errors.append("unsupported claim or unexpected script: " + unwanted)
    return errors


class VisibilityGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.rendered = OUTPUT.read_text(encoding="utf-8")

    def test_guide_has_intro_route_and_exact_source_rendered_parity(self):
        self.assertEqual(guide_errors(self.source), [])
        self.assertEqual(guide_errors(self.rendered), [])
        self.assertEqual(section(self.source), section(self.rendered))
        self.assertEqual(self.source.count('href="/downloads/gsc-monthly-local-audit.py"'), 1)
        self.assertEqual(self.rendered.count('href="/downloads/gsc-monthly-local-audit.py"'), 1)

    def test_article_metadata_preserves_case_origin(self):
        self.assertIn('rel="canonical" href="https://nolankido.com/technology/ai-website-visibility/"', self.rendered)
        self.assertIn('"datePublished": "2026-11-03"', self.rendered)
        self.assertIn('"dateModified": "2026-11-06"', self.rendered)
        self.assertEqual(self.rendered.count('id="site-visibility-evidence"'), 1)
        self.assertEqual(self.rendered.count('id="site-visibility-limits"'), 1)
        self.assertNotIn("\u2014", section(self.source))

    def test_inserted_markup_has_balanced_structure_and_sequential_steps(self):
        parser = html5lib.HTMLParser(strict=True, namespaceHTMLElements=False)
        root = parser.parseFragment(START + section(self.source))
        lists = root.findall("ol")
        self.assertEqual(len(lists), 1)
        self.assertEqual(len(lists[0].findall("li")), 4)
        pre = lists[0].findall("li")[1].find("div[@class='worksheet']/pre")
        self.assertIsNotNone(pre)
        self.assertIn("py -3 .\\gsc-monthly-local-audit.py", pre.text or "")

    def test_text_matches_offline_tool_options_not_unverified_metrics(self):
        script = TOOL.read_text(encoding="utf-8")
        self.assertIn('CHART_DATE_FORMATS = ("iso", "mdy", "dmy")', script)
        self.assertIn('"calendar_days_validated": True', script)
        self.assertIn("query_pages", script)
        self.assertIn("No network calls", script)
        self.assertNotIn("sitewide uplift", section(self.source))

    def test_negative_controls_reject_missing_route_sources_and_caveats(self):
        cases = (
            self.source.replace('href="#free-visibility-check"', 'href="#missing"', 1),
            self.source.replace('id="free-visibility-check"', 'id="missing"', 1),
            self.source.replace('/pull/201', '/pull/999', 1),
            self.source.replace('no measured search improvement', 'rankings increased', 1),
            self.source.replace('<div class="worksheet"><pre>py -3 .\\gsc-monthly-local-audit.py',
                                '<div class="other"><pre>py -3 .\\gsc-monthly-local-audit.py', 1),
        )
        for changed in cases:
            with self.subTest(change=changed[:90]):
                self.assertTrue(guide_errors(changed))


if __name__ == "__main__":
    unittest.main()
