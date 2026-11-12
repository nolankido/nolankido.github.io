"""Homepage project links reach identifiable headings without stealing control."""

from hashlib import sha256
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = "assets/workflow-evidence.css"
JS_PATH = "assets/project-fragment-arrivals.js"
EXTRA_RULE = (
    ".page-ai-book-continuity-checker .section-content > h2[id]:target,\n"
    ".page-dinner-on-time .section-content > h2[id]:target {\n"
    "  outline: 2px solid var(--red);\n"
    "  outline-offset: 4px;\n"
    "}"
)
CASES = (
    ("ai-book-continuity-checker", "continuity-example", "continuity"),
    ("dinner-on-time", "dinner-demo", "dinner"),
)


def integration_issues(css: str, script: str) -> list[str]:
    issues = []
    if css.count(EXTRA_RULE) != 1:
        issues.append("the two page-scoped target outlines changed")
    for slug, _, prefix in CASES:
        if f".page-{slug} .section-content > h2[id]:target" not in css:
            issues.append(f"missing heading scope: {slug}")
        if f"fragment: /^#{prefix}-[a-z-]+$/" not in script:
            issues.append(f"missing fragment allowlist: {slug}")
    return issues


class ProjectCaseArrivalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / CSS_PATH).read_text(encoding="utf-8")
        cls.script = (ROOT / JS_PATH).read_text(encoding="utf-8")
        cls.home = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        cls.hub = (ROOT / "_source/technology/home.html").read_text(encoding="utf-8")

    def test_both_homepage_examples_land_on_one_real_headline(self):
        for slug, anchor, prefix in CASES:
            with self.subTest(case=slug):
                route = f"/technology/{slug}/#{anchor}"
                source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
                rendered = (ROOT / f"technology/{slug}/index.html").read_text(encoding="utf-8")
                self.assertIn(f'href="{route}"', self.home)
                self.assertIn(f'href="{route}"', self.hub)
                self.assertEqual(source.count(f'<h2 id="{anchor}">'), 1)
                self.assertIn(source, rendered)
                self.assertIn(f'<body class="site-page page-{slug}">', rendered)
                self.assertIn(f'fragment: /^#{prefix}-[a-z-]+$/', self.script)

    def test_scoped_highlight_does_not_change_plain_headings(self):
        self.assertEqual(self.css.count(EXTRA_RULE), 1)
        self.assertNotIn("animation:", EXTRA_RULE)
        self.assertNotIn("scroll-margin", EXTRA_RULE)
        for slug, _, _ in CASES:
            self.assertIn(f".page-{slug} .section-content > h2[id]:target", EXTRA_RULE)
        self.assertNotIn(".page-home", EXTRA_RULE)
        self.assertNotIn(".page-technology", EXTRA_RULE)
        self.assertNotIn("\u2014", self.css)

    def test_all_three_case_pages_use_one_guarded_versioned_script(self):
        version = sha256(self.script.encode("utf-8")).hexdigest()[:12]
        style_version = sha256(self.css.encode("utf-8")).hexdigest()[:12]
        for slug in ("local-ai-review-replies", *(item[0] for item in CASES)):
            with self.subTest(case=slug):
                rendered = (ROOT / f"technology/{slug}/index.html").read_text(encoding="utf-8")
                self.assertIn(f'<script defer src="/{JS_PATH}?v={version}"></script>', rendered)
                self.assertIn(f'href="/{CSS_PATH}?v={style_version}"', rendered)
        for path in ("index.html", "technology/ai-weekly-reset/index.html"):
            self.assertNotIn(JS_PATH, (ROOT / path).read_text(encoding="utf-8"))
        for guard in ("document.fonts.ready", "pending.signal.aborted", "location.hash !== hash",
                      "header.getBoundingClientRect().bottom", "heading.getBoundingClientRect().top",
                      "behavior: 'instant'", "addEventListener('hashchange', followFragment)",
                      "clearTimeout(timeout)"):
            self.assertIn(guard, self.script)
        for event in ("keydown", "pointerdown", "wheel", "touchstart", "pagehide"):
            self.assertIn(f"'{event}'", self.script)
        for unsafe in ("fetch(", "localStorage", ".focus("):
            self.assertNotIn(unsafe, self.script)

    def test_original_evidence_and_publication_dates_are_unchanged(self):
        pages = {item["id"]: item for item in json.loads((ROOT / "_source/pages.json").read_text())}
        for slug, _, _ in CASES:
            with self.subTest(case=slug):
                self.assertEqual(pages[slug]["date"], "2026-10-27")
                html = (ROOT / f"technology/{slug}/index.html").read_text(encoding="utf-8")
                self.assertIn(f'rel="canonical" href="https://nolankido.com/technology/{slug}/"', html)
                self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', html)

    def test_negative_controls_detect_missing_scope_or_fragment_prefix(self):
        self.assertEqual(integration_issues(self.css, self.script), [])
        self.assertTrue(integration_issues(self.css.replace(EXTRA_RULE, "", 1), self.script))
        for slug, _, prefix in CASES:
            with self.subTest(case=slug):
                mutated = self.script.replace(f"fragment: /^#{prefix}-[a-z-]+$/", "", 1)
                self.assertTrue(integration_issues(self.css, mutated))


if __name__ == "__main__":
    unittest.main()
