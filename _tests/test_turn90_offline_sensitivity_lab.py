"""Turn 90: a browser-local, privacy-respecting fixed-scenario sensitivity lab.

All these checks are offline. They do not call a poker solver, an AI service,
a browser, or an opponent database. Browser interaction has a separate suite.
"""
from fractions import Fraction as F
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source/poker/pot-odds-sensitivity-lab.html"
OUTPUT = ROOT / "downloads/poker-pot-odds-sensitivity-lab.html"
ROUTE = "/downloads/poker-pot-odds-sensitivity-lab.html"
WORKSHOP_SOURCE = ROOT / "_source/poker/pot-odds-workshop.html"
WORKSHOP_PUBLIC = ROOT / "poker/pot-odds-workshop/index.html"


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def content_problems(html):
    parser = Elements(html)
    tags = parser.tags
    ids = [a["id"] for _, a in tags if "id" in a]
    inputs = [a for tag, a in tags if tag == "input"]
    labels = [a for tag, a in tags if tag == "label"]
    errors = []
    if len(ids) != len(set(ids)):
        errors.append("Duplicate ID")
    if len([a for tag, a in tags if tag == "h1"]) != 1:
        errors.append("Missing one h1")
    if len([a for tag, a in tags if tag == "main" and a.get("id") == "main"]) != 1:
        errors.append("Missing main")
    if not any(tag == "meta" and a.get("name") == "robots"
               and a.get("content") == "noindex, follow" for tag, a in tags):
        errors.append("Missing noindex")
    policy = [a.get("content", "") for tag, a in tags
              if tag == "meta" and a.get("http-equiv") == "Content-Security-Policy"]
    if len(policy) != 1 or not all(x in policy[0] for x in
            ("default-src 'none'", "connect-src 'none'", "form-action 'none'",
             "script-src 'unsafe-inline'", "style-src 'unsafe-inline'")):
        errors.append("Missing offline CSP")
    if len(inputs) != 4 or any(a.get("type") != "range" or "disabled" not in a
                               or a.get("min") != "0" or a.get("max") != "100"
                               or a.get("step") != "1" for a in inputs):
        errors.append("Range control policy")
    if len({x.get("for") for x in labels}) != 4 or (
            {x.get("for") for x in labels} != {x.get("id") for x in inputs}):
        errors.append("Input labels")
    if len([a for tag, a in tags if tag == "output"]) != 4:
        errors.append("Missing output labels")
    if len([a for tag, a in tags if a.get("role") == "status"]) != 3:
        errors.append("Missing announced results")
    if not any(tag == "noscript" for tag, _ in tags):
        errors.append("Missing no-JS explanation")
    if any(tag in {"form", "iframe", "object"} for tag, _ in tags):
        errors.append("Submission or remote embedding")
    if any(tag == "script" and "src" in a for tag, a in tags):
        errors.append("External script")
    return errors


