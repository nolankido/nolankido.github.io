"""Turn 145: readers can reach counts, method and limitations without guessing."""

from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SLUG = "local-ai-review-replies"
SOURCE = f"_source/technology/{SLUG}.html"
OUTPUT = f"technology/{SLUG}/index.html"
NAV_OPEN = '<nav class="project-case-jumps reply-study-jumps" aria-label="Evaluation shortcuts">'
NAV_TITLE = '<span class="project-case-jumps-title">Explore the evaluation</span>'
DESTINATIONS = (
    ("reply-evaluation-results", "Recorded template counts"),
    ("reply-evaluation-gemma", "Earlier Gemma runs"),
    ("reply-evaluation-method", "Repeat the offline check"),
    ("reply-evaluation-limits", "What remains unproven"),
)
RESULTS_CUE = (
    '<p class="evidence-note reply-study-next"><strong>Before interpreting these counts:</strong> '
    '<a href="#reply-evaluation-method">Review the test method</a> and '
    '<a href="#reply-evaluation-limits">what the numbers do not establish</a>.</p>'
)
LIMITS_CUE = (
    '<p class="evidence-note reply-study-next"><strong>Check the underlying record:</strong> '
    '<a href="#reply-evaluation-method">See how to reproduce the offline exercise</a> or '
    '<a href="#reply-sources">open the project evidence and scope</a>.</p>'
)


def section(source: str, fragment: str) -> str:
    match = re.search(
        rf'<section class="section folio-row" aria-labelledby="{fragment}">(.*?)</section>',
        source, re.S,
    )
    return match.group(1) if match else ""


def evidence_path_errors(source: str, css: str, script: str) -> list[str]:
    errors = []
    evaluation = section(source, "reply-evaluation")
    results = section(source, "reply-evaluation-results")
    limits = section(source, "reply-evaluation-limits")
    if source.count(NAV_OPEN) != 1 or evaluation.count(NAV_TITLE) != 1:
        errors.append("missing single named evaluation navigation")
    match = re.search(re.escape(NAV_OPEN) + r"(.*?)</nav>", evaluation, re.S)
    links = re.findall(r'<a href="#([a-z-]+)">([^<]+)</a>', match.group(1)) if match else []
    if tuple(links) != DESTINATIONS:
        errors.append("evaluation routes changed or point somewhere else")
    for destination, _ in DESTINATIONS:
        if source.count(f'<h2 id="{destination}">') != 1:
            errors.append(f"missing or duplicate evaluation target {destination}")
    if results.count(RESULTS_CUE) != 1 or limits.count(LIMITS_CUE) != 1:
        errors.append("contextual routes to method, limits and sources are missing")
    if source.count('class="evidence-note reply-study-next"') != 2:
        errors.append("unbounded or missing contextual study links")
    if source.count('<nav class="entry-jumps project-case-jumps" aria-label="Project shortcuts">') != 1:
        errors.append("original case shortcuts were changed")
    scoped_rule = re.search(
        re.escape(":is(.page-local-ai-review-replies, .page-ai-book-continuity-checker, .page-dinner-on-time) .project-case-jumps a {") + r"([^}]*)}",
        css,
    )
    if not scoped_rule or "min-height: 44px;" not in scoped_rule.group(1):
        errors.append("evaluation links lack existing accessible target styling")
    if "fragment: /^#reply-[a-z-]+$/" not in script or ".section-content > h2[id]" not in script:
        errors.append("direct evaluation arrivals no longer have existing correction")
    return errors


class ReplyEvaluationPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / SOURCE).read_text(encoding="utf-8")
        cls.page = (ROOT / OUTPUT).read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/workflow-evidence.css").read_text(encoding="utf-8")
        cls.script = (ROOT / "assets/project-fragment-arrivals.js").read_text(encoding="utf-8")

    def test_evaluation_has_bounded_shortcuts_with_real_destinations(self):
        self.assertEqual(evidence_path_errors(self.source, self.css, self.script), [])
        positions = [self.source.index(f'<h2 id="{fragment}">') for fragment, _ in DESTINATIONS]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(self.source.index(NAV_OPEN), positions[0])

    def test_results_link_to_method_and_limits_then_to_primary_sources(self):
        self.assertIn(RESULTS_CUE, section(self.source, "reply-evaluation-results"))
        self.assertIn(LIMITS_CUE, section(self.source, "reply-evaluation-limits"))
        self.assertEqual(self.source.count('id="reply-sources"'), 1)
        for label in ("29 completed drafts is not a 96.7% safety rate", "no independent assessment of all 30"):
            self.assertIn(label.lower(), self.source.lower())

    def test_public_page_preserves_canonical_date_identity_and_source(self):
        self.assertIn(self.source, self.page)
        self.assertEqual(self.page.count(NAV_OPEN), 1)
        self.assertIn(f'rel="canonical" href="https://nolankido.com/technology/{SLUG}/"', self.page)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.page)
        pages = {entry["id"]: entry for entry in json.loads((ROOT / "_source/pages.json").read_text())}
        self.assertEqual(pages[SLUG]["date"], "2026-10-27")
        self.assertNotIn("\u2014", self.source)

    def test_negative_controls_fail_for_stale_or_missing_reader_routes(self):
        self.assertFalse(evidence_path_errors(self.source, self.css, self.script))
        for source, css, script in (
            (self.source.replace(NAV_TITLE, "", 1), self.css, self.script),
            (self.source.replace('href="#reply-evaluation-results"', 'href="#missing"', 1), self.css, self.script),
            (self.source.replace('id="reply-evaluation-method"', 'id="missing-method"', 1), self.css, self.script),
            (self.source.replace(RESULTS_CUE, "", 1), self.css, self.script),
            (self.source.replace(LIMITS_CUE, "", 1), self.css, self.script),
            (self.source, self.css.replace("  min-height: 44px;\n  min-width: 0;", "  min-height: 22px;\n  min-width: 0;", 1), self.script),
            (self.source, self.css, self.script.replace("fragment: /^#reply-[a-z-]+$/", "fragment: /^#reply-old$/", 1)),
        ):
            with self.subTest(changed=(source != self.source, css != self.css, script != self.script)):
                self.assertTrue(evidence_path_errors(source, css, script))


if __name__ == "__main__":
    unittest.main()
