"""Homepage readers meet a practical choice before the longer project gallery."""
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build


CHOICES = re.compile(
    r'<section class="section folio-row identity-selection" '
    r'aria-labelledby="selected-reading-title">.*?</section>', re.S)
PROOF = '<section class="section folio-row identity-selection home-proof"'
GALLERY = '<section class="section folio-row visibility-projects"'
DESTINATIONS = '<section class="section folio-row destination-section"'
ROUTES = (
    ("use", "/technology/task-brief/"),
    ("inspect", "/technology/checking-ai-website-changes/"),
    ("understand", "/notes/keep-the-judgment/"),
)


def errors(html: str) -> list[str]:
    issues = []
    matches = CHOICES.findall(html)
    if len(matches) != 1:
        return ["missing or duplicate actionable choice section"]
    choice = matches[0]
    try:
        if not (html.index(PROOF) < html.index(choice) < html.index(GALLERY)
                < html.index(DESTINATIONS)):
            issues.append("practical choices must follow evidence and precede project browsing")
    except ValueError:
        issues.append("missing evidence, project gallery, or destination section")

    if html.count('id="selected-reading-title"') != 1:
        issues.append("ambiguous action section heading")
    if choice.count('<h2 class="section-title" id="selected-reading-title">') != 1:
        issues.append("action section heading not programmatically labeled")
    if re.findall(r'data-home-choice="([^"]+)"', choice) != [item[0] for item in ROUTES]:
        issues.append("three actions or their order changed")
    if re.findall(r'<h3><a href="([^"]+)"', choice) != [item[1] for item in ROUTES]:
        issues.append("action destinations changed or are no longer descriptive links")
    for caveat in (
        "A local browser tool. No account. No AI runs here.",
        "A documented defect, not a claim of time savings.",
        "An essay on what to keep in human hands.",
    ):
        if caveat not in choice:
            issues.append("missing evidence boundary: " + caveat)
    if choice.count('<details class="practical-home">') != 1:
        issues.append("optional additional choices are not a native disclosure")
    if '<script' in choice or '<iframe' in choice or 'onclick=' in choice:
        issues.append("action choices must remain native and script-free")
    if '\u2014' in choice:
        issues.append("em dash in public homepage copy")
    return issues


class HomeUsefulFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        cls.public = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_existing_three_useful_paths_appear_before_the_project_gallery(self):
        for content in (self.source, self.public):
            with self.subTest(source=content[:45]):
                self.assertEqual(errors(content), [])
        self.assertEqual(CHOICES.search(self.source).group(),
                         CHOICES.search(self.public).group())

    def test_no_new_content_is_needed_for_actionable_reader_routes(self):
        choice = CHOICES.search(self.public).group()
        self.assertEqual(choice.count('class="identity-reading" data-home-choice='), 3)
        self.assertIn('aria-label="More useful starting points"', choice)
        self.assertEqual(self.public.count('href="#home-proof-title"'), 1)
        self.assertEqual(self.public.count('id="home-proof-title"'), 1)
        self.assertEqual(self.public.count('id="visibility-projects-title"'), 1)
        self.assertEqual(self.public.count('id="selected-reading-title"'), 1)

    def test_builder_generates_the_exact_public_homepage(self):
        self.assertEqual(build.build_outputs()[Path("index.html")], self.public)

    def test_reordering_or_inflating_the_entrance_fails(self):
        original = CHOICES.search(self.public).group()
        for variant in (
            self.public.replace(original, "", 1),
            self.public.replace(original, original + original, 1),
            self.public.replace(original, "", 1).replace(
                DESTINATIONS, original + DESTINATIONS, 1),
            self.public.replace('data-home-choice="use"', 'data-home-choice="inspect"', 1),
            self.public.replace('/technology/task-brief/', '/bad-route/', 1),
            self.public.replace('No AI runs here.', 'AI runs here.', 1),
        ):
            with self.subTest(variant=variant[:80]):
                self.assertTrue(errors(variant))


if __name__ == "__main__":
    unittest.main()
