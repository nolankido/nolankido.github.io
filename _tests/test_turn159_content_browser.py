"""Turn 159: verify an in-memory, network-free full-page browser test is runnable.

These tests inspect committed file routes and the browser script without
requiring Chromium for every routine site release. The browser run itself
is invoked locally with the existing manual --browser flag.
"""
from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "_tests/poker_hand_review_content_browser.py"
ROUTES = (
    ("/poker/episodes/portland-meadows-ep1/", "hand-64o-review",
     "/poker/six-to-ten-bb-tournament-decisions/#bridge-sb"),
    ("/poker/episodes/portland-meadows-ep1/", "hand-77-review",
     "/poker/short-stack-decisions/#depths"),
    ("/poker/episodes/portland-meadows-standoff/", "standoff-second-review",
     "/poker/short-stack-decisions/#icm-call"),
)
LINK = re.compile(r'<link\b(?=[^>]*\brel="stylesheet")(?=[^>]*\bhref="([^"]+)")[^>]*>', re.I)


def validation_issues(source: str) -> list[str]:
    errors = []
    for required in (
        "page.set_content(local_document(route)",
        "page.set_content(local_document(parsed.path)",
        "java_script_enabled=False",
        "context.route(\"**/*\", block)",
        'page.keyboard.press("Shift+Tab")',
        'page.keyboard.press("Enter")',
        'page.keyboard.press("Space")',
        'page.keyboard.press("Tab")',
        "assert_arrival(page, width, target)",
        "assert_arrival(page, width, parsed.fragment)",
        "getComputedStyle(el.querySelector('summary'))",
        "el.matches(':focus-visible')",
        "blocked_asset_requests",
        "network_responses",
        "file.is_relative_to(ROOT)",
        'os.environ.get("POKER_BROWSER_ROOT"',
    ):
        if required not in source:
            errors.append("Missing offline test guarantee: " + required)
    for forbidden in (
        "page.goto(",
        "http.server",
        "requests.get(",
        "urllib.request.urlopen(",
        "subprocess.Popen(",
        "context.storage_state(",
        "GitHub Actions workflow",
    ):
        if forbidden in source:
            errors.append("Unexpected network, service, or export call: " + forbidden)
    if "320, 390, 768, 1440" not in source:
        errors.append("The four expected viewport widths are missing")
    if "\u2014" in source:
        errors.append("Unexpected em dash")
    return errors


class OfflineContentBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.syntax = ast.parse(cls.source, filename=str(SCRIPT))

    def test_browser_script_parses_and_remains_entirely_offline(self):
        self.assertEqual(validation_issues(self.source), [])
        self.assertGreater(len(list(ast.walk(self.syntax))), 200)

    def test_existing_authored_routes_and_local_stylesheets_are_present(self):
        seen = set()
        for path, anchor, guide in ROUTES:
            with self.subTest(source=path, anchor=anchor):
                source = (ROOT / path.strip("/") / "index.html").read_text(encoding="utf-8")
                self.assertEqual(source.count('id="' + anchor + '"'), 1)
                self.assertIn('href="' + guide + '"', source)
                self.assertIn('class="site-header"', source)
                styles = LINK.findall(source)
                self.assertGreaterEqual(len(styles), 4)
                self.assertIn("/assets/site-core.css", [s.split("?")[0] for s in styles])
                for href in styles:
                    local = href.split("?")[0]
                    self.assertTrue(local.startswith("/assets/"))
                    self.assertTrue((ROOT / local.lstrip("/")).is_file(), local)
                guide_path, fragment = guide.split("#")
                dest = (ROOT / guide_path.strip("/") / "index.html").read_text(encoding="utf-8")
                self.assertEqual(dest.count('id="' + fragment + '"'), 1)
                seen.add(path)
        self.assertEqual(len(seen), 2)

    def test_deliberate_missing_keyboard_or_network_regressions_are_detected(self):
        variants = (
            self.source.replace("page.set_content(local_document(route)", "page.goto(route", 1),
            self.source.replace('page.keyboard.press("Shift+Tab")', 'summary.focus()', 1),
            self.source.replace("assert_arrival(page, width, parsed.fragment)", "pass", 1),
            self.source.replace("java_script_enabled=False", "java_script_enabled=True", 1),
            self.source.replace('context.route("**/*", block)', "pass", 1),
        )
        for index, variant in enumerate(variants):
            with self.subTest(index=index):
                self.assertTrue(validation_issues(variant))


if __name__ == "__main__":
    unittest.main()