class Turn90SensitivityLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.output = OUTPUT.read_text(encoding="utf-8")
        cls.workshop = WORKSHOP_PUBLIC.read_text(encoding="utf-8")

    def test_author_and_public_html_are_exactly_the_same(self):
        self.assertEqual(self.source, self.output)
        self.assertTrue(self.source.startswith("<!doctype html>"))
        self.assertNotIn(chr(0x2014), self.source)

    def test_accessibility_and_no_external_network_or_submission(self):
        self.assertEqual(content_problems(self.source), [])
        self.assertIn("No forms, analytics, storage, cookies", self.source)
        self.assertNotIn("https://", self.source)
        self.assertNotIn("localStorage", self.source)
        self.assertNotIn("sessionStorage", self.source)
        self.assertNotIn("XMLHttpRequest", self.source)
        self.assertNotIn("fetch(", self.source)
        self.assertNotIn("innerHTML", self.source)

    def test_no_javascript_controls_are_disabled_until_ready(self):
        self.assertEqual(self.source.count("<noscript>"), 1)
        self.assertIn("Interactive controls are unavailable", self.source)
        self.assertIn("input.disabled = false", self.source)
        for default in ['value="22" disabled', 'value="29" disabled',
                        'value="25" step="1" disabled',
                        'value="40" step="1" disabled']:
            self.assertIn(default, self.source)

    def test_fixed_examples_reproduce_exact_fraction_math(self):
        self.assertEqual(F(10, 40), F(1, 4))
        self.assertEqual([F(q, 100) * 40 - 10 for q in [22, 29]], [F(-6, 5), F(8, 5)])
        self.assertEqual(F(10, 38), F(5, 19))
        self.assertEqual(F(25, 100) * 38 - 10, F(-1, 2))
        self.assertEqual(F(30, 100) * 38 - 10, F(7, 5))
        self.assertEqual(F(6, 16), F(3, 8))
        self.assertEqual(F(6, 22), F(3, 11))
        self.assertEqual(F(40, 100) * 10 - F(60, 100) * 6, F(2, 5))
        for text in ("-1.20 to +1.60 BB", "25%:", "40% folds:",
                     "5/19", "3/11", "37.5%"):
            self.assertIn(text, self.output)

    def test_each_control_has_an_unambiguous_live_result(self):
        for ident in ("river-low", "river-high", "raise-equity", "bluff-fold"):
            self.assertIn('id="' + ident + '" type="range"', self.source)
        for ident in ("river-result", "raise-result", "bluff-result"):
            self.assertIn('id="' + ident + '" role="status"', self.source)
        for ident in ("river-low-label", "river-high-label", "raise-label", "bluff-label"):
            self.assertIn('id="' + ident + '"', self.source)
        self.assertIn("Math.min(low, high)", self.source)
        self.assertIn("Math.max(low, high)", self.source)
        self.assertIn("textContent", self.source)

    def test_workshop_navigation_contains_one_lab_link_and_original_links(self):
        source = WORKSHOP_SOURCE.read_text(encoding="utf-8")
        nav_start = '<nav class="article-navigation" aria-label="Continue studying">'
        def nav(html):
            i = html.index(nav_start)
            return html[i:html.index("</nav>", i) + 6]
        self.assertEqual(nav(source), nav(self.workshop))
        self.assertEqual(nav(source).count('href="' + ROUTE + '"'), 1)
        for resource in ("/downloads/poker-pot-odds-sensitivity-workbook.md",
                         "/downloads/poker-pot-odds-sensitivity-verify.py",
                         "/poker/practice-room/", "/poker/range-combinations/"):
            self.assertIn('href="' + resource + '"', nav(source))

    def test_sitemap_and_local_finder_not_inflated_by_standalone_lab(self):
        self.assertNotIn("https://nolankido.com" + ROUTE,
                         (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        finder = (ROOT / "poker/find/index.html").read_text(encoding="utf-8")
        self.assertNotIn(ROUTE, finder)
        self.assertIn("301 entries available.", finder)

    def test_download_is_in_exact_public_inventory_and_html5_suite(self):
        inventory = (ROOT / "_scripts/check_live.py").read_text(encoding="utf-8")
        self.assertEqual(inventory.count("'downloads/poker-pot-odds-sensitivity-lab.html'"), 1)
        coverage = (ROOT / "_tests/test_turn63_public_html_downloads.py").read_text(encoding="utf-8")
        self.assertIn('"' + ROUTE + '"', coverage)
        self.assertIn("test_turn90_offline_sensitivity_lab.py",
                      (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8"))

    def test_invalid_html_contract_mutations_are_rejected(self):
        mutations = (
            self.source.replace('content="noindex, follow"', 'content="index, follow"', 1),
            self.source.replace("connect-src 'none'", "connect-src *", 1),
            self.source.replace('id="river-low"', 'id="river-high"', 1),
            self.source.replace('value="22" disabled', 'value="22"', 1),
            self.source.replace('for="bluff-fold"', 'for="unknown-input"', 1),
        )
        for candidate in mutations:
            with self.subTest(change=candidate != self.source):
                self.assertNotEqual(candidate, self.source)
                self.assertTrue(content_problems(candidate))

    def test_no_github_actions_added(self):
        actions = ROOT / ".github/workflows"
        self.assertFalse(actions.exists() and any(
            p.is_file() and p.suffix.lower() in (".yml", ".yaml")
            for p in actions.iterdir()))


if __name__ == "__main__":
    unittest.main()
