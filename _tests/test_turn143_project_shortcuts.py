"""Turn 143: project evidence shortcuts are labeled, tappable and scoped."""

from hashlib import sha256
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = "assets/workflow-evidence.css"
SCOPE = ":is(.page-local-ai-review-replies, .page-ai-book-continuity-checker, .page-dinner-on-time)"
NAV_OPEN = '<nav class="entry-jumps project-case-jumps" aria-label="Project shortcuts">'
NAV_TITLE = '<span class="project-case-jumps-title">Explore this case</span>'
CASES = {
    "local-ai-review-replies": (
        ("reply-example", "Follow one review"),
        ("reply-failure", "Inspect an actual model failure"),
        ("reply-try", "Try the workflow"),
        ("reply-sources", "Open the evidence"),
    ),
    "ai-book-continuity-checker": (
        ("continuity-example", "See the wound example"),
        ("continuity-method", "Follow the method"),
        ("continuity-results", "Read the measured limits"),
        ("continuity-try", "Inspect the project"),
    ),
    "dinner-on-time": (
        ("dinner-demo", "Watch the demonstration"),
        ("dinner-decisions", "Follow the decisions"),
        ("dinner-method", "Reuse the design questions"),
    ),
}


def shortcut_issues(source: str, css: str, slug: str) -> list[str]:
    issues = []
    if source.count(NAV_OPEN) != 1 or source.count(NAV_TITLE) != 1:
        issues.append("missing labeled project shortcuts navigation")
    match = re.search(r'<nav class="entry-jumps project-case-jumps"[^>]*>(.*?)</nav>', source, re.S)
    links = re.findall(r'<a href="#([a-z-]+)">([^<]+)</a>', match.group(1)) if match else []
    if tuple(links) != CASES[slug]:
        issues.append("authored shortcut labels or destinations changed")
    for fragment, _ in CASES[slug]:
        if source.count(f'<h2 id="{fragment}">') != 1:
            issues.append(f"missing or duplicated destination {fragment}")
    link_rule = re.search(re.escape(f"{SCOPE} .project-case-jumps a {{") + r"([^}]*)}", css)
    if not link_rule or "min-height: 44px;" not in link_rule.group(1):
        issues.append("missing scoped 44px link targets")
    if f"{SCOPE} .project-case-jumps a:focus-visible {{" not in css:
        issues.append("missing scoped keyboard focus cue")
    return issues


class ProjectShortcutsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / CSS_PATH).read_text(encoding="utf-8")
        cls.version = sha256(cls.css.encode("utf-8")).hexdigest()[:12]
        cls.pages = {entry["id"]: entry for entry in json.loads((ROOT / "_source/pages.json").read_text())}

    def test_each_case_has_one_labeled_landmark_with_exact_real_destinations(self):
        for slug in CASES:
            with self.subTest(case=slug):
                source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
                self.assertEqual(shortcut_issues(source, self.css, slug), [])
                self.assertNotIn('<div class="entry-jumps">', source)
                self.assertNotIn("\u2014", source)

    def test_shipped_pages_include_the_same_links_and_versioned_style(self):
        for slug in CASES:
            with self.subTest(case=slug):
                source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
                page = (ROOT / f"technology/{slug}/index.html").read_text(encoding="utf-8")
                self.assertIn(source, page)
                self.assertIn(f'href="/{CSS_PATH}?v={self.version}"', page)
                self.assertEqual(page.count(NAV_OPEN), 1)
                self.assertIn(f'<body class="site-page page-{slug}">', page)
                self.assertIn(f'rel="canonical" href="https://nolankido.com/technology/{slug}/"', page)
                self.assertEqual(self.pages[slug]["date"], "2026-10-27")

    def test_navigation_tap_targets_reflow_and_focus_remain_case_scoped(self):
        self.assertIn(f"{SCOPE} .project-case-jumps {{", self.css)
        self.assertIn("grid-template-columns: repeat(auto-fit, minmax(min(100%, 9.5rem), 1fr));", self.css)
        self.assertIn("min-height: 44px;", self.css)
        self.assertIn("outline: 3px solid var(--red);", self.css)
        self.assertIn(f"{SCOPE} .project-case-jumps {{display: none !important;}}", self.css)
        self.assertNotIn(".page-home .project-case-jumps", self.css)
        self.assertNotIn(".page-technology .project-case-jumps", self.css)
        for page in ("index.html", "technology/ai-weekly-reset/index.html"):
            self.assertNotIn("project-case-jumps", (ROOT / page).read_text(encoding="utf-8"))

    def test_existing_project_target_outlines_remain_intact(self):
        for rule in (
            ".page-local-ai-review-replies .section-content > h2[id]:target",
            ".page-ai-book-continuity-checker .section-content > h2[id]:target",
            ".page-dinner-on-time .section-content > h2[id]:target",
        ):
            self.assertIn(rule, self.css)

    def test_negative_controls_fail_closed(self):
        source = (ROOT / "_source/technology/ai-book-continuity-checker.html").read_text(encoding="utf-8")
        self.assertEqual(shortcut_issues(source, self.css, "ai-book-continuity-checker"), [])
        for broken_source, broken_css in (
            (source.replace(NAV_TITLE, "", 1), self.css),
            (source.replace('href="#continuity-example"', 'href="#missing"', 1), self.css),
            (source.replace('id="continuity-example"', 'id="missing"', 1), self.css),
            (source, self.css.replace(f"{SCOPE} .project-case-jumps a {{", ".project-case-jumps a {", 1)),
            (source, self.css.replace("  min-height: 44px;\n  min-width: 0;", "  min-height: 28px;\n  min-width: 0;", 1)),
            (source, self.css.replace(f"{SCOPE} .project-case-jumps a:focus-visible {{", "", 1)),
        ):
            with self.subTest(broken=(broken_source != source, broken_css != self.css)):
                self.assertTrue(shortcut_issues(broken_source, broken_css, "ai-book-continuity-checker"))


if __name__ == "__main__":
    unittest.main()
