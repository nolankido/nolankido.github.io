"""Turn 158: keyboard position, focus cue, and reproducible hand-review audit.

Focused source contracts do not substitute for the optional real Chromium
browser test. No network, GitHub Actions or analytics service is required.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "assets/poker-hand-review.css"
BROWSER = ROOT / "_tests/poker_hand_review_browser.py"
COMPANIONS = (
    ROOT / "poker/episodes/portland-meadows-ep1/index.html",
    ROOT / "poker/episodes/portland-meadows-standoff/index.html",
)


def check_focus_contract(css: str, browser: str) -> list[str]:
    issues = []
    required_styles = (
        ".poker-episode-companion .poker-hand-review-check:focus-within",
        ".poker-episode-companion .poker-hand-review-check .poker-details > summary:focus",
        ".poker-episode-companion .poker-hand-review-check .poker-hand-review-next a:focus",
        ".poker-details > summary:focus-visible",
        ".poker-hand-review-next a:focus-visible",
    )
    for item in required_styles:
        if item not in css:
            issues.append("missing focus context or control styling: " + item)
    if "outline: 2px solid var(--red)" not in css or "outline: 3px solid var(--red)" not in css:
        issues.append("visible high-contrast focus outlines must remain")
    expected_script = (
        'page.keyboard.press("Shift+Tab")',
        'page.keyboard.press("Enter")',
        'page.keyboard.press("Space")',
        'page.keyboard.press("Tab")',
        "e => e.matches(':focus-visible')",
        "containerFocusWithin",
        "header_safe_arrivals",
        "anchor_arrival(page, width, details)",
        'java_script_enabled=False',
        'context.route("**/*", request_handler())',
    )
    for item in expected_script:
        if item not in browser:
            issues.append("missing keyboard or offline browser gate: " + item)
    if "summary.focus()" in browser:
        issues.append("programmatic focus is not an actual keyboard Tab arrival")
    if 'next_link.focus()' not in browser:
        issues.append("anchored keyboard start point is missing")
    if any(term in css + browser for term in ("—", "window.fetch(", "requests.get(")):
        issues.append("no em dashes or remote network test calls")
    return issues


def asset_version(css_bytes: bytes) -> str:
    blob = b"blob " + str(len(css_bytes)).encode("ascii") + b"\0" + css_bytes
    return hashlib.sha1(blob).hexdigest()[:12]


class BrowserFocusContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = STYLE.read_text(encoding="utf-8")
        cls.browser = BROWSER.read_text(encoding="utf-8")

    def test_keyboard_audit_tests_real_tab_order_and_proper_focus_indication(self):
        self.assertEqual(check_focus_contract(self.css, self.browser), [])
        ast.parse(self.browser, filename=str(BROWSER))
        self.assertIn("assert report[\"external_requests\"] == 0", self.browser)
        for width in ("320", "390", "768", "1440"):
            self.assertIn(width, self.browser)

    def test_fingerprinted_companion_style_is_source_scoped_and_current(self):
        source = STYLE.read_bytes()
        version = asset_version(source)
        expected = f'/assets/poker-hand-review.css?v={version}'
        for target in COMPANIONS:
            with self.subTest(file=target):
                page = target.read_text(encoding="utf-8")
                self.assertEqual(page.count('href="' + expected + '"'), 1)
                self.assertIn('article:modified_time" content="2026-11-16"', page)
                self.assertNotIn("—", page)
        for page in ("poker/index.html", "poker/library/index.html"):
            self.assertNotIn(
                "poker-hand-review.css",
                (ROOT / page).read_text(encoding="utf-8"),
            )

    def test_negative_controls_reject_missing_focus_and_fake_keyboard_arrivals(self):
        mutations = (
            (self.css.replace(".poker-hand-review-check:focus-within",
                              ".poker-hand-review-check:hover", 1), self.browser),
            (self.css.replace(".poker-details > summary:focus,",
                              ".poker-details > summary:hover,", 1), self.browser),
            (self.css, self.browser.replace('page.keyboard.press("Shift+Tab")',
                                            'summary.focus()', 1)),
            (self.css, self.browser.replace("                    anchor_arrival(page, width, details)",
                                            "                    summary.focus()", 1)),
        )
        for index, (css, browser) in enumerate(mutations):
            with self.subTest(index=index):
                self.assertTrue(check_focus_contract(css, browser))


if __name__ == "__main__":
    unittest.main()
