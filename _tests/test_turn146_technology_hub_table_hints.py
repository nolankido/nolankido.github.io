"""Turn 146: the Technology hub's three evidence tables signal hidden columns."""

from hashlib import sha256
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "_source/technology/home.html"
PAGE = "technology/index.html"
CSS_PATH = "assets/visibility-projects.css"
INSTRUCTION = (
    "<strong>Reading this table:</strong> On a narrow screen, swipe sideways "
    "within the table to see all columns. With a keyboard, focus the table "
    "and use the left or right arrow key."
)
TABLES = (
    ("technology-identity-table-hint",
     "Identity metadata before and after publication audit",
     "What the public repository records before and after the correction"),
    ("technology-poker-facts-table-hint",
     "Public poker hand facts and graphics boundaries",
     "What a graphics and narration review can use from the published companion"),
    ("technology-poker-scene-table-hint",
     "Synthetic poker scene before and after findings",
     "Reproducible demonstrations, not observed defects in a released video"),
)


def guidance_issues(source: str, css: str) -> list[str]:
    issues = []
    if source.count('class="project-table-hint"') != len(TABLES):
        issues.append("wrong number of visible table instructions")
    if source.count('class="project-table-scroll"') != len(TABLES):
        issues.append("wrong number of source-backed table regions")
    for note_id, label, caption in TABLES:
        expected = (
            f'<p class="project-table-hint" id="{note_id}">{INSTRUCTION}</p>'
            f'\n    <div class="project-table-scroll" role="region" '
            f'aria-label="{label}" aria-describedby="{note_id}" tabindex="0">'
        )
        if source.count(expected) != 1:
            issues.append(f"instruction is missing or detached: {note_id}")
        if source.count(f'id="{note_id}"') != 1:
            issues.append(f"duplicate or missing instruction ID: {note_id}")
        if source.count(f'<caption>{caption}</caption>') != 1:
            issues.append(f"source-backed caption changed: {caption}")
    if not re.search(
        re.escape('.page-technology .project-table-hint {') +
        r'[^}]*color: var\(--ink-soft\);[^}]*font: \.86rem/1\.6 var\(--sans\);',
        css,
    ):
        issues.append("hub-specific readable instruction style missing")
    if '.page-technology .project-table-hint {display: none !important;}' not in css:
        issues.append("print view still shows irrelevant swipe instructions")
    if not re.search(r'\.project-table-scroll table \{[^}]*min-width: 38rem;', css):
        issues.append("table overflow assumptions changed")
    return issues


class TechnologyHubTableHintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / SOURCE).read_text(encoding="utf-8")
        cls.page = (ROOT / PAGE).read_text(encoding="utf-8")
        cls.css = (ROOT / CSS_PATH).read_text(encoding="utf-8")
        cls.version = sha256(cls.css.encode("utf-8")).hexdigest()[:12]

    def test_all_three_tables_explain_sideways_and_keyboard_reading(self):
        self.assertEqual(guidance_issues(self.source, self.css), [])
        self.assertNotIn("\u2014", self.source)
        self.assertIn('id="identity-claim-audit"', self.source)
        self.assertIn('id="poker-vlog-qa"', self.source)
        self.assertIn('id="poker-vlog-qa-demo"', self.source)

    def test_published_hub_contains_matching_help_and_stable_metadata(self):
        self.assertIn(f'href="/{CSS_PATH}?v={self.version}"', self.page)
        self.assertIn('rel="canonical" href="https://nolankido.com/technology/"', self.page)
        pages = {entry["id"]: entry for entry in json.loads((ROOT / "_source/pages.json").read_text())}
        self.assertEqual(pages["technology"]["updated"], "2026-11-06")
        for note_id, label, caption in TABLES:
            self.assertIn(
                f'<div class="project-table-scroll" role="region" aria-label="{label}" '
                f'aria-describedby="{note_id}" tabindex="0">', self.page,
            )
            self.assertEqual(self.page.count(f'id="{note_id}"'), 1)
            self.assertEqual(self.page.count(f'<caption>{caption}</caption>'), 1)

    def test_guidance_is_scoped_to_hub_not_other_projects(self):
        self.assertIn('.page-technology .project-table-hint {', self.css)
        self.assertNotRegex(self.css, r'(?m)^\s*\.project-table-hint\s*\{')
        self.assertNotIn('project-table-hint', (ROOT / '_source/technology/dinner-on-time.html').read_text())
        self.assertNotIn('project-table-hint', (ROOT / 'index.html').read_text())

    def test_negative_controls_detect_missing_or_misleading_guidance(self):
        self.assertFalse(guidance_issues(self.source, self.css))
        for source, css in (
            (self.source.replace('aria-describedby="technology-identity-table-hint"', '', 1), self.css),
            (self.source.replace('id="technology-poker-facts-table-hint"', 'id="wrong-note"', 1), self.css),
            (self.source.replace('swipe sideways', 'scroll the page', 1), self.css),
            (self.source.replace('tabindex="0"', '', 1), self.css),
            (self.source.replace('<caption>Reproducible demonstrations, not observed defects in a released video</caption>', '', 1), self.css),
            (self.source, self.css.replace('.page-technology .project-table-hint {', '.project-table-hint {', 1)),
            (self.source, self.css.replace('.page-technology .project-table-hint {display: none !important;}', '', 1)),
        ):
            with self.subTest(source_changed=source != self.source, css_changed=css != self.css):
                self.assertTrue(guidance_issues(source, css))


if __name__ == "__main__":
    unittest.main()
