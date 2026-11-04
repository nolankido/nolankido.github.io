"""Turn 15: relevant, crawlable links to inspectable AI and poker records."""
import re
import subprocess
import unittest
from pathlib import Path

import turn15_evidence_links_history as history


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "/technology/local-ai-gaming-laptop/": "technology/local-ai-gaming-laptop/index.html",
    "/technology/review-reply-evidence-audit/": "technology/review-reply-evidence-audit/index.html",
    "/poker/nolan-kido/": "poker/nolan-kido/index.html",
}
EVIDENCE = (
    "Running local AI on a gaming laptop",
    "An independent audit of AI review replies",
)
ABOUT_EVIDENCE = ("local AI gaming-laptop guide", "review-reply evidence audit")


def paragraph(path, starting):
    html = (ROOT / path).read_text(encoding="utf-8")
    match = re.search(r'<p(?: class="small-copy")?><strong>' +
                      re.escape(starting) + r'</strong>.*?</p>', html, re.S)
    if not match:
        raise AssertionError("Missing reviewed evidence paragraph in " + path)
    return match.group(0)


class Turn15EvidenceLinksTests(unittest.TestCase):
    def test_source_and_rendered_evidence_are_identical(self):
        for source, rendered, marker in (
            ("_source/home.html", "index.html", "Inspect the checks behind the work:"),
            ("_source/about.html", "about/index.html", "Methods behind the projects:"),
        ):
            with self.subTest(source=source):
                self.assertEqual(paragraph(source, marker),
                                 paragraph(rendered, marker))

    def test_visible_home_and_about_links_are_real_and_descriptive(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        about = (ROOT / "about/index.html").read_text(encoding="utf-8")
        for route, path in TARGETS.items():
            with self.subTest(route=route):
                self.assertTrue((ROOT / path).is_file())
                self.assertEqual(home.count('href="' + route + '"'), 1)
                self.assertEqual(about.count('href="' + route + '"'), 1)
                self.assertIn('rel="canonical" href="https://nolankido.com' + route + '"',
                              (ROOT / path).read_text(encoding="utf-8"))
        for name in EVIDENCE:
            self.assertIn(name, home)
        for name in ABOUT_EVIDENCE:
            self.assertIn(name, about)
        self.assertEqual(home.count('class="project-card"'), 3)
        self.assertEqual(home.count('class="destination destination-'), 4)

    def test_explanations_keep_evidence_limits(self):
        home = paragraph("index.html", "Inspect the checks behind the work:")
        about = paragraph("about/index.html", "Methods behind the projects:")
        self.assertIn("without claiming a measured laptop benchmark", home)
        self.assertIn("not production error rates", home)
        self.assertIn("Neither record establishes measured business impact", about)
        self.assertIn("laptop-speed benchmark", about)
        for body in (home, about):
            self.assertNotIn("\u2014", body)
            self.assertNotIn("proven savings", body.lower())

    def test_history_restores_only_sha_verified_predecessors(self):
        for path, (old_sha, current_sha) in history.BLOBS.items():
            with self.subTest(path=path):
                content = (ROOT / path).read_bytes()
                self.assertEqual(history.blob(content), current_sha)
                original = history.before(path, content)
                self.assertEqual(history.blob(original), old_sha)
                self.assertEqual(original, subprocess.check_output(
                    ["git", "show", history.PARENT + ":" + path], cwd=ROOT))
                self.assertEqual(history.before(path, original), original)
                self.assertEqual(
                    history.before(Path(path), content.decode("utf-8")),
                    original.decode("utf-8"))

    def test_unreviewed_mutations_are_not_hidden(self):
        for path in history.BLOBS:
            raw = (ROOT / path).read_bytes()
            for mutation in (raw + b"OTHER", b"OTHER" + raw, raw[1:]):
                self.assertEqual(history.before(path, mutation), mutation)
            self.assertEqual(history.before("other/" + path, raw), raw)
        self.assertEqual(history.before("unknown.bin", bytes([0, 255])),
                         bytes([0, 255]))


if __name__ == "__main__":
    unittest.main()
