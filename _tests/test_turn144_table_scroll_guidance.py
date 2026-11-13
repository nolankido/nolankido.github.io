"""Turn 144: evidence tables explain horizontal reading without changing facts."""

from hashlib import sha256
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = "assets/workflow-evidence.css"
SCOPE = ":is(.page-local-ai-review-replies, .page-ai-book-continuity-checker)"
INSTRUCTION = (
    "<strong>Reading this table:</strong> On a narrow screen, swipe sideways "
    "within the table to see all columns. With a keyboard, focus the table "
    "and use the left or right arrow key."
)
TABLES = {
    "ai-book-continuity-checker": (
        ("continuity-benchmark-table-hint", "Recorded continuity benchmark scores", "Holmes seeded benchmark, October 27, 2026"),
    ),
    "local-ai-review-replies": (
        ("reply-template-table-hint", "Review Reply Writer offline study summary", "October 29, 2026: synthetic offline template evaluation"),
        ("reply-model-table-hint", "Historical Gemma smoke test comparison", "Two historical three-scenario smoke runs, not a current model benchmark"),
    ),
}


def table_guidance_issues(source: str, css: str, slug: str) -> list[str]:
    issues: list[str] = []
    expected = TABLES[slug]
    if source.count('class="project-table-hint"') != len(expected):
        issues.append("wrong number of table hints")
    if source.count('class="project-table-scroll"') != len(expected):
        issues.append("wrong number of scrollable tables")
    for note_id, label, caption in expected:
        opening = (
            f'<p class="project-table-hint" id="{note_id}">{INSTRUCTION}</p>'
            f'\n    <div class="project-table-scroll" role="region" '
            f'aria-label="{label}" aria-describedby="{note_id}" tabindex="0">'
        )
        if source.count(opening) != 1:
            issues.append(f"missing adjacent, labeled, focusable table guidance: {note_id}")
        if source.count(f'id="{note_id}"') != 1:
            issues.append(f"duplicate or missing hint ID: {note_id}")
        if source.count(f"<caption>{caption}</caption>") != 1:
            issues.append(f"changed source-backed table caption: {caption}")
    if not re.search(re.escape(SCOPE + " .project-table-hint {") + r"[^}]*color: var\(--ink-soft\);", css):
        issues.append("missing scoped, legible table hint styling")
    if SCOPE + " .project-table-hint {display: none !important;}" not in css:
        issues.append("print output must omit screen-only scrolling instruction")
    return issues


class TableScrollGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / CSS_PATH).read_text(encoding="utf-8")
        cls.version = sha256(cls.css.encode("utf-8")).hexdigest()[:12]
        cls.pages = {entry["id"]: entry for entry in json.loads((ROOT / "_source/pages.json").read_text())}

    def test_all_three_scrollable_evidence_tables_explain_how_to_read_them(self):
        for slug in TABLES:
            with self.subTest(case=slug):
                source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
                self.assertEqual(table_guidance_issues(source, self.css, slug), [])
                self.assertNotIn("\u2014", source)

    def test_public_pages_ship_hints_and_unchanged_metadata(self):
        for slug in TABLES:
            with self.subTest(case=slug):
                source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
                page = (ROOT / f"technology/{slug}/index.html").read_text(encoding="utf-8")
                self.assertIn(source, page)
                self.assertIn(f'href="/{CSS_PATH}?v={self.version}"', page)
                self.assertIn(f'rel="canonical" href="https://nolankido.com/technology/{slug}/"', page)
                self.assertEqual(self.pages[slug]["date"], "2026-10-27")
                for note_id, _, _ in TABLES[slug]:
                    self.assertEqual(page.count(f'aria-describedby="{note_id}"'), 1)

    def test_guide_is_specific_to_results_and_preserves_existing_shortcuts(self):
        self.assertIn(SCOPE + " .project-table-hint {", self.css)
        self.assertIn(".project-table-scroll table {", (ROOT / "assets/visibility-projects.css").read_text())
        for slug in TABLES:
            source = (ROOT / f"_source/technology/{slug}.html").read_text(encoding="utf-8")
            self.assertIn('aria-label="Project shortcuts"', source)
        self.assertNotIn("project-table-hint", (ROOT / "_source/technology/dinner-on-time.html").read_text())
        self.assertNotIn("project-table-hint", (ROOT / "index.html").read_text())

    def test_negative_controls_fail_when_guidance_is_broken(self):
        source = (ROOT / "_source/technology/ai-book-continuity-checker.html").read_text(encoding="utf-8")
        self.assertFalse(table_guidance_issues(source, self.css, "ai-book-continuity-checker"))
        for changed_source, changed_css in (
            (source.replace('aria-describedby="continuity-benchmark-table-hint"', '', 1), self.css),
            (source.replace('id="continuity-benchmark-table-hint"', 'id="wrong-note"', 1), self.css),
            (source.replace("swipe sideways", "read more", 1), self.css),
            (source.replace('tabindex="0"', '', 1), self.css),
            (source.replace("<caption>Holmes seeded benchmark, October 27, 2026</caption>", "", 1), self.css),
            (source, self.css.replace(SCOPE + " .project-table-hint {", ".project-table-hint {", 1)),
            (source, self.css.replace(SCOPE + " .project-table-hint {display: none !important;}", "", 1)),
        ):
            with self.subTest(broken=(changed_source != source, changed_css != self.css)):
                self.assertTrue(table_guidance_issues(changed_source, changed_css, "ai-book-continuity-checker"))


if __name__ == "__main__":
    unittest.main()
