"""Turn 147: every source-backed Technology table exposes its hidden columns."""

from hashlib import sha256
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS_FILE = ROOT / "assets/visibility-projects.css"
INSTRUCTION = (
    "<strong>Reading this table:</strong> On a narrow screen, swipe sideways "
    "within the table to see all columns. With a keyboard, focus the table "
    "and use the left or right arrow key."
)
TABLES = {
    "ai-poker-video-evidence": (
        ("poker-video-source-table-hint", "What the poker source actually supports"),
        ("poker-video-claim-table-hint", "Examples of unsupported poker video claims and defensible alternatives"),
    ),
    "local-ai-gaming-laptop": (
        ("laptop-evidence-table-hint", "Public local-model evidence and unmeasured laptop results"),
    ),
    "ai-website-visibility": (
        ("site-visibility-checks-table-hint", "Recorded Turn 41 website release checks"),
    ),
    "organize-public-notes": (
        ("notes-output-table-hint", "Selected unchanged rows from the recorded notes checklist"),
        ("notes-checker-table-hint", "Constructed checklist mistakes and targeted checker responses"),
    ),
    "check-ai-answers": (
        ("answer-check-examples-table-hint", "Documented AI failures and useful checks"),
    ),
    "local-ai-test-record": (
        ("local-test-configuration-table-hint", "Historical local model test configuration"),
        ("local-test-timings-table-hint", "Historical Gemma case timings"),
    ),
    "review-reply-evidence-audit": (
        ("reply-audit-archive-table-hint", "Three recorded model cases and their bounded checks"),
        ("reply-audit-probes-table-hint", "Boundary probes for the independent reply screen"),
        ("reply-audit-results-table-hint", "Independent audit result and interpretation"),
    ),
}
SCOPED_SELECTOR = ":is(" + ", ".join(f".page-{slug}" for slug in TABLES) + ") .project-table-hint"
REGION = re.compile(r'(?m)^(?P<indent>[ \t]*)<div class="project-table-scroll"(?P<attrs>[^>]*)>')


def guidance_issues(source: str, expected: tuple[tuple[str, str], ...]) -> list[str]:
    issues: list[str] = []
    if source.count('class="project-table-hint"') != len(expected):
        issues.append("missing or extra visible instructions")
    regions = list(REGION.finditer(source))
    if len(regions) != len(expected):
        issues.append("missing or extra scroll regions")
    for hint_id, label in expected:
        if source.count(f'id="{hint_id}"') != 1:
            issues.append(f"missing or duplicate hint ID: {hint_id}")
        hint = f'<p class="project-table-hint" id="{hint_id}">{INSTRUCTION}</p>'
        exact = (
            f'{hint}\n'
            f'{{indent}}<div class="project-table-scroll" role="region" '
            f'aria-label="{label}" aria-describedby="{hint_id}" tabindex="0">'
        )
        if not any(exact.replace('{indent}', m.group('indent')) in source for m in regions):
            issues.append(f"instruction not adjacent to its named region: {hint_id}")
    for match in regions:
        attrs = match.group('attrs')
        described = re.search(r'\baria-describedby="([^"]+)"', attrs)
        if not described or source.count(f'id="{described.group(1)}"') != 1:
            issues.append("scroll region references no unique instruction")
        if not re.search(r'<table>\s*<caption>[^<]+</caption>', source[match.end():match.end() + 320]):
            issues.append("scroll region is missing its source-backed table caption")
    return issues


class RemainingTechnologyTableHintsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = CSS_FILE.read_text(encoding="utf-8")
        cls.version = sha256(cls.css.encode("utf-8")).hexdigest()[:12]

    def test_all_twelve_remaining_comparisons_have_visible_accessible_help(self):
        self.assertEqual(sum(len(tables) for tables in TABLES.values()), 12)
        for slug, expected in TABLES.items():
            source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                self.assertEqual(guidance_issues(source, expected), [])
                self.assertNotIn("\u2014", source)

    def test_all_technology_scroll_regions_are_now_described(self):
        total = 0
        for path in (ROOT / "_source/technology").glob("*.html"):
            source = path.read_text(encoding="utf-8")
            regions = list(REGION.finditer(source))
            total += len(regions)
            self.assertEqual(len(regions), source.count('class="project-table-hint"'), path.name)
            for region in regions:
                described = re.search(r'\baria-describedby="([^"]+)"', region.group('attrs'))
                self.assertIsNotNone(described, path.name)
                self.assertEqual(source.count(f'id="{described.group(1)}"'), 1, path.name)
        # New Technology guides may add accessible tables after this regression
        # was written. The per-region checks above still cover every one.
        self.assertGreaterEqual(total, 18)

    def test_scoped_style_and_public_pages_keep_canonical_routes(self):
        self.assertIn(SCOPED_SELECTOR + " {", self.css)
        self.assertIn(SCOPED_SELECTOR + " {display: none !important;}", self.css)
        self.assertNotRegex(self.css, r'(?m)^\s*\.project-table-hint\s*\{')
        for slug, expected in TABLES.items():
            page = (ROOT / f"technology/{slug}/index.html").read_text(encoding="utf-8")
            self.assertIn(f'href="/assets/visibility-projects.css?v={self.version}"', page)
            self.assertIn(f'rel="canonical" href="https://nolankido.com/technology/{slug}/"', page)
            for hint_id, label in expected:
                self.assertIn(f'aria-label="{label}" aria-describedby="{hint_id}" tabindex="0"', page)
                self.assertEqual(page.count(f'id="{hint_id}"'), 1)

    def test_mutations_reveal_unlabeled_or_misleading_tables(self):
        original = (ROOT / "_source/technology/ai-website-visibility.html").read_text(encoding="utf-8")
        expected = TABLES["ai-website-visibility"]
        self.assertFalse(guidance_issues(original, expected))
        for changed in (
            original.replace('aria-describedby="site-visibility-checks-table-hint"', '', 1),
            original.replace('id="site-visibility-checks-table-hint"', 'id="other-hint"', 1),
            original.replace('swipe sideways', 'scroll the entire page', 1),
            original.replace('tabindex="0"', '', 1),
            original.replace('<caption>November 5, 2026:', '<p>November 5, 2026:', 1),
        ):
            with self.subTest(changed=changed != original):
                self.assertTrue(guidance_issues(changed, expected))


if __name__ == "__main__":
    unittest.main()
