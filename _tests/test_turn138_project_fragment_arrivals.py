"""Turn 138: native arrivals identify the selected Review Reply Writer section."""

from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


CASE_PATH = "technology/local-ai-review-replies/index.html"
STYLE_PATH = "assets/workflow-evidence.css"
EXPECTED_ANCHORS = {"reply-example", "reply-boundary", "reply-failure"}
RULE = (
    ".page-local-ai-review-replies .section-content > h2[id]:target {\n"
    "  outline: 2px solid var(--red);\n"
    "  outline-offset: 4px;\n"
    "}"
)
INBOUND_SOURCES = (
    "_source/home.html",
    "_source/technology/home.html",
    "_source/technology/check-ai-answers.html",
    "_source/technology/review-reply-evidence-audit.html",
    "_source/notes/keep-the-judgment.html",
)


def arrival_errors(css: str, case: str, sources: list[str]) -> list[str]:
    errors = []
    if css.count(RULE) != 1:
        errors.append("scoped native target outline is missing or duplicated")
    if ".section-content > h2[id]:target" in css.replace(RULE, ""):
        errors.append("a broader unscoped target rule was introduced")
    if '<body class="site-page page-local-ai-review-replies">' not in case:
        errors.append("page-scoped selector no longer matches the case")
    linked = set()
    for source in sources:
        linked.update(re.findall(r'href="/technology/local-ai-review-replies/#(reply-[a-z-]+)"', source))
    if linked != EXPECTED_ANCHORS:
        errors.append("expected public inbound fragment links changed")
    for anchor in linked:
        if case.count(f'<h2 id="{anchor}">') != 1:
            errors.append(f"public fragment destination is missing or repeated: {anchor}")
    return errors


class ProjectFragmentArrivalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / STYLE_PATH).read_text(encoding="utf-8")
        cls.case_source = (ROOT / "_source/technology/local-ai-review-replies.html").read_text(encoding="utf-8")
        cls.case = (ROOT / CASE_PATH).read_text(encoding="utf-8")
        cls.sources = [(ROOT / path).read_text(encoding="utf-8") for path in INBOUND_SOURCES]

    def test_native_fragment_arrivals_are_scoped_and_have_visible_outline(self):
        self.assertEqual(arrival_errors(self.css, self.case, self.sources), [])
        self.assertIn("outline: 2px solid var(--red)", RULE)
        self.assertIn("outline-offset: 4px", RULE)
        self.assertNotIn("animation:", RULE)
        self.assertNotIn("scroll-margin", RULE)

    def test_source_and_generated_page_preserve_the_recorded_case(self):
        self.assertIn(self.case_source, self.case)
        self.assertIn("Fictional customer / Actual application example", self.case)
        self.assertIn("The owner still has to decide", self.case)
        self.assertIn("not feedback from a real cafe", self.case)
        self.assertIn('href="/technology/review-reply-evidence-audit/"', self.case)
        self.assertNotIn("\u2014", self.case_source)

    def test_versioned_stylesheet_updates_only_its_existing_consumers(self):
        outputs = build.build_outputs()
        self.assertEqual(outputs[Path(CASE_PATH)], self.case)
        version = sha256(self.css.encode("utf-8")).hexdigest()[:12]
        owners = [path for path, html in outputs.items() if "/assets/workflow-evidence.css?v=" in html]
        self.assertIn(Path(CASE_PATH), owners)
        self.assertGreater(len(owners), 1)
        for path in owners:
            self.assertIn(f'href="/assets/workflow-evidence.css?v={version}"', outputs[path], str(path))
        for path in (
            "technology/local-ai-gaming-laptop/index.html",
            "technology/review-reply-evidence-audit/index.html",
        ):
            standalone = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(f'href="/assets/workflow-evidence.css?v={version}"', standalone, path)
        self.assertNotIn('href="/assets/workflow-evidence.css', outputs[Path("index.html")])

    def test_identity_and_publication_metadata_are_not_reissued(self):
        pages = {p["path"]: p for p in json.loads((ROOT / "_source/pages.json").read_text())}
        self.assertEqual(pages["/technology/local-ai-review-replies/"]["date"], "2026-10-27")
        self.assertIn('rel="canonical" href="https://nolankido.com/technology/local-ai-review-replies/"', self.case)
        self.assertIn('"@id": "https://nolankido.com/about/#nolan-kido"', self.case)
        self.assertIn('content="2026-10-27"', self.case)

    def test_negative_controls_catch_lost_destinations_and_broad_styles(self):
        mutations = (
            (self.css.replace(RULE, "", 1), self.case, self.sources),
            (self.css.replace(".page-local-ai-review-replies ", "", 1), self.case, self.sources),
            (self.css.replace("2px solid var(--red)", "0 none transparent", 1), self.case, self.sources),
            (self.css, self.case.replace('id="reply-example"', 'id="missing-example"', 1), self.sources),
            (self.css, self.case.replace('page-local-ai-review-replies', 'page-missing-reply-case', 1), self.sources),
        )
        for css, case, sources in mutations:
            with self.subTest(mutation=(css != self.css, case != self.case)):
                self.assertTrue(arrival_errors(css, case, sources))


if __name__ == "__main__":
    unittest.main()
